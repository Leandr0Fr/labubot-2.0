"""Constantes de SuTrabajo: la REST pública de su WordPress, que ya trae la descripción."""

_BASE = "https://www.sutrabajo.com"

SEARCH_URL = f"{_BASE}/{{section}}/wp-json/wp/v2/jobs"

ARGENTINA_SECTION = "argentina"

SECTIONS = (ARGENTINA_SECTION, "remoto")

JOBS_PER_PAGE = 100

FIELDS = "title,content,civi-jobs_apply_external"

TRACKING_PREFIX = "utm_"
