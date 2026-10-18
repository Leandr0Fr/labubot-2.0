"""Parsea el RSS de una categoría de We Work Remotely."""

from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

from bs4 import BeautifulSoup

from src.schemas.job import Offer


def extract_offers(raw: str, since: float) -> list[Offer]:
    """
    Extrae las ofertas publicadas desde `since`, ya con su descripción.
    Args:
        raw: XML del feed RSS.
        since: Epoch UTC a partir del cual una oferta cuenta como reciente.
    Returns:
        list[Offer]: Las ofertas recientes del feed.
    """
    offers: list[Offer] = []
    for item in ElementTree.fromstring(raw).iter("item"):
        published_at = parsedate_to_datetime(item.findtext("pubDate")).timestamp()
        if published_at < since:
            continue
        description = BeautifulSoup(item.findtext("description"), "html.parser")
        offers.append(
            Offer(
                title=item.findtext("title").strip(),
                description=description.get_text(separator="\n", strip=True),
                url=item.findtext("link").strip(),
            )
        )
    return offers
