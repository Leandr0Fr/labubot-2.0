"""Constantes de SuTrabajo: la REST pública de su WordPress, que ya trae la descripción."""

_BASE = "https://www.sutrabajo.com"

# El prefijo de la URL filtra por país también en la REST; "remoto" es uno más.
SEARCH_URL = f"{_BASE}/{{section}}/wp-json/wp/v2/jobs"

SECTIONS = ("argentina", "remoto")

JOBS_PER_PAGE = 100

# Sin esto cada oferta trae ~25 KB de metadatos del tema.
FIELDS = "title,content,civi-jobs_apply_external"
