"""Telegram: manda las ofertas que valen la pena al chat del bot."""

import logging
import time

from src.config.settings import settings
from src.constants.telegram import EMOJIS, PAUSE, SEND_MESSAGE_URL
from src.driver.http import Driver
from src.enums.traffic_light import TrafficLight
from src.exceptions.exceptions import LabubotRequestError
from src.schemas.job import Offer


logger = logging.getLogger(__name__)


class Telegram:
    """Un mensaje por oferta al chat configurado, por la Bot API."""

    def __init__(self, driver: Driver) -> None:
        self.driver = driver
        self.url = SEND_MESSAGE_URL.format(token=settings.telegram_token)

    def send(self, offer: Offer, light: TrafficLight) -> None:
        """
        Manda una oferta con su color.
        Args:
            offer: La oferta ya clasificada.
            light: El color que le dio el modelo; verde o amarillo.
        Raises:
            LabubotRateLimitError: Si Telegram contestó 429.
            LabubotRequestError: Si el token o el chat no sirven, o falla la red.
        """
        time.sleep(PAUSE)
        raw = self.driver.post_json(
            self.url,
            "el mensaje de Telegram",
            {
                "chat_id": settings.telegram_chat_id,
                "text": f"{EMOJIS[light]} {offer['title']}\n{offer['url']}",
            },
        )
        # Un token inválido da 404, y el Driver devuelve vacío en vez de fallar.
        if not raw:
            raise LabubotRequestError("Telegram no reconoce TELEGRAM_TOKEN")
        logger.debug(f"Enviada a Telegram: {offer['title']}")
