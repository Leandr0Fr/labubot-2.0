"""Constantes de LinkedIn: el endpoint `jobs-guest`, lo que ve un deslogueado."""

_BASE = "https://www.linkedin.com"

# Devuelve un fragmento de <li>, no una página.
SEARCH_URL = f"{_BASE}/jobs-guest/jobs/api/seeMoreJobPostings/search"

JOBS_PER_PAGE = 10

# Espera antes de reintentar. Medido sin pausa entre pedidos: ~18 % da 429 y
# nunca más de 3 seguidos.
PAUSE = 3.0
RETRIES = 10

SEL_JOB_CARD = ".base-search-card"
SEL_JOB_TITLE = ".base-search-card__title"
SEL_JOB_LINK = ".base-card__full-link"
