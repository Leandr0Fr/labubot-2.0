"""Constantes de Buscojobs Argentina: la API JSON pública que usa su front."""

SEARCH_URL = "https://api.buscojobs.com/v3/ar/api/ofertas"

DETAIL_URL = f"{SEARCH_URL}/{{job_id}}"

# La url pública termina en "-ID-15103388".
ID_SEPARATOR = "-"

JOBS_PER_PAGE = 50

# El filtro de recencia va en días enteros.
DAY_HOURS = 24

REMOTE = "Remoto"
HYBRID = "Híbrido"
