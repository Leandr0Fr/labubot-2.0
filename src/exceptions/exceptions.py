"""Las excepciones propias de labubot."""


class LabubotError(Exception):
    """Base de todas las excepciones de labubot."""


class LabubotRequestError(LabubotError):
    """Fallo de red o respuesta inesperada."""


class LabubotRateLimitError(LabubotError):
    """El sitio devolvió 429: hay que bajar el ritmo, y se cura esperando."""


class LabubotForbiddenError(LabubotError):
    """El sitio devolvió 403; en Telegram, que el usuario bloqueó el bot."""
