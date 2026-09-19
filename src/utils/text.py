"""
Helpers de texto, compartidos entre los parsers y el filtro.

Acá no se parsea nada: son las operaciones chiquitas que hacen falta después,
cuando ya tenés el texto y lo necesitás en condiciones para comparar.
"""

import re
import unicodedata

from selectolax.lexbor import LexborNode

_SPACES = re.compile(r"\s+")


def text(node: LexborNode | None) -> str:
    """
    Texto de un nodo con los espacios colapsados.

    `node.text(strip=True)` solo recorta las puntas: el HTML de LinkedIn viene
    indentado, así que "  Python   Developer \\n" queda con el doble espacio
    adentro y rompe cualquier comparación.
    Args:
        node: Nodo de selectolax, o None si el selector no encontró nada.
    Returns:
        str: Texto en una línea, o "" si el nodo no existe.
    """
    if node is None:
        return ""
    return _SPACES.sub(" ", node.text()).strip()


def normalize(raw: str) -> str:
    """
    Minúsculas y sin acentos, para que "automatización" matchee "automatizacion".

    Los avisos mezclan las dos formas sin criterio, a veces en la misma oración.
    Args:
        raw: Texto tal como vino.
    Returns:
        str: Texto normalizado, listo para buscar términos adentro.
    """
    decomposed = unicodedata.normalize("NFKD", raw.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def first_int(raw: str) -> int | None:
    """
    Primer número del texto, ignorando separadores de miles.

    Sirve para "33 solicitudes" y para "1.204 candidatos" por igual.
    Args:
        raw: Texto que contiene un número.
    Returns:
        int | None: El número, o None si no hay ninguno.
    """
    match = re.search(r"\d[\d.,]*", raw)
    if match is None:
        return None
    clean = match.group(0).replace(".", "").replace(",", "")
    return int(clean) if clean.isdigit() else None
