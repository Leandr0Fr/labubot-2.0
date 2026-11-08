"""Constantes de la corrida: portales sin búsqueda, el hub y dónde quedan los resultados."""

from pathlib import Path

RESULTS_DIR = Path("resultados")
# Sin búsqueda: traen todo lo reciente y la palabra sale del título.
# Por nombre de clase, como las claves de `portals` en main.py.
WITHOUT_SEARCH = ("Bumeran", "EmpleosIT", "Jobicy", "SuTrabajo", "WeWorkRemotely")
# Republica avisos de otros sitios, reescritos, con la url del original.
HUB = "SuTrabajo"
# Cada cuánto el worker mira si alguien pidió una búsqueda con /start.
SEARCH_POLL_SECONDS = 5
