"""We Work Remotely: qué feeds pedir y a quién parsearlos."""

import time

from src.config.settings import settings
from src.driver.http import Driver
from src.portals.weworkremotely.constants import FEED_URLS
from src.portals.weworkremotely.xml_extractor import extract_offers


class WeWorkRemotely:
    """Ofertas remotas de back-end y full-stack de We Work Remotely, por RSS."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver
        self.descriptions: dict[str, str] = {}

    def search(self) -> dict[str, str]:
        """
        Trae url y título de las ofertas recientes de los feeds.

        Sin término: los feeds son por categoría (back-end y full-stack).
        Returns:
            dict[str, str]: url : título, sin repetir entre feeds.
        """
        since = time.time() - settings.hours * 3600
        jobs: dict[str, str] = {}
        for feed_url in FEED_URLS:
            raw = self.driver.get(feed_url, "el feed de ofertas")
            for offer in extract_offers(raw, since):
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
