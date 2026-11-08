# labubot

Bot de Telegram que busca ofertas laborales: "scrapea" portales de empleo por HTTP
puro y las evalúa con un LLM contra el perfil de cada usuario del bot.

## Estilo

- **Comentarios acotados.** Un comentario solo cuando el *por qué* no se lee en
  el código. Nada de párrafos explicativos, ensayos ni justificaciones de diseño
  dentro del archivo: eso va al README si hace falta.
- Docstrings con `Args` / `Returns` / `Raises` donde ya los hay: es la convención
  del proyecto. El resumen, en una línea.
- Español en comentarios, docstrings y mensajes al usuario. Inglés en
  identificadores y claves JSON.
- Sin sobreingeniería: nada de random, heurísticas de evasión ni capas de
  abstracción para casos que todavía no existen. Que funcione primero.
- Textos con f-strings (`f"hola {test}"`), también en los logs. `.format()` solo
  para plantillas que viven en `constants`.
- Nada de `print`: cada módulo hace `logger = logging.getLogger(__name__)`.
  `src/config/settings.py` configura el log (`logs/app.log`) con `basicConfig`.

## Arquitectura

Dos procesos sobre `labubot.db` (SQLite en modo WAL): `api.py` recibe a Telegram
por webhook (FastAPI + uvicorn) y `daemon.py` corre `main(chat_id)` de cada usuario
activo en su propio hilo, al arrancar y cada hora. Un `/start` anota un pedido en
`search_requests` y el worker lanza el hilo de ese usuario. `python main.py` sin
argumentos corre a todos uno tras otro, con una caché de búsquedas en memoria.

- `src/driver/` es el ÚNICO que toca httpx. `Driver.get()` y `Driver.post_json()`
  reciben una URL y devuelven lo que vuelve (429, 403 y otros errores como
  excepciones `Labubot*`). Nada específico de un portal, de Telegram ni de un
  proveedor de LLM entra acá.
- `src/portals/` una carpeta por portal, con TODO lo de ese sitio adentro:
  `portal.py` (qué pedir, recibe el `Driver` inyectado), su extractor
  (`html_extractor.py`, `json_extractor.py` o `xml_extractor.py`) y
  `constants.py` (URLs, paginación, selectores). Sumar un portal es crear una
  carpeta y anotarlo en la lista de `main.py` (y en `WITHOUT_SEARCH` de
  `src/constants/run.py` si no busca por palabra), no tocar tres.
- `src/telegram/` todo lo de la Bot API, como un portal: `bot.py` (lo que sale,
  siempre por el `Driver`), `webhook.py` y `handlers.py` (lo que entra: FastAPI
  solo recibe), `keyboards.py` y `constants.py` (URLs, comandos y textos). Nada
  de python-telegram-bot ni aiogram.
- `src/classifier/` sabe qué preguntarle al LLM: arma el prompt con el perfil de
  cada usuario y hace una llamada a Decisions por oferta. Habla con OpenAI por el
  SDK oficial (`openai`), no por el `Driver`.
- `src/db/` lo que se recuerda entre corridas, en `labubot.db`: `connect()`,
  `Users` (estado, perfil, términos y bloqueadas), `Offers` (una descripción por
  url) y `Deliveries` (qué se evaluó y se mandó a cada usuario, y con qué palabra).
- `src/schemas/` los TypedDicts del dominio (`Offer`, `Found`, `User`) y del
  Update de Telegram, sin lógica.
- `src/enums/` `TrafficLight`, `UserStatus`, `ChatState`, `Command` (los comandos) y
  `Callback` (el `callback_data` de los botones): nada de strings sueltos en los `case`.
- `src/exceptions/` `LabubotError` y sus hijas: `LabubotRequestError`,
  `LabubotRateLimitError` (429) y `LabubotForbiddenError` (403; en Telegram, el
  usuario bloqueó el bot).
- `src/constants/` lo configurable y lo medido que NO es de un sitio externo
  (`http.py` transporte, `openai.py` ese modelo, `prompt.py` la pregunta,
  `run.py` la corrida). Lo de cada portal y lo de Telegram va en su carpeta.
- `src/config/settings.py` el `.env` y el log. Los términos y las bloqueadas son
  de cada usuario y viven en `labubot.db`: no hay listas de búsqueda en el código.
- En la raíz, además: `migrate.py` (se corre una vez) y `set_webhook.py` (una vez
  por deploy). La configuración del servidor (systemd, ngrok, logrotate) está en
  `docs/telegram/despliegue.md`.

**Solo HTTP.** Nada de Playwright, Selenium ni navegador headless.

## Comandos

```bash
poetry install
python -m ruff check . && python -m ruff format --check .
.venv/Scripts/python.exe -m uvicorn api:app --port 8000 --reload   # la api en la PC
.venv/Scripts/python.exe main.py                                   # una corrida
```

El diseño está en `docs/telegram/` y el despliegue paso a paso en
`docs/telegram/despliegue.md`.
