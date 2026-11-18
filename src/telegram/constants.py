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
    {"command": Command.INFO, "description": "De qué sitios salen las ofertas"},
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
BUTTON_IT_ON = "💻 Sumar portales IT"
BUTTON_IT_OFF = "💻 Quitar portales IT"
BUTTON_ADD = "➕ Agregar"
BUTTON_REMOVE = "➖ Quitar"
BUTTON_BACK = "⬅ Volver"
BUTTON_CANCEL = "✖ Cancelar"
BUTTON_REPLACE = "✏️ Reemplazar"
BUTTON_APPROVE = "✅ Aprobar"
BUTTON_REJECT = "❌ Rechazar"

WELCOME_PENDING = (
    "👋 Hola {first_name}. Soy labubot: busco ofertas en 13 portales y te mando "
    "las que encajan con tu perfil.\n"
    "Tu solicitud quedó pendiente: te aviso cuando la apruebe el admin."
)
STILL_PENDING = "⏳ Tu solicitud sigue pendiente."
REJECTED = "No tenés acceso a este bot."
BACK_AGAIN = "👋 ¡Volviste! Las alertas siguen como las dejaste."
SEARCH_QUEUED = (
    "🔎 Arranco una búsqueda para vos: si aparece alguna oferta que te sirva, "
    "te llega con el resumen."
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
    "Alertas: {alerts} · Portales IT: {it}"
)
PROFILE_LOADED = "✅"
PROFILE_MISSING = "❌"
ALERTS_ACTIVE = "activas"
ALERTS_PAUSED = "pausadas"
IT_ON = "sí"
IT_OFF = "no"
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
    "🤖 labubot busca ofertas en 13 portales con tus términos, cada hora y cuando "
    "mandás /start. Las compara con tu CV y te manda las que sirven: "
    "🟢 encaja · 🟡 puede servir.\n"
    "Te llega un bloque por término y, al final, el resumen de la corrida. "
    "Si no hay ninguna, no te escribo.\n\n"
    "/settings Términos, bloqueadas y perfil\n"
    "/permitido python, django Sumar términos de búsqueda\n"
    "/bloquear php, wordpress Sumar palabras bloqueadas\n"
    "/start Buscar ofertas ya\n"
    "/perfil Ver o reemplazar tu CV\n"
    "/template Plantilla para armar tu CV\n"
    "/pausa Pausar las alertas\n"
    "/reanudar Volver a recibir alertas\n"
    "/clear Borrar los mensajes del chat (últimas 48 h)\n"
    "/info De qué sitios salen las ofertas\n"
    "/ayuda Este mensaje\n\n"
    "El CV funciona mejor en Markdown y con: seniority, herramientas, idiomas (tu nivel "
    "de inglés), modalidad (dónde aceptás presencial o híbrido) y lo que no querés: "
    "/template te da la plantilla."
)
INFO = (
    "🌐 Busco en estos 13 portales.\n\n"
    "Con cada uno de tus términos:\n"
    "• LinkedIn — linkedin.com\n"
    "• Computrabajo — ar.computrabajo.com\n"
    "• Bumeran y ZonaJobs — bumeran.com.ar y zonajobs.com.ar (un mismo buscador)\n"
    "• Indeed — ar.indeed.com\n"
    "• Randstad — randstad.com.ar\n"
    "• Clarín Clasificados — clasificados.clarin.com\n"
    "• Canales de Telegram — publicaciones de LinkedIn que comparte t.me/LaburoArgento\n"
    "• Workable — jobs.workable.com\n"
    "• Get on Board — getonbrd.com\n"
    "• Himalayas — himalayas.app\n\n"
    "Solo si sumás los portales IT en /settings, todo lo reciente de tecnología:\n"
    "• Empleos IT — empleosit.com.ar\n"
    "• Jobicy — jobicy.com\n"
    "• We Work Remotely — weworkremotely.com\n\n"
    "En cada oferta, debajo del título, figura el sitio del que salió."
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
# Nombre Apellido — Rol que buscás (ej.: Analista contable, Desarrollador backend)

## Resumen
Dos o tres líneas: qué hacés, en qué sos fuerte y qué tipo de puesto buscás.

## Seniority
**Experiencia profesional: 2 años** (desde marzo de 2024).
- Junior y Semi Senior: encajo.
- Piden 3 años: me falta poco; amarillo.
- Senior, jefatura o 4+ años: no encajo.

## Roles que me sirven
- El puesto principal que buscás (ej.: analista contable; backend con Python).
- Otros puestos que también aceptarías (ej.: administración, facturación).

## Experiencia
### Puesto — Empresa · mes año – actualidad · presencial, híbrido o remoto
- Qué hiciste, con qué herramientas y qué resultado tuvo.
- Otro logro concreto, con números si los tenés.

### Puesto anterior — Empresa · mes año – mes año
- Lo mismo: tareas, herramientas y resultado.

## Herramientas y conocimientos
**Uso diario:** las que manejás bien (ej.: Excel avanzado, Tango, SAP; o Python,
PostgreSQL, Docker).
**Conozco, sin experiencia laboral:** las que viste en cursos o proyectos propios.
**Nivel inicial:** las que recién empezás.

## Formación
Carrera o curso, institución y año (o "en curso").

## Idiomas
**Inglés: B1 (intermedio).** Leo textos de trabajo, pero no sostengo una
entrevista ni el día a día en inglés. Un aviso escrito en inglés, o que pida
inglés avanzado, fluido o B2+, no me sirve.

## Modalidad y contratación
Remoto desde cualquier lugar me sirve. Presencial o híbrido, solo en AMBA
(CABA y conurbano). Si el aviso no dice dónde es, no lo descartes por eso.
Relación de dependencia o contractor, en pesos o en USD.

## Lo que NO quiero
- Rubros o tareas que no te interesan (ej.: ventas, atención al público, call center).
- Puestos de liderazgo o gestión de equipos.
- Turnos rotativos, de noche o de fin de semana.
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
