"""Un usuario del bot, tal como está en la tabla users."""

from typing import TypedDict


class User(TypedDict):
    """
    Una fila de users.
    chat_id: Chat privado con el bot; es también el id del usuario de Telegram.
    username: El @, sin la arroba; None si no tiene.
    first_name: Nombre que muestra Telegram.
    status: Un UserStatus.
    profile: El CV; '' si todavía no lo cargó.
    state: Un ChatState: qué espera el bot del próximo mensaje.
    created_at: Alta, ISO 8601 en UTC.
    it: 1 si también le llegan los portales de tecnología; 0 si no.
    """

    chat_id: int
    username: str | None
    first_name: str
    status: str
    profile: str
    state: str
    created_at: str
    it: int
