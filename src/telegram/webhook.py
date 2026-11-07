"""Webhook de Telegram: valida el secreto y despacha cada update a los handlers."""

import logging
import secrets
from typing import Annotated, Any

from fastapi import APIRouter, Header, HTTPException

from src.config.settings import settings
from src.db.database import connect
from src.driver.http import Driver
from src.telegram.bot import Telegram
from src.telegram.handlers import on_callback, on_message

logger = logging.getLogger(__name__)

router = APIRouter()
telegram = Telegram(Driver())


@router.post("/telegram/webhook")
def webhook(
    update: dict[str, Any],
    x_telegram_bot_api_secret_token: Annotated[str, Header()] = "",
) -> dict[str, bool]:
    """
    Recibe un update de Telegram y lo atiende antes de contestar.

    Es def y no async def: el Driver es sincrónico y FastAPI lo corre en su threadpool.
    Args:
        update: El Update tal como lo manda Telegram, sin validar (un 422 haría
            que Telegram lo reintente).
        x_telegram_bot_api_secret_token: El secret_token registrado con setWebhook.
    Returns:
        dict[str, bool]: Siempre {"ok": True}; con un error, Telegram reintentaría
        el mismo update.
    Raises:
        HTTPException: 403 si el secreto falta o no coincide.
    """
    # En bytes: con un str no ASCII, compare_digest lanza en vez de dar False.
    if not settings.webhook_secret or not secrets.compare_digest(
        x_telegram_bot_api_secret_token.encode(), settings.webhook_secret.encode()
    ):
        raise HTTPException(status_code=403)

    conn = connect()
    try:
        if "message" in update and update["message"]["chat"]["type"] == "private":
            on_message(conn, telegram, update["message"])
        if "callback_query" in update:
            on_callback(conn, telegram, update["callback_query"])
    except Exception:
        logger.exception(f"Falló el update {update.get('update_id')}")
    finally:
        conn.close()
    return {"ok": True}
