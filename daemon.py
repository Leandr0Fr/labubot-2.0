"""Corre la búsqueda cada hora: busca, clasifica y manda verdes y amarillos a Telegram."""

import logging
import time

import schedule

from main import main

logger = logging.getLogger(__name__)


def run() -> None:
    """Una corrida; si falla, deja el error en el log y la siguiente sigue en pie."""
    logger.info("Arranca la corrida")
    start = time.monotonic()
    try:
        main()
    except Exception:
        logger.exception("La corrida falló")
        return
    minutes = (time.monotonic() - start) / 60
    logger.info(f"Corrida terminada en {minutes:.1f} min")


def daemon() -> None:
    """Corre una vez al arrancar y después cada hora, hasta que se lo corte."""
    logger.info("Daemon iniciado")
    run()
    schedule.every().hour.do(run)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    daemon()
