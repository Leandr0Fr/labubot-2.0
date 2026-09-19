"""
Filtro previo al LLM.

Descarta lo obvio antes de gastar una llamada. En un free tier el cupo diario es
el recurso escaso: cada oferta que se filtra acá es una que sí se puede evaluar
más tarde.
"""

import re

from src.config.search import BLOCKED_TITLE_WORDS
from src.utils.text import normalize

# Corta por todo lo que no sea letra, número, punto, almohadilla o signo más.
# Esos tres se conservan para que ".net", "c#" y "c++" queden enteros; lo demás
# (comas, paréntesis, barras, guiones) separa: "Programador (SAP)" tiene que dar
# "sap" suelto, y "Dev .NET/C#" tiene que dar ".net" y "c#".
_SEPARATOR = re.compile(r"[^a-z0-9.#+]+")


def words(title: str) -> set[str]:
    """
    Parte un título en sus palabras, normalizadas.
    Args:
        title: Título de la oferta, tal como vino del listado.
    Returns:
        set[str]: Las palabras sueltas, en minúscula y sin acentos.
    """
    return set(_SEPARATOR.split(normalize(title))) - {""}


def blocked_word(title: str) -> str | None:
    """
    Devuelve la palabra baneada que aparece en el título, si hay alguna.

    Compara contra palabras enteras y no contra el texto crudo: "sap" no tiene
    que saltar dentro de "Whatsapp".

    Corre antes de bajar la descripción, así que cada descarte ahorra dos cosas:
    el request del detalle y la llamada al LLM.
    Args:
        title: Título de la oferta, tal como vino del listado.
    Returns:
        str | None: La palabra que disparó el descarte, o None si está limpio.
    """
    in_title = words(title)
    return next((w for w in BLOCKED_TITLE_WORDS if w in in_title), None)
