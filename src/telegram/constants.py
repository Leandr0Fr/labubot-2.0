"""Constantes de Telegram: la Bot API, los comandos, los botones y los textos del bot."""

from src.enums.command import Command
from src.enums.traffic_light import TrafficLight
from src.enums.user_status import UserStatus

BOT_API_URL = "https://api.telegram.org/bot{token}/{method}"
FILE_URL = "https://api.telegram.org/file/bot{token}/{file_path}"

# La Bot API pide no pasar de un mensaje por segundo en un mismo chat.
PAUSE = 1.0

EMOJIS = {
    TrafficLight.GREEN: "🟢",
    TrafficLight.YELLOW: "🟡",
}

COMMANDS = [
    {"command": Command.START, "description": "Pedir acceso o buscar ofertas ya"},
    {"command": Command.SETTINGS, "description": "Términos, bloqueadas y perfil"},
    {"command": Command.PROFILE, "description": "Ver o reemplazar tu CV"},
    {
        "command": Command.ALLOW,
        "description": "Sumar términos: /permitido python, django",
    },
    {
        "command": Command.BLOCK,
        "description": "Bloquear palabras: /bloquear php, wordpress",
    },
    {"command": Command.TEMPLATE, "description": "Plantilla para armar tu CV"},
    {"command": Command.PAUSE, "description": "Pausar las alertas"},
    {"command": Command.RESUME, "description": "Volver a recibir alertas"},
    {"command": Command.CLEAR, "description": "Borrar los mensajes del chat"},
    {"command": Command.HELP, "description": "Qué hace el bot y cómo usarlo"},
]
ADMIN_COMMANDS = [
    {"command": Command.USERS, "description": "Usuarios y su estado"},
]
COMMAND_PREFIX = "/"
CALLBACK_SEPARATOR = ":"
PRIVATE_CHAT = "private"

BUTTON_TERMS = "🔎 Términos"
BUTTON_BLOCKED = "🚫 Bloqueadas"
BUTTON_PROFILE = "📄 Perfil"
BUTTON_PAUSE = "⏸ Pausar"
BUTTON_RESUME = "▶️ Reanudar"
BUTTON_ADD = "➕ Agregar"
BUTTON_REMOVE = "➖ Quitar"
BUTTON_BACK = "⬅ Volver"
BUTTON_CANCEL = "✖ Cancelar"
BUTTON_REPLACE = "✏️ Reemplazar"
BUTTON_APPROVE = "✅ Aprobar"
BUTTON_REJECT = "❌ Rechazar"

WELCOME_PENDING = (
    "👋 Hola {first_name}. Soy labubot: busco ofertas en 12 portales y te mando "
    "las que encajan con tu perfil.\n"
    "Tu solicitud quedó pendiente: te aviso cuando la apruebe el admin."
)
STILL_PENDING = "⏳ Tu solicitud sigue pendiente."
REJECTED = "No tenés acceso a este bot."
BACK_AGAIN = "👋 ¡Volviste! Las alertas siguen como las dejaste."
SEARCH_QUEUED = (
    "🔎 Arranco una búsqueda para vos: cuando termine te llegan las ofertas y "
    "el resumen."
)
ADMIN_REQUEST = "🆕 Solicitud de acceso\n{first_name} (@{username})\nchat_id {chat_id}"
ADMIN_APPROVED = "✅ Aprobada: {first_name} (@{username})"
ADMIN_REJECTED = "❌ Rechazada: {first_name} (@{username})"
APPROVED = (
    "✅ ¡Listo, ya tenés acceso!\n"
    "Mandame tu CV con /perfil: lo uso para decidir qué ofertas te sirven. "
    "Con /template te paso una plantilla para armarlo.\n"
    "Después cargá en /settings los términos que querés buscar y las palabras "
    "que descartan una oferta por el título."
)
NO_USERNAME = "-"

ASK_PROFILE = (
    "📄 Mandame tu perfil como texto o como archivo .md / .txt. Reemplaza al anterior.\n"
    "¿No sabés cómo armarlo? Mirá /template."
)
PROFILE_CURRENT = "📄 Este es tu perfil actual:"
PROFILE_REPLACE_HINT = "Para cambiarlo, tocá ✏️ Reemplazar."
# La Bot API corta en 4096, contados en UTF-16: un emoji ocupa 2.
MESSAGE_LIMIT = 4096
PROFILE_SAVED = "📄 Perfil guardado. Lo podés leer con /perfil; mandá /start para buscar ofertas ya."
PROFILE_EXTENSIONS = (".md", ".txt")

SETTINGS_PANEL = (
    "⚙️ Tu configuración\n"
    "Términos: {terms} · Bloqueadas: {blocked} · Perfil: {profile_mark} · "
    "Alertas: {alerts}"
)
PROFILE_LOADED = "✅"
PROFILE_MISSING = "❌"
ALERTS_ACTIVE = "activas"
ALERTS_PAUSED = "pausadas"
TERMS_LIST = "🔎 Términos ({count})\n{items}"
BLOCKED_LIST = "🚫 Bloqueadas ({count})\n{items}"
LIST_SEPARATOR = " · "
EMPTY_LIST = "—"
ASK_TERMS = "Mandame los términos separados por coma."
ASK_BLOCKED = "Mandame las palabras separadas por coma."
INPUT_SEPARATOR = ","
ADDED = "Agregados: {items}. Ahora tenés {count}."
REMOVED = "Quitados: {items}. Ahora tenés {count}."
ALLOW_USAGE = "Escribí los términos después del comando, separados por coma: /permitido python, django"
BLOCK_USAGE = "Escribí las palabras después del comando, separadas por coma: /bloquear php, wordpress"
NONE_CHANGED = "ninguno"

PAUSED = "⏸ Alertas pausadas. Usá /reanudar cuando quieras volver."
CHAT_CLEARED = (
    "🧹 Listo: borré los mensajes de las últimas 48 h. Los más viejos Telegram no "
    "deja borrarlos."
)
# deleteMessages acepta hasta 100 ids por llamada.
DELETE_BATCH = 100
CLEAR_LOOKBACK = 3000
RESUMED = "▶️ Alertas activas de nuevo."
ALREADY_PAUSED = (
    "⏸ Tus alertas ya estaban pausadas. Usá /reanudar cuando quieras volver."
)
ALREADY_ACTIVE = "▶️ Tus alertas ya están activas."
UNKNOWN = "No entendí. Usá /settings para ver tu configuración o /ayuda."
HELP = (
    "🤖 labubot busca ofertas en 12 portales con tus términos, cada hora y cuando "
    "mandás /start. Las compara con tu CV y te manda las que sirven: "
    "🟢 encaja · 🟡 puede servir.\n"
    "Te llega un bloque por término y, al final, el resumen de la corrida.\n\n"
    "/settings Términos, bloqueadas y perfil\n"
    "/permitido python, django Sumar términos de búsqueda\n"
    "/bloquear php, wordpress Sumar palabras bloqueadas\n"
    "/start Buscar ofertas ya\n"
    "/perfil Ver o reemplazar tu CV\n"
    "/template Plantilla para armar tu CV\n"
    "/pausa Pausar las alertas\n"
    "/reanudar Volver a recibir alertas\n"
    "/clear Borrar los mensajes del chat (últimas 48 h)\n"
    "/ayuda Este mensaje\n\n"
    "El CV funciona mejor en Markdown y con: seniority, stack, idiomas (tu nivel "
    "de inglés), modalidad (dónde aceptás presencial o híbrido) y lo que no querés: "
    "/template te da la plantilla."
)
TEMPLATE_INTRO = (
    "📝 Abajo va la plantilla. Copiala, completala con tus datos y mandámela con "
    "/perfil, como texto o como archivo .md.\n\n"
    "Escribí concreto y en primera persona: comparo cada oferta contra esto. "
    "Seniority, Idiomas, Modalidad y «Lo que NO quiero» son lo que más descarta, "
    "así que no los saltees.\n\n"
    "Si tenés el CV en PDF, pasáselo a un chat de IA junto con la plantilla y "
    "pedile que la complete; después revisá que diga la verdad."
)
PROFILE_TEMPLATE = """\
# Nombre Apellido — Rol que buscás (ej.: Desarrolladora Backend Python)

## Resumen
Dos o tres líneas: qué hacés, en qué sos fuerte y qué tipo de puesto buscás.

## Seniority
**Experiencia profesional: 2 años** (desde marzo de 2024).
- Junior y Semi Senior: encajo.
- Piden 3 años: me falta poco; amarillo.
- Senior, Lead o 4+ años: no encajo.

## Roles que me sirven
- Backend con Python (APIs REST, integraciones).
- Automatización y procesos de datos.

## Experiencia
### Puesto — Empresa · mes año – actualidad · remoto
- Qué hiciste, con qué tecnologías y qué resultado tuvo.
- Otro logro concreto, con números si los tenés.

### Puesto anterior — Empresa · mes año – mes año
- Lo mismo: tareas, stack y resultado.

## Stack
**Uso diario, en producción:** Python, FastAPI, PostgreSQL, Docker, Git.
**Conozco, sin producción:** Django, React.
**Nivel inicial:** Node.js.

## Formación
Carrera o curso, institución y año (o "en curso").

## Idiomas
**Inglés: B1 (intermedio).** Leo documentación técnica, pero no sostengo una
entrevista ni el día a día en inglés. Un aviso escrito en inglés, o que pida
inglés avanzado, fluido o B2+, no me sirve.

## Modalidad y contratación
Remoto desde cualquier lugar me sirve. Presencial o híbrido, solo en AMBA
(CABA y conurbano). Si el aviso no dice dónde es, no lo descartes por eso.
Relación de dependencia o contractor, en pesos o en USD.

## Lo que NO quiero
- Roles mayormente frontend.
- Soporte técnico, mesa de ayuda o QA manual.
- Puestos de liderazgo o gestión de equipos.
"""

START_ONLY = (UserStatus.PENDING, UserStatus.REJECTED, UserStatus.BLOCKED)

USERS_HEADER = "👥 Usuarios ({count})"
USER_LINE = "{first_name}{username}\n{status} · {chat_id}"
STATUS_LABELS = {
    UserStatus.ACTIVE: "✅ activo",
    UserStatus.PAUSED: "⏸ pausado",
    UserStatus.PENDING: "⏳ pendiente",
    UserStatus.REJECTED: "❌ rechazado",
    UserStatus.BLOCKED: "🚫 bloqueó el bot",
}

OFFER = '{emoji} <b>{title}</b>\n<a href="{url}">{site}</a>'
KEYWORD_HEADER = "🔎 <b>{term}</b>"
OTHER_PORTALS_HEADER = "🌐 <b>Otros portales</b>"
OTHER_PORTALS = "Otros portales"
SUMMARY_TITLE = "📋 <b>Resumen</b> · {start} a {end}"
SUMMARY_TOTAL = "{total} ofertas nuevas: 🟢 {greens} · 🟡 {yellows} · 🔴 {reds}"
SUMMARY_LINE = "{term}: {counts}"
SUMMARY_SEPARATOR = " · "
SUMMARY_GREENS = "🟢 {count}"
SUMMARY_YELLOWS = "🟡 {count}"
SUMMARY_EMPTY = "Sin coincidencias: {terms}"
