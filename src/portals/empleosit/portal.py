"""Empleos IT: qué pedirle al buscador de SmartJobBoard y a quién parsearlo."""

import logging
import math
import time
from itertools import count

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.empleosit.constants import (
    CRAWL_DELAY,
    JOBS_PER_PAGE,
    SEARCH_URL,
    SORTING_FIELD,
    SORTING_ORDER,
)
from src.portals.empleosit.html_extractor import extract_description, extract_job_cards


logger = logging.getLogger(__name__)


class EmpleosIT:
    """Ofertas de empleosit.com.ar, la bolsa argentina de puestos de sistemas."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las ofertas de la búsqueda, sin pedir su detalle.
        Args:
            keywords: Términos unidos con OR; los de varias palabras, entre comillas.
        Returns:
            dict[str, str]: url : título, sin repetir.
        """
        days = math.ceil(settings.hours / 24)
        jobs: dict[str, str] = {}
        for page in count(1):
            try:
                list_offers_html = self._get(
                    SEARCH_URL,
                    "el listado de ofertas",
                    {
                        "keywords[boolean]": keywords,
                        "PostedWithin[multi_like][]": str(days),
                        "listings_per_page": str(JOBS_PER_PAGE),
                        "sorting_field": SORTING_FIELD,
                        "sorting_order": SORTING_ORDER,
                        "page": str(page),
                    },
                )
            except LabubotError as error:
                logger.warning(f"Búsqueda cortada: {error}")
                break
            page_jobs = extract_job_cards(list_offers_html)
            # Una página fuera de rango repite la última en vez de venir vacía.
            new_jobs = page_jobs.keys() - jobs.keys()
            if not new_jobs:
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
            o Empleos IT no la pudo servir.
        """
        try:
            offer_html = self._get(url, "el detalle de la oferta")
        except LabubotError as error:
            logger.warning(f"Sin descripción de {url}: {error}")
            return ""
        if not offer_html:
            return ""
        return extract_description(offer_html)

    def _get(self, url: str, subject: str, params: dict[str, str] | None = None) -> str:
        """
        Pide la URL después de la pausa que pide robots.txt.
        Args:
            url: URL completa a pedir.
            subject: Cómo nombrar el recurso dentro del mensaje de error.
            params: Query string, si el endpoint la lleva.
        Returns:
            str: Lo que devuelva `Driver.get()`.
        Raises:
            LabubotRateLimitError: Si el sitio contestó 429.
            LabubotRequestError: Si la red falla o el sitio contesta otra cosa.
        """
        time.sleep(CRAWL_DELAY)
        return self.driver.get(url, subject, params)
