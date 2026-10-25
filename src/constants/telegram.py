"""Constantes de Telegram: la Bot API, un mensaje por oferta."""

from src.enums.traffic_light import TrafficLight

SEND_MESSAGE_URL = "https://api.telegram.org/bot{token}/sendMessage"

# La Bot API pide no pasar de un mensaje por segundo en un mismo chat.
PAUSE = 1.0

EMOJIS = {
    TrafficLight.GREEN: "🟢",
    TrafficLight.YELLOW: "🟡",
}
