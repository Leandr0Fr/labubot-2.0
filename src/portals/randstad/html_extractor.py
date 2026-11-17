"""Parsea las páginas de Randstad Argentina: el JSON que su front deja en el HTML."""

import json
from datetime import datetime

from bs4 import BeautifulSoup

from src.portals.randstad.constants import DATE_FORMAT, JOB_URL, ROUTE_DATA


def extract_job_cards(html: str, since: float) -> dict[str, str] | None:
    """
    Extrae url y título de las ofertas publicadas desde `since` de una página.
    Args:
        html: Página devuelta por /trabajos/q-{término}/.
        since: Epoch a partir del cual una oferta cuenta como reciente.
    Returns:
        dict[str, str] | None: url : título de las recientes, o None si la
        página no traía ofertas.
    """
    jobs = _route_data(html)["searchResults"]["hits"]["hits"]
    if not jobs:
        return None

    cards: dict[str, str] = {}
    for job in jobs:
        source = job["_source"]
        created = datetime.strptime(source["JobDates"]["DateCreatedTime"], DATE_FORMAT)
        if created.timestamp() < since:
            continue
        url = JOB_URL.format(
            title=source["BlueXSanitized"]["Title"],
            city=source["BlueXSanitized"]["City"],
            job_id=job["_id"],
        )
        cards[url] = source["JobInformation"]["Title"].strip()
    return cards


def extract_description(html: str) -> str:
    """
    Extrae la ubicación y la descripción de la página de una oferta.
    Args:
        html: Página devuelta por /trabajos/{título}_{ciudad}_{id}/.
    Returns:
        str: Ubicación en la primera línea, si el aviso la trae, y descripción,
        en texto plano.
    """
    source = _route_data(html)["jobData"]["hits"]["hits"][0]["_source"]
    # City y Region faltan en los avisos que no los informan.
    places = []
    for key in ("City", "Region"):
        if source["JobLocation"].get(key):
            places.append(source["JobLocation"][key])
    lines = []
    if places:
        lines.append(f"Ubicación: {', '.join(places)}")
    description = BeautifulSoup(source["JobInformation"]["Description"], "html.parser")
    lines.append(description.get_text(separator="\n", strip=True))
    return "\n".join(lines)


def _route_data(html: str) -> dict:
    """
    Decodifica el objeto que el front asigna a ROUTE_DATA.
    Args:
        html: Una página de Randstad.
    Returns:
        dict: Los datos de la ruta: `searchResults` en el listado, `jobData` en el aviso.
    """
    start = html.index("{", html.index(ROUTE_DATA))
    return json.JSONDecoder().raw_decode(html, start)[0]
