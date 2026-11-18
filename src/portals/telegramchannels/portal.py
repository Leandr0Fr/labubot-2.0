"""Canales de Telegram: qué pedirle a su vista web y quién lee cada publicación."""

import logging
from datetime import UTC, datetime, timedelta

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.linkedin import LinkedIn
from src.portals.telegramchannels.constants import CHANNEL_URL, CHANNELS
from src.portals.telegramchannels.html_extractor import extract_posts
from src.schemas.job import Offer


logger = logging.getLogger(__name__)


class TelegramChannels:
    """Publicaciones de LinkedIn que comparten los canales públicos de empleo."""

    def __init__(self, driver: Driver) -> None:
        """Recibe el driver y arranca sin publicaciones: las trae el primer `search()`."""
        self.driver = driver
        self.linkedin = LinkedIn(driver)
        self.posts: dict[str, Offer] | None = None

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las publicaciones recientes que nombran el término.

        Los canales se leen una sola vez por corrida. El término se busca en la
        tarjeta del link (título y primeras líneas), no en el texto completo.
        Args:
            keywords: Término de búsqueda, en minúsculas.
        Returns:
            dict[str, str]: url : título, sin repetir dentro del término.
        """
        if self.posts is None:
            self.posts = self._read_channels()

        jobs: dict[str, str] = {}
        for url, post in self.posts.items():
            if keywords in post["description"].lower():
                jobs[url] = post["title"]
        return jobs

    def description(self, url: str) -> str:
        """
        Trae el texto completo de una publicación, que está en LinkedIn.
        Args:
            url: URL de la publicación, tal como la devuelve `search()`.
        Returns:
            str: Autor y texto. Vacío si LinkedIn no la muestra sin login.
        """
        return self.linkedin.post(url)

    def _read_channels(self) -> dict[str, Offer]:
        """
        Recorre cada canal hacia atrás hasta salir de la ventana de publicación.
        Returns:
            dict[str, Offer]: url : publicación, con todo el texto de la
            tarjeta como descripción.
        """
        since = datetime.now(UTC) - timedelta(hours=settings.hours)
        posts: dict[str, Offer] = {}
        for channel in CHANNELS:
            params = None
            while True:
                try:
                    html = self.driver.get(
                        CHANNEL_URL.format(channel=channel),
                        "los mensajes del canal",
                        params,
                    )
                except LabubotError as error:
                    logger.warning(f"Canal '{channel}' cortado: {error}")
                    break
                page_posts, before = extract_posts(html, since)
                for post in page_posts:
                    posts[post["url"]] = post
                if before is None:
                    break
                params = {"before": before}
        return posts
