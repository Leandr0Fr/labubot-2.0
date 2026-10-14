"""LinkedIn: qué pedirle al endpoint `jobs-guest` y a quién parsearlo."""

import time

from src.config.settings import settings
from src.driver.http import Driver
from src.portals.linkedin.constants import (
    JOBS_PER_PAGE,
    MAX_PAGES,
    PAUSE,
    SEARCH_URL,
)
from src.portals.linkedin.html_extractor import extract_job_cards, extract_description
from src.schemas.job import Offer


class LinkedIn:
    """Ofertas del endpoint `jobs-guest`: lo que ve un visitante deslogueado."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    def search(self, keywords: str) -> list[Offer]:
        """
        Trae las ofertas del término, cada una con su descripción completa.
        Args:
            keywords: Término de búsqueda, tal como lo escribirías en el portal.
        Returns:
            list[Offer]: Las ofertas del término, sin repetir dentro de él.
        """
        jobs = {}
        for page in range(MAX_PAGES):
            time.sleep(PAUSE)
            list_offers_html = self.driver.get(
                SEARCH_URL,
                "el listado de ofertas",
                {
                    "keywords": keywords,
                    "location": settings.location,
                    "f_TPR": f"r{settings.hours * 3600}",
                    "start": str(page * JOBS_PER_PAGE),
                },
            )
            page_jobs = extract_job_cards(list_offers_html)
            if not page_jobs:
                break
            jobs.update(page_jobs)

        offers: list[Offer] = []
        for url, title in jobs.items():
            time.sleep(PAUSE)
            offer_html = self.driver.get(url, "el detalle de la oferta")
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
