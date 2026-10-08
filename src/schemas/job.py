"""Las ofertas, de tarjeta suelta a oferta evaluada."""

from typing import NotRequired, TypedDict


class JobCard(TypedDict):
    """
    Una oferta como viene en el listado: lo poco que entra en la tarjeta.

    No alcanza para decidir nada. El título miente seguido ("Data Scientist" que
    por dentro pide Python y nada de ciencia de datos): para eso está JobDetail.
    """

    id: str
    title: str
    company: str
    location: str
    date: str
    url: str


class Criteria(TypedDict):
    """
    Los campos estructurados que el portal publica en el detalle.

    Vienen etiquetados por la propia web (no los inferimos del título), así que
    `seniority` acá es lo que la empresa cargó en el formulario, no una adivinanza.
    """

    seniority: NotRequired[str]
    employment_type: NotRequired[str]


class JobDetail(TypedDict):
    """La oferta completa: descripción larga, criterios y competencia."""

    description: str
    criteria: Criteria
    applicants: int | None


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
