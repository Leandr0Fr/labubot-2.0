"""El esquema de semáforos: lo que el clasificador devuelve por oferta."""

from typing import TypedDict

from src.enums.traffic_light import TrafficLight


class Verdict(TypedDict):
    """
    Lo que el LLM opina de una oferta.

    `reason` es lo que se lee primero y muchas veces lo único que se lee: tiene
    que alcanzar para decidir si abrir el link o seguir de largo.
    """

    light: TrafficLight
    reason: str
    pros: list[str]
    cons: list[str]
