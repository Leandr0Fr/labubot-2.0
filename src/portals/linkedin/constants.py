"""Constantes de LinkedIn: el endpoint `jobs-guest`, lo que ve un deslogueado."""

_BASE = "https://www.linkedin.com"

# Devuelve un fragmento de <li>, no una página.
SEARCH_URL = f"{_BASE}/jobs-guest/jobs/api/seeMoreJobPostings/search"

# Se le pega el id al final.
DETAIL_URL = f"{_BASE}/jobs-guest/jobs/api/jobPosting"

JOB_URL = f"{_BASE}/jobs/view/{{job_id}}"

JOBS_PER_PAGE = 10

# Medido: en start=100 devuelve 429, nunca una página vacía.
MAX_PAGES = 10

SEL_JOB_CARD = ".base-search-card"
SEL_JOB_TITLE = ".base-search-card__title"
SEL_JOB_LINK = ".base-card__full-link"

SEL_DESCRIPTION_ALT = "section.show-more-less-html"

URN_PREFIX = "urn:li:jobPosting:"
