"""En qué punto del alta está un usuario y si recibe ofertas."""

from enum import StrEnum


class UserStatus(StrEnum):
    """
    Cinco estados.
    PENDING: Pidió acceso y espera al admin.
    ACTIVE: Recibe ofertas, si ya cargó el perfil.
    PAUSED: Pausó las alertas con /pausa.
    REJECTED: El admin lo rechazó; no vuelve a pedir.
    BLOCKED: Bloqueó el bot: Telegram dio 403 al mandarle.
    """

    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    REJECTED = "rejected"
    BLOCKED = "blocked"
