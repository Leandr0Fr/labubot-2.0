"""
Helpers de texto, compartidos entre los parsers y el filtro.

Acá no se parsea nada: son las operaciones chiquitas que hacen falta después,
cuando ya tenés el texto y lo necesitás en condiciones para comparar.
"""

import re

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
