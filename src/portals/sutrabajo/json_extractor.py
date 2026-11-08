"""Parsea el JSON de la REST de WordPress de SuTrabajo."""

import html
import json
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from bs4 import BeautifulSoup

from src.portals.sutrabajo.constants import TRACKING_PREFIX
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
        # Desde el primer <div> es plantilla, con una ubicación falsa (Colombia).
        parts = []
        for node in content.find_all(recursive=False):
            if node.name == "div":
                break
            parts.append(node.get_text(separator="\n", strip=True))
        offers.append(
            Offer(
                title=html.unescape(job["title"]["rendered"]).strip(),
                description="\n".join(parts),
                url=_without_tracking(job["civi-jobs_apply_external"]),
            )
        )
    return offers


def _without_tracking(url: str) -> str:
    """
    La url sin los parámetros de seguimiento, para que coincida con la del portal de origen.
    Args:
        url: La url del aviso original, tal como la da SuTrabajo.
    Returns:
        str: La misma url sin los utm_*; el resto de la query (el id de Talent) queda.
    """
    parts = urlsplit(url)
    query = []
    for key, value in parse_qsl(parts.query):
        if not key.startswith(TRACKING_PREFIX):
            query.append((key, value))
    return urlunsplit(parts._replace(query=urlencode(query)))
