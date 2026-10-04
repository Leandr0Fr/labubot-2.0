"""Configuración de la aplicación."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Variables de entorno:
    - LOCATION: Ubicación tal como la escribe LinkedIn ("Argentina").
    - HOURS: Ventana de publicación (24 = solo lo de hoy).
    - LLM_API_KEY: Clave de OpenAI (platform.openai.com/api-keys).
    """

    location: str = "Argentina"
    hours: int = 24
    llm_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
