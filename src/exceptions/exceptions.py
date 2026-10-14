"""
Módulo de errores.
"""


class LabubotError(Exception):
    """Error base."""


class LabubotRequestError(LabubotError):
    """Fallo de red o respuesta inesperada."""


class LabubotRateLimitError(LabubotError):
    """
    El sitio devolvió 429.

    No es un error de código: es la señal de que hay que bajar el ritmo.
    A diferencia de un ban, se cura solo esperando. La excepción es OpenAI sin
    créditos (`insufficient_quota`): también llega como 429 y ese no se cura.
    """
