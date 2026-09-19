"""Constantes de Gemini. Se habla por el SDK oficial `google-genai`."""

MODEL = "gemini-3-flash-preview"

# Gemini 3 piensa y esos tokens cuentan como salida.
THINKING_LEVEL = "low"
TEMPERATURE = 0.2

# Ofertas por request. El techo real es el RPM del free tier, no los tokens.
BATCH_SIZE = 10

# Tiene que cubrir razonamiento + BATCH_SIZE veredictos.
MAX_TOKENS = 8000
