"""La corrida: busca ofertas, las clasifica y le manda a cada usuario sus 🟢🟡."""

import csv
import json
import logging
import sqlite3
import time
from collections import Counter
from datetime import datetime
from html import escape
from typing import Any

from src.classifier.openai import Classifier
from src.constants.run import HUB, RESULTS_DIR, WITHOUT_SEARCH
from src.db.database import connect
from src.db.offers import Deliveries, Offers
from src.db.users import Users
from src.driver.http import Driver
from src.enums.traffic_light import TrafficLight
from src.enums.user_status import UserStatus
from src.exceptions.exceptions import LabubotForbiddenError
from src.portals.bumeran import Bumeran
from src.portals.computrabajo import Computrabajo
from src.portals.empleosit import EmpleosIT
from src.portals.getonbrd import GetOnBoard
from src.portals.himalayas import Himalayas
from src.portals.indeed import Indeed
from src.portals.jobicy import Jobicy
from src.portals.linkedin import LinkedIn
from src.portals.sutrabajo import SuTrabajo
from src.portals.talent import Talent
from src.portals.weworkremotely import WeWorkRemotely
from src.portals.workable import Workable
from src.schemas.job import Found, Offer
from src.schemas.user import User
from src.telegram.bot import Telegram
from src.telegram.constants import (
    KEYWORD_HEADER,
    OTHER_PORTALS,
    OTHER_PORTALS_HEADER,
    PAUSE,
    SUMMARY_EMPTY,
    SUMMARY_GREENS,
    SUMMARY_LINE,
    SUMMARY_SEPARATOR,
    SUMMARY_TITLE,
    SUMMARY_TOTAL,
    SUMMARY_YELLOWS,
)

logger = logging.getLogger(__name__)


def main(chat_id: int | None = None) -> None:
    """
    Una corrida: a cada usuario activo, uno tras otro, le busca y le manda 🟢🟡.

    Cada (portal, palabra) se pide una sola vez para todos, el /start pendiente de
    cada usuario se da por cumplido y los veredictos quedan en RESULTS_DIR.
    Args:
        chat_id: Solo ese usuario (el worker corre uno por hilo); None = todos los activos.
    """
    started = datetime.now()
    conn = connect()
    driver = Driver()
    try:
        users = Users(conn)
        active = users.active()
        if chat_id is not None:
            selected = []
            for user in active:
                if user["chat_id"] == chat_id:
                    selected.append(user)
            active = selected
        if not active:
            logger.info("No hay usuarios activos")
            return

        portals: dict[str, Any] = {
            "LinkedIn": LinkedIn(driver),
            "Computrabajo": Computrabajo(driver),
            "GetOnBoard": GetOnBoard(driver),
            "Himalayas": Himalayas(driver),
            "Talent": Talent(driver),
            "Indeed": Indeed(driver),
            "Workable": Workable(driver),
            "Bumeran": Bumeran(driver),
            "EmpleosIT": EmpleosIT(driver),
            "Jobicy": Jobicy(driver),
            "SuTrabajo": SuTrabajo(driver),
            "WeWorkRemotely": WeWorkRemotely(driver),
        }
        searches: dict[tuple[str, str], dict[str, str]] = {}
        telegram = Telegram(driver)

        verdicts = []
        for user in active:
            verdicts.extend(_run_user(conn, telegram, portals, searches, user))
            users.remove_search_request(user["chat_id"])
        _save_results(verdicts, started, chat_id)
    finally:
        driver.close()
        conn.close()


def _run_user(
    conn: sqlite3.Connection,
    telegram: Telegram,
    portals: dict[str, Any],
    searches: dict[tuple[str, str], dict[str, str]],
    user: User,
) -> list[list]:
    """
    Busca las palabras de un usuario, clasifica lo nuevo y le manda 🟢🟡 y el resumen.

    También manda las 🟢🟡 que quedaron sin enviar, aunque su palabra ya no esté.
    Una descripción guardada del hub se vuelve a bajar si la oferta llega por su
    portal original, porque el hub la reescribe y pierde datos. Si el usuario
    bloqueó el bot, pasa a blocked.
    Args:
        conn: La conexión de la corrida.
        telegram: El cliente de la Bot API.
        portals: Los portales de la corrida, por nombre de clase.
        searches: Lo ya buscado en esta corrida, por (portal, palabra).
        user: El usuario, tal como estaba al arrancar la corrida.
    Returns:
        list[list]: chat_id, palabra, color y oferta de cada clasificación.
    """
    started = datetime.now()
    users = Users(conn)
    deliveries = Deliveries(conn)
    cache = Offers(conn)
    chat_id = user["chat_id"]
    terms = users.terms(chat_id)
    blocked_words = users.blocked_words(chat_id)
    listings = _search_terms(portals, searches, terms)

    matches: dict[str | None, list[tuple[Offer, TrafficLight]]] = {}
    for row in deliveries.pending(chat_id):
        offer = Offer(title=row["title"], description="", url=row["url"])
        matches.setdefault(row["term"], []).append((offer, TrafficLight(row["light"])))

    verdicts = []
    colors: Counter[TrafficLight] = Counter()
    already_seen = blocked_by_title = no_description = 0
    classifier = Classifier(user["profile"])
    for url, listing in listings.items():
        if deliveries.exists(chat_id, url):
            already_seen += 1
            continue
        blocked_word = _word_in_title(listing["title"], blocked_words)
        if blocked_word:
            logger.debug(f"Título bloqueado por '{blocked_word}': {listing['title']}")
            blocked_by_title += 1
            continue
        offer = Offer(title=listing["title"], description="", url=url)
        cached = cache.get(url)
        if cached is None or (cached["portal"] == HUB and listing["portal"] != HUB):
            offer["description"] = portals[listing["portal"]].description(url)
            cache.add(offer, listing["portal"])
        else:
            offer["description"] = cached["description"]
        if not offer["description"]:
            no_description += 1
            continue
        light = classifier.classify(offer)
        deliveries.add(chat_id, url, light, listing["term"])
        verdicts.append([chat_id, listing["term"], light, offer])
        colors[light] += 1
        if light != TrafficLight.RED:
            matches.setdefault(listing["term"], []).append((offer, light))
    logger.info(
        f"{user['first_name']}: {len(verdicts)} ofertas nuevas; salteadas: "
        f"{already_seen} ya vistas, {blocked_by_title} por título, "
        f"{no_description} sin descripción"
    )
    logger.info(
        f"{user['first_name']}: clasificadas {colors[TrafficLight.GREEN]} verdes, "
        f"{colors[TrafficLight.YELLOW]} amarillas, {colors[TrafficLight.RED]} rojas"
    )

    keywords: list[str | None] = list(terms)
    for term in matches:
        if term is not None and term not in keywords:
            keywords.append(term)
    keywords.sort()
    if None in matches:
        keywords.append(None)

    try:
        sent = _send_by_keyword(telegram, deliveries, chat_id, keywords, matches)
        _send_summary(telegram, chat_id, keywords, matches, colors, started)
    except LabubotForbiddenError:
        logger.warning(f"El chat {chat_id} bloqueó el bot: pasa a blocked")
        users.set_status(chat_id, UserStatus.BLOCKED)
        return verdicts
    logger.info(f"{user['first_name']}: {sent} enviadas a Telegram")
    return verdicts


def _search_terms(
    portals: dict[str, Any],
    searches: dict[tuple[str, str], dict[str, str]],
    terms: list[str],
) -> dict[str, Found]:
    """
    Junta las ofertas de las palabras de un usuario, con la que trajo cada una.

    Los portales sin búsqueda traen todo lo reciente y la palabra sale del título.
    Args:
        portals: Los portales de la corrida, por nombre de clase.
        searches: Lo ya buscado en esta corrida, por (portal, palabra); lo que
            falta se pide acá y se agrega.
        terms: Las palabras del usuario, en orden alfabético.
    Returns:
        dict[str, Found]: url : oferta, una sola vez, con la primera palabra
        que la trajo.
    """
    listings: dict[str, Found] = {}
    for name, portal in portals.items():
        if name in WITHOUT_SEARCH:
            continue
        for term in terms:
            key = (name, term)
            if key not in searches:
                searches[key] = portal.search(term)
                logger.debug(f"{name} '{term}': {len(searches[key])} ofertas")
            for url, title in searches[key].items():
                if url not in listings:
                    listings[url] = Found(title=title, term=term, portal=name)

    for name in WITHOUT_SEARCH:
        key = (name, "")
        if key not in searches:
            searches[key] = portals[name].search()
            logger.debug(f"{name}: {len(searches[key])} ofertas")
        for url, title in searches[key].items():
            if url not in listings:
                term = _word_in_title(title, terms)
                listings[url] = Found(title=title, term=term, portal=name)
    return listings


def _send_by_keyword(
    telegram: Telegram,
    deliveries: Deliveries,
    chat_id: int,
    keywords: list[str | None],
    matches: dict[str | None, list[tuple[Offer, TrafficLight]]],
) -> int:
    """
    Manda un bloque por palabra con 🟢🟡: el encabezado y cada oferta en su mensaje.

    Las palabras sin coincidencias no mandan nada: aparecen solo en el resumen.
    Args:
        telegram: El cliente de la Bot API.
        deliveries: Las entregas, para anotar cada envío.
        chat_id: El chat del usuario.
        keywords: Sus palabras en orden alfabético; None = otros portales, al final.
        matches: Las ofertas verdes y amarillas por palabra; None = otros portales.
    Returns:
        int: Cuántas ofertas se mandaron.
    Raises:
        LabubotForbiddenError: Si el usuario bloqueó el bot.
    """
    sent = 0
    for term in keywords:
        if term not in matches:
            continue
        header = OTHER_PORTALS_HEADER
        if term is not None:
            header = KEYWORD_HEADER.format(term=escape(term))
        time.sleep(PAUSE)
        telegram.send_message(chat_id, header, html=True)
        for color in (TrafficLight.GREEN, TrafficLight.YELLOW):
            for offer, light in matches[term]:
                if light != color:
                    continue
                telegram.send_offer(chat_id, offer, light)
                deliveries.mark_sent(chat_id, offer["url"])
                sent += 1
    return sent


def _send_summary(
    telegram: Telegram,
    chat_id: int,
    keywords: list[str | None],
    matches: dict[str | None, list[tuple[Offer, TrafficLight]]],
    colors: Counter[TrafficLight],
    started: datetime,
) -> None:
    """
    Manda sin sonido el resumen: el total por color y cuántas 🟢🟡 trajo cada palabra.

    Las palabras sin coincidencias van juntas en un solo renglón, al final.
    Args:
        telegram: El cliente de la Bot API.
        chat_id: El chat del usuario.
        keywords: Sus palabras en orden alfabético; None = otros portales, al final.
        matches: Las 🟢🟡 que se le mandaron, por palabra; None = otros portales.
        colors: Cuántas ofertas nuevas de cada color se clasificaron en esta corrida.
        started: Cuándo arrancó la corrida de este usuario.
    Raises:
        LabubotForbiddenError: Si el usuario bloqueó el bot.
    """
    found = []
    empty = []
    for term in keywords:
        label = OTHER_PORTALS
        if term is not None:
            label = escape(term)
        if term not in matches:
            empty.append(label)
            continue
        greens = yellows = 0
        for _offer, light in matches[term]:
            if light == TrafficLight.GREEN:
                greens += 1
            else:
                yellows += 1
        counts = []
        if greens:
            counts.append(SUMMARY_GREENS.format(count=greens))
        if yellows:
            counts.append(SUMMARY_YELLOWS.format(count=yellows))
        found.append(
            SUMMARY_LINE.format(term=label, counts=SUMMARY_SEPARATOR.join(counts))
        )

    time.sleep(PAUSE)
    end = datetime.now()
    title = SUMMARY_TITLE.format(start=f"{started:%H:%M}", end=f"{end:%H:%M}")
    total = SUMMARY_TOTAL.format(
        total=colors.total(),
        greens=colors[TrafficLight.GREEN],
        yellows=colors[TrafficLight.YELLOW],
        reds=colors[TrafficLight.RED],
    )
    blocks = [f"{title}\n{total}"]
    if found:
        blocks.append("\n".join(found))
    if empty:
        blocks.append(SUMMARY_EMPTY.format(terms=", ".join(empty)))
    telegram.send_message(chat_id, "\n\n".join(blocks), silent=True, html=True)


def _save_results(verdicts: list[list], started: datetime, chat_id: int | None) -> None:
    """
    Guarda el .json con cada oferta, una sola vez, y el .csv con cada veredicto.
    Args:
        verdicts: chat_id, palabra, color y oferta de cada clasificación, de todos los usuarios.
        started: Cuándo arrancó la corrida; da el nombre de los dos archivos.
        chat_id: El usuario de la corrida, si era de uno solo; va en el nombre para
            que las corridas en paralelo, que arrancan juntas, no se pisen.
    """
    offers: dict[str, Offer] = {}
    for _chat_id, _term, _light, offer in verdicts:
        offers[offer["url"]] = offer
    RESULTS_DIR.mkdir(exist_ok=True)
    name = f"{started:%Y-%m-%d_%H%M%S}"
    if chat_id is not None:
        name = f"{name}_{chat_id}"
    path = RESULTS_DIR / f"{name}.json"
    path.write_text(
        json.dumps(list(offers.values()), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with path.with_suffix(".csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["chat_id", "term", "light", "title", "url"])
        for chat_id, term, light, offer in verdicts:
            writer.writerow([chat_id, term, light, offer["title"], offer["url"]])


def _word_in_title(title: str, words: list[str]) -> str | None:
    """
    La primera de las palabras que aparece en el título.
    Args:
        title: Título de la oferta.
        words: Palabras en minúsculas: las bloqueadas o las de búsqueda de un usuario.
    Returns:
        str | None: La palabra, o None si no aparece ninguna.
    """
    for word in words:
        if word in title.lower():
            return word
    return None


if __name__ == "__main__":
    main()
