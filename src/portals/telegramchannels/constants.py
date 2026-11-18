"""Constantes de los canales de Telegram: su vista web pública, sin login."""

CHANNEL_URL = "https://t.me/s/{channel}"

# Solo canales públicos: un grupo no tiene vista web y redirige a una página sin mensajes.
CHANNELS = ("LaburoArgento",)

# Los mensajes son un link pelado. Solo se toman las publicaciones de LinkedIn:
# los otros links van a portales que labubot ya busca por su cuenta.
POST_PREFIXES = ("https://lnkd.in/p/", "https://www.linkedin.com/posts/")

SEL_MESSAGE = ".tgme_widget_message"
SEL_DATE = "time[datetime]"
# La tarjeta que Telegram arma con el título y las primeras líneas del link.
SEL_PREVIEW = "a.tgme_widget_message_link_preview"
SEL_PREVIEW_TITLE = ".link_preview_title"
SEL_PREVIEW_TEXT = ".link_preview_description"

# Una publicación no tiene título: el título son sus primeros caracteres.
TITLE_LENGTH = 80

# "LaburoArgento/87916": el número es el id con el que se pagina hacia atrás.
ATTR_ID = "data-post"
