"""Constantes de Clarín Clasificados: la API JSON de su front, rubro Empleos."""

_BASE = "https://clasificados.clarin.com"

# El último tramo es el orden por fecha ascendente: false = lo más nuevo primero.
SEARCH_URL = f"{_BASE}/aviso/{{page}}/listado/{{keywords}}/filtro/Empleos/false"

JOB_URL = f"{_BASE}/inicio/index#!/detalle-aviso/{{job_id}}"

DAY_SECONDS = 86400

# El rubro llega como "Empleos;Oficios y Ocupaciones Varias".
SECTION_SEPARATOR = ";"

# El aviso es un texto corrido, sin título: el título son sus primeros caracteres.
TITLE_LENGTH = 80
