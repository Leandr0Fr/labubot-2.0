"""El veredicto del LLM sobre una oferta."""

from enum import StrEnum


class TrafficLight(StrEnum):
    """
    Tres colores, sin puntajes.

    Un número del 0 al 100 finge una precisión que no existe: nadie sabe si un 73
    es mejor que un 68. Tres colores se leen de un vistazo y es lo que uno decide
    de verdad al mirar un aviso: le entro, lo miro después, o paso.
    """

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
