"""LinkedIn: qué pedirle al endpoint `jobs-guest` y a quién parsearlo."""

import time
from itertools import count

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotRateLimitError
from src.portals.linkedin.constants import (
    JOBS_PER_PAGE,
    PAUSE,
    RETRIES,
    SEARCH_URL,
)
from src.portals.linkedin.html_extractor import extract_job_cards, extract_description
from src.schemas.job import Offer


class LinkedIn:
    """Ofertas del endpoint `jobs-guest`: lo que ve un visitante deslogueado."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    def _get(self, url: str, subject: str, params: dict[str, str] | None = None) -> str:
        """
        Pide la URL, reintentando mientras LinkedIn conteste 429.
        Args:
            url: URL completa a pedir.
            subject: Cómo nombrar el recurso dentro del mensaje de error.
            params: Query string, si el endpoint la lleva.
        Returns:
            str: Lo que devuelva `Driver.get()`.
        Raises:
            LabubotRateLimitError: Si contestó 429 en los RETRIES intentos.
        """
        # Tira 429 sueltos, hasta a un navegador: el pedido siguiente pasa.
        for _ in range(RETRIES - 1):
            time.sleep(PAUSE)
            try:
                return self.driver.get(url, subject, params)
            except LabubotRateLimitError:
                continue
        time.sleep(PAUSE)
        return self.driver.get(url, subject, params)

    def search(self, keywords: str) -> list[Offer]:
        """
        Trae las ofertas del término, cada una con su descripción completa.
        Args:
            keywords: Término de búsqueda, tal como lo escribirías en el portal.
        Returns:
            list[Offer]: Las ofertas del término, sin repetir dentro de él.
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

        offers: list[Offer] = []
        for url, title in jobs.items():
            offer_html = self._get(url, "el detalle de la oferta")
            if not offer_html:
                continue
            offers.append(
                Offer(
                    title=title,
                    description=extract_description(offer_html),
                    url=url,
                )
            )
        return offers
