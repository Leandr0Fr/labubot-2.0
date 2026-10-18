"""Parsea el JSON de la búsqueda de Workable."""

import json
from datetime import datetime

from bs4 import BeautifulSoup

from src.portals.workable.constants import DESCRIPTION_SECTIONS
from src.schemas.job import Offer


def extract_offers(raw: str, since: datetime) -> list[Offer]:
    """
    Extrae las ofertas publicadas desde `since`, ya con su descripción.
    Args:
        raw: JSON devuelto por /api/v1/jobs.
        since: Momento (UTC) a partir del cual una oferta cuenta como reciente.
    Returns:
        list[Offer]: Las ofertas recientes de la página.
    """
    offers: list[Offer] = []
    for job in json.loads(raw)["jobs"]:
        published_at = datetime.fromisoformat(job["created"])
        if published_at < since:
            continue
        parts = []
        for section in DESCRIPTION_SECTIONS:
            parts.append(job[section] or "")
        description = BeautifulSoup("\n".join(parts), "html.parser")
        offers.append(
            Offer(
                title=job["title"].strip(),
                description=description.get_text(separator="\n", strip=True),
                url=job["url"],
            )
        )
    return offers


def extract_next_page_token(raw: str) -> str | None:
    """
    Lee el token de la página siguiente.
    Args:
        raw: JSON devuelto por /api/v1/jobs.
    Returns:
        str | None: El token, o None si esta era la última página.
    """
    return json.loads(raw).get("nextPageToken")
