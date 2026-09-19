"""LinkedIn: qué pedirle al endpoint `jobs-guest` y a quién parsearlo."""

from src.config.settings import settings
from src.portals.linkedin.constants import (
    DETAIL_URL,
    JOBS_PER_PAGE,
    MAX_PAGES,
    SEARCH_URL,
)
from src.driver.http import Driver
from src.schemas.job import JobCard, JobDetail
from src.portals.linkedin.parser import parse_cards, parse_detail


class LinkedIn:
    """
    Ofertas del endpoint `jobs-guest`: lo que ve un visitante deslogueado.
    """

    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    def search(self, keywords: str) -> list[JobCard]:
        """
        Trae todas las ofertas del término: las 10 páginas que da el endpoint.
        Args:
            keywords: Término de búsqueda, tal como lo escribirías en el portal.
        Returns:
            list[JobCard]: Todas las ofertas del término, sin deduplicar.
        """
        found: list[JobCard] = []

        for page in range(MAX_PAGES):
            html = self.driver.get(
                SEARCH_URL,
                "el listado de ofertas",
                {
                    "keywords": keywords,
                    "location": settings.location,
                    "f_TPR": f"r{settings.hours * 3600}",
                    "start": str(page * JOBS_PER_PAGE),
                },
            )
            cards = parse_cards(html)
            if not cards:
                break
            found.extend(cards)

        return found

    def detail(self, job_id: str) -> JobDetail | None:
        """
        Descripción completa, criterios y competencia de una oferta.

        Es el paso que justifica el proyecto: la tarjeta del listado no trae el
        cuerpo del aviso, y el cuerpo es donde aparece "Python" en las ofertas
        tituladas "Developer" a secas.
        Args:
            job_id: Id de la oferta.
        Returns:
            JobDetail | None: None si la oferta ya no existe (se dio de baja).
        """
        html = self.driver.get(f"{DETAIL_URL}/{job_id}", "el detalle de la oferta")
        return parse_detail(html) if html else None
