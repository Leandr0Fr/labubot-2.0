"""Parsea el JSON de la API de Jobicy."""

import json
from datetime import datetime

from bs4 import BeautifulSoup

from src.schemas.job import Offer


def extract_offers(raw: str, since: datetime) -> list[Offer]:
    """
    Extrae las ofertas publicadas desde `since`, ya con su descripción.
    Args:
        raw: JSON devuelto por /api/v2/remote-jobs.
        since: Momento (con zona horaria) a partir del cual una oferta cuenta
            como reciente.
    Returns:
        list[Offer]: Las ofertas recientes de la página.
    """
    offers: list[Offer] = []
    for job in json.loads(raw)["jobs"]:
        published_at = datetime.fromisoformat(job["pubDate"])
        if published_at < since:
            continue
        description = BeautifulSoup(job["jobDescription"], "html.parser")
        offers.append(
            Offer(
                title=job["jobTitle"].strip(),
                description=description.get_text(separator="\n", strip=True),
                url=job["url"],
            )
        )
    return offers


def extract_next_cursor(raw: str) -> str | None:
    """
    Lee el cursor de la página siguiente.
    Args:
        raw: JSON devuelto por /api/v2/remote-jobs.
    Returns:
        str | None: El cursor, o None si esta era la última página.
    """
    return json.loads(raw)["nextCursor"]
