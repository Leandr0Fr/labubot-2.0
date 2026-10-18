"""Talent.com: qué pedirle al listado /jobs y a quién parsearlo."""

import math
from itertools import count

from src.config.settings import settings
from src.driver.http import Driver
from src.portals.talent.constants import SEARCH_URL
from src.portals.talent.html_extractor import extract_description, extract_job_cards


class Talent:
    """Ofertas de Talent.com Argentina, un agregador que levanta avisos de ATS."""

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
        days = math.ceil(settings.hours / 24)
        jobs: dict[str, str] = {}
        for page in count(1):
            list_offers_html = self.driver.get(
                SEARCH_URL,
                "el listado de ofertas",
                {
                    "k": keywords,
                    "l": settings.location,
                    "date": str(days),
                    "p": str(page),
                },
            )
            page_jobs = extract_job_cards(list_offers_html)
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
            str: La descripción en texto plano. Vacía si la oferta ya no existe.
        """
        offer_html = self.driver.get(url, "el detalle de la oferta")
        if not offer_html:
            return ""
        return extract_description(offer_html)
