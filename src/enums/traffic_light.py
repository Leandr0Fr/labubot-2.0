"""El veredicto del LLM sobre una oferta."""

from enum import StrEnum


class TrafficLight(StrEnum):
    """
    Tres colores.
    GREEN: Oferta compatible
    YELLOW: Oferta para revisar manualmente
    RED: Oferta no compatible.
    """

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
