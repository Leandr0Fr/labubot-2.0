"""Parsea el JSON de la búsqueda de Get on Board."""

import json

from bs4 import BeautifulSoup

from src.portals.getonbrd.constants import DESCRIPTION_SECTIONS
from src.schemas.job import Offer


def extract_offers(raw: str, since: float) -> list[Offer] | None:
    """
    Extrae las ofertas publicadas desde `since`, ya con su descripción.
    Args:
        raw: JSON devuelto por /api/v0/search/jobs.
        since: Epoch UTC a partir del cual una oferta cuenta como reciente.
    Returns:
        list[Offer] | None: Las ofertas recientes de la página, o None si la
        página vino vacía.
    """
    data = json.loads(raw)["data"]
    if not data:
        return None

    offers: list[Offer] = []
    for item in data:
        attributes = item["attributes"]
        published_at = attributes["published_at"]
        if published_at < since:
            continue
        parts = []
        for section in DESCRIPTION_SECTIONS:
            parts.append(attributes.get(f"{section}_headline") or "")
            parts.append(attributes[section] or "")
        description = BeautifulSoup("\n".join(parts), "html.parser")
        offers.append(
            Offer(
                title=attributes["title"].strip(),
                description=description.get_text(separator="\n", strip=True),
                url=item["links"]["public_url"],
            )
        )
    return offers
