"""
LABUBOT 2.0
"""

import json
from datetime import datetime
from pathlib import Path

from src.config.search import TERMS
from src.db.seen import SeenUrls
from src.driver.http import Driver
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
                jobs.update(portal.search(term))
                print(f"  {type(portal).__name__} {term}: {len(jobs)} ofertas")
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
            print(f"  {type(portal).__name__}: {len(jobs)} ofertas")
            found.append((portal, jobs))

        # Sin búsqueda: traen todo lo reciente y filtra el LLM.
        for portal in (Jobicy(driver), WeWorkRemotely(driver)):
            jobs = portal.search()
            print(f"  {type(portal).__name__}: {len(jobs)} ofertas")
            found.append((portal, jobs))

        for portal, jobs in found:
            for url, title in jobs.items():
                if seen.exists(url):
                    continue
                description = portal.description(url)
                seen.add(url)
                if not description:
                    continue
                offers.append(Offer(title=title, description=description, url=url))
    finally:
        driver.close()
        # Aunque corte a mitad: lo leído se guarda junto con sus ofertas.
        seen.save()
        RESULTS_DIR.mkdir(exist_ok=True)
        path = RESULTS_DIR / f"{datetime.now():%Y-%m-%d_%H%M}.json"
        path.write_text(
            json.dumps(offers, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(f"{len(offers)} ofertas nuevas en {path}")


if __name__ == "__main__":
    main()
