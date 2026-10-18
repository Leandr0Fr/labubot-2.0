"""LinkedIn: qué pedirle al endpoint `jobs-guest` y a quién parsearlo."""

import time
from itertools import count

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotRateLimitError, LabubotRequestError
from src.portals.linkedin.constants import (
    JOBS_PER_PAGE,
    PAUSE,
    RETRIES,
    SEARCH_URL,
)
from src.portals.linkedin.html_extractor import extract_job_cards, extract_description


class LinkedIn:
    """Ofertas del endpoint `jobs-guest`: lo que ve un visitante deslogueado."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las ofertas del término, sin pedir su detalle.
        Args:
            keywords: Término de búsqueda, tal como lo escribirías en el portal.
        Returns:
            dict[str, str]: url : título, sin repetir dentro del término.
        """
        jobs = {}
        for start in count(0, JOBS_PER_PAGE):
            list_offers_html = self._get(
                SEARCH_URL,
                "el listado de ofertas",
                {
                    "keywords": keywords,
                    "location": settings.location,
                    "f_TPR": f"r{settings.hours * 3600}",
                    "start": str(start),
                },
            )
            page_jobs = extract_job_cards(list_offers_html)
            if not page_jobs:
                break
            jobs.update(page_jobs)
        return jobs

    def description(self, url: str) -> str:
        """
        Trae la descripción completa de una oferta.
        Args:
            url: URL de la oferta, tal como la devuelve `search()`.
        Returns:
            str: La descripción en texto plano. Vacía si la oferta ya no existe.
        """
        offer_html = self._get(url, "el detalle de la oferta")
        if not offer_html:
            return ""
        return extract_description(offer_html)

    def _get(self, url: str, subject: str, params: dict[str, str] | None = None) -> str:
        """
        Pide la URL, reintentando si LinkedIn contesta 429 o deja colgado el pedido.
        Args:
            url: URL completa a pedir.
            subject: Cómo nombrar el recurso dentro del mensaje de error.
            params: Query string, si el endpoint la lleva.
        Returns:
            str: Lo que devuelva `Driver.get()`.
        Raises:
            LabubotRateLimitError: Si contestó 429 en el último intento.
            LabubotRequestError: Si el último intento falló por red u otro status.
        """
        # 429 sueltos y timeouts, hasta a un navegador: el pedido siguiente pasa.
        for _ in range(RETRIES - 1):
            try:
                return self.driver.get(url, subject, params)
            except (LabubotRateLimitError, LabubotRequestError):
                time.sleep(PAUSE)
        return self.driver.get(url, subject, params)
