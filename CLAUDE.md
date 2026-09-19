# labubot

Buscador de ofertas laborales: scrapea portales de empleo por HTTP puro y las
evalúa contra `perfil.md` con un LLM.

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

## Arquitectura

- `src/driver/` es el ÚNICO que toca httpx. `Driver.get()` y `Driver.post_json()`
  reciben una URL y devuelven lo que vuelve. Nada específico de un portal ni de
  un proveedor de LLM entra acá.
- `src/portals/` una carpeta por portal, con TODO lo de ese sitio adentro:
  `portal.py` (qué pedir, recibe el `Driver` inyectado), `parser.py` (leer su
  HTML) y `constants.py` (URLs, paginación, selectores). Sumar un portal es
  crear una carpeta, no tocar tres.
- `src/classifier/` sabe qué preguntarle al LLM: arma el prompt, lotea y parsea.
  Habla con Gemini por el SDK oficial (`google-genai`), no por el `Driver`.
- `src/parsers/` interpreta lo que no es de un portal: hoy solo el veredicto
  del LLM. El parser de un sitio vive con su portal.
- `src/schemas/` los TypedDicts del dominio, sin lógica.
- `src/constants/` lo configurable y lo medido que NO es de un portal
  (`http.py` transporte, `gemini.py` ese modelo). Lo de cada portal va en su
  carpeta.

**Solo HTTP.** Nada de Playwright, Selenium ni navegador headless.

Pendiente: una clase `Scraper` que recorra todos los portales y junte las
ofertas. Todavía no existe, no la anticipes en el diseño.

## Comandos

```bash
poetry install
python -m ruff check . && python -m ruff format --check .
```
