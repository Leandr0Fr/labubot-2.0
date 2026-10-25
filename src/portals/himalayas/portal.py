"""Himalayas: qué pedirle a su API pública y a quién parsearlo."""

import logging
import time
from itertools import count

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.himalayas.constants import SEARCH_URL, SORT
from src.portals.himalayas.json_extractor import extract_offers


logger = logging.getLogger(__name__)


class Himalayas:
    """Ofertas remotas de Himalayas abiertas a Argentina, por su API pública."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver
        self.descriptions: dict[str, str] = {}

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las ofertas recientes del término.
        Args:
            keywords: Término de búsqueda, tal como lo escribirías en el portal.
        Returns:
            dict[str, str]: url : título, sin repetir dentro del término.
        """
        since = time.time() - settings.hours * 3600
        jobs: dict[str, str] = {}
        for page in count(1):
            try:
                raw = self.driver.get(
                    SEARCH_URL,
                    "el listado de ofertas",
                    {
                        "q": keywords,
                        "country": settings.location,
                        "sort": SORT,
                        "page": str(page),
                    },
                )
            except LabubotError as error:
                logger.warning(f"Búsqueda '{keywords}' cortada: {error}")
                break
            offers = extract_offers(raw, since)
            if not offers:
                break
            for offer in offers:
                jobs[offer["url"]] = offer["title"]
                self.descriptions[offer["url"]] = offer["description"]
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
