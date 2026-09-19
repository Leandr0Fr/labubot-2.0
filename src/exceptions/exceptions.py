"""
Módulo de errores.
"""


class LabubotError(Exception):
    """Error base."""


class LabubotRequestError(LabubotError):
    """Fallo de red o respuesta inesperada."""


class LabubotRateLimitError(LabubotError):
    """
    El sitio devolvió 429 y se agotaron los reintentos.

    No es un error de código: es la señal de que hay que bajar el ritmo.
    A diferencia de un ban, se cura solo esperando.
    """


class LabubotLLMError(LabubotError):
    """El LLM falló, agotó su cuota o devolvió algo que no es JSON."""
