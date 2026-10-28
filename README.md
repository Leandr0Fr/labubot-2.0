# LABUBOT 2.0

Buscás como buscarías a mano, en 11 portales a la vez. Con Decisions de OpenAI analiza cada oferta
contra tu CV y la pinta de 🟢 🟡 🔴.

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
| LinkedIn | HTML del endpoint `jobs-guest` | un término por vez |
| Bumeran | API JSON de su front | un término por vez |
| Computrabajo | HTML de ar.computrabajo.com | un término por vez |
| Get on Board | API pública | un término por vez |
| Himalayas | API pública | un término por vez |
| Talent | HTML de ar.talent.com | un término por vez |
| Indeed | API GraphQL de su app | todos juntos con `OR` |
| Empleos IT | HTML de su buscador | todos juntos con `OR` |
| Workable | API de jobs.workable.com | todos juntos con `OR` |
| Jobicy | API pública | sin búsqueda: todo lo reciente |
| We Work Remotely | RSS de back-end y full-stack | sin búsqueda: todo lo reciente |

Los que no aceptan búsqueda traen todo lo publicado en la ventana y el filtro lo
hace el LLM.

### Ubicación

Se busca en todo el país: el remoto vale desde cualquier provincia, y lo
presencial o híbrido solo en AMBA. Ningún portal sabe pedir "remoto o AMBA" en
un solo request, así que se resuelve después de buscar:

- **Bumeran y Computrabajo** traen modalidad y provincia en el listado: lo
  presencial o híbrido de otra provincia se descarta ahí, antes de bajar el
  detalle. La provincia de Buenos Aires pasa entera; el interior bonaerense lo
  descarta el LLM.
- **LinkedIn, Indeed, Talent y Computrabajo** dan la ubicación pero no la
  modalidad (el listado guest de LinkedIn ignora `f_WT`). La anteponen a la
  descripción como `Ubicación: …` y decide el LLM con la regla de `perfil.md`:
  una ciudad del interior puede ser un remoto.

## Flujo

```
buscar  →  filtrar títulos baneados  →  saltear ya vistas  →  bajar descripción  →  LLM  →  🟢🟡🔴
             (gratis, ahorra cuota)                                                 (lo caro)
```

1. Cada portal devuelve `url → título` de lo publicado en las últimas `HOURS`.
2. Los títulos con una palabra de `BLOCKED_TITLE_WORDS` se descartan sin leer.
3. Las urls que ya están en `vistas.txt` se saltean: no se vuelve a pedir su
   detalle ni a gastar tokens en ellas.
4. Del resto se baja la descripción completa.
5. El `Classifier` le pone color a cada oferta contra `perfil.md`.
6. Las ofertas quedan en `resultados/AAAA-MM-DD_HHMM.json` y su color en el
   `.csv` del mismo nombre.
7. Un bot de Telegram manda las 🟢 y 🟡, una por mensaje.
8. Recién ahí se guarda `vistas.txt`.

El filtro y el chequeo de vistas corren **antes** de bajar un solo detalle: cada
descarte ahorra un request al portal y una llamada al LLM, que es lo único que se
paga. `vistas.txt` se escribe al final, con todo clasificado y enviado: si la
corrida se corta a mitad (OpenAI sin cuota, Telegram caído), la próxima vuelve a
leer esas ofertas en vez de perderlas.

## Arquitectura

Drivers que traen datos y no saben nada más; cada portal sabe qué pedir y cómo
leer lo que vuelve.

```
main.py                     orquesta el flujo de arriba
daemon.py                   corre main() al arrancar y después cada hora
perfil.md                   ← tu CV. La vara con la que se mide todo
src/
  config/
    settings.py             .env (pydantic-settings) y el log en logs/app.log
    search.py               ← términos y palabras baneadas
  constants/
    http.py                 timeout, idioma y user agent
    openai.py               modelo
    prompt.py               ← las instrucciones y los tres colores
    telegram.py             Bot API, pausa entre mensajes y emojis
  driver/                   el único que toca httpx
    http.py                 Driver: get() y post_json()
  portals/                  una carpeta por portal
    linkedin/
      portal.py             LinkedIn(driver): search() y description()
      html_extractor.py     ← lo único que sabe del DOM de LinkedIn
      constants.py          URLs, paginación, pausa y reintentos
    bumeran/ computrabajo/ empleosit/ getonbrd/ himalayas/
    indeed/ jobicy/ talent/ weworkremotely/ workable/
  classifier/
    openai.py               Classifier(cv): classify()
  notifier/
    telegram.py             Telegram(driver): send()
  db/
    seen.py                 SeenUrls: las urls ya leídas, en vistas.txt
  schemas/
    job.py                  Offer
  enums/traffic_light.py    green / yellow / red
  exceptions/exceptions.py
```

División por módulos:

- **`driver/`** es el único que toca httpx. `Driver` recibe una URL y devuelve lo
  que vuelve; no sabe con quién habla. Un 404 o 410 vuelve vacío, un 429 levanta
  `LabubotRateLimitError` y cualquier otra cosa `LabubotRequestError`.
- **`portals/`** tiene todo lo de cada sitio: `portal.py` (qué pedir, recibe el
  `Driver` inyectado), su extractor (`html_`, `json_` o `xml_extractor.py`) y
  `constants.py`. Todos exponen `search()` y `description(url)`; los reintentos,
  si el sitio los necesita, viven acá (LinkedIn reintenta 429 y timeouts sueltos).
  Un error que no se cura reintentando corta solo esa búsqueda con lo que alcanzó
  a traer, o deja vacía esa descripción: el resto de la corrida sigue.
- **`classifier/`** mediante Decisions realiza la comparacion de ofertas y el CV. Y le habla por el SDK oficial de
  OpenAI, no por el `Driver`.
- **`notifier/`** manda las 🟢🟡 a Telegram por `Driver.post_json()`: la Bot API
  es un POST más.
- **`db/`** lo que se recuerda entre corridas. Un simple .TXT. No es necesario hacer un overkill sobre algo tan sencillo.
- **`schemas/`** son los tipos, sin lógica.

Si LinkedIn cambia el markup se toca `portals/linkedin/html_extractor.py`; si
cambia la query, `portals/linkedin/portal.py`. Sumar un portal es crear una
carpeta en `portals/` y agregarlo al loop que corresponda en `main.py`: ni el
`Driver` ni el `Classifier` se enteran.

### El LLM: Luna, por la Decisions API

`gpt-6-luna` por la Decisions API del SDK `openai` (`client.decisions.create`).
Va **una oferta por llamada**: el CV viaja en las instructions de una pregunta de
tipo `choice` con tres opciones —verde, amarillo, rojo— y el modelo elige una.
Como la respuesta es una de esas tres, no hay JSON que parsear ni veredictos a
medias.

Las instructions (`constants/prompt.py`) fijan las reglas: usar solo el CV y el
texto del aviso, no inventar requisitos, separar excluyente de deseable y
descartar por excluyentes duros (idioma, seniority, stack sin Python).

Sin créditos OpenAI contesta 429 (`insufficient_quota`), y ese no se arregla
esperando. Los límites de tu cuenta están en
[platform.openai.com/settings/organization/limits](https://platform.openai.com/settings/organization/limits).

## Instalación

```bash
poetry install
cp .env.example .env     # y cargá LLM_API_KEY (platform.openai.com/api-keys)
```

Después escribí tu CV en `perfil.md`: es contra lo que se compara cada oferta.

Para Telegram:

1. Hablale a [@BotFather](https://t.me/BotFather), `/newbot`, y el token que te
   da va en `TELEGRAM_TOKEN`.
2. Mandale cualquier mensaje a tu bot.
3. Abrí `https://api.telegram.org/bot<token>/getUpdates`: el `chat.id` que
   aparece va en `TELEGRAM_CHAT_ID`.

## Uso

```bash
python main.py      # una corrida
python daemon.py    # una al arrancar y después una por hora
```

Si una corrida falla, el daemon deja el error en el log y vuelve a intentar a la
hora siguiente. Se corre desde la raíz del repo: `perfil.md`, `vistas.txt`,
`resultados/` y `logs/` van por ruta relativa.

### Logs

No hay `print`: todo va a `logs/app.log`. `src/config/settings.py` lo configura
una vez con `logging.basicConfig` y cada módulo hace
`logger = logging.getLogger(__name__)`.

```
2026-10-25 15:06:30,770 - src.portals.computrabajo.portal - WARNING - portal.py:48 - Búsqueda 'python' cortada: Respondió 429 al obtener el listado de ofertas
```

En `INFO` queda una línea por portal y el resumen de la corrida (colores y
envíos). Con `LOG_LEVEL=DEBUG` se suma cada término, cada título
bloqueado, cada oferta clasificada y cada reintento de LinkedIn. Para seguirlo en
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
| `TELEGRAM_CHAT_ID` | Chat al que se mandan las ofertas |
| `LOG_LEVEL` | Nivel mínimo del log: `INFO` (por defecto) o `DEBUG` |

`vistas.txt` guarda una url por línea de lo ya leído: la corrida del día
siguiente solo baja lo nuevo. Para empezar de cero, borralo.

## Configurar

**`perfil.md`** — tu CV en texto plano. Cuanto más concreto (años reales por
tecnología, nivel real de inglés), menos verdes falsos.

**`src/config/search.py`** — dos listas, nada más:

| Lista | Qué hace |
|---|---|
| `TERMS` | Lo que escribirías en el buscador |
| `BLOCKED_TITLE_WORDS` | Si aparece en el título, se descarta sin leer |

Las baneadas van contra el **título** y no contra la descripción porque media
descripción menciona "SAP" o "Java" de pasada al listar el stack de la empresa, y
eso no convierte al aviso en una oferta de SAP.
