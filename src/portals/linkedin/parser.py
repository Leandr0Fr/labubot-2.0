"""Parsea el HTML que devuelve el endpoint jobs-guest de LinkedIn."""

from selectolax.lexbor import LexborHTMLParser

from src.portals.linkedin.constants import (
    SEL_CARD,
    SEL_DESCRIPTION,
    SEL_DESCRIPTION_ALT,
    SEL_TITLE,
    URN_PREFIX,
)
from src.utils.text import text


def parse_cards(html: str) -> dict[str, str]:
    """
    Extrae id y título de cada oferta de un fragmento del listado.
    Args:
        html: Fragmento devuelto por seeMoreJobPostings/search.
    Returns:
        dict[str, str]: Título por id; vacío si el fragmento no traía ofertas.
    """
    tree = LexborHTMLParser(html)
    cards: dict[str, str] = {}

    for node in tree.css(SEL_CARD):
        urn = node.attributes.get("data-entity-urn") or ""
        job_id = urn.removeprefix(URN_PREFIX)
        title = text(node.css_first(SEL_TITLE))
        if job_id and title:
            cards[job_id] = title

    return cards


def parse_description(html: str) -> str:
    """
    Extrae la descripción de la página de una oferta.
    Args:
        html: HTML devuelto por jobPosting/{id}.
    Returns:
        str: Descripción en texto plano.
    """
    tree = LexborHTMLParser(html)
    body = tree.css_first(SEL_DESCRIPTION) or tree.css_first(SEL_DESCRIPTION_ALT)
    return text(body)
