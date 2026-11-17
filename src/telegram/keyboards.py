"""Los inline keyboards del bot: el reply_markup de cada mensaje con botones."""

from src.enums.callback import Callback
from src.enums.user_status import UserStatus
from src.schemas.user import User
from src.telegram.constants import (
    BUTTON_ADD,
    BUTTON_APPROVE,
    BUTTON_BACK,
    BUTTON_BLOCKED,
    BUTTON_CANCEL,
    BUTTON_IT_OFF,
    BUTTON_IT_ON,
    BUTTON_PAUSE,
    BUTTON_PROFILE,
    BUTTON_REJECT,
    BUTTON_REMOVE,
    BUTTON_REPLACE,
    BUTTON_RESUME,
    BUTTON_TERMS,
    CALLBACK_SEPARATOR,
)


def settings_keyboard(user: User) -> dict:
    """
    Los botones del panel /settings.
    Args:
        user: El usuario; Pausar o Reanudar según su status, y sumar o quitar
            los portales IT según los tenga.
    Returns:
        dict: El reply_markup.
    """
    toggle = {"text": BUTTON_PAUSE, "callback_data": Callback.PAUSE}
    if user["status"] == UserStatus.PAUSED:
        toggle = {"text": BUTTON_RESUME, "callback_data": Callback.RESUME}
    it_toggle = {"text": BUTTON_IT_ON, "callback_data": Callback.IT_ON}
    if user["it"]:
        it_toggle = {"text": BUTTON_IT_OFF, "callback_data": Callback.IT_OFF}
    return {
        "inline_keyboard": [
            [
                {"text": BUTTON_TERMS, "callback_data": Callback.TERMS},
                {"text": BUTTON_BLOCKED, "callback_data": Callback.BLOCKED},
            ],
            [{"text": BUTTON_PROFILE, "callback_data": Callback.PROFILE}, toggle],
            [it_toggle],
        ]
    }


def list_keyboard(add: Callback, remove: Callback) -> dict:
    """
    Agregar, Quitar y Volver de una lista.
    Args:
        add: El botón de agregar de esa lista, como Callback.TERMS_ADD.
        remove: El botón de quitar de esa lista, como Callback.TERMS_REMOVE.
    Returns:
        dict: El reply_markup.
    """
    return {
        "inline_keyboard": [
            [
                {"text": BUTTON_ADD, "callback_data": add},
                {"text": BUTTON_REMOVE, "callback_data": remove},
            ],
            [{"text": BUTTON_BACK, "callback_data": Callback.MENU}],
        ]
    }


def cancel_keyboard() -> dict:
    """
    Un solo botón, para salir de un "Mandame…".
    Returns:
        dict: El reply_markup con ✖ Cancelar.
    """
    return {
        "inline_keyboard": [[{"text": BUTTON_CANCEL, "callback_data": Callback.CANCEL}]]
    }


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
                {
                    "text": BUTTON_APPROVE,
                    "callback_data": f"{Callback.APPROVE}{CALLBACK_SEPARATOR}{chat_id}",
                },
                {
                    "text": BUTTON_REJECT,
                    "callback_data": f"{Callback.REJECT}{CALLBACK_SEPARATOR}{chat_id}",
                },
            ]
        ]
    }


def replace_profile_keyboard() -> dict:
    """
    Un solo botón, para reemplazar el CV que se acaba de mostrar.
    Returns:
        dict: El reply_markup con ✏️ Reemplazar.
    """
    return {
        "inline_keyboard": [
            [{"text": BUTTON_REPLACE, "callback_data": Callback.PROFILE_REPLACE}]
        ]
    }
