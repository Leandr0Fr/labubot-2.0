"""Constantes de Bumeran: la API JSON que usa su propio front (`/api/*`)."""

_BASE = "https://www.bumeran.com.ar"

SEARCH_URL = f"{_BASE}/api/avisos/searchV2"

DETAIL_URL = f"{_BASE}/api/candidates/fichaAvisoNormalizada/{{job_id}}"

JOB_URL = f"{_BASE}/empleos/{{job_id}}.html"
ZONAJOBS_JOB_URL = "https://www.zonajobs.com.ar/empleos/{job_id}.html"
ZONAJOBS_PORTAL = "zonajobs"

HEADERS = {
    "x-site-id": "BMAR",
    "Referer": f"{_BASE}/",
}

JOBS_PER_PAGE = 100

SORT = "RECIENTES"
