"""Configuración de la aplicación; importarlo deja el log armado en logs/app.log."""

import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_FILE = BASE_DIR / "logs" / "app.log"


class Settings(BaseSettings):
    """
    Configuración leída del entorno o de .env.
    LOCATION: Ubicación para los portales que filtran por lugar ("Argentina").
    HOURS: Ventana de publicación, en horas (24 = lo del último día).
    LLM_API_KEY: Clave de OpenAI (platform.openai.com/api-keys).
    TELEGRAM_TOKEN: Token del bot, el que da @BotFather.
    ADMIN_CHAT_ID: Chat del admin: aprueba las altas y ve /usuarios.
    WEBHOOK_URL: URL pública a la que Telegram manda los updates.
    WEBHOOK_SECRET: Secreto que Telegram manda en cada update; vacío = rechaza todo.
    DB_PATH: Archivo SQLite que comparten la api y el worker.
    LOG_LEVEL: Nivel mínimo que se loguea (DEBUG suma cada término y oferta).
    """

    location: str = "Argentina"
    hours: int = 24
    llm_api_key: str = ""
    telegram_token: str = ""
    admin_chat_id: int = 0
    webhook_url: str = ""
    webhook_secret: str = ""
    db_path: str = "labubot.db"
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
