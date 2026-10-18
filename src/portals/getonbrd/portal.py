"""Get on Board: qué pedirle a su API pública y a quién parsearlo."""

import time
from itertools import count

from src.config.settings import settings
from src.driver.http import Driver
from src.portals.getonbrd.constants import JOBS_PER_PAGE, LOCATIONS, SEARCH_URL
from src.portals.getonbrd.json_extractor import extract_offers


class GetOnBoard:
    """Ofertas de Get on Board en Argentina y en remoto global, por su API pública."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver
        self.descriptions: dict[str, str] = {}

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las ofertas recientes del término.
        Args:
            keywords: Término de búsqueda, tal como lo escribirías en el portal.
        Returns:
            dict[str, str]: url : título, sin repetir dentro del término.
        """
        since = time.time() - settings.hours * 3600
        jobs: dict[str, str] = {}
        for location in LOCATIONS:
            for page in count(1):
                raw = self.driver.get(
                    SEARCH_URL,
                    "el listado de ofertas",
                    {
                        "query": keywords,
                        **location,
                        "per_page": str(JOBS_PER_PAGE),
                        "page": str(page),
                    },
                )
                offers = extract_offers(raw, since)
                if offers is None:
                    break
                for offer in offers:
                    jobs[offer["url"]] = offer["title"]
                    self.descriptions[offer["url"]] = offer["description"]
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
