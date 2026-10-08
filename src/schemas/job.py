"""Las ofertas tal como las ve el clasificador."""

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
