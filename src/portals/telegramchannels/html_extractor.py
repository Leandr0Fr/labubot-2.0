"""Parsea el HTML de la vista web de un canal de Telegram (t.me/s/...)."""

from datetime import datetime

from bs4 import BeautifulSoup

from src.portals.telegramchannels.constants import (
    ATTR_ID,
    POST_PREFIXES,
    SEL_DATE,
    SEL_MESSAGE,
    SEL_PREVIEW,
    SEL_PREVIEW_TEXT,
    SEL_PREVIEW_TITLE,
    TITLE_LENGTH,
)
from src.schemas.job import Offer


def extract_posts(html: str, since: datetime) -> tuple[list[Offer], str | None]:
    """
    Extrae las publicaciones de LinkedIn compartidas desde `since` en una página del canal.
    Args:
        html: Página de t.me/s/{canal}, con los mensajes del más viejo al más nuevo.
        since: Momento a partir del cual un mensaje cuenta como reciente.
    Returns:
        tuple[list[Offer], str | None]: Las publicaciones, con todo el texto de
        la tarjeta como descripción, y el id desde el que sigue la página
        anterior; None si no hay más que pedir.
    """
    soup = BeautifulSoup(html, "html.parser")
    posts: list[Offer] = []
    before = None
    oldest = True
    for message in soup.select(SEL_MESSAGE):
        date_node = message.select_one(SEL_DATE)
        if date_node is None:
            continue
        recent = datetime.fromisoformat(date_node["datetime"]) >= since
        # Si el más viejo de la página todavía es reciente, falta la página anterior.
        if oldest and recent:
            before = message[ATTR_ID].rsplit("/", 1)[1]
        oldest = False
        preview = message.select_one(SEL_PREVIEW)
        if not recent or preview is None:
            continue
        url = preview["href"].split("?")[0]
        if not url.startswith(POST_PREFIXES):
            continue
        heading = preview.select_one(SEL_PREVIEW_TITLE).get_text(" ", strip=True)
        # El encabezado puede ser solo hashtags y el autor; el texto son las
        # primeras líneas. Una publicación corta entra entera en el encabezado.
        text = heading
        text_node = preview.select_one(SEL_PREVIEW_TEXT)
        if text_node:
            text = text_node.get_text(" ", strip=True)
        title = " ".join(text.split())
        if len(title) > TITLE_LENGTH:
            title = f"{title[:TITLE_LENGTH].rsplit(' ', 1)[0]}…"
        posts.append(Offer(title=title, description=f"{heading} {text}", url=url))
    return posts, before
