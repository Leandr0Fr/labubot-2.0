"""Las ofertas, de tarjeta suelta a oferta evaluada."""

from typing import NotRequired, TypedDict

from src.schemas.verdict import Verdict


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


# Lo que el clasificador recibe: la tarjeta y su detalle, todavía sin veredicto.
Offer = tuple[JobCard, JobDetail]


class Job(TypedDict):
    """Tarjeta + detalle + veredicto: lo que finalmente se guarda y se muestra."""

    id: str
    title: str
    company: str
    location: str
    date: str
    url: str
    description: str
    criteria: Criteria
    applicants: int | None
    verdict: Verdict
