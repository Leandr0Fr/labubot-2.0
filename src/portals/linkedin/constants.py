"""Constantes de LinkedIn: el endpoint `jobs-guest`, lo que ve un deslogueado."""

_BASE = "https://www.linkedin.com"

SEARCH_URL = f"{_BASE}/jobs-guest/jobs/api/seeMoreJobPostings/search"

JOBS_PER_PAGE = 10

# Medido sin pausa entre pedidos: ~18 % da 429, nunca más de 3 seguidos.
PAUSE = 3.0
RETRIES = 10

SEL_JOB_CARD = ".base-search-card"
SEL_JOB_TITLE = ".base-search-card__title"
SEL_JOB_LINK = ".base-card__full-link"

# El primero es la ubicación; el segundo, la cantidad de postulantes.
SEL_DETAIL_LOCATION = ".topcard__flavor--bullet"
SEL_DESCRIPTION = "div.show-more-less-html__markup"

# La página pública de una publicación (/posts/...) trae su texto en un JSON-LD.
SEL_JSON_LD = 'script[type="application/ld+json"]'
POST_TYPE = "SocialMediaPosting"
