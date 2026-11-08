"""
Constantes de transporte HTTP.
HTTP_TIMEOUT: Segundos de espera por request antes de darlo por fallado.
ACCEPT_LANGUAGE: Los idiomas que se piden, castellano primero.
USER_AGENT: El de un Chrome de escritorio, para no presentarse como python-httpx.
"""

HTTP_TIMEOUT = 25.0

ACCEPT_LANGUAGE = "es-AR,es;q=0.9,en;q=0.8"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)
