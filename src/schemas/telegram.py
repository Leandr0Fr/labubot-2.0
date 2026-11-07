"""Las partes del Update de Telegram que usa el bot, sin validar."""

from typing import NotRequired, TypedDict


class TelegramUser(TypedDict):
    """Quién manda el mensaje."""

    first_name: str
    username: NotRequired[str]


class Chat(TypedDict):
    """
    El chat del mensaje.
    type: "private", "group", "supergroup" o "channel".
    """

    id: int
    type: str


class Document(TypedDict):
    """Un archivo adjunto."""

    file_id: str
    file_name: NotRequired[str]


# "from" es palabra reservada: solo entra con la sintaxis funcional.
Message = TypedDict(
    "Message",
    {
        "message_id": int,
        "from": TelegramUser,
        "chat": Chat,
        "text": NotRequired[str],
        "document": NotRequired[Document],
    },
)

CallbackQuery = TypedDict(
    "CallbackQuery",
    {
        "id": str,
        "message": Message,
        "data": NotRequired[str],
    },
)
