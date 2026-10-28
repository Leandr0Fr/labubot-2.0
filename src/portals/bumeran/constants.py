"""Constantes de Bumeran: la API JSON que usa su propio front (`/api/*`)."""

_BASE = "https://www.bumeran.com.ar"

SEARCH_URL = f"{_BASE}/api/avisos/searchV2"

DETAIL_URL = f"{_BASE}/api/candidates/fichaAvisoNormalizada/{{job_id}}"

JOB_URL = f"{_BASE}/empleos/{{job_id}}.html"
ZONAJOBS_JOB_URL = "https://www.zonajobs.com.ar/empleos/{job_id}.html"
ZONAJOBS_PORTAL = "zonajobs"

REMOTE = "Remoto"
# `localizacion` es "Localidad, Provincia"; CABA es "Capital Federal, Buenos Aires".
# La provincia suma el interior bonaerense: ese lo descarta el LLM.
AMBA_PROVINCE = "Buenos Aires"

HEADERS = {
    "x-site-id": "BMAR",
    "Referer": f"{_BASE}/",
}

JOBS_PER_PAGE = 100

SORT = "RECIENTES"

RECENCY_FILTER = "dias_fecha_publicacion"

RECENCY_BUCKETS = {
    21: "publicacion-menor-a-2-dias",
    69: "publicacion-menor-a-3-dias",
    93: "publicacion-menor-a-4-dias",
    117: "publicacion-menor-a-5-dias",
    141: "publicacion-menor-a-6-dias",
    165: "publicacion-menor-a-7-dias",
    357: "publicacion-menor-a-15-dias",
    741: "publicacion-menor-a-1-mes",
}
