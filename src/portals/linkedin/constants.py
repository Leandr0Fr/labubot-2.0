"""Constantes de LinkedIn: el endpoint `jobs-guest`, lo que ve un deslogueado."""

_BASE = "https://www.linkedin.com"

# Devuelve un fragmento de <li>, no una página.
SEARCH_URL = f"{_BASE}/jobs-guest/jobs/api/seeMoreJobPostings/search"

JOBS_PER_PAGE = 10

# Medido: con 3 s, ~10 % de los detalles da 429 y nunca más de 2 seguidos.
PAUSE = 3.0
RETRIES = 10

SEL_JOB_CARD = ".base-search-card"
SEL_JOB_TITLE = ".base-search-card__title"
SEL_JOB_LINK = ".base-card__full-link"
