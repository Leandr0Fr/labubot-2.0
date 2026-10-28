"""Parsea el JSON de la API GraphQL de Indeed."""

import html
import json
from typing import Any

from bs4 import BeautifulSoup

from src.exceptions.exceptions import LabubotRequestError
from src.portals.indeed.constants import JOB_URL
from src.schemas.job import Offer


def _search(raw: str) -> dict[str, Any]:
    """
    Decodifica la respuesta y devuelve el nodo jobSearch.
    Args:
        raw: JSON devuelto por la API GraphQL.
    Returns:
        dict[str, Any]: El nodo jobSearch.
    Raises:
        LabubotRequestError: Si GraphQL devolvió errores.
    """
    data = json.loads(raw)
    if data.get("errors"):
        raise LabubotRequestError(f"Indeed devolvió errores: {data['errors']}")
    return data["data"]["jobSearch"]


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
    for result in _search(raw)["results"]:
        job = result["job"]
        # Las remotas vienen como "Desde casa".
        location = job["location"]["formatted"]["long"]
        description = BeautifulSoup(job["description"]["html"], "html.parser")
        text = description.get_text(separator="\n", strip=True)
        offers.append(
            Offer(
                title=html.unescape(job["title"]).strip(),
                description=f"Ubicación: {location}\n{text}",
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
    return _search(raw)["pageInfo"]["nextCursor"]
