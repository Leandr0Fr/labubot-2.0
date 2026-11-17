"""Parsea el JSON de la API de Bumeran, que mezcla avisos de Bumeran y ZonaJobs."""

import json

from bs4 import BeautifulSoup

from src.portals.bumeran.constants import (
    JOB_URL,
    ZONAJOBS_JOB_URL,
    ZONAJOBS_PORTAL,
)


def extract_job_cards(raw: str) -> dict[str, str] | None:
    """
    Extrae url y título de las ofertas de una página del listado, de todo el país.
    Args:
        raw: JSON devuelto por avisos/searchV2.
    Returns:
        dict[str, str] | None: url : título, o None si la página no traía ofertas.
    """
    jobs = json.loads(raw)["content"]
    if not jobs:
        return None

    cards: dict[str, str] = {}
    for job in jobs:
        url = JOB_URL
        if job["portal"] == ZONAJOBS_PORTAL:
            url = ZONAJOBS_JOB_URL
        title = " ".join(job["titulo"].split())
        cards[url.format(job_id=job["id"])] = title
    return cards


def extract_description(raw: str) -> str:
    """
    Extrae la ubicación, la modalidad y la descripción del detalle de una oferta.
    Args:
        raw: JSON devuelto por fichaAvisoNormalizada/{id}.
    Returns:
        str: Ubicación y modalidad en las dos primeras líneas, si el aviso las
        trae, y la descripción en texto plano.
    """
    job = json.loads(raw)["aviso"]
    lines = []
    if job["localizacion"]:
        lines.append(f"Ubicación: {job['localizacion']['detalle']}")
    if job["modalidadTrabajo"]:
        lines.append(f"Modalidad: {job['modalidadTrabajo']['nombre']}")
    description = BeautifulSoup(job["descripcion"], "html.parser")
    lines.append(description.get_text(separator="\n", strip=True))
    return "\n".join(lines)
