"""Configuración de la aplicación y del log."""

import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_FILE = BASE_DIR / "logs" / "app.log"


class Settings(BaseSettings):
    """
    Variables de entorno:
    - LOCATION: Ubicación tal como la escribe LinkedIn ("Argentina").
    - HOURS: Ventana de publicación (24 = solo lo de hoy).
    - LLM_API_KEY: Clave de OpenAI (platform.openai.com/api-keys).
    - TELEGRAM_TOKEN: Token del bot, el que da @BotFather.
    - TELEGRAM_CHAT_ID: Chat al que el bot manda las ofertas.
    - LOG_LEVEL: Nivel mínimo que se loguea (DEBUG suma cada término y oferta).
    """

    location: str = "Argentina"
    hours: int = 24
    llm_api_key: str = ""
    telegram_token: str = ""
    telegram_chat_id: str = ""
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

LOG_FILE.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")],
    force=True,
)
# httpx loguea cada request con su url, y la de Telegram lleva el token.
logging.getLogger("httpx").setLevel(logging.WARNING)
