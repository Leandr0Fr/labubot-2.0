"""El callback_data de cada botón del bot."""

from enum import StrEnum


class Callback(StrEnum):
    """
    Lo que Telegram devuelve cuando se toca un botón.
    TERMS / BLOCKED: Mostrar la lista de términos o de bloqueadas.
    TERMS_ADD / TERMS_REMOVE / BLOCKED_ADD / BLOCKED_REMOVE: Pedir qué agregar o quitar.
    PROFILE / PROFILE_REPLACE: Mostrar el CV o pedir el nuevo.
    PAUSE / RESUME: Pausar o reanudar las alertas.
    MENU / CANCEL: Volver al panel.
    APPROVE / REJECT: Decidir una solicitud; van seguidos de ":" y el chat_id.
    """

    TERMS = "terms"
    BLOCKED = "blocked"
    TERMS_ADD = "terms:add"
    TERMS_REMOVE = "terms:remove"
    BLOCKED_ADD = "blocked:add"
    BLOCKED_REMOVE = "blocked:remove"
    PROFILE = "profile"
    PROFILE_REPLACE = "profile:replace"
    PAUSE = "pause"
    RESUME = "resume"
    MENU = "menu"
    CANCEL = "cancel"
    APPROVE = "approve"
    REJECT = "reject"
