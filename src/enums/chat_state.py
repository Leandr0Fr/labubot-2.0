"""Qué espera el bot del próximo mensaje de un chat."""

from enum import StrEnum


class ChatState(StrEnum):
    """
    Lo que se guarda en users.state.
    IDLE: Nada; un texto suelto no se entiende.
    AWAITING_PROFILE: El CV, como texto o archivo.
    AWAITING_TERMS_ADD / AWAITING_TERMS_REMOVE: Términos separados por coma.
    AWAITING_BLOCKED_ADD / AWAITING_BLOCKED_REMOVE: Palabras separadas por coma.
    """

    IDLE = ""
    AWAITING_PROFILE = "awaiting_profile"
    AWAITING_TERMS_ADD = "awaiting_terms_add"
    AWAITING_TERMS_REMOVE = "awaiting_terms_remove"
    AWAITING_BLOCKED_ADD = "awaiting_blocked_add"
    AWAITING_BLOCKED_REMOVE = "awaiting_blocked_remove"
