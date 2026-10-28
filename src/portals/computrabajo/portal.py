"""Computrabajo: qué páginas pedirle al sitio de Argentina y a quién parsearlas."""

import logging
from itertools import count

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.computrabajo.constants import RECENCY_BUCKETS, SEARCH_URL
from src.portals.computrabajo.html_extractor import (
    extract_description,
    extract_job_cards,
)


logger = logging.getLogger(__name__)


class Computrabajo:
    """Ofertas de ar.computrabajo.com: el listado y el detalle públicos, en HTML."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las ofertas remotas o de AMBA del término, sin su detalle.
        Args:
            keywords: Término de búsqueda, tal como lo escribirías en el portal.
        Returns:
            dict[str, str]: url : título, sin repetir dentro del término.
        """
        slug = keywords.lower().replace(" ", "-")
        url = SEARCH_URL.format(slug=slug)
        # El bucket más chico que cubre la ventana; si ninguno alcanza, sin filtro.
        params = {}
        for hours, pubdate in RECENCY_BUCKETS.items():
            if hours >= settings.hours:
                params["pubdate"] = pubdate
                break

        jobs: dict[str, str] = {}
        for page in count(1):
            params["p"] = str(page)
            try:
                list_offers_html = self.driver.get(url, "el listado de ofertas", params)
            except LabubotError as error:
                logger.warning(f"Búsqueda '{keywords}' cortada: {error}")
                break
            page_jobs = extract_job_cards(list_offers_html)
            # Pasada la última, el sitio devuelve una página sin ofertas.
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
            o Computrabajo no la pudo servir.
        """
        try:
            offer_html = self.driver.get(url, "el detalle de la oferta")
        except LabubotError as error:
            logger.warning(f"Sin descripción de {url}: {error}")
            return ""
        if not offer_html:
            return ""
        return extract_description(offer_html)
