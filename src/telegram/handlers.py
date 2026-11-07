"""Lo que entra por el webhook: un mensaje o un botón, y qué contestarle."""

import sqlite3

from src.config.settings import settings
from src.db.users import Users
from src.enums.chat_state import ChatState
from src.enums.user_status import UserStatus
from src.schemas.telegram import CallbackQuery, Message
from src.schemas.user import User
from src.telegram.bot import Telegram
from src.telegram.constants import (
    ADDED,
    ADMIN_APPROVED,
    ADMIN_REJECTED,
    ADMIN_REQUEST,
    ALERTS_ACTIVE,
    ALERTS_PAUSED,
    APPROVED,
    ASK_BLOCKED,
    ASK_PROFILE,
    ASK_TERMS,
    BACK_AGAIN,
    BLOCKED_LIST,
    EMPTY_LIST,
    HELP,
    INPUT_SEPARATOR,
    LIST_SEPARATOR,
    NO_USERNAME,
    NONE_CHANGED,
    PAUSED,
    PROFILE_EXTENSIONS,
    PROFILE_LOADED,
    PROFILE_MISSING,
    PROFILE_SAVED,
    PROFILE_TEMPLATE,
    REJECTED,
    REMOVED,
    RESUMED,
    SETTINGS_PANEL,
    START_ONLY,
    STATUS_LABELS,
    STILL_PENDING,
    TEMPLATE_INTRO,
    TERMS_LIST,
    UNKNOWN,
    USER_LINE,
    USERS_HEADER,
    WELCOME_PENDING,
)
from src.telegram.keyboards import (
    approval_keyboard,
    cancel_keyboard,
    list_keyboard,
    settings_keyboard,
)


def on_message(conn: sqlite3.Connection, telegram: Telegram, message: Message) -> None:
    """
    Contesta un mensaje privado según el comando o lo que espera el bot.
    Args:
        conn: La conexión que abrió el webhook para este update.
        telegram: El cliente de la Bot API.
        message: El mensaje, tal como vino en el update.
    """
    users = Users(conn)
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    user = users.get(chat_id)

    if text.startswith("/start") or user is None or user["status"] in START_ONLY:
        _handle_start(users, telegram, message, user)
        return
    if text.startswith("/"):
        users.set_state(chat_id, ChatState.IDLE)
        # "/settings@labubot_bot" también es /settings.
        _handle_command(users, telegram, user, text.split()[0].split("@")[0])
        return

    match user["state"]:
        case ChatState.AWAITING_PROFILE:
            _save_profile(users, telegram, message)
            return
        case ChatState.AWAITING_TERMS_ADD:
            items = users.add_terms(chat_id, text.split(INPUT_SEPARATOR))
            count = len(users.terms(chat_id))
            template = ADDED
        case ChatState.AWAITING_TERMS_REMOVE:
            items = users.remove_terms(chat_id, text.split(INPUT_SEPARATOR))
            count = len(users.terms(chat_id))
            template = REMOVED
        case ChatState.AWAITING_BLOCKED_ADD:
            items = users.add_blocked_words(chat_id, text.split(INPUT_SEPARATOR))
            count = len(users.blocked_words(chat_id))
            template = ADDED
        case ChatState.AWAITING_BLOCKED_REMOVE:
            items = users.remove_blocked_words(chat_id, text.split(INPUT_SEPARATOR))
            count = len(users.blocked_words(chat_id))
            template = REMOVED
        case _:
            telegram.send_message(chat_id, UNKNOWN)
            return
    users.set_state(chat_id, ChatState.IDLE)
    # Vacía si ya los tenía (o, al quitar, si no los tenía).
    reply = template.format(items=", ".join(items) or NONE_CHANGED, count=count)
    telegram.send_message(chat_id, reply)


def on_callback(
    conn: sqlite3.Connection, telegram: Telegram, callback: CallbackQuery
) -> None:
    """
    Atiende un botón: el panel, pedir una lista, pausa, o aprobar/rechazar.
    Args:
        conn: La conexión que abrió el webhook para este update.
        telegram: El cliente de la Bot API.
        callback: El callback_query, tal como vino en el update.
    """
    # Primero: si después falla un edit, el botón no queda "cargando".
    telegram.answer_callback(callback["id"])
    users = Users(conn)
    callback_data = callback.get("data", "")
    chat_id = callback["message"]["chat"]["id"]
    message_id = callback["message"]["message_id"]

    if callback_data.startswith(("approve:", "reject:")):
        _approve_or_reject(users, telegram, chat_id, message_id, callback_data)
        return

    user = users.get(chat_id)
    if user is None or user["status"] in START_ONLY:
        return
    match callback_data:
        case "terms":
            text = _list_text(TERMS_LIST, users.terms(chat_id))
            telegram.edit_message(chat_id, message_id, text, list_keyboard("terms"))
        case "blocked":
            text = _list_text(BLOCKED_LIST, users.blocked_words(chat_id))
            telegram.edit_message(chat_id, message_id, text, list_keyboard("blocked"))
        case "terms:add":
            users.set_state(chat_id, ChatState.AWAITING_TERMS_ADD)
            telegram.edit_message(chat_id, message_id, ASK_TERMS, cancel_keyboard())
        case "terms:remove":
            users.set_state(chat_id, ChatState.AWAITING_TERMS_REMOVE)
            telegram.edit_message(chat_id, message_id, ASK_TERMS, cancel_keyboard())
        case "blocked:add":
            users.set_state(chat_id, ChatState.AWAITING_BLOCKED_ADD)
            telegram.edit_message(chat_id, message_id, ASK_BLOCKED, cancel_keyboard())
        case "blocked:remove":
            users.set_state(chat_id, ChatState.AWAITING_BLOCKED_REMOVE)
            telegram.edit_message(chat_id, message_id, ASK_BLOCKED, cancel_keyboard())
        case "profile":
            users.set_state(chat_id, ChatState.AWAITING_PROFILE)
            telegram.edit_message(chat_id, message_id, ASK_PROFILE, cancel_keyboard())
        case "pause" | "resume":
            status = UserStatus.PAUSED
            if callback_data == "resume":
                status = UserStatus.ACTIVE
            users.set_status(chat_id, status)
            _edit_panel(users, telegram, chat_id, message_id)
        case "menu" | "cancel":
            users.set_state(chat_id, ChatState.IDLE)
            _edit_panel(users, telegram, chat_id, message_id)


def _handle_start(
    users: Users, telegram: Telegram, message: Message, user: User | None
) -> None:
    """
    Da de alta o saluda según cómo estaba el usuario antes de este mensaje.
    Args:
        users: El repositorio de usuarios.
        telegram: El cliente de la Bot API.
        message: El mensaje que llegó; de ahí salen nombre y @.
        user: Cómo estaba antes; None si nunca había escrito.
    """
    sender = message["from"]
    chat_id = message["chat"]["id"]
    users.register(chat_id, sender.get("username"), sender["first_name"])
    users.set_state(chat_id, ChatState.IDLE)

    if user is None and chat_id == settings.admin_chat_id:
        users.set_status(chat_id, UserStatus.ACTIVE)
        telegram.send_message(chat_id, APPROVED)
        return
    if user is None:
        first_name = sender["first_name"]
        telegram.send_message(chat_id, WELCOME_PENDING.format(first_name=first_name))
        request = ADMIN_REQUEST.format(
            first_name=first_name,
            username=sender.get("username", NO_USERNAME),
            chat_id=chat_id,
        )
        telegram.send_message(
            settings.admin_chat_id, request, approval_keyboard(chat_id)
        )
        return

    match user["status"]:
        case UserStatus.PENDING:
            telegram.send_message(chat_id, STILL_PENDING)
        case UserStatus.REJECTED:
            telegram.send_message(chat_id, REJECTED)
        case UserStatus.BLOCKED:
            users.set_status(chat_id, UserStatus.ACTIVE)
            telegram.send_message(chat_id, BACK_AGAIN)
        case _:
            telegram.send_message(chat_id, BACK_AGAIN)


def _handle_command(users: Users, telegram: Telegram, user: User, command: str) -> None:
    """
    Atiende un comando de un usuario active o paused.
    Args:
        users: El repositorio de usuarios.
        telegram: El cliente de la Bot API.
        user: El usuario que lo mandó.
        command: El comando, como "/settings".
    """
    chat_id = user["chat_id"]
    match command:
        case "/settings":
            text, keyboard = _panel(users, user)
            telegram.send_message(chat_id, text, keyboard)
        case "/perfil":
            users.set_state(chat_id, ChatState.AWAITING_PROFILE)
            telegram.send_message(chat_id, ASK_PROFILE)
        case "/template":
            telegram.send_message(chat_id, TEMPLATE_INTRO)
            # Sola en su mensaje, para copiarla o reenviarla entera.
            telegram.send_message(chat_id, PROFILE_TEMPLATE)
        case "/pausa":
            users.set_status(chat_id, UserStatus.PAUSED)
            telegram.send_message(chat_id, PAUSED)
        case "/reanudar":
            users.set_status(chat_id, UserStatus.ACTIVE)
            telegram.send_message(chat_id, RESUMED)
        case "/ayuda":
            telegram.send_message(chat_id, HELP)
        case "/usuarios" if chat_id == settings.admin_chat_id:
            telegram.send_message(chat_id, _users_text(users))
        case _:
            telegram.send_message(chat_id, UNKNOWN)


def _save_profile(users: Users, telegram: Telegram, message: Message) -> None:
    """
    Guarda el CV que llegó como texto o como archivo .md / .txt.
    Args:
        users: El repositorio de usuarios.
        telegram: El cliente de la Bot API.
        message: El mensaje con el CV.
    """
    chat_id = message["chat"]["id"]
    profile = message.get("text", "")
    document = message.get("document")
    if document and document.get("file_name", "").lower().endswith(PROFILE_EXTENSIONS):
        profile = telegram.download_file(document["file_id"])
    # Una foto, un sticker o un .pdf dejarían el perfil vacío y al usuario
    # fuera de la corrida sin aviso.
    if not profile.strip():
        telegram.send_message(chat_id, ASK_PROFILE)
        return
    users.set_profile(chat_id, profile)
    users.set_state(chat_id, ChatState.IDLE)
    telegram.send_message(chat_id, PROFILE_SAVED.format(chars=len(profile)))


def _approve_or_reject(
    users: Users,
    telegram: Telegram,
    chat_id: int,
    message_id: int,
    callback_data: str,
) -> None:
    """
    Aprueba o rechaza una solicitud, si la decide el admin y sigue pendiente.
    Args:
        users: El repositorio de usuarios.
        telegram: El cliente de la Bot API.
        chat_id: El chat donde se tocó el botón; tiene que ser el del admin.
        message_id: El mensaje de la solicitud, que se edita sin botones.
        callback_data: "approve:{chat_id}" o "reject:{chat_id}".
    """
    if chat_id != settings.admin_chat_id:
        return
    action, applicant_id = callback_data.split(":")
    applicant = users.get(int(applicant_id))
    # Un botón viejo no aprueba dos veces ni reactiva a un rechazado.
    if applicant is None or applicant["status"] != UserStatus.PENDING:
        return
    first_name = applicant["first_name"]
    username = applicant["username"] or NO_USERNAME

    if action == "approve":
        users.set_status(applicant["chat_id"], UserStatus.ACTIVE)
        text = ADMIN_APPROVED.format(first_name=first_name, username=username)
        telegram.edit_message(chat_id, message_id, text)
        # Después del edit: si ya bloqueó el bot, la solicitud igual queda resuelta.
        telegram.send_message(applicant["chat_id"], APPROVED)
        return
    users.set_status(applicant["chat_id"], UserStatus.REJECTED)
    text = ADMIN_REJECTED.format(first_name=first_name, username=username)
    telegram.edit_message(chat_id, message_id, text)


def _edit_panel(
    users: Users, telegram: Telegram, chat_id: int, message_id: int
) -> None:
    """
    Vuelve a dibujar el panel sobre el mismo mensaje.
    Args:
        users: El repositorio de usuarios.
        telegram: El cliente de la Bot API.
        chat_id: El chat del usuario.
        message_id: El mensaje del panel.
    """
    text, keyboard = _panel(users, users.get(chat_id))
    telegram.edit_message(chat_id, message_id, text, keyboard)


def _panel(users: Users, user: User) -> tuple[str, dict]:
    """
    El texto y los botones del panel /settings.
    Args:
        users: El repositorio de usuarios.
        user: El usuario, con su estado y su perfil al día.
    Returns:
        tuple[str, dict]: El texto con los contadores y el reply_markup.
    """
    chat_id = user["chat_id"]
    profile_mark = PROFILE_MISSING
    if user["profile"]:
        profile_mark = PROFILE_LOADED
    alerts = ALERTS_ACTIVE
    if user["status"] == UserStatus.PAUSED:
        alerts = ALERTS_PAUSED
    text = SETTINGS_PANEL.format(
        terms=len(users.terms(chat_id)),
        blocked=len(users.blocked_words(chat_id)),
        profile_mark=profile_mark,
        alerts=alerts,
    )
    return text, settings_keyboard(user)


def _list_text(template: str, items: list[str]) -> str:
    """
    Una lista del panel: el título con la cantidad y los ítems separados por " · ".
    Args:
        template: TERMS_LIST o BLOCKED_LIST.
        items: Los términos o las palabras, en orden alfabético.
    Returns:
        str: El texto del mensaje.
    """
    return template.format(
        count=len(items), items=LIST_SEPARATOR.join(items) or EMPTY_LIST
    )


def _users_text(users: Users) -> str:
    """
    El texto de /usuarios: cada usuario con su @, su estado y su chat_id.
    Args:
        users: El repositorio de usuarios.
    Returns:
        str: El encabezado y un bloque por usuario, separados por un renglón en blanco.
    """
    all_users = users.all()
    blocks = [USERS_HEADER.format(count=len(all_users))]
    for user in all_users:
        username = ""
        if user["username"]:
            username = f" @{user['username']}"
        blocks.append(
            USER_LINE.format(
                first_name=user["first_name"],
                username=username,
                status=STATUS_LABELS[user["status"]],
                chat_id=user["chat_id"],
            )
        )
    return "\n\n".join(blocks)
