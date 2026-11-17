"""Clarín Clasificados: qué pedirle a la API de su front y a quién parsearlo."""

import logging
import time
from itertools import count
from urllib.parse import quote

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.clarin.constants import SEARCH_URL
from src.portals.clarin.json_extractor import extract_offers


logger = logging.getLogger(__name__)


class Clarin:
    """Avisos del rubro Empleos de Clarín Clasificados: oficios, comercio y empleados."""

    def __init__(self, driver: Driver) -> None:
        """Recibe el driver y arranca sin descripciones: las guarda `search()`."""
        self.driver = driver
        self.descriptions: dict[str, str] = {}

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de los avisos recientes del término.

        El listado no viene por fecha: se recorre entero, que son pocas páginas.
        Args:
            keywords: Término de búsqueda, tal como lo escribirías en el portal.
        Returns:
            dict[str, str]: url : título, sin repetir dentro del término.
        """
        since = time.time() - settings.hours * 3600
        jobs: dict[str, str] = {}
        for page in count(1):
            url = SEARCH_URL.format(page=page, keywords=quote(keywords, safe=""))
            try:
                raw = self.driver.get(url, "el listado de avisos")
            except LabubotError as error:
                logger.warning(f"Búsqueda '{keywords}' cortada: {error}")
                break
            offers = extract_offers(raw, since)
            if offers is None:
                break
            for offer in offers:
                jobs[offer["url"]] = offer["title"]
                self.descriptions[offer["url"]] = offer["description"]
        return jobs

    def description(self, url: str) -> str:
        """
        Devuelve el texto que ya trajo la búsqueda.
        Args:
            url: URL del aviso, tal como la devuelve `search()`.
        Returns:
            str: El rubro y el texto del aviso.
        """
        return self.descriptions[url]
