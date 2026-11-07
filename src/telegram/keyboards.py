"""Los inline keyboards del bot: el reply_markup de cada mensaje con botones."""

from src.enums.user_status import UserStatus
from src.schemas.user import User
from src.telegram.constants import (
    BUTTON_ADD,
    BUTTON_APPROVE,
    BUTTON_BACK,
    BUTTON_BLOCKED,
    BUTTON_CANCEL,
    BUTTON_PAUSE,
    BUTTON_PROFILE,
    BUTTON_REJECT,
    BUTTON_REMOVE,
    BUTTON_RESUME,
    BUTTON_TERMS,
)


def settings_keyboard(user: User) -> dict:
    """
    Los cuatro botones del panel /settings.
    Args:
        user: El usuario; Pausar o Reanudar según su status.
    Returns:
        dict: El reply_markup.
    """
    toggle = {"text": BUTTON_PAUSE, "callback_data": "pause"}
    if user["status"] == UserStatus.PAUSED:
        toggle = {"text": BUTTON_RESUME, "callback_data": "resume"}
    return {
        "inline_keyboard": [
            [
                {"text": BUTTON_TERMS, "callback_data": "terms"},
                {"text": BUTTON_BLOCKED, "callback_data": "blocked"},
            ],
            [{"text": BUTTON_PROFILE, "callback_data": "profile"}, toggle],
        ]
    }


def list_keyboard(kind: str) -> dict:
    """
    Agregar, Quitar y Volver de una lista.
    Args:
        kind: "terms" o "blocked".
    Returns:
        dict: El reply_markup.
    """
    return {
        "inline_keyboard": [
            [
                {"text": BUTTON_ADD, "callback_data": f"{kind}:add"},
                {"text": BUTTON_REMOVE, "callback_data": f"{kind}:remove"},
            ],
            [{"text": BUTTON_BACK, "callback_data": "menu"}],
        ]
    }


def cancel_keyboard() -> dict:
    """
    Un solo botón, para salir de un "Mandame…".
    Returns:
        dict: El reply_markup con ✖ Cancelar.
    """
    return {"inline_keyboard": [[{"text": BUTTON_CANCEL, "callback_data": "cancel"}]]}


def approval_keyboard(chat_id: int) -> dict:
    """
    Aprobar y Rechazar la solicitud de un chat.
    Args:
        chat_id: El chat que pidió acceso.
    Returns:
        dict: El reply_markup.
    """
    return {
        "inline_keyboard": [
            [
                {"text": BUTTON_APPROVE, "callback_data": f"approve:{chat_id}"},
                {"text": BUTTON_REJECT, "callback_data": f"reject:{chat_id}"},
            ]
        ]
    }
