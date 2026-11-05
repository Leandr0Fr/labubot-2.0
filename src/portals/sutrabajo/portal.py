"""SuTrabajo: qué pedirle a la REST de su WordPress y a quién parsearlo."""

import logging
from datetime import UTC, datetime, timedelta
from itertools import count

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.sutrabajo.constants import (
    FIELDS,
    JOBS_PER_PAGE,
    SEARCH_URL,
    SECTIONS,
)
from src.portals.sutrabajo.json_extractor import extract_offers


logger = logging.getLogger(__name__)


class SuTrabajo:
    """Ofertas de SuTrabajo, un hub que republica avisos de LinkedIn y otros sitios."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver
        self.descriptions: dict[str, str] = {}

    def search(self) -> dict[str, str]:
        """
        Trae url y título de las ofertas recientes de Argentina y de remoto.

        Sin término: es de primer empleo y cada sección publica unas 45 por
        día. Filtra el LLM.
        Returns:
            dict[str, str]: url del sitio de origen : título.
        """
        since = datetime.now(UTC) - timedelta(hours=settings.hours)
        jobs: dict[str, str] = {}
        for section in SECTIONS:
            for page in count(1):
                try:
                    raw = self.driver.get(
                        SEARCH_URL.format(section=section),
                        "el listado de ofertas",
                        {
                            "after": since.isoformat(timespec="seconds"),
                            "per_page": str(JOBS_PER_PAGE),
                            "page": str(page),
                            "_fields": FIELDS,
                        },
                    )
                except LabubotError as error:
                    logger.warning(f"Búsqueda en '{section}' cortada: {error}")
                    break
                offers = extract_offers(raw)
                for offer in offers:
                    jobs[offer["url"]] = offer["title"]
                    self.descriptions[offer["url"]] = offer["description"]
                # Pedir una página de más da 400, no una lista vacía.
                if len(offers) < JOBS_PER_PAGE:
                    break
        return jobs

    def description(self, url: str) -> str:
        """
        Devuelve la descripción que ya trajo la búsqueda.
        Args:
            url: URL de la oferta, tal como la devuelve `search()`.
        Returns:
            str: La descripción en texto plano.
        """
        return self.descriptions[url]
