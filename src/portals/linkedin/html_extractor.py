"""Parsea el HTML de LinkedIn: el endpoint jobs-guest y la página de una publicación."""

import json

from bs4 import BeautifulSoup

from src.portals.linkedin.constants import (
    POST_TYPE,
    SEL_DESCRIPTION,
    SEL_DETAIL_LOCATION,
    SEL_JOB_CARD,
    SEL_JOB_TITLE,
    SEL_JOB_LINK,
    SEL_JSON_LD,
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
        # Si la empresa no tiene página en LinkedIn, la tarjeta entera es el link.
        if card.name == "a":
            link_node = card
        if title_node and link_node:
            title = title_node.get_text(strip=True)
            url = link_node.get("href").split("?")[0]
            cards[url] = title
    return cards


def extract_description(html: str) -> str:
    """
    Extrae la ubicación y la descripción de la página de una oferta.
    Args:
        html: Página de la oferta (/jobs/view/...).
    Returns:
        str: Ubicación en la primera línea y descripción, en texto plano.
    """
    soup = BeautifulSoup(html, "html.parser")
    location = soup.select_one(SEL_DETAIL_LOCATION).get_text(strip=True)
    description_container = soup.select_one(SEL_DESCRIPTION)
    description = description_container.get_text(separator="\n", strip=True)
    return f"Ubicación: {location}\n{description}"


def extract_post(html: str) -> str:
    """
    Extrae el autor y el texto de la página pública de una publicación.
    Args:
        html: Página de la publicación (/posts/...).
    Returns:
        str: Autor en la primera línea y el texto, en texto plano. Vacío si
        LinkedIn mandó al registro o la publicación no tiene texto.
    """
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.select(SEL_JSON_LD):
        data = json.loads(node.string)
        if data["@type"] == POST_TYPE and data.get("articleBody"):
            return f"Publicado por: {data['author']['name']}\n{data['articleBody']}"
    return ""
