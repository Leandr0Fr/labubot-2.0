"""Constantes de transporte HTTP."""

HTTP_TIMEOUT = 25.0

PAUSE = 1.5

# Transitorios: el 429 del rate limit y los 5xx de un backend saturado.
RETRY_STATUS = (500, 502, 503, 504)

# Sin retry-after, espera 20s, 40s, 80s.
RETRIES_TRANSIENT = 3
WAIT_TRANSIENT = 20.0

# Techo a lo que un sitio puede pedirnos esperar.
MAX_WAIT = 120.0

NETWORK_RETRIES = 2

ACCEPT_LANGUAGE = "es-AR,es;q=0.9,en;q=0.8"

# Para no presentarse como python-httpx.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)
