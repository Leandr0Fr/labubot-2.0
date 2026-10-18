"""Parsea el HTML de Talent.com: el listado /jobs y el detalle /view."""

from bs4 import BeautifulSoup

from src.portals.talent.constants import (
    DESCRIPTION_LABEL,
    JOB_URL,
    SEL_JOB_CARD,
    SEL_JOB_TITLE,
)


def extract_job_cards(html: str) -> dict[str, str]:
    """
    Extrae url y título de cada oferta de una página del listado.
    Args:
        html: Página devuelta por /jobs.
    Returns:
        dict[str, str]: url : título; vacío si la página no traía ofertas.
    """
    soup = BeautifulSoup(html, "html.parser")
    cards: dict[str, str] = {}

    for card in soup.select(SEL_JOB_CARD):
        title_node = card.select_one(SEL_JOB_TITLE)
        url = JOB_URL.format(job_id=card["data-new-id"])
        cards[url] = title_node.get_text(strip=True)
    return cards


def extract_description(html: str) -> str:
    """
    Extrae la descripción de la página de una oferta.
    Args:
        html: HTML devuelto por /view?id={id}.
    Returns:
        str: Descripción en texto plano.
    """
    soup = BeautifulSoup(html, "html.parser")
    label = soup.find("span", string=DESCRIPTION_LABEL)
    return label.find_next_sibling("div").get_text(separator="\n", strip=True)
