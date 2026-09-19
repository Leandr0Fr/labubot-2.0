"""
Parsea la respuesta del clasificador.

Está separado del clasificador por la misma razón que el HTML: quien llama no
sabe qué forma tiene lo que vuelve. Si mañana el modelo cambia de formato de
salida, se toca este archivo y ninguno más.
"""

import json
import re
from typing import Any

from src.enums.traffic_light import TrafficLight
from src.exceptions.exceptions import LabubotLLMError
from src.schemas.verdict import Verdict

# Algunos modelos devuelven el JSON envuelto en ```json ... ``` aunque se les pida
# que no. Es más barato tolerarlo acá que pelearse con el prompt.
_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)

MAX_ITEMS = 3


def extract_json(content: str) -> dict[str, Any]:
    """
    Saca el objeto JSON de la respuesta, venga limpio o con adornos.

    Tolera tres formas: el objeto pelado, envuelto en un bloque de código, y con
    una frase de cortesía antes o después ("Claro, acá va: {...}").
    Args:
        content: Texto tal como lo devolvió el modelo.
    Returns:
        dict[str, Any]: El objeto parseado.
    Raises:
        LabubotLLMError: Si no hay JSON reconocible adentro.
    """
    raw = content.strip()
    if (fenced := _FENCE.search(raw)) is not None:
        raw = fenced.group(1)

    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise LabubotLLMError(f"El modelo no devolvió JSON: {content[:200]}")

    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError as e:
        raise LabubotLLMError(f"JSON inválido del modelo: {raw[:200]}") from e


def _verdict(data: dict[str, Any]) -> Verdict:
    """
    Convierte un objeto suelto de la respuesta en un Verdict.

    Todo lo que viene de un LLM es texto hasta que se demuestre lo contrario, así
    que cada campo se valida: un color inventado cae en amarillo (el aviso no
    tiene la culpa de que el modelo se haya ido por las ramas) y las listas se
    recortan por si devolvió diez ítems en vez de tres.
    Args:
        data: Un elemento de `verdicts`.
    Returns:
        Verdict: Color, motivo y los dos listados de pros y contras.
    """
    light = str(data.get("light", "")).strip().lower()
    if light not in tuple(TrafficLight):
        light = TrafficLight.YELLOW.value

    def items(key: str) -> list[str]:
        value = data.get(key)
        return [str(x) for x in value][:MAX_ITEMS] if isinstance(value, list) else []

    return Verdict(
        light=TrafficLight(light),
        reason=str(data.get("reason", "")).strip(),
        pros=items("pros"),
        cons=items("cons"),
    )


def parse_verdicts(content: str, count: int) -> list[Verdict | None]:
    """
    Reparte los veredictos del lote por posición.

    El modelo puede devolver menos de los que se le pidieron, repetidos o con un
    id que no existe. Se indexa por id y se arma la lista completa: lo que no
    llegó queda en None, para que el caller descarte esa oferta en vez de
    mostrarle al usuario un veredicto que nadie emitió.
    Args:
        content: Texto tal como lo devolvió el modelo.
        count: Cuántas ofertas tenía el lote.
    Returns:
        list[Verdict | None]: Un lugar por oferta, en el orden en que se enviaron.
    Raises:
        LabubotLLMError: Si no hay JSON reconocible o no trae `verdicts`.
    """
    raw = extract_json(content).get("verdicts")
    if not isinstance(raw, list):
        raise LabubotLLMError("El modelo no devolvió una lista `verdicts`.")

    by_id: dict[int, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            index = int(item["id"])
        except (KeyError, TypeError, ValueError):
            continue
        if 1 <= index <= count:
            by_id.setdefault(index, item)

    return [_verdict(by_id[i]) if i in by_id else None for i in range(1, count + 1)]
