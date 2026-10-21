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

## Flujo

```
buscar  →  filtrar títulos baneados  →  saltear ya vistas  →  bajar descripción  →  LLM  →  🟢🟡🔴
             (gratis, ahorra cuota)                                                 (lo caro)
```

1. Cada portal devuelve `url → título` de lo publicado en las últimas `HOURS`.
2. Los títulos con una palabra de `BLOCKED_TITLE_WORDS` se descartan sin leer.
3. Las urls que ya están en `vistas.txt` se saltean: no se vuelve a pedir su
   detalle ni a gastar tokens en ellas.
4. Del resto se baja la descripción completa y se marca como vista.
5. El `Classifier` le pone color a cada oferta contra `perfil.md`.
6. Todo queda en `resultados/AAAA-MM-DD_HHMM.json`, con su color.
7. Mediante un Bot de Telegram envía las ofertas 🟢🟡.

El filtro y el chequeo de vistas corren **antes** de bajar un solo detalle: cada
descarte ahorra un request al portal y una llamada al LLM, que es lo único que se
paga. Aunque la corrida se corte a mitad, `vistas.txt` y el JSON se guardan con
lo que se alcanzó a leer.

## Arquitectura

Drivers que traen datos y no saben nada más; cada portal sabe qué pedir y cómo
leer lo que vuelve.

```
main.py                     orquesta el flujo de arriba
perfil.md                   ← tu CV. La vara con la que se mide todo
src/
  config/
    settings.py             .env (pydantic-settings)
    search.py               ← términos y palabras baneadas
  constants/
    http.py                 timeout, idioma y user agent
    openai.py               modelo
    prompt.py               ← las instrucciones y los tres colores
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
- **`classifier/`** mediante Decisions realiza la comparacion de ofertas y el CV. Y le habla por el SDK oficial de
  OpenAI, no por el `Driver`.
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

## Uso

```bash
python main.py
```

Todo se configura en `.env`:

| Variable | Qué hace |
|---|---|
| `LOCATION` | Ubicación tal como la escribe cada portal (`Argentina`) |
| `HOURS` | Ventana de publicación (24 = solo lo de hoy) |
| `LLM_API_KEY` | Clave de OpenAI |

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
