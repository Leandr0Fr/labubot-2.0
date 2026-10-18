"""
LABUBOT 2.0
"""

import json
from datetime import datetime
from pathlib import Path

from src.config.search import TERMS
from src.driver.http import Driver
from src.portals.linkedin import LinkedIn

RESULTS_DIR = Path("resultados")


def main() -> None:
    driver = Driver()
    # Por url: los términos se pisan entre sí.
    found: dict[str, dict[str, str]] = {}

    try:
        linkedin = LinkedIn(driver)
        for term in TERMS:
            for offer in linkedin.search(term):
                found.setdefault(offer["url"], offer)
            print(f"  {term}: {len(found)} ofertas")
    finally:
        driver.close()

    RESULTS_DIR.mkdir(exist_ok=True)
    path = RESULTS_DIR / f"{datetime.now():%Y-%m-%d_%H%M}.json"
    path.write_text(
        json.dumps(list(found.values()), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"{len(found)} ofertas en {path}")


if __name__ == "__main__":
    main()
