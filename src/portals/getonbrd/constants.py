"""Constantes de Get on Board: su API pública v0, que ya trae la descripción."""

SEARCH_URL = "https://www.getonbrd.com/api/v0/search/jobs"

JOBS_PER_PAGE = 120
# Su API corta con 429 a los ~30 pedidos seguidos; medido: con 0,3 s ya no corta.
PAUSE = 0.5

LOCATIONS: tuple[dict[str, str], ...] = (
    {"country_code": "AR"},
    {"remote": "true"},
)

DESCRIPTION_SECTIONS = ("projects", "functions", "description", "desirable", "benefits")
