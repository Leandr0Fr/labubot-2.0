"""Buscojobs: qué pedirle a su API pública y a quién parsearlo."""

import json
import logging
from itertools import count

from src.config.settings import settings
from src.driver.http import Driver
from src.exceptions.exceptions import LabubotError
from src.portals.buscojobs.constants import (
    DAY_HOURS,
    DETAIL_URL,
    ID_SEPARATOR,
    JOBS_PER_PAGE,
    SEARCH_URL,
)
from src.portals.buscojobs.json_extractor import extract_description, extract_job_cards


logger = logging.getLogger(__name__)


class Buscojobs:
    """Ofertas de Buscojobs Argentina, un agregador general con avisos propios."""

    def __init__(self, driver: Driver) -> None:
        """Recibe el driver con el que hace todos los pedidos."""
        self.driver = driver

    def search(self, keywords: str) -> dict[str, str]:
        """
        Trae url y título de las ofertas recientes del término, sin su detalle.
        Args:
            keywords: Término de búsqueda, tal como lo escribirías en el portal.
        Returns:
            dict[str, str]: url : título, sin repetir dentro del término.
        """
        days = (settings.hours + DAY_HOURS - 1) // DAY_HOURS
        where = {"BusquedaQue": keywords, "PublicadaHace": days}

        jobs: dict[str, str] = {}
        for page in count():
            search_filter = {
                "where": where,
                "limit": JOBS_PER_PAGE,
                "skip": page * JOBS_PER_PAGE,
            }
            try:
                raw = self.driver.get(
                    SEARCH_URL,
                    "el listado de ofertas",
                    {"filter": json.dumps(search_filter)},
                )
            except LabubotError as error:
                logger.warning(f"Búsqueda '{keywords}' cortada: {error}")
                break
            page_jobs = extract_job_cards(raw)
            if page_jobs is None:
                break
            jobs.update(page_jobs)
        return jobs

    def description(self, url: str) -> str:
        """
        Trae la descripción completa de una oferta.
        Args:
            url: URL de la oferta, tal como la devuelve `search()`.
        Returns:
            str: La descripción en texto plano. Vacía si la oferta ya no existe
            o Buscojobs no la pudo servir.
        """
        job_id = url.rsplit(ID_SEPARATOR, 1)[1]
        try:
            raw = self.driver.get(
                DETAIL_URL.format(job_id=job_id), "el detalle de la oferta"
            )
        except LabubotError as error:
            logger.warning(f"Sin descripción del aviso {job_id}: {error}")
            return ""
        if not raw:
            return ""
        return extract_description(raw)
