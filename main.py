"""
LABUBOT 2.0
"""

import json
from datetime import datetime
from pathlib import Path

from src.config.search import TERMS
from src.db.seen import SeenUrls
from src.driver.http import Driver
from src.portals.linkedin import LinkedIn
from src.schemas.job import Offer

RESULTS_DIR = Path("resultados")
SEEN_PATH = Path("vistas.txt")


def main() -> None:
    seen = SeenUrls(SEEN_PATH)
    driver = Driver()
    # Por url: los términos se pisan entre sí.
    jobs: dict[str, str] = {}
    offers: list[Offer] = []

    try:
        linkedin = LinkedIn(driver)
        for term in TERMS:
            jobs.update(linkedin.search(term))
            print(f"  {term}: {len(jobs)} ofertas")

        for url, title in jobs.items():
            if seen.exists(url):
                continue
            description = linkedin.description(url)
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
