"""Parsea el JSON del listado de avisos de Clarín Clasificados."""

import json

from src.portals.clarin.constants import (
    DAY_SECONDS,
    JOB_URL,
    SECTION_SEPARATOR,
    TITLE_LENGTH,
)
from src.schemas.job import Offer


def extract_offers(raw: str, since: float) -> list[Offer] | None:
    """
    Extrae los avisos publicados desde `since`, ya con su texto completo.
    Args:
        raw: JSON devuelto por /aviso/{página}/listado/{término}/filtro/Empleos.
        since: Epoch UTC a partir del cual un aviso cuenta como reciente.
    Returns:
        list[Offer] | None: Los avisos recientes de la página, o None si la
        página vino vacía.
    """
    ads = json.loads(raw)["paginas"]["content"]
    if not ads:
        return None

    offers: list[Offer] = []
    for ad in ads:
        # fechaPublicacion es la medianoche del día, en milisegundos: sin hora,
        # el aviso cuenta como reciente hasta que termina ese día.
        if ad["fechaPublicacion"] / 1000 + DAY_SECONDS <= since:
            continue
        text = " ".join(ad["textoLibre"].split())
        title = text
        if len(title) > TITLE_LENGTH:
            title = f"{title[:TITLE_LENGTH].rsplit(' ', 1)[0]}…"
        section = ad["nivelEstructura"].split(SECTION_SEPARATOR, 1)[-1]
        offers.append(
            Offer(
                title=title,
                description=f"Rubro: {section}\n{text}",
                url=JOB_URL.format(job_id=ad["id"]),
            )
        )
    return offers
