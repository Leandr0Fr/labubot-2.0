"""Bumeran: qué pedirle a la API de su front y a quién parsearlo."""

from itertools import count

from src.config.settings import settings
from src.driver.http import Driver
from src.portals.bumeran.constants import (
    DETAIL_URL,
    HEADERS,
    JOBS_PER_PAGE,
    RECENCY_BUCKETS,
    RECENCY_FILTER,
    SEARCH_URL,
    SORT,
)
from src.portals.bumeran.json_extractor import extract_description, extract_job_cards


class Bumeran:
    """Ofertas de Bumeran y de ZonaJobs, que comparten índice y API."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las ofertas del término, sin pedir su detalle.
        Args:
            keywords: Término de búsqueda; el endpoint busca solo en el título.
        Returns:
            dict[str, str]: url : título, sin repetir dentro del término.
        """
        filters = []
        for hours, value in RECENCY_BUCKETS.items():
            if hours >= settings.hours:
                filters = [{"id": RECENCY_FILTER, "value": value}]
                break
        body = {"filtros": filters, "query": keywords, "internacional": False}

        jobs: dict[str, str] = {}
        for page in count():
            raw = self.driver.post_json(
                SEARCH_URL,
                "el listado de ofertas",
                body,
                {"pageSize": str(JOBS_PER_PAGE), "page": str(page), "sort": SORT},
                HEADERS,
            )
            page_jobs = extract_job_cards(raw)
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
        job_id = url.rsplit("/", 1)[1].removesuffix(".html")
        raw = self.driver.get(
            DETAIL_URL.format(job_id=job_id), "el detalle de la oferta", headers=HEADERS
        )
        if not raw:
            return ""
        return extract_description(raw)
