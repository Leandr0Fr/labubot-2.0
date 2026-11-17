"""Parsea el JSON de la API de Buscojobs."""

import json

from src.portals.buscojobs.constants import HYBRID, REMOTE


def extract_job_cards(raw: str) -> dict[str, str] | None:
    """
    Extrae url y título de las ofertas de una página del listado.
    Args:
        raw: JSON devuelto por /api/ofertas, una lista sin envoltorio.
    Returns:
        dict[str, str] | None: url : título, o None si la página no traía ofertas.
    """
    jobs = json.loads(raw)
    if not jobs:
        return None

    cards: dict[str, str] = {}
    for job in jobs:
        cards[job["UrlOferta"]] = " ".join(job["CargoVacante"].split())
    return cards


def extract_description(raw: str) -> str:
    """
    Extrae la ubicación, la modalidad y la descripción del detalle de una oferta.
    Args:
        raw: JSON devuelto por /api/ofertas/{id}.
    Returns:
        str: Ubicación y modalidad en las primeras líneas, si el aviso las trae,
        y la descripción en texto plano.
    """
    job = json.loads(raw)
    # Ciudad y Departamento faltan en los avisos que no los informan.
    places = []
    for key in ("Ciudad", "Departamento"):
        if job.get(key):
            places.append(job[key]["Nombre"])
    lines = []
    if places:
        lines.append(f"Ubicación: {', '.join(places)}")
    if job.get("PermiteTeletrabajo"):
        lines.append(f"Modalidad: {REMOTE}")
    elif job.get("PermiteTrabajoHibrido"):
        lines.append(f"Modalidad: {HYBRID}")
    lines.append(job["Descripcion"])
    return "\n".join(lines)
