"""Parsea el JSON de la REST de WordPress de SuTrabajo."""

import html
import json

from bs4 import BeautifulSoup

from src.schemas.job import Offer


def extract_offers(raw: str) -> list[Offer]:
    """
    Extrae las ofertas de una página, ya con su descripción.
    Args:
        raw: JSON devuelto por wp-json/wp/v2/jobs.
    Returns:
        list[Offer]: Las ofertas de la página, con la url del sitio de origen.
    """
    offers: list[Offer] = []
    for job in json.loads(raw):
        content = BeautifulSoup(job["content"]["rendered"], "html.parser")
        # Desde el primer <div> es plantilla, y su ubicación dice Colombia
        # aunque la oferta sea de otro país.
        parts = []
        for node in content.find_all(recursive=False):
            if node.name == "div":
                break
            parts.append(node.get_text(separator="\n", strip=True))
        offers.append(
            Offer(
                title=html.unescape(job["title"]["rendered"]).strip(),
                description="\n".join(parts),
                url=job["civi-jobs_apply_external"],
            )
        )
    return offers
