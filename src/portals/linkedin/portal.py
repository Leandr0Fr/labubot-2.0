"""LinkedIn: qué pedirle al endpoint `jobs-guest` y a quién parsearlo."""

from src.config.settings import settings
from src.driver.http import Driver
from src.portals.linkedin.constants import (
    DETAIL_URL,
    JOB_URL,
    JOBS_PER_PAGE,
    MAX_PAGES,
    SEARCH_URL,
)
from src.portals.linkedin.parser import parse_cards, parse_description
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
        # Por id: el propio portal repite ofertas entre páginas.
        titles: dict[str, str] = {}

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
            titles.update(cards)

        offers: list[Offer] = []
        for job_id, title in titles.items():
            html = self.driver.get(f"{DETAIL_URL}/{job_id}", "el detalle de la oferta")
            # Vacío: la oferta se dio de baja entre el listado y el detalle.
            if not html:
                continue
            offers.append(
                Offer(
                    title=title,
                    description=parse_description(html),
                    url=JOB_URL.format(job_id=job_id),
                )
            )

        return offers
