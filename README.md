# LABUBOT

Buscás como buscarías a mano, en 12 portales a la vez. Con Decisions de OpenAI analiza cada oferta
contra tu CV, la pinta de 🟢 🟡 🔴 y te manda por Telegram las que valen la pena.

Es un bot interno, para hasta 5 personas. Cada una tiene su CV, sus palabras clave y sus palabras
bloqueadas, y lo configura todo desde el chat con el bot.

<p align="center"><img src="docs/telegram/logo/labubot-512.png" alt="Logo de labubot" width="160"></p>

## La idea

Poner "python" en LinkedIn y revisar los resultados uno por uno. Eso es todo. La
diferencia es que las lee todas, entra en cada una a leer la descripción completa
—que es donde aparece el Python de los avisos titulados "Developer" a secas— y no
se cansa en la número 40.

Sin filtro de nivel: entran junior, senior y todo lo del medio. El LLM decide.

## Sin navegador, sin sesión

La v1 manejaba un Chrome real con Selenium sobre una cuenta logueada: apoyaba todo
el proyecto sobre lo único que LinkedIn sí castiga.

La v2 es **solo HTTP**: endpoints públicos, APIs de los propios sitios y HTML
que cualquier visitante anónimo puede ver. **No hay cookie, no hay sesión, no hay
cuenta.** El peor escenario dejó de ser una cuenta restringida y pasó a ser un
`429` que se cura esperando.

En LinkedIn se usa el endpoint `jobs-guest`, lo que ve un visitante deslogueado.
Verificado antes de escribir una línea: los ids que devuelve son un subconjunto
exacto de los que muestra `/jobs/search` deslogueado. Misma búsqueda.

> No es una API oficial ni documentada, y el ToS de LinkedIn desalienta la
> recolección automatizada aunque la página sea pública. Lo que cambia es que no
> hay una cuenta tuya de por medio.

## Portales

| Portal | Cómo se le habla | Búsqueda |
|---|---|---|
| LinkedIn | HTML del endpoint `jobs-guest` | una palabra clave por vez |
| Computrabajo | HTML de ar.computrabajo.com | una palabra clave por vez |
| Get on Board | API pública | una palabra clave por vez |
| Himalayas | API pública | una palabra clave por vez |
| Talent | HTML de ar.talent.com | una palabra clave por vez |
| Indeed | API GraphQL de su app | una palabra clave por vez |
| Workable | API de jobs.workable.com | una palabra clave por vez |
| Bumeran y ZonaJobs | API JSON de su front, que mezcla los dos sitios | una palabra clave por vez |
| Randstad | HTML con los avisos en un JSON embebido | una palabra clave por vez |
| Clarín Clasificados | API JSON de su front, rubro Empleos | una palabra clave por vez |
| Empleos IT | HTML de su buscador | sin búsqueda: todo lo reciente |
| Jobicy | API pública | sin búsqueda: todo lo reciente |
| SuTrabajo | REST de su WordPress | sin búsqueda: lo reciente de Argentina y de remoto |
| We Work Remotely | RSS de back-end y full-stack | sin búsqueda: todo lo reciente |

**Talent y SuTrabajo están fuera de la corrida:** bloquean la IP del VPS (403).
Su código sigue en `src/portals/`; para volver a sumarlos se anotan en `portals`
de `main.py`, y SuTrabajo también en `WITHOUT_SEARCH`.

**Buscojobs se eliminó:** no tiene avisos propios. Redistribuye los de WhatJobs,
Jobleads y Jooble como resúmenes de unas líneas, con títulos y ubicaciones que
no son los del aviso, y su link termina en un muro de registro.

Indeed y Workable buscaban con todos los términos juntos (`OR`). Pasan a buscar
palabra por palabra para saber qué palabra trajo cada oferta. Si empiezan a
contestar 429, se vuelve al `OR` y la palabra se saca del título.

Los que van sin búsqueda traen todo lo publicado en la ventana y el filtro lo
hace el LLM. Los tres son de tecnología, así que solo se le piden a quien sumó
los "portales IT" en su `/settings` (la columna `it` de `users`); un usuario
nuevo arranca sin ellos. Empleos IT sí busca, pero publica tan poco que por
término traía de 1 a 3 ofertas por corrida.

Bumeran traía solo el área de sistemas, sin término. Pasa a buscar con las
palabras de cada usuario en todas las áreas, para que sirva a quien no es de
sistemas: quien quiera lo que antes llegaba solo tiene que sumar esos términos.
Clarín Clasificados son avisos de una a tres líneas, sobre todo de oficios,
comercio y empleados; no tienen título, así que el título son sus primeros
caracteres. Randstad es una consultora de personal de todos los rubros; su
listado viene por relevancia y se recorre entero.

SuTrabajo es un hub: republica avisos de LinkedIn, Computrabajo, Jooble, Talent y
otros sitios, con el título y la descripción reescritos en español. Se guarda la
url del aviso original, así que lo que ya trajo LinkedIn no se repite, y suma
avisos de LinkedIn que `jobs-guest` no devuelve.

La reescritura traduce y pierde el idioma y el país del original, así que antes
de clasificar se verifica (`HUB_ORIGINS` en `src/constants/run.py`):

- Si el original es de `ar.linkedin.com`, `ar.computrabajo.com` o
  `ar.talent.com`, se baja con ese portal y el LLM evalúa el aviso real. La url
  se guarda sin los `utm_*`, así que una oferta que también trajo LinkedIn no se
  repite.
- Si no, o si ese portal no la puede servir, solo se usa la reescritura de la
  sección `/argentina/`, que SuTrabajo ya filtra para el país. Lo de `/remoto/`
  sin verificar se descarta: son bolsas internacionales (Himalayas, Greenhouse,
  Workday…) casi siempre en inglés y solo para EE. UU. o Europa.

### Ubicación

Se busca en todo el país y la zona la pone cada usuario en su CV, en la sección
"Modalidad y contratación": dónde acepta presencial o híbrido y si le sirve el
remoto. Ningún portal filtra por provincia en el código: decide el LLM con esa
regla del perfil, así que el bot sirve igual para alguien de AMBA que de Córdoba.

- **Bumeran** antepone a la descripción `Ubicación: …` y `Modalidad: …`, que
  vienen en el detalle del aviso.
- **LinkedIn, Indeed, Talent y Computrabajo** dan la ubicación pero no siempre
  la modalidad (el listado guest de LinkedIn ignora `f_WT`). La anteponen a la
  descripción como `Ubicación: …`: una ciudad del interior puede ser un remoto.
- **SuTrabajo** se pide por sección, `/argentina/` y `/remoto/`; la ubicación
  sale del aviso original o, si no se puede leer, de su reescritura de
  `/argentina/`.

`LOCATION` y `HOURS` son las mismas para todos los usuarios.

## Telegram: cada usuario, su chat

Cada persona habla con el bot en su chat privado. Ese chat es su espacio: nadie
ve el de otro, y todo lo suyo se guarda con su `chat_id`. Los grupos se ignoran.

**Alta.** La persona manda `/start` y queda pendiente. Al admin le llega la
solicitud con los botones ✅ Aprobar y ❌ Rechazar. Una vez aprobada, carga su CV
con `/perfil`, como texto o como archivo `.md` / `.txt` (un CV suele pasar los
4096 caracteres que entran en un mensaje). Hasta que no tenga perfil, no le
llegan ofertas.

| Comando | Qué hace |
|---|---|
| `/start` | Pide acceso; si está activo y tiene CV, arranca una búsqueda para él (si había bloqueado el bot, además lo reactiva). En pausa no busca: primero `/reanudar` |
| `/settings` | Panel con sus palabras clave, sus bloqueadas, su perfil y la pausa |
| `/perfil` | Muestra su CV actual y le pide uno nuevo para reemplazarlo |
| `/permitido python, django` | Suma términos de búsqueda sin pasar por `/settings` |
| `/bloquear php, wordpress` | Suma palabras bloqueadas sin pasar por `/settings` |
| `/template` | Manda una plantilla en Markdown para armar el CV, con las secciones que más pesan al clasificar |
| `/pausa` · `/reanudar` | Deja de recibir ofertas, o vuelve a recibirlas |
| `/clear` | Borra los mensajes del chat de las últimas 48 h (Telegram no deja borrar los más viejos) |
| `/ayuda` | Qué hace el bot y cómo usarlo |
| `/info` | De qué sitios salen las ofertas |
| `/usuarios` | Solo el admin: todos los usuarios, con su estado y su `chat_id` |

**El panel `/settings`** es un solo mensaje con botones, que se edita al navegar
en vez de mandar mensajes nuevos: 🔎 Términos, 🚫 Bloqueadas, 📄 Perfil,
⏸ Pausar y 💻 Sumar o quitar los portales IT. En cada lista, ➕ Agregar y ➖ Quitar piden las palabras separadas por
coma. Los usuarios nuevos arrancan con las dos listas vacías: el mensaje de
aprobación les pide cargarlas.

**Qué llega en cada corrida.** Un bloque por cada palabra clave que trajo 🟢 o 🟡,
en orden alfabético: un encabezado y después cada oferta en su propio mensaje
(para poder reenviarla o borrarla sola), las verdes primero. Cada oferta muestra
el título en negrita y, abajo, el sitio de origen como link, sin la url cruda. Al
final, el resumen de la corrida. Si no hubo ninguna 🟢 ni 🟡, no llega nada,
tampoco el resumen:

```
🔎 python
🟢 Desarrollador Python Backend (FastAPI)
   ar.linkedin.com
🟡 Analista Programador Python Jr
   ar.computrabajo.com

📋 Resumen · 14:00 a 14:23
120 ofertas nuevas: 🟢 1 · 🟡 3 · 🔴 116

django: 🟡 2
python: 🟢 1 · 🟡 1

Sin coincidencias: backend, developer, fastapi
```

Las palabras sin resultados no mandan mensaje: quedan juntas en el último renglón
del resumen. Solo suenan las ofertas; el resumen llega **sin sonido**
(`disable_notification`), para no hacer sonar el celular cada hora.

Una coincidencia es una 🟢 o 🟡 que te llega en esa corrida; las rojas y las ya
vistas no cuentan. Una oferta aparece una sola vez, en la primera de tus palabras
que la trajo. Lo de los portales sin búsqueda va a la palabra que aparezca en su
título; si no aparece ninguna, a un bloque "Otros portales" al final, que se
manda solo si trajo algo.

Cómo se ve todo esto en el teléfono:
[`docs/telegram/capturas/`](docs/telegram/capturas/index.html). El logo del bot
está en [`docs/telegram/logo/`](docs/telegram/logo/index.html).

## Flujo

La corrida es cada hora y va **usuario por usuario, uno tras otro**:

```
por cada usuario activo:
  buscar sus palabras  →  saltear ya evaluadas  →  filtrar sus bloqueadas  →  bajar descripción  →  LLM con su CV  →  un bloque por palabra + resumen
  (caché de la corrida)    (deliveries)              (gratis)                   (una vez por url)     (lo caro)
```

1. Se toman los usuarios activos que ya cargaron su perfil, por orden de alta.
2. Para cada uno se busca con **sus** palabras clave. Lo que otro usuario ya
   buscó en la misma corrida se reusa: si dos tienen "python", LinkedIn se
   consulta una sola vez. Los portales sin búsqueda se piden una vez por corrida.
3. Se saltean las ofertas que ese usuario ya tiene evaluadas y las que tienen en
   el título una de **sus** palabras bloqueadas.
4. La descripción se baja una sola vez por url y queda guardada para todos.
5. El `Classifier` le pone color a cada oferta contra **su** CV, y el resultado
   se guarda en el momento: si la corrida se corta, lo ya clasificado no se
   vuelve a pagar.
6. Se manda un bloque por cada palabra con 🟢 o 🟡 y después el resumen de la
   corrida. Si no hubo ninguna, no se manda nada.
   Lo que no se pudo mandar se reintenta en la corrida siguiente.
7. Las ofertas nuevas quedan en `resultados/AAAA-MM-DD_HHMM.json` y los colores
   de cada usuario en el `.csv` del mismo nombre.

**Por qué uno tras otro y no en paralelo.** Con un hilo por usuario serían hasta
5 búsquedas simultáneas a LinkedIn desde la misma IP, y con una sola ya hay entre
11 % y 18 % de 429. Una tras otra entra holgada en la hora: el primer usuario
paga el scraping y los demás usan casi todo de la caché.

**Lo que se paga es el LLM, y es por usuario**: unas 50 llamadas por hora por
cada uno, porque el color depende del CV de cada persona.

Si alguien bloquea el bot, Telegram contesta 403: ese usuario queda marcado como
`blocked`, la corrida sigue con los demás y deja de buscarle. Vuelve con `/start`.

## Base de datos

`labubot.db`, un SQLite en modo WAL que comparten los dos procesos. Reemplaza a
`vistas.txt` y a `perfil.md`:

| Tabla | Qué guarda |
|---|---|
| `users` | Un usuario por chat: estado (`pending`, `active`, `paused`, `rejected`, `blocked`), su perfil y qué espera el bot de su próximo mensaje |
| `user_terms` | Sus palabras clave |
| `user_blocked_words` | Sus palabras bloqueadas |
| `offers` | Las descripciones ya bajadas, compartidas: una por url |
| `deliveries` | Qué se evaluó para cada usuario: color, palabra clave que la trajo y si ya se mandó |

Diagrama y columnas: [`docs/telegram/bdd.html`](docs/telegram/bdd.html).

## Arquitectura

Dos procesos sobre el mismo SQLite. No hay Redis ni Celery: para hasta 5 usuarios
y una corrida por hora no hacen falta.

- **api** (`api.py`, FastAPI): recibe lo que los usuarios escriben. Telegram lo
  manda por webhook y el endpoint valida el secreto
  (`X-Telegram-Bot-Api-Secret-Token`).
- **worker** (`daemon.py`): corre la búsqueda de cada usuario en su propio hilo, al
  arrancar, cada hora y cada vez que alguien manda `/start` (el webhook anota el
  pedido en `search_requests` y el worker lo toma a los pocos segundos). Cada usuario
  va a su ritmo, sin esperar a los demás; el mismo usuario nunca corre dos veces a la
  vez.

Telegram se maneja a mano, sin `python-telegram-bot` ni `aiogram`, porque traen
su propio cliente HTTP. FastAPI solo recibe: todo lo que sale hacia la Bot API
pasa por el `Driver`, igual que los portales.

Drivers que traen datos y no saben nada más; cada portal sabe qué pedir y cómo
leer lo que vuelve.

```
main.py                     la corrida: usuario por usuario
daemon.py                   worker: un hilo por usuario, al arrancar, cada hora y con cada /start
api.py                      FastAPI: monta el webhook de Telegram
migrate.py                  una vez: crea labubot.db desde la versión de un chat (perfil.md, vistas.txt y sus listas)
set_webhook.py              una vez por deploy: registra el webhook y el menú de comandos
src/
  config/
    settings.py             .env (pydantic-settings) y el log en logs/app.log
  constants/
    http.py                 timeout, idioma y user agent
    openai.py               modelo
    prompt.py               ← las instrucciones y los tres colores
    run.py                  portales sin búsqueda, el hub y resultados/
  driver/                   el único que toca httpx
    http.py                 Driver: get() y post_json()
  portals/                  una carpeta por portal
    linkedin/
      portal.py             LinkedIn(driver): search() y description()
      html_extractor.py     ← lo único que sabe del DOM de LinkedIn
      constants.py          URLs, paginación, pausa y reintentos
    bumeran/ clarin/ computrabajo/ empleosit/ getonbrd/
    himalayas/ indeed/ jobicy/ randstad/ sutrabajo/ talent/
    weworkremotely/ workable/
  classifier/
    openai.py               Classifier(cv): classify()
  telegram/                 todo lo del bot
    bot.py                  Telegram(driver): mensajes, botones, archivos, webhook
    webhook.py              POST /telegram/webhook
    handlers.py             comandos, botones y lo que espera de cada usuario
    keyboards.py            los teclados de botones
    constants.py            Bot API, pausa, emojis y los textos del bot
  db/
    schema.sql              las tablas
    database.py             la conexión (WAL)
    users.py                usuarios, palabras clave, bloqueadas y perfil
    offers.py               descripciones y entregas
  schemas/                  TypedDicts: ofertas, usuarios y el Update de Telegram
  enums/                    colores, estados del usuario y del chat
  exceptions/exceptions.py
```

División por módulos:

- **`driver/`** es el único que toca httpx. `Driver` recibe una URL y devuelve lo
  que vuelve; no sabe con quién habla. Un 404 o 410 vuelve vacío, un 403 levanta
  `LabubotForbiddenError`, un 429 `LabubotRateLimitError` y cualquier otra cosa
  `LabubotRequestError`.
- **`portals/`** tiene todo lo de cada sitio: `portal.py` (qué pedir, recibe el
  `Driver` inyectado), su extractor (`html_`, `json_` o `xml_extractor.py`) y
  `constants.py`. Todos exponen `search()` y `description(url)`; los reintentos,
  si el sitio los necesita, viven acá (LinkedIn reintenta 429 y timeouts sueltos).
  Un error que no se cura reintentando corta solo esa búsqueda con lo que alcanzó
  a traer, o deja vacía esa descripción: el resto de la corrida sigue.
- **`classifier/`** compara cada oferta con el CV usando Decisions. Le habla a
  OpenAI por el SDK oficial, no por el `Driver`.
- **`telegram/`** es el bot entero: lo que recibe por el webhook y lo que manda.
  La Bot API es un POST más del `Driver`.
- **`db/`** lo que se recuerda entre corridas y entre usuarios, en SQLite, con
  `sqlite3` de la stdlib y sin ORM.
- **`schemas/`** y **`enums/`** son los tipos, sin lógica.

Si LinkedIn cambia el markup se toca `portals/linkedin/html_extractor.py`; si
cambia la query, `portals/linkedin/portal.py`. Sumar un portal es crear una
carpeta en `portals/` y agregarlo a la lista de portales de `main.py` (y a
`WITHOUT_SEARCH`, en `src/constants/run.py`, si no busca por palabra): ni el `Driver` ni el `Classifier` se
enteran.

### El LLM: Luna, por la Decisions API

`gpt-6-luna` por la Decisions API del SDK `openai` (`client.decisions.create`).
Va **una oferta por llamada y por usuario**: el CV de esa persona viaja en las
instructions de una pregunta de tipo `choice` con tres opciones —verde, amarillo,
rojo— y el modelo elige una. Como la respuesta es una de esas tres, no hay JSON
que parsear ni veredictos a medias.

Las instructions (`constants/prompt.py`) fijan las reglas: usar solo el CV y el
texto del aviso, no inventar requisitos, separar excluyente de deseable y
descartar por excluyentes duros (idioma, seniority, herramientas ajenas al
perfil). No nombran ningún rubro ni tecnología: lo específico sale del CV.

Sin créditos OpenAI contesta 429 (`insufficient_quota`), y ese no se arregla
esperando. Los límites de tu cuenta están en
[platform.openai.com/settings/organization/limits](https://platform.openai.com/settings/organization/limits).

## Despliegue

Corre en **un VPS Linux, de un proveedor todavía a definir**. Pide poco: dos
procesos que esperan la red casi todo el tiempo y un SQLite. Con 1 a 2 GB de RAM
alcanza. El paso a paso está en
[`docs/telegram/despliegue.md`](docs/telegram/despliegue.md).

- **Un túnel de ngrok** con el dominio fijo y gratis de la cuenta
  (`<nombre>.ngrok-free.dev`): Telegram solo llama a un webhook por HTTPS, y así
  no hace falta comprar un dominio ni abrir puertos. uvicorn escucha solo en
  `127.0.0.1:8000`. Con dominio propio, la alternativa es Caddy con HTTPS
  automático.
- **systemd** levanta `labubot-api`, `labubot-worker` y `labubot-ngrok` y los
  reinicia si se caen.
- **Python 3.14**, como en la PC (en Ubuntu, con `uv python install 3.14`).
- **Backups**: un `sqlite3 labubot.db ".backup …"` diario, copiado fuera del VPS.
- **Firewall**: solo SSH, con clave.

**Antes de elegir proveedor, probar la IP.** Hoy se busca desde una IP
residencial. Cualquier VPS da una IP de datacenter, y LinkedIn (más del 60 % de
las ofertas) o los portales detrás de Cloudflare pueden tratarla peor. La prueba
corre la misma búsqueda desde la PC y desde el VPS a la misma hora y compara
cuántas ofertas trae cada portal y cuántos 429 aparecen. Conviene contratar 1 mes
sin plazo para hacerla. El plan está en
[`docs/telegram/vps.md`](docs/telegram/vps.md) (§7) y vale para cualquier
proveedor.

**Si la IP no pasa**, se corre en una PC de casa con el mismo túnel apuntando a
uvicorn: IP residencial y el mismo código. Un túnel es también la forma de
desarrollar en Windows (ver [Desarrollo en la PC](#desarrollo-en-la-pc)).

## Instalación

```bash
poetry install
cp .env.example .env     # LLM_API_KEY, TELEGRAM_TOKEN, ADMIN_CHAT_ID, WEBHOOK_*
python migrate.py        # crea labubot.db: el admin con perfil.md y lo ya visto de vistas.txt
python set_webhook.py    # registra el webhook y el menú de comandos en Telegram
```

Para el bot:

1. Hablale a [@BotFather](https://t.me/BotFather), `/newbot`, y el token que te
   da va en `TELEGRAM_TOKEN`. Con `/setname` y `/setuserpic` le ponés el nombre
   y el logo (`docs/telegram/logo/labubot-640.png`); el bot real ya los tiene.
2. Tu `chat_id` va en `ADMIN_CHAT_ID`: sos quien aprueba las altas. Mandale un
   mensaje al bot y buscalo en `https://api.telegram.org/bot<token>/getUpdates`
   (con el webhook apagado; si no, Telegram contesta 409).
3. `WEBHOOK_URL` es `https://<dominio del túnel>/telegram/webhook` y
   `WEBHOOK_SECRET` un valor al azar:
   `python -c "import secrets; print(secrets.token_hex(32))"`.

`migrate.py` se corre una sola vez: vuelve a pisar el perfil del admin y le
devuelve las listas que haya quitado si se corre con el bot ya en uso.

## Uso

```bash
uvicorn api:app --host 127.0.0.1 --port 8000   # el bot: atiende comandos y botones
python daemon.py                               # el worker: una corrida al arrancar y una por hora
python main.py                                 # una corrida sola, para todos los usuarios activos
```

En el VPS los dos primeros los levanta systemd. Si una corrida falla, el daemon
deja el error en el log y vuelve a intentar a la hora siguiente. Se corre desde
la raíz del repo: `labubot.db`, `resultados/` y `logs/` van por ruta relativa.

### Desarrollo en la PC

Mismo código, con un **bot de prueba** (otro token de @BotFather): un bot tiene
un solo webhook, y el del bot real apunta al VPS.

1. `.env` de la PC: `TELEGRAM_TOKEN` del bot de prueba, tu `ADMIN_CHAT_ID`,
   `DB_PATH=prueba.db` y cualquier `WEBHOOK_SECRET`.
2. Terminal 1: `.venv/Scripts/python.exe -m uvicorn api:app --port 8000 --reload`.
3. Terminal 2, un túnel: `ngrok http 8000` (con tu cuenta, usa el dominio fijo) o
   `cloudflared tunnel --url http://localhost:8000` (sin cuenta; la URL
   `https://<algo>.trycloudflare.com` cambia cada vez que se levanta).
4. `WEBHOOK_URL=https://<dominio del túnel>/telegram/webhook` en el `.env` y
   `.venv/Scripts/python.exe set_webhook.py`.
5. El worker, a mano: `.venv/Scripts/python.exe main.py` hace una corrida.
6. Al terminar, `https://api.telegram.org/bot<TOKEN>/deleteWebhook` en el navegador.

### Logs

No hay `print`: todo va a `logs/app.log`. `src/config/settings.py` lo configura
una vez con `logging.basicConfig` y cada módulo hace
`logger = logging.getLogger(__name__)`.

```
2026-10-25 15:06:30,770 - src.portals.computrabajo.portal - WARNING - portal.py:48 - Búsqueda 'python' cortada: Respondió 429 al obtener el listado de ofertas
```

En `INFO` quedan, por usuario, cuántas ofertas nuevas y salteadas hubo, los
colores y cuántas se mandaron, y la duración de la corrida. Con
`LOG_LEVEL=DEBUG` se suma cada búsqueda pedida de verdad (las que salen de la
caché no), cada título bloqueado, cada oferta clasificada y cada reintento de
LinkedIn. Para seguirlo en
vivo:

```powershell
Get-Content logs\app.log -Wait -Tail 20
```

Todo se configura en `.env`:

| Variable | Qué hace |
|---|---|
| `LOCATION` | Ubicación tal como la escribe cada portal (`Argentina`) |
| `HOURS` | Ventana de publicación (24 = solo lo de hoy) |
| `LLM_API_KEY` | Clave de OpenAI |
| `TELEGRAM_TOKEN` | Token del bot, el que da @BotFather |
| `ADMIN_CHAT_ID` | Tu chat: aprueba las altas y ve `/usuarios` |
| `WEBHOOK_URL` | La URL pública que llama Telegram: la del túnel (o tu dominio), con `/telegram/webhook` |
| `WEBHOOK_SECRET` | El secreto que viaja en cada update; vacío, el webhook rechaza todo |
| `DB_PATH` | El SQLite (`labubot.db` por defecto) |
| `LOG_LEVEL` | Nivel mínimo del log: `INFO` (por defecto) o `DEBUG` |

## Configurar

**El perfil** — cada usuario carga el suyo con `/perfil`. Cuanto más concreto
(años reales por tecnología, nivel real de inglés), menos verdes falsos.
`perfil.md` es el perfil del admin que importa `migrate.py`; después de migrar
no se lee más. Las reglas del prompt nombran secciones como las de ese archivo
(seniority, idiomas, modalidad, "Lo que NO quiero"): un CV con esas secciones
clasifica mejor.

**Palabras clave y bloqueadas** — son de cada usuario: las carga y las edita
desde `/settings`, y arranca con las dos listas vacías. No hay listas en el
código. Las palabras clave son lo que escribirías en el buscador; una palabra
bloqueada que aparece en el título descarta la oferta sin gastar LLM.

Las bloqueadas van contra el **título** y no contra la descripción porque media
descripción menciona "SAP" o "Java" de pasada al listar el stack de la empresa, y
eso no convierte al aviso en una oferta de SAP.

## Documentación del diseño

Todo lo de la versión multiusuario está en [`docs/telegram/`](docs/telegram/README.md):
decisiones, diagramas (base de datos, conexiones, ciclo del usuario, casos de
uso, secuencias), capturas, el diseño del código módulo por módulo
([`diseno.md`](docs/telegram/diseno.md)) y las tareas por fase
([`tareas.md`](docs/telegram/tareas.md)). El despliegue paso a paso está en
[`despliegue.md`](docs/telegram/despliegue.md).
