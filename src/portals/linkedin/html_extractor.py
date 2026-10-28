"""Parsea el HTML que devuelve el endpoint jobs-guest de LinkedIn."""

from bs4 import BeautifulSoup

from src.portals.linkedin.constants import (
    SEL_DETAIL_LOCATION,
    SEL_JOB_CARD,
    SEL_JOB_TITLE,
    SEL_JOB_LINK,
)


def extract_job_cards(html: str) -> dict[str, str]:
    """
    Extrae url y título de cada oferta de un fragmento del listado.
    Args:
        html: Fragmento devuelto por seeMoreJobPostings/search.
    Returns:
        dict[str, str]: url : título.
    """
    soup = BeautifulSoup(html, "html.parser")
    cards: dict[str, str] = {}

    for card in soup.select(SEL_JOB_CARD):
        title_node = card.select_one(SEL_JOB_TITLE)
        link_node = card.select_one(SEL_JOB_LINK)
        if title_node and link_node:
            title = title_node.get_text(strip=True)
            url = link_node.get("href").split("?")[0]
            cards[url] = title
    return cards


def extract_description(html: str) -> str:
    """
    Extrae la ubicación y la descripción de la página de una oferta.
    Args:
        html: HTML devuelto por jobPosting/{id}.
    Returns:
        str: Ubicación en la primera línea y descripción, en texto plano.
    """
    soup = BeautifulSoup(html, "html.parser")
    location = soup.select_one(SEL_DETAIL_LOCATION).get_text(strip=True)
    description_container = soup.find("div", class_="show-more-less-html__markup")
    description = description_container.get_text(separator="\n", strip=True)
    return f"Ubicación: {location}\n{description}"
