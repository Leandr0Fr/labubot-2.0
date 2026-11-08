"""Telegram: lo que el bot manda hacia la Bot API, siempre por el Driver."""

import json
import logging
import time
from typing import Any

from src.config.settings import settings
from src.driver.http import Driver
from src.enums.traffic_light import TrafficLight
from src.exceptions.exceptions import LabubotRequestError
from src.schemas.job import Offer
from src.telegram.constants import (
    ADMIN_COMMANDS,
    BOT_API_URL,
    COMMANDS,
    EMOJIS,
    FILE_URL,
    OFFER,
    PAUSE,
)

logger = logging.getLogger(__name__)


class Telegram:
    """La Bot API por el Driver: un método por cada cosa que el bot hace hacia afuera."""

    def __init__(self, driver: Driver) -> None:
        """
        Guarda el Driver por el que salen todas las llamadas.
        Args:
            driver: El cliente HTTP.
        """
        self.driver = driver

    def send_message(
        self,
        chat_id: int,
        text: str,
        keyboard: dict | None = None,
        silent: bool = False,
    ) -> None:
        """
        Manda un texto, con botones si vienen y sin sonido si silent.

        Sin vista previa de links: cada oferta es un link y la tarjeta llenaría el chat.
        Args:
            chat_id: El chat al que va.
            text: El texto, hasta MESSAGE_LIMIT unidades UTF-16.
            keyboard: Un inline keyboard, como los arma keyboards.py.
            silent: True = la notificación llega sin sonido.
        Raises:
            LabubotForbiddenError: Si el usuario bloqueó el bot.
            LabubotRateLimitError: Si Telegram contestó 429.
            LabubotRequestError: Si el token no sirve, Telegram rechaza el
                mensaje o falla la red.
        """
        body: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "link_preview_options": {"is_disabled": True},
        }
        if keyboard:
            body["reply_markup"] = keyboard
        if silent:
            body["disable_notification"] = True
        self._call("sendMessage", body)

    def edit_message(
        self, chat_id: int, message_id: int, text: str, keyboard: dict | None = None
    ) -> None:
        """
        Reemplaza el texto y los botones de un mensaje ya mandado.
        Args:
            chat_id: El chat del mensaje.
            message_id: El mensaje a editar.
            text: El texto nuevo.
            keyboard: Los botones nuevos; sin botones, el mensaje los pierde.
        Raises:
            LabubotError: Si Telegram lo rechaza (por ejemplo, el texto no
                cambió) o falla la red.
        """
        body: dict[str, Any] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
        }
        if keyboard:
            body["reply_markup"] = keyboard
        self._call("editMessageText", body)

    def delete_messages(self, chat_id: int, message_ids: list[int]) -> None:
        """
        Borra mensajes de un chat; los que no existen o ya no se pueden borrar se saltean.
        Args:
            chat_id: El chat.
            message_ids: Hasta DELETE_BATCH ids.
        Raises:
            LabubotError: Si Telegram rechaza la tanda o falla la red.
        """
        self._call("deleteMessages", {"chat_id": chat_id, "message_ids": message_ids})

    def answer_callback(self, callback_id: str) -> None:
        """
        Le avisa a Telegram que el botón se atendió, para que deje de mostrar "cargando".
        Args:
            callback_id: El id del callback_query.
        Raises:
            LabubotError: Si Telegram lo rechaza o falla la red.
        """
        self._call("answerCallbackQuery", {"callback_query_id": callback_id})

    def send_offer(self, chat_id: int, offer: Offer, light: TrafficLight) -> None:
        """
        Manda una oferta con su emoji, después de esperar PAUSE.
        Args:
            chat_id: El chat del usuario.
            offer: La oferta ya clasificada.
            light: El color que le dio el modelo; verde o amarillo.
        Raises:
            LabubotForbiddenError: Si el usuario bloqueó el bot.
            LabubotRateLimitError: Si Telegram contestó 429.
            LabubotRequestError: Si el token no sirve o falla la red.
        """
        time.sleep(PAUSE)
        text = OFFER.format(emoji=EMOJIS[light], title=offer["title"], url=offer["url"])
        self.send_message(chat_id, text)
        logger.debug(f"Enviada a {chat_id}: {offer['title']}")

    def set_commands(self) -> None:
        """
        Publica el menú /: COMMANDS para todos y COMMANDS + ADMIN_COMMANDS para el admin.
        Raises:
            LabubotError: Si Telegram lo rechaza o falla la red.
        """
        self._call("setMyCommands", {"commands": COMMANDS})
        self._call(
            "setMyCommands",
            {
                "commands": COMMANDS + ADMIN_COMMANDS,
                "scope": {"type": "chat", "chat_id": settings.admin_chat_id},
            },
        )

    def set_webhook(self) -> None:
        """
        Registra WEBHOOK_URL con WEBHOOK_SECRET y descarta los updates pendientes.

        Telegram solo manda updates de message y callback_query.
        Raises:
            LabubotError: Si Telegram lo rechaza o falla la red.
        """
        self._call(
            "setWebhook",
            {
                "url": settings.webhook_url,
                "secret_token": settings.webhook_secret,
                "allowed_updates": ["message", "callback_query"],
                "drop_pending_updates": True,
            },
        )

    def download_file(self, file_id: str) -> str:
        """
        Baja un archivo que mandó el usuario.
        Args:
            file_id: El file_id del documento.
        Returns:
            str: El contenido como texto; vacío si Telegram ya no lo tiene.
        Raises:
            LabubotError: Si Telegram rechaza el pedido o falla la red.
        """
        file = self._call("getFile", {"file_id": file_id})
        url = FILE_URL.format(
            token=settings.telegram_token, file_path=file["file_path"]
        )
        return self.driver.get(url, "el archivo de Telegram")

    def _call(self, method: str, body: dict[str, Any]) -> Any:
        """
        Llama a un método de la Bot API.
        Args:
            method: El método, como sendMessage.
            body: Sus parámetros.
        Returns:
            Any: El result de la respuesta.
        Raises:
            LabubotForbiddenError: Si Telegram contestó 403.
            LabubotRateLimitError: Si Telegram contestó 429.
            LabubotRequestError: Si el token no sirve (Telegram da 404 y el Driver
                devuelve vacío), otro status o falla la red.
        """
        # El subject nombra el método y nunca la URL, que lleva el token.
        raw = self.driver.post_json(
            BOT_API_URL.format(token=settings.telegram_token, method=method),
            f"el {method} de Telegram",
            body,
        )
        if not raw:
            raise LabubotRequestError("Telegram no reconoce TELEGRAM_TOKEN")
        return json.loads(raw)["result"]
