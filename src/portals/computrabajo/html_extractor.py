"""Parsea las páginas HTML de Computrabajo Argentina."""

from bs4 import BeautifulSoup

from src.portals.computrabajo.constants import (
    BASE_URL,
    SEL_DESCRIPTION,
    SEL_JOB_CARD,
    SEL_JOB_LINK,
)


def extract_job_cards(html: str) -> dict[str, str]:
    """
    Extrae url y título de cada oferta de una página del listado.
    Args:
        html: Página devuelta por /trabajo-de-{slug}.
    Returns:
        dict[str, str]: url : título; vacío si la página no traía ofertas.
    """
    soup = BeautifulSoup(html, "html.parser")
    cards: dict[str, str] = {}

    for card in soup.select(SEL_JOB_CARD):
        link_node = card.select_one(SEL_JOB_LINK)
        url = BASE_URL + link_node.get("href").split("#")[0]
        cards[url] = link_node.get_text(strip=True)
    return cards


def extract_description(html: str) -> str:
    """
    Extrae la descripción de la página de una oferta.
    Args:
        html: Página devuelta por /ofertas-de-trabajo/oferta-de-trabajo-de-...
    Returns:
        str: Descripción en texto plano. Vacía si la página no es una oferta: una
        que ya no existe redirige a una búsqueda vacía con 200.
    """
    soup = BeautifulSoup(html, "html.parser")
    parts = []
    for node in soup.select(SEL_DESCRIPTION):
        parts.append(node.get_text(separator="\n", strip=True))
    return "\n".join(parts)
