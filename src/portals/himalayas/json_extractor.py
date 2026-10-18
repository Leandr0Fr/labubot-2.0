"""Parsea el JSON de la búsqueda de Himalayas."""

import json

from bs4 import BeautifulSoup

from src.schemas.job import Offer


def extract_offers(raw: str, since: float) -> list[Offer]:
    """
    Extrae las ofertas publicadas desde `since`, ya con su descripción.
    Args:
        raw: JSON devuelto por /jobs/api/search.
        since: Epoch UTC a partir del cual una oferta cuenta como reciente.
    Returns:
        list[Offer]: Las ofertas recientes de la página; vacía si no hay.
    """
    offers: list[Offer] = []
    for job in json.loads(raw)["jobs"]:
        published_at = int(job["pubDate"])
        if published_at < since:
            continue
        description = BeautifulSoup(job["description"], "html.parser")
        offers.append(
            Offer(
                title=job["title"].strip(),
                description=description.get_text(separator="\n", strip=True),
                url=job["guid"],
            )
        )
    return offers
