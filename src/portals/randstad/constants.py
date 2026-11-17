"""Constantes de Randstad Argentina: páginas HTML con los avisos en un JSON embebido."""

_BASE = "https://www.randstad.com.ar/trabajos"

SEARCH_URL = f"{_BASE}/q-{{keywords}}/"
# La primera página no lleva número.
NEXT_PAGE_URL = f"{SEARCH_URL}page-{{page}}/"

JOB_URL = f"{_BASE}/{{title}}_{{city}}_{{job_id}}/"

# El front guarda sus datos en `window.__ROUTE_DATA__ = {...};`.
ROUTE_DATA = "window.__ROUTE_DATA__"

# "2026-11-13 14:48:22", en hora de Argentina.
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
