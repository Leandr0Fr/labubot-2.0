"""Parsea las páginas HTML de Computrabajo Argentina."""

from bs4 import BeautifulSoup

from src.portals.computrabajo.constants import (
    AMBA_PROVINCES,
    BASE_URL,
    COMPANY_SEPARATOR,
    SEL_DESCRIPTION,
    SEL_DETAIL_LOCATION,
    SEL_JOB_CARD,
    SEL_JOB_LINK,
    SEL_JOB_LOCATION,
    SEL_JOB_REMOTE,
)


def extract_job_cards(html: str) -> dict[str, str] | None:
    """
    Extrae url y título de las ofertas remotas o de AMBA de una página del listado.
    Args:
        html: Página devuelta por /trabajo-de-{slug}.
    Returns:
        dict[str, str] | None: url : título, o None si la página no traía ofertas.
    """
    soup = BeautifulSoup(html, "html.parser")
    card_nodes = soup.select(SEL_JOB_CARD)
    if not card_nodes:
        return None

    cards: dict[str, str] = {}
    for card in card_nodes:
        location = card.select_one(SEL_JOB_LOCATION).get_text(strip=True)
        remote = card.select_one(SEL_JOB_REMOTE)
        if not remote and not location.endswith(AMBA_PROVINCES):
            continue
        link_node = card.select_one(SEL_JOB_LINK)
        url = BASE_URL + link_node.get("href").split("#")[0]
        cards[url] = link_node.get_text(strip=True)
    return cards


def extract_description(html: str) -> str:
    """
    Extrae la ubicación y la descripción de la página de una oferta.
    Args:
        html: Página devuelta por /ofertas-de-trabajo/oferta-de-trabajo-de-...
    Returns:
        str: Ubicación en la primera línea y descripción, en texto plano. Vacía
        si la página no es una oferta: una que ya no existe redirige a una
        búsqueda vacía con 200.
    """
    soup = BeautifulSoup(html, "html.parser")
    parts = []
    for node in soup.select(SEL_DESCRIPTION):
        parts.append(node.get_text(separator="\n", strip=True))
    if not parts:
        return ""
    company_location = soup.select_one(SEL_DETAIL_LOCATION).get_text(" ", strip=True)
    location = company_location.rsplit(COMPANY_SEPARATOR, 1)[-1]
    description = "\n".join(parts)
    return f"Ubicación: {location}\n{description}"
