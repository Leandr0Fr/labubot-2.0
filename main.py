"""
LABUBOT 2.0
"""

import csv
import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path

from src.classifier.openai import Classifier
from src.config.search import BLOCKED_TITLE_WORDS, TERMS
from src.db.seen import SeenUrls
from src.driver.http import Driver
from src.enums.traffic_light import TrafficLight
from src.notifier.telegram import Telegram
from src.portals.bumeran import Bumeran
from src.portals.computrabajo import Computrabajo
from src.portals.empleosit import EmpleosIT
from src.portals.getonbrd import GetOnBoard
from src.portals.himalayas import Himalayas
from src.portals.indeed import Indeed
from src.portals.jobicy import Jobicy
from src.portals.linkedin import LinkedIn
from src.portals.talent import Talent
from src.portals.weworkremotely import WeWorkRemotely
from src.portals.workable import Workable
from src.schemas.job import Offer

RESULTS_DIR = Path("resultados")
SEEN_PATH = Path("vistas.txt")
PROFILE_PATH = Path("perfil.md")

logger = logging.getLogger(__name__)


def main() -> None:
    seen = SeenUrls(SEEN_PATH)
    driver = Driver()
    offers: list[Offer] = []

    try:
        found = []
        for portal in (
            LinkedIn(driver),
            Bumeran(driver),
            Computrabajo(driver),
            GetOnBoard(driver),
            Himalayas(driver),
            Talent(driver),
        ):
            # Por url: los términos se pisan entre sí.
            jobs: dict[str, str] = {}
            for term in TERMS:
                term_jobs = portal.search(term)
                jobs.update(term_jobs)
                logger.debug(
                    f"{type(portal).__name__} '{term}': {len(term_jobs)} ofertas"
                )
            logger.info(f"{type(portal).__name__}: {len(jobs)} ofertas")
            found.append((portal, jobs))

        # Entienden OR: una sola búsqueda con todos los términos.
        quoted_terms = []
        for term in TERMS:
            quoted = term
            if " " in term:
                quoted = f'"{term}"'
            quoted_terms.append(quoted)
        any_term = " OR ".join(quoted_terms)
        for portal in (Indeed(driver), EmpleosIT(driver), Workable(driver)):
            jobs = portal.search(any_term)
            logger.info(f"{type(portal).__name__}: {len(jobs)} ofertas")
            found.append((portal, jobs))

        # Sin búsqueda: traen todo lo reciente y filtra el LLM.
        for portal in (Jobicy(driver), WeWorkRemotely(driver)):
            jobs = portal.search()
            logger.info(f"{type(portal).__name__}: {len(jobs)} ofertas")
            found.append((portal, jobs))

        already_seen = blocked = empty = 0
        for portal, jobs in found:
            for url, title in jobs.items():
                if seen.exists(url):
                    already_seen += 1
                    continue
                word = None
                for banned in BLOCKED_TITLE_WORDS:
                    if banned in title.lower():
                        word = banned
                        break
                if word:
                    logger.debug(f"Título bloqueado por '{word}': {title}")
                    blocked += 1
                    continue
                description = portal.description(url)
                seen.add(url)
                if not description:
                    empty += 1
                    continue
                offers.append(Offer(title=title, description=description, url=url))
        logger.info(
            f"{len(offers)} ofertas nuevas; salteadas: {already_seen} ya vistas, "
            f"{blocked} por título, {empty} sin descripción"
        )

        RESULTS_DIR.mkdir(exist_ok=True)
        path = RESULTS_DIR / f"{datetime.now():%Y-%m-%d_%H%M}.json"
        path.write_text(
            json.dumps(offers, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        lights = Classifier(PROFILE_PATH.read_text(encoding="utf-8")).classify(offers)
        csv_path = path.with_suffix(".csv")
        with csv_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["light", "title", "url"])
            for offer in offers:
                writer.writerow([lights[offer["url"]], offer["title"], offer["url"]])
        colors = Counter(lights.values())
        logger.info(
            f"Clasificadas: {colors[TrafficLight.GREEN]} verdes, "
            f"{colors[TrafficLight.YELLOW]} amarillas, "
            f"{colors[TrafficLight.RED]} rojas (en {csv_path})"
        )

        telegram = Telegram(driver)
        sent = 0
        for offer in offers:
            light = lights[offer["url"]]
            if light == TrafficLight.RED:
                continue
            telegram.send(offer, light)
            sent += 1
        logger.info(f"{sent} enviadas a Telegram")
    finally:
        driver.close()
    # Recién acá: si algo falló, la próxima corrida vuelve a leer esas ofertas.
    seen.save()


if __name__ == "__main__":
    main()
