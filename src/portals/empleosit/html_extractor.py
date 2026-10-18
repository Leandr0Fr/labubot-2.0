"""Parsea el HTML de Empleos IT: el listado de búsqueda y la página de la oferta."""

from bs4 import BeautifulSoup

from src.portals.empleosit.constants import (
    ANCHOR_PREFIX,
    JOB_URL,
    SEL_DESCRIPTION,
    SEL_JOB_ANCHOR,
    SEL_JOB_CARD,
    SEL_JOB_TITLE,
)


def extract_job_cards(html: str) -> dict[str, str]:
    """
    Extrae url y título de cada oferta de una página del listado.
    Args:
        html: Página devuelta por search-results-jobs.
    Returns:
        dict[str, str]: url : título.
    """
    soup = BeautifulSoup(html, "html.parser")
    cards: dict[str, str] = {}

    for card in soup.select(SEL_JOB_CARD):
        anchor_node = card.select_one(SEL_JOB_ANCHOR)
        title_node = card.select_one(SEL_JOB_TITLE)
        if anchor_node and title_node:
            job_id = anchor_node.get("name").removeprefix(ANCHOR_PREFIX)
            cards[JOB_URL.format(job_id=job_id)] = title_node.get_text(strip=True)
    return cards


def extract_description(html: str) -> str:
    """
    Extrae la descripción de la página de una oferta.
    Args:
        html: HTML devuelto por display-job/{id}/.
    Returns:
        str: Descripción en texto plano.
    """
    soup = BeautifulSoup(html, "html.parser")
    description_container = soup.select_one(SEL_DESCRIPTION)
    return description_container.get_text(separator="\n", strip=True)
