"""Registra el webhook y el menú de comandos en Telegram: una vez por deploy o cuando cambia la URL."""

import logging

from src.config.settings import settings
from src.driver.http import Driver
from src.telegram.bot import Telegram

logger = logging.getLogger(__name__)


def main() -> None:
    """Registra WEBHOOK_URL con su secreto y publica el menú de comandos."""
    telegram = Telegram(Driver())
    telegram.set_webhook()
    telegram.set_commands()
    logger.info(f"Webhook registrado en {settings.webhook_url} y comandos publicados")


if __name__ == "__main__":
    main()
