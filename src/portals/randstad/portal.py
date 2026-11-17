"""Randstad: qué páginas pedirle al sitio de Argentina y a quién parsearlas."""

import logging
import time
from itertools import count
from urllib.parse import quote

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.randstad.constants import NEXT_PAGE_URL, SEARCH_URL
from src.portals.randstad.html_extractor import extract_description, extract_job_cards


logger = logging.getLogger(__name__)


class Randstad:
    """Ofertas de Randstad Argentina, una consultora de personal de todos los rubros."""

    def __init__(self, driver: Driver) -> None:
        """Recibe el driver con el que hace todos los pedidos."""
        self.driver = driver

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las ofertas recientes del término, sin su detalle.

        El listado viene por relevancia y no por fecha: se recorre entero, que
        son una o dos páginas.
        Args:
            keywords: Término de búsqueda, tal como lo escribirías en el portal.
        Returns:
            dict[str, str]: url : título, sin repetir dentro del término.
        """
        since = time.time() - settings.hours * 3600
        slug = quote(keywords, safe="")
        jobs: dict[str, str] = {}
        for page in count(1):
            url = SEARCH_URL.format(keywords=slug)
            if page > 1:
                url = NEXT_PAGE_URL.format(keywords=slug, page=page)
            try:
                html = self.driver.get(url, "el listado de ofertas")
            except LabubotError as error:
                logger.warning(f"Búsqueda '{keywords}' cortada: {error}")
                break
            page_jobs = extract_job_cards(html, since)
            if page_jobs is None:
                break
            jobs.update(page_jobs)
        return jobs

    def description(self, url: str) -> str:
        """
        Trae la descripción completa de una oferta.
        Args:
            url: URL de la oferta, tal como la devuelve `search()`.
        Returns:
            str: La descripción en texto plano. Vacía si la oferta ya no existe
            o Randstad no la pudo servir.
        """
        try:
            html = self.driver.get(url, "el detalle de la oferta")
        except LabubotError as error:
            logger.warning(f"Sin descripción de {url}: {error}")
            return ""
        if not html:
            return ""
        return extract_description(html)
