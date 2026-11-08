"""Indeed: qué pedirle a la API GraphQL de su app y a quién parsearlo."""

import json
import logging

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.indeed.constants import (
    GRAPHQL_URL,
    HEADERS,
    JOBS_PER_PAGE,
    QUERY,
    RADIUS,
)
from src.portals.indeed.json_extractor import extract_next_cursor, extract_offers


logger = logging.getLogger(__name__)


class Indeed:
    """Ofertas de Indeed Argentina, por la API que usa su app de iPhone."""

    def __init__(self, driver: Driver) -> None:
        """Recibe el driver y arranca sin descripciones: las guarda `search()`."""
        self.driver = driver
        self.descriptions: dict[str, str] = {}

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las ofertas de un término.
        Args:
            keywords: Un término; si tiene espacios, se busca como frase.
        Returns:
            dict[str, str]: url : título, sin repetir.
        """
        what = keywords
        if " " in keywords:
            what = f'"{keywords}"'
        jobs: dict[str, str] = {}
        cursor = None
        while True:
            cursor_arg = ""
            if cursor:
                cursor_arg = f"cursor: {json.dumps(cursor)}"
            query = QUERY.format(
                what=json.dumps(what),
                where=json.dumps(settings.location),
                radius=RADIUS,
                limit=JOBS_PER_PAGE,
                cursor=cursor_arg,
                hours=settings.hours,
            )
            try:
                raw = self.driver.post_json(
                    GRAPHQL_URL,
                    "el listado de ofertas",
                    {"query": query},
                    headers=HEADERS,
                )
                offers = extract_offers(raw)
            except LabubotError as error:
                logger.warning(f"Búsqueda '{keywords}' cortada: {error}")
                break
            for offer in offers:
                jobs[offer["url"]] = offer["title"]
                self.descriptions[offer["url"]] = offer["description"]
            cursor = extract_next_cursor(raw)
            if not cursor:
                break
        return jobs

    def description(self, url: str) -> str:
        """
        Devuelve la descripción que ya trajo la búsqueda.
        Args:
            url: URL de la oferta, tal como la devuelve `search()`.
        Returns:
            str: La descripción en texto plano.
        """
        return self.descriptions[url]
