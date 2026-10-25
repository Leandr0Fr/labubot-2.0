"""Jobicy: qué pedirle a su API pública y a quién parsearlo."""

import logging
from datetime import UTC, datetime, timedelta

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.jobicy.constants import GEO, JOBS_PER_PAGE, SEARCH_URL
from src.portals.jobicy.json_extractor import extract_next_cursor, extract_offers


logger = logging.getLogger(__name__)


class Jobicy:
    """Ofertas remotas de Jobicy abiertas a Latinoamérica, por su API pública."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver
        self.descriptions: dict[str, str] = {}

    def search(self) -> dict[str, str]:
        """
        Trae url y título de todas las ofertas recientes para Latinoamérica.

        Sin término: `tag` no entiende OR ni frases en español, y todo lo de la
        región entra en una página. Filtra el LLM.
        Returns:
            dict[str, str]: url : título.
        """
        since = datetime.now(UTC) - timedelta(hours=settings.hours)
        params = {"count": str(JOBS_PER_PAGE), "geo": GEO}
        jobs: dict[str, str] = {}
        while True:
            try:
                raw = self.driver.get(SEARCH_URL, "el listado de ofertas", params)
            except LabubotError as error:
                logger.warning(f"Búsqueda cortada: {error}")
                break
            for offer in extract_offers(raw, since):
                jobs[offer["url"]] = offer["title"]
                self.descriptions[offer["url"]] = offer["description"]
            cursor = extract_next_cursor(raw)
            if not cursor:
                break
            params["cursor"] = cursor
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
