"""Parsea el JSON de la API GraphQL de Indeed."""

import html
import json
from typing import Any

from bs4 import BeautifulSoup

from src.exceptions.exceptions import LabubotRequestError
from src.portals.indeed.constants import JOB_URL
from src.schemas.job import Offer


def extract_offers(raw: str) -> list[Offer]:
    """
    Extrae las ofertas de una página de la búsqueda, ya con su descripción.
    Args:
        raw: JSON devuelto por la API GraphQL.
    Returns:
        list[Offer]: Una por oferta, con la ubicación en la primera línea de la
        descripción; vacía si la página no traía ninguna.
    Raises:
        LabubotRequestError: Si GraphQL devolvió errores.
    """
    offers: list[Offer] = []
    for result in _parse_job_search(raw)["results"]:
        job = result["job"]
        # Las remotas vienen como "Desde casa".
        location = job["location"]["formatted"]["long"]
        soup = BeautifulSoup(job["description"]["html"], "html.parser")
        description = soup.get_text(separator="\n", strip=True)
        offers.append(
            Offer(
                title=html.unescape(job["title"]).strip(),
                description=f"Ubicación: {location}\n{description}",
                url=JOB_URL.format(job_id=job["key"]),
            )
        )
    return offers


def extract_next_cursor(raw: str) -> str | None:
    """
    Lee el cursor de la página siguiente.
    Args:
        raw: JSON devuelto por la API GraphQL.
    Returns:
        str | None: El cursor, o None si esta era la última página.
    Raises:
        LabubotRequestError: Si GraphQL devolvió errores.
    """
    return _parse_job_search(raw)["pageInfo"]["nextCursor"]


def _parse_job_search(raw: str) -> dict[str, Any]:
    """
    Decodifica la respuesta y devuelve el nodo jobSearch.
    Args:
        raw: JSON devuelto por la API GraphQL.
    Returns:
        dict[str, Any]: El nodo jobSearch.
    Raises:
        LabubotRequestError: Si GraphQL devolvió errores.
    """
    response = json.loads(raw)
    if response.get("errors"):
        raise LabubotRequestError(f"Indeed devolvió errores: {response['errors']}")
    return response["data"]["jobSearch"]
