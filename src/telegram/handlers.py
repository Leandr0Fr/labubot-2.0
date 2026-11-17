"""Lo que entra por el webhook: un mensaje o un botón, y qué contestarle."""

import sqlite3
import time

from src.config.settings import settings
from src.db.users import Users
from src.enums.callback import Callback
from src.enums.chat_state import ChatState
from src.enums.command import Command
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
    ALLOW_USAGE,
    ALREADY_ACTIVE,
    ALREADY_PAUSED,
    APPROVED,
    ASK_BLOCKED,
    ASK_PROFILE,
    ASK_TERMS,
    BACK_AGAIN,
    BLOCK_USAGE,
    BLOCKED_LIST,
    CALLBACK_SEPARATOR,
    CHAT_CLEARED,
    CLEAR_LOOKBACK,
    COMMAND_PREFIX,
    DELETE_BATCH,
    EMPTY_LIST,
    HELP,
    INPUT_SEPARATOR,
    LIST_SEPARATOR,
    MESSAGE_LIMIT,
    NO_USERNAME,
    NONE_CHANGED,
    PAUSE,
    PAUSED,
    PROFILE_CURRENT,
    PROFILE_EXTENSIONS,
    PROFILE_LOADED,
    PROFILE_MISSING,
    PROFILE_REPLACE_HINT,
    PROFILE_SAVED,
    PROFILE_TEMPLATE,
    REJECTED,
    REMOVED,
    RESUMED,
    SEARCH_QUEUED,
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
    replace_profile_keyboard,
    settings_keyboard,
)


def on_message(conn: sqlite3.Connection, telegram: Telegram, message: Message) -> None:
    """
    Contesta un mensaje privado según el comando o lo que espera el bot.

    A un usuario nuevo, pendiente, rechazado o que bloqueó el bot, cualquier
    mensaje se le contesta como un /start. "/settings@labubot_bot" vale como /settings.
    Args:
        conn: La conexión que abrió el webhook para este update.
        telegram: El cliente de la Bot API.
        message: El mensaje, tal como vino en el update.
    Raises:
        LabubotError: Si falla una llamada a la Bot API.
    """
    users = Users(conn)
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    user = users.get(chat_id)
    command = None
    arguments = ""
    if text.startswith(COMMAND_PREFIX):
        words = text.split(maxsplit=1)
        command = words[0].split("@")[0].removeprefix(COMMAND_PREFIX)
        if len(words) > 1:
            arguments = words[1]

    if command == Command.START or user is None or user["status"] in START_ONLY:
        _handle_start(users, telegram, message, user)
        return
    if command is not None:
        users.set_state(chat_id, ChatState.IDLE)
        _handle_command(
            users, telegram, user, command, arguments, message["message_id"]
        )
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
    telegram.send_message(chat_id, _changed_text(template, items, count))


def on_callback(
    conn: sqlite3.Connection, telegram: Telegram, callback: CallbackQuery
) -> None:
    """
    Atiende un botón: el panel, pedir una lista, pausa, o aprobar/rechazar.

    Los botones de quien no tiene acceso se ignoran.
    Args:
        conn: La conexión que abrió el webhook para este update.
        telegram: El cliente de la Bot API.
        callback: El callback_query, tal como vino en el update.
    Raises:
        LabubotError: Si falla una llamada a la Bot API.
    """
    # Primero: si después falla un edit, el botón no queda "cargando".
    telegram.answer_callback(callback["id"])
    users = Users(conn)
    callback_data = callback.get("data", "")
    chat_id = callback["message"]["chat"]["id"]
    message_id = callback["message"]["message_id"]

    if callback_data.startswith((Callback.APPROVE, Callback.REJECT)):
        _approve_or_reject(users, telegram, chat_id, message_id, callback_data)
        return

    user = users.get(chat_id)
    if user is None or user["status"] in START_ONLY:
        return
    match callback_data:
        case Callback.TERMS:
            text = _list_text(TERMS_LIST, users.terms(chat_id))
            keyboard = list_keyboard(Callback.TERMS_ADD, Callback.TERMS_REMOVE)
            telegram.edit_message(chat_id, message_id, text, keyboard)
        case Callback.BLOCKED:
            text = _list_text(BLOCKED_LIST, users.blocked_words(chat_id))
            keyboard = list_keyboard(Callback.BLOCKED_ADD, Callback.BLOCKED_REMOVE)
            telegram.edit_message(chat_id, message_id, text, keyboard)
        case Callback.TERMS_ADD:
            users.set_state(chat_id, ChatState.AWAITING_TERMS_ADD)
            telegram.edit_message(chat_id, message_id, ASK_TERMS, cancel_keyboard())
        case Callback.TERMS_REMOVE:
            users.set_state(chat_id, ChatState.AWAITING_TERMS_REMOVE)
            telegram.edit_message(chat_id, message_id, ASK_TERMS, cancel_keyboard())
        case Callback.BLOCKED_ADD:
            users.set_state(chat_id, ChatState.AWAITING_BLOCKED_ADD)
            telegram.edit_message(chat_id, message_id, ASK_BLOCKED, cancel_keyboard())
        case Callback.BLOCKED_REMOVE:
            users.set_state(chat_id, ChatState.AWAITING_BLOCKED_REMOVE)
            telegram.edit_message(chat_id, message_id, ASK_BLOCKED, cancel_keyboard())
        case Callback.PROFILE:
            _show_profile(users, telegram, user)
        case Callback.PROFILE_REPLACE:
            users.set_state(chat_id, ChatState.AWAITING_PROFILE)
            telegram.edit_message(chat_id, message_id, ASK_PROFILE, cancel_keyboard())
        case Callback.PAUSE | Callback.RESUME:
            status = UserStatus.PAUSED
            if callback_data == Callback.RESUME:
                status = UserStatus.ACTIVE
            users.set_status(chat_id, status)
            _edit_panel(users, telegram, chat_id, message_id)
        case Callback.MENU | Callback.CANCEL:
            users.set_state(chat_id, ChatState.IDLE)
            _edit_panel(users, telegram, chat_id, message_id)


def _handle_start(
    users: Users, telegram: Telegram, message: Message, user: User | None
) -> None:
    """
    Da de alta o saluda según cómo estaba el usuario antes de este mensaje.

    Un activo, o uno que había bloqueado el bot, queda activo y, si ya cargó el
    CV, se le encola una búsqueda.
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
        _request_approval(telegram, message)
        return

    match user["status"]:
        case UserStatus.PENDING:
            telegram.send_message(chat_id, STILL_PENDING)
            # Si el primer aviso al admin se perdió, este se lo vuelve a mostrar.
            _request_approval(telegram, message)
        case UserStatus.REJECTED:
            telegram.send_message(chat_id, REJECTED)
        case UserStatus.PAUSED:
            telegram.send_message(chat_id, BACK_AGAIN)
        case _:
            users.set_status(chat_id, UserStatus.ACTIVE)
            if not user["profile"]:
                telegram.send_message(chat_id, BACK_AGAIN)
                return
            users.request_search(chat_id)
            telegram.send_message(chat_id, f"{BACK_AGAIN}\n{SEARCH_QUEUED}")


def _handle_command(
    users: Users,
    telegram: Telegram,
    user: User,
    command: str,
    arguments: str,
    message_id: int,
) -> None:
    """
    Atiende un comando de un usuario active o paused.
    Args:
        users: El repositorio de usuarios.
        telegram: El cliente de la Bot API.
        user: El usuario que lo mandó.
        command: El comando sin la barra, como "settings".
        arguments: Lo que vino después del comando; "" si nada.
        message_id: El mensaje del comando; /clear borra de ahí para atrás.
    """
    chat_id = user["chat_id"]
    match command:
        case Command.SETTINGS:
            text, keyboard = _panel(users, user)
            telegram.send_message(chat_id, text, keyboard)
        case Command.PROFILE:
            _show_profile(users, telegram, user)
        case Command.ALLOW if not arguments:
            telegram.send_message(chat_id, ALLOW_USAGE)
        case Command.ALLOW:
            items = users.add_terms(chat_id, arguments.split(INPUT_SEPARATOR))
            count = len(users.terms(chat_id))
            telegram.send_message(chat_id, _changed_text(ADDED, items, count))
        case Command.BLOCK if not arguments:
            telegram.send_message(chat_id, BLOCK_USAGE)
        case Command.BLOCK:
            items = users.add_blocked_words(chat_id, arguments.split(INPUT_SEPARATOR))
            count = len(users.blocked_words(chat_id))
            telegram.send_message(chat_id, _changed_text(ADDED, items, count))
        case Command.TEMPLATE:
            telegram.send_message(chat_id, TEMPLATE_INTRO)
            # Sola en su mensaje, para copiarla o reenviarla entera.
            telegram.send_message(chat_id, PROFILE_TEMPLATE)
        case Command.PAUSE if user["status"] == UserStatus.PAUSED:
            telegram.send_message(chat_id, ALREADY_PAUSED)
        case Command.PAUSE:
            users.set_status(chat_id, UserStatus.PAUSED)
            telegram.send_message(chat_id, PAUSED)
        case Command.RESUME if user["status"] == UserStatus.ACTIVE:
            telegram.send_message(chat_id, ALREADY_ACTIVE)
        case Command.RESUME:
            users.set_status(chat_id, UserStatus.ACTIVE)
            telegram.send_message(chat_id, RESUMED)
        case Command.HELP:
            telegram.send_message(chat_id, HELP)
        case Command.CLEAR:
            _clear_chat(telegram, chat_id, message_id)
            telegram.send_message(chat_id, CHAT_CLEARED)
        case Command.USERS if chat_id == settings.admin_chat_id:
            telegram.send_message(chat_id, _users_text(users))
        case _:
            telegram.send_message(chat_id, UNKNOWN)


def _save_profile(users: Users, telegram: Telegram, message: Message) -> None:
    """
    Guarda el CV que llegó como texto o como archivo .md / .txt.

    Si no trae texto (una foto, un sticker, un .pdf), lo vuelve a pedir en vez de
    guardar un perfil vacío que dejaría al usuario fuera de la corrida.
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
    if not profile.strip():
        telegram.send_message(chat_id, ASK_PROFILE)
        return
    users.set_profile(chat_id, profile)
    users.set_state(chat_id, ChatState.IDLE)
    telegram.send_message(chat_id, PROFILE_SAVED)


def _request_approval(telegram: Telegram, message: Message) -> None:
    """
    Le manda al admin la solicitud de quien escribió, con los botones para decidir.
    Args:
        telegram: El cliente de la Bot API.
        message: El /start del solicitante; de ahí salen nombre, @ y chat.
    """
    sender = message["from"]
    chat_id = message["chat"]["id"]
    request = ADMIN_REQUEST.format(
        first_name=sender["first_name"],
        username=sender.get("username", NO_USERNAME),
        chat_id=chat_id,
    )
    telegram.send_message(settings.admin_chat_id, request, approval_keyboard(chat_id))


def _approve_or_reject(
    users: Users,
    telegram: Telegram,
    chat_id: int,
    message_id: int,
    callback_data: str,
) -> None:
    """
    Aprueba o rechaza una solicitud, si la decide el admin y sigue pendiente.

    Así un botón viejo no aprueba dos veces ni reactiva a un rechazado.
    Args:
        users: El repositorio de usuarios.
        telegram: El cliente de la Bot API.
        chat_id: El chat donde se tocó el botón; tiene que ser el del admin.
        message_id: El mensaje de la solicitud, que se edita sin botones.
        callback_data: "approve:{chat_id}" o "reject:{chat_id}".
    """
    if chat_id != settings.admin_chat_id:
        return
    action, applicant_id = callback_data.split(CALLBACK_SEPARATOR)
    applicant = users.get(int(applicant_id))
    if applicant is None or applicant["status"] != UserStatus.PENDING:
        return
    first_name = applicant["first_name"]
    username = applicant["username"] or NO_USERNAME

    if action == Callback.APPROVE:
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


def _changed_text(template: str, items: list[str], count: int) -> str:
    """
    La respuesta a un agregar o quitar de una lista.
    Args:
        template: ADDED o REMOVED.
        items: Lo que cambió de verdad; vacía si ya los tenía (o, al quitar, si no).
        count: Cuántos tiene ahora.
    Returns:
        str: Por ejemplo "Agregados: php, wordpress. Ahora tenés 34."
    """
    return template.format(items=", ".join(items) or NONE_CHANGED, count=count)


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


def _show_profile(users: Users, telegram: Telegram, user: User) -> None:
    """
    Muestra el CV cargado con un botón para reemplazarlo; sin CV, lo pide.

    Con CV no queda esperando el reemplazo: lo que el usuario escriba después no lo pisa.
    Args:
        users: El repositorio de usuarios.
        telegram: El cliente de la Bot API.
        user: El usuario, con su perfil.
    """
    chat_id = user["chat_id"]
    if not user["profile"]:
        users.set_state(chat_id, ChatState.AWAITING_PROFILE)
        telegram.send_message(chat_id, ASK_PROFILE, cancel_keyboard())
        return
    telegram.send_message(chat_id, PROFILE_CURRENT)
    for part in _split_message(user["profile"]):
        time.sleep(PAUSE)
        telegram.send_message(chat_id, part)
    time.sleep(PAUSE)
    telegram.send_message(chat_id, PROFILE_REPLACE_HINT, replace_profile_keyboard())


def _clear_chat(telegram: Telegram, chat_id: int, last_message_id: int) -> None:
    """
    Borra los últimos CLEAR_LOOKBACK mensajes del chat, del /clear para atrás.

    Los ids de un chat son correlativos: va por tandas de DELETE_BATCH, de lo más
    nuevo a lo más viejo, así lo reciente se borra aunque falle una tanda vieja.
    CLEAR_LOOKBACK cubre más de las 48 h que Telegram deja borrar.
    Args:
        telegram: El cliente de la Bot API.
        chat_id: El chat del usuario.
        last_message_id: El mensaje del /clear.
    Raises:
        LabubotError: Si Telegram rechaza una tanda o falla la red.
    """
    end = last_message_id + 1
    oldest = max(1, end - CLEAR_LOOKBACK)
    while end > oldest:
        start = max(oldest, end - DELETE_BATCH)
        telegram.delete_messages(chat_id, list(range(start, end)))
        end = start


def _split_message(text: str) -> list[str]:
    """
    Parte un texto largo en mensajes que entran en Telegram, por renglones.

    Un renglón que solo ya no entra se corta en pedazos de medio MESSAGE_LIMIT
    caracteres, que en UTF-16 nunca pasan el tope.
    Args:
        text: El texto, por ejemplo un CV.
    Returns:
        list[str]: Las partes, sin las que son solo espacios, que Telegram rechaza.
    """
    parts = []
    current = ""
    for line in text.splitlines(keepends=True):
        if current and _utf16_len(current + line) > MESSAGE_LIMIT:
            if current.strip():
                parts.append(current)
            current = ""
        while _utf16_len(line) > MESSAGE_LIMIT:
            parts.append(line[: MESSAGE_LIMIT // 2])
            line = line[MESSAGE_LIMIT // 2 :]
        current += line
    if current.strip():
        parts.append(current)
    return parts


def _utf16_len(text: str) -> int:
    """
    El largo de un texto como lo cuenta Telegram.
    Args:
        text: El texto.
    Returns:
        int: Unidades UTF-16: un emoji cuenta 2.
    """
    return len(text.encode("utf-16-le")) // 2
