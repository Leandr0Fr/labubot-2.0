"""Constantes de Talent.com Argentina: el listado /jobs y la página /view."""

_BASE = "https://ar.talent.com"

SEARCH_URL = f"{_BASE}/jobs"

JOB_URL = f"{_BASE}/view?id={{job_id}}"

SEL_JOB_CARD = "div[data-new-id]"
SEL_JOB_TITLE = 'h2[class*="JobCard_title__"]'

DESCRIPTION_LABEL = "Descripción del trabajo"

# Viene como "Empresa • lugar".
SEL_DETAIL_LOCATION = 'span[class*="styles_jobLocation__"]'
COMPANY_SEPARATOR = "•"
