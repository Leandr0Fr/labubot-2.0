"""El veredicto del LLM sobre una oferta."""

from enum import StrEnum


class TrafficLight(StrEnum):
    """
    El color que el LLM le pone a una oferta.
    GREEN: Oferta compatible.
    YELLOW: Oferta para revisar a mano.
    RED: Oferta no compatible.
    """

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
