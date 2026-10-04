"""Constantes de OpenAI. Se habla por el SDK oficial `openai`, Responses API."""

MODEL = "gpt-5.6-luna"

# Luna razona antes de responder y esos tokens se cobran como salida. Con
# razonamiento activado la API no acepta `temperature`.
REASONING_EFFORT = "high"

# Ofertas por request: el perfil y el system prompt viajan una vez por lote.
BATCH_SIZE = 10

# Tiene que cubrir razonamiento + BATCH_SIZE veredictos. Es el piso que OpenAI
# recomienda con razonamiento activado; si se queda corto, la respuesta vuelve
# `incomplete`.
MAX_OUTPUT_TOKENS = 25_000
