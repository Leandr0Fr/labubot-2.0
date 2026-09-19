"""
Constantes de LinkedIn: el endpoint `jobs-guest`, lo que ve un deslogueado.

No es una API oficial ni documentada, así que puede cambiar de forma sin aviso.
Por eso los selectores viven acá y el parseo entero en parser.py.
"""

_BASE = "https://www.linkedin.com"

# Devuelve un fragmento de <li>, no una página.
SEARCH_URL = f"{_BASE}/jobs-guest/jobs/api/seeMoreJobPostings/search"

# Se le pega el id al final.
DETAIL_URL = f"{_BASE}/jobs-guest/jobs/api/jobPosting"

# Link público, para cuando la tarjeta no trae el href.
JOB_URL = f"{_BASE}/jobs/view/{{job_id}}"

JOBS_PER_PAGE = 10

# Medido: en start=100 devuelve 429, nunca una página vacía. Es profundidad por
# búsqueda, no cantidad de requests.
MAX_PAGES = 10

# --- Listado -----------------------------------------------------------------
SEL_CARD = "div.base-card"
SEL_TITLE = "h3.base-search-card__title"
SEL_COMPANY = "h4.base-search-card__subtitle"
SEL_LOCATION = "span.job-search-card__location"
SEL_LINK = "a.base-card__full-link"
SEL_DATE = "time"

# --- Detalle -----------------------------------------------------------------
SEL_DESCRIPTION = "div.description__text"
SEL_DESCRIPTION_ALT = "section.show-more-less-html"
SEL_CRITERION = "li.description__job-criteria-item"
SEL_CRITERION_LABEL = "h3.description__job-criteria-subheader"
SEL_CRITERION_VALUE = "span.description__job-criteria-text"
SEL_APPLICANTS = "span.num-applicants__caption"

URN_PREFIX = "urn:li:jobPosting:"

# LinkedIn rotula los criterios en el idioma del Accept-Language. Mapeamos las
# dos variantes que nos pueden tocar en vez de confiar en el orden de la lista,
# que cambia según la oferta. Solo nos quedamos con los dos que el prompt usa:
# "Función laboral" y "Sectores" se parseaban y no los leía nadie.
LABELS: dict[str, str] = {
    "nivel de antiguedad": "seniority",
    "seniority level": "seniority",
    "tipo de empleo": "employment_type",
    "employment type": "employment_type",
}
