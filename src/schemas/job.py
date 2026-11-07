"""Las ofertas tal como las ve el clasificador, y lo que se sabe antes de bajarlas."""

from typing import TypedDict


class Offer(TypedDict):
    """
    Oferta.
    Title: Titulo de la oferta.
    description: Detalle de la oferta.
    url: URL de la oferta.
    """

    title: str
    description: str
    url: str


class Found(TypedDict):
    """
    Una oferta de un listado, antes de bajar su descripción.
    title: Título de la oferta.
    term: La palabra clave que la trajo; None = "Otros portales".
    portal: Nombre de la clase del portal, para pedirle la descripción a esa instancia.
    """

    title: str
    term: str | None
    portal: str
