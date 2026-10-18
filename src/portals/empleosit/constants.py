"""Constantes de Empleos IT: un SmartJobBoard renderizado del lado del servidor."""

_BASE = "https://www.empleosit.com.ar"

SEARCH_URL = f"{_BASE}/search-results-jobs/"

JOB_URL = f"{_BASE}/display-job/{{job_id}}/"

JOBS_PER_PAGE = 100

CRAWL_DELAY = 10.0

SORTING_FIELD = "activation_date"
SORTING_ORDER = "DESC"

SEL_JOB_CARD = "div.searchResultsJobs div.listing-section"
SEL_JOB_ANCHOR = "div.listing-title a[name]"
SEL_JOB_TITLE = "div.listing-title a[href]"
ANCHOR_PREFIX = "listing_"

SEL_DESCRIPTION = "fieldset#col-wide div.displayField"
