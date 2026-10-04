# LABUBOT 2.0

Buscás como buscarías a mano. Un LLM lee cada oferta contra tu CV y la pinta de
🟢 🟡 🔴.

## La idea

Poner "python" en LinkedIn y revisar los resultados uno por uno. Eso es todo. La
diferencia es que las lee todas, entra en cada una a leer la descripción completa
—que es donde aparece el Python de los avisos titulados "Developer" a secas— y no
se cansa en la número 40.

Sin filtro de nivel: entran junior, senior y todo lo del medio. El LLM decide.

## Sin navegador, sin sesión

La v1 manejaba un Chrome real con Selenium sobre una cuenta logueada: apoyaba todo
el proyecto sobre lo único que LinkedIn sí castiga.

La v2 le habla al endpoint `jobs-guest`, que es lo que LinkedIn le sirve a
cualquier visitante anónimo. **No hay cookie, no hay sesión, no hay cuenta.** El
peor escenario dejó de ser una cuenta restringida y pasó a ser un `429` que se
cura esperando.

Verificado antes de escribir una línea: los ids que devuelve el endpoint son un
subconjunto exacto de los que muestra `/jobs/search` deslogueado. Misma búsqueda.

> No es una API oficial ni documentada, y el ToS de LinkedIn desalienta la
> recolección automatizada aunque la página sea pública. Lo que cambia es que no
> hay una cuenta tuya de por medio.

## Flujo

```
buscar  →  filtrar palabras baneadas  →  bajar descripción  →  LLM  →  🟢🟡🔴
             (gratis, ahorra cuota)                          (lo caro)
```

El filtro corre **antes** de bajar un solo detalle: cada descarte ahorra un
request a LinkedIn y una llamada al LLM, que es lo único que se paga.

## Arquitectura

Misma forma que `hitron-cgnv2`: drivers que traen datos y no saben nada más,
utils puros que los interpretan.

```
main.py                     orquesta el flujo de arriba
perfil.md                   ← tu CV. La vara con la que se mide todo
src/
  config/
    settings.py             .env (pydantic-settings)
    search.py               ← términos y palabras baneadas
  constants/
    http.py                 ritmo, backoff y user agent
    linkedin.py             URLs del jobs-guest y paginación
    openai.py               modelo, reasoning effort y tamaño de lote
    prompt.py               ← el prompt de comparación
  driver/                   el único que toca httpx
    http.py                 Driver: get(), post_json(), ritmo y reintentos
  portals/                  qué pedirle a cada sitio y a quién parsearlo
    linkedin.py             LinkedIn(driver): search() y detail()
  classifier/               qué preguntarle al LLM y cómo lotearlo
    openai.py               Classifier(perfil, system): classify()
  schemas/                  los tipos del dominio
    job.py                  JobCard, Criteria, JobDetail, Offer, Job
    verdict.py              Verdict
  parsers/                  interpretan; no piden nada
    html.py                 ← único archivo que sabe del DOM de LinkedIn
    verdicts.py             respuesta del LLM → list[Verdict | None]
  enums/traffic_light.py    verde / amarillo / rojo
  exceptions/exceptions.py
  utils/
    text.py                 normalizar, primer entero (compartidos)
    filters.py              palabras baneadas
```

Una sola razón para cambiar por capa:

- **`driver/`** es el único que toca httpx. `Driver` recibe una URL y devuelve lo
  que vuelve, con la pausa y los reintentos; no sabe con quién habla.
- **`portals/`** saben qué pedir: URLs, params, paginación. Reciben el `Driver`
  inyectado y lo comparten.
- **`classifier/`** sabe qué preguntarle al LLM y le habla por el SDK oficial de
  OpenAI, no por el `Driver`.
- **`parsers/`** convierte texto en tipos y no pide nada.
- **`schemas/`** son los tipos, sin lógica.

Si LinkedIn cambia el markup se toca `parsers/html.py`. Si cambia la query, solo
`portals/linkedin.py`. Si OpenAI cambia el formato de salida, `parsers/verdicts.py`.
Sumar un portal es un archivo nuevo en `portals/` y su parser: ni el `Driver` ni
el `Classifier` se enteran.

### Por qué no hay tabla de puntajes

Había una: ~470 líneas de pesos calibrados a mano (`python: 25`, `rag: 12`...).
Se borró. Un keyword match no sabe que "5 años de experiencia" descalifica a
alguien con 2, ni distingue un aviso que **pide** Django de uno que ofrece
enseñarlo. Contaba apariciones y había que recalibrarla a cada rato.

Además un número del 0 al 100 finge una precisión que no existe: nadie sabe si un
73 es mejor que un 68. Tres colores se leen de un vistazo.

### El LLM: GPT-5.6 Luna, por el SDK oficial

`gpt-5.6-luna` con `reasoning.effort: "high"`, por la Responses API del SDK
`openai`. Luna es el modelo chico de la familia 5.6, el que OpenAI apunta a
clasificación en volumen: U$S 0,20 por millón de tokens de entrada y 1,20 por
millón de salida. Leer un aviso y cruzarlo contra un CV no necesita más modelo
que eso; sí necesita que piense, y por eso el esfuerzo va en `high`.

**Va de a 10 ofertas por request.** El perfil y el system prompt viajan una vez
por lote y no una vez por oferta: son la parte fija de cada llamada. Cada oferta
viaja numerada y el modelo devuelve un `verdicts[]` con el mismo id; lo que no
vuelve queda en `None` y se descarta, así una respuesta incompleta no inventa
veredictos. Si un lote entero se cae se pierden esas 10 y no la corrida.

Luna piensa antes de responder y esos tokens se cobran como salida aunque no se
vean. Por eso `max_output_tokens` va holgado (25.000, el piso que OpenAI
recomienda con razonamiento activado): tiene que cubrir razonamiento + JSON. Si
se queda corto, la respuesta vuelve con status `incomplete` y el clasificador
descarta el lote en vez de parsear un JSON a medias. Con razonamiento activado
la API no acepta `temperature`, así que no hay.

La salida va en JSON mode (`text.format: json_object`): garantiza un objeto JSON
válido, no que respete el esquema. El parser sigue validando cada campo, porque
lo que viene de un LLM es texto hasta que se demuestre lo contrario.

### Límites y costo

No hay free tier: se paga por token y los límites dependen del tier de la
cuenta. En Tier 1 Luna da 500 requests y 500.000 tokens por minuto, así que acá
no ata el ritmo sino el gasto. Los límites de tu cuenta están en
[platform.openai.com/settings/organization/limits](https://platform.openai.com/settings/organization/limits).

Ante un 429 o un 5xx el SDK reintenta dos veces con backoff y respeta
`retry-after`; si igual falla, el clasificador corta la corrida con
`LabubotRateLimitError` en vez de seguir gastando. Ojo: sin créditos OpenAI
también contesta 429 (`insufficient_quota`), y ese no se arregla esperando.

### Por qué selectolax y no regex

En `hitron` regex es correcto: ahí se leen variables JavaScript dentro de páginas
ASP, que no son estructura HTML. Acá LinkedIn devuelve DOM real con clases, y un
regex se rompe cuando cambia el orden de los atributos o aparece un tag anidado.
`selectolax` usa Lexbor (C), tiene wheel para cp314 y no arrastra dependencias.

## Instalación

```bash
poetry install
cp .env.example .env     # y cargá LLM_API_KEY (platform.openai.com/api-keys)
```

Después escribí tu CV en `perfil.md`. Sin eso no arranca: es contra lo que se
compara cada oferta.

## Uso

```bash
python main.py                 # últimas 24 h
python main.py --horas 72      # ventana más ancha
python main.py --solo-verdes   # solo lo que encaja de verdad
python main.py --todo          # ignora el cache de ya vistas
python main.py --max 20        # tope de evaluaciones (cuida el gasto)
```

`vistas.json` guarda los ids ya evaluados: la corrida del día siguiente solo gasta
LLM en lo nuevo. Los resultados quedan en `resultados/` en JSON, listos para el
bot de Telegram.

## Configurar

**`perfil.md`** — tu CV en texto plano. Cuanto más concreto (años reales por
tecnología, nivel real de inglés), menos verdes falsos.

**`src/config/busqueda.py`** — dos listas, nada más:

| Lista | Qué hace |
|---|---|
| `TERMINOS` | Lo que escribirías en el buscador |
| `TITULOS_BANEADOS` | Si aparece en el título, se descarta sin leer |

Las baneadas van contra el **título** y no contra la descripción porque media
descripción menciona "SAP" o "Java" de pasada al listar el stack de la empresa, y
eso no convierte al aviso en una oferta de SAP.

### Un detalle que no es obvio

El matcheo es por **palabra completa**, no por substring. Por substring `sap`
matchea dentro de `Whatsapp`, `ios` dentro de `servicios`, `.net` dentro de
cualquier dominio. Silenciosamente te esconderían ofertas buenas.

## Pendiente

- Clase `Scraper`: recorre todos los portales y junta las ofertas de cada uno.
  Solo HTTP, nada de Playwright ni Selenium.
- Más portales en `portals/`.
- Bot de Telegram: los JSON de `resultados/` ya tienen todo lo necesario.
