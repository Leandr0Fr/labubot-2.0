"""Parsea el JSON de la API de Bumeran, que mezcla avisos de Bumeran y ZonaJobs."""

import json

from bs4 import BeautifulSoup

from src.portals.bumeran.constants import JOB_URL, ZONAJOBS_JOB_URL, ZONAJOBS_PORTAL


def extract_job_cards(raw: str) -> dict[str, str]:
    """
    Extrae url y título de cada oferta de una página del listado.
    Args:
        raw: JSON devuelto por avisos/searchV2.
    Returns:
        dict[str, str]: url : título; vacío si la página no traía ofertas.
    """
    cards: dict[str, str] = {}
    for item in json.loads(raw)["content"]:
        url = JOB_URL
        if item["portal"] == ZONAJOBS_PORTAL:
            url = ZONAJOBS_JOB_URL
        title = " ".join(item["titulo"].split())
        cards[url.format(job_id=item["id"])] = title
    return cards


def extract_description(raw: str) -> str:
    """
    Extrae la descripción del detalle de una oferta.
    Args:
        raw: JSON devuelto por fichaAvisoNormalizada/{id}.
    Returns:
        str: Descripción en texto plano.
    """
    description = BeautifulSoup(json.loads(raw)["aviso"]["descripcion"], "html.parser")
    return description.get_text(separator="\n", strip=True)
