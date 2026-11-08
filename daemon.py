"""El worker: la búsqueda de cada usuario en su hilo, al arrancar, cada hora y con cada /start."""

import logging
import sqlite3
import threading
import time

import schedule

from main import main
from src.constants.run import SEARCH_POLL_SECONDS
from src.db.database import connect
from src.db.users import Users

logger = logging.getLogger(__name__)

# Los usuarios con una búsqueda en curso: nadie corre dos veces a la vez.
running: set[int] = set()
running_lock = threading.Lock()


def daemon() -> None:
    """Busca para todos al arrancar y cada hora, y para cada /start apenas llega."""
    logger.info("Daemon iniciado")
    _start_all()
    schedule.every().hour.do(_start_all)
    while True:
        # Un lock o un error de la base no tiene que tumbar al worker.
        try:
            schedule.run_pending()
            conn = connect()
            chat_ids = Users(conn).take_search_requests()
            conn.close()
        except sqlite3.Error:
            logger.exception("No se pudieron leer las búsquedas pedidas")
            chat_ids = []
        for chat_id in chat_ids:
            _start(chat_id)
        time.sleep(SEARCH_POLL_SECONDS)


def run(chat_id: int) -> None:
    """
    La búsqueda de un usuario; si falla, deja el error en el log y las demás siguen.
    Args:
        chat_id: El usuario.
    """
    logger.info(f"Arranca la búsqueda de {chat_id}")
    start = time.monotonic()
    try:
        main(chat_id)
    except Exception:
        logger.exception(f"La búsqueda de {chat_id} falló")
        return
    finally:
        with running_lock:
            running.discard(chat_id)
    minutes = (time.monotonic() - start) / 60
    logger.info(f"Búsqueda de {chat_id} terminada en {minutes:.1f} min")


def _start_all() -> None:
    """Lanza la búsqueda de cada usuario activo."""
    conn = connect()
    active = Users(conn).active()
    conn.close()
    for user in active:
        _start(user["chat_id"])


def _start(chat_id: int) -> None:
    """
    Lanza la búsqueda de un usuario en su propio hilo, si no tiene una en curso.
    Args:
        chat_id: El usuario.
    """
    with running_lock:
        if chat_id in running:
            return
        running.add(chat_id)
    threading.Thread(target=run, args=(chat_id,)).start()


if __name__ == "__main__":
    daemon()
