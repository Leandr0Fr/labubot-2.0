"""Workable: qué pedirle a su API JSON y a quién parsearlo."""

import logging
import math
from datetime import UTC, datetime, timedelta

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.workable.constants import SEARCH_URL
from src.portals.workable.json_extractor import (
    extract_next_page_token,
    extract_offers,
)


logger = logging.getLogger(__name__)


class Workable:
    """Ofertas de Workable en Argentina (con sede o remoto), por su API JSON."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver
        self.descriptions: dict[str, str] = {}

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las ofertas recientes de la búsqueda.
        Args:
            keywords: Búsqueda, tal como la escribirías en el portal; entiende
                varios términos unidos por OR y frases entre comillas.
        Returns:
            dict[str, str]: url : título, sin repetir dentro de la búsqueda.
        """
        since = datetime.now(UTC) - timedelta(hours=settings.hours)
        # Filtra en días calendario: se pide lo que cubre la ventana y se recorta
        # con `since`.
        days = math.ceil(settings.hours / 24)
        params = {
            "query": keywords,
            "location": settings.location,
            "day_range": str(days),
        }
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
            token = extract_next_page_token(raw)
            if not token:
                break
            params["pageToken"] = token
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
