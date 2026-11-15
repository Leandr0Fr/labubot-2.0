"""
Constantes de la corrida.
RESULTS_DIR: Dónde quedan el .json y el .csv de cada corrida.
WITHOUT_SEARCH: Portales sin búsqueda: traen todo lo reciente y la palabra sale
    del título. Por nombre de clase, como las claves de `portals` en main.py.
HUB: El portal que republica avisos de otros sitios, reescritos, con la url
    del original.
HUB_ORIGINS: Los sitios de origen del hub cuyo aviso original labubot baja por
    url con su propio portal, en vez de usar la reescritura: dominio : nombre de
    clase del portal.
SEARCH_POLL_SECONDS: Cada cuántos segundos el worker mira si alguien pidió una
    búsqueda con /start.
"""

from pathlib import Path

RESULTS_DIR = Path("resultados")
WITHOUT_SEARCH = ("Bumeran", "EmpleosIT", "Jobicy", "WeWorkRemotely")
HUB = "SuTrabajo"
HUB_ORIGINS = {
    "ar.linkedin.com": "LinkedIn",
    "ar.computrabajo.com": "Computrabajo",
    "ar.talent.com": "Talent",
}
SEARCH_POLL_SECONDS = 5
