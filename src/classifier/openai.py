"""Clasificador: le pregunta a OpenAI de qué color es cada oferta."""

from openai import APIError, OpenAI, RateLimitError

from src.config.settings import settings
from src.constants.openai import (
    BATCH_SIZE,
    MAX_OUTPUT_TOKENS,
    MODEL,
    REASONING_EFFORT,
)
from src.constants.prompt import OFFER_BLOCK, TEMPLATE
from src.exceptions.exceptions import LabubotLLMError, LabubotRateLimitError
from src.parsers.verdicts import parse_verdicts
from src.schemas.job import Offer
from src.schemas.verdict import Verdict


class Classifier:
    """
    Le pone color a cada oferta comparándola contra el perfil.

    El perfil y el system prompt se inyectan una vez y viajan en cada lote: son
    pocos tokens al lado de las descripciones, y mantenerlos afuera del historial
    hace que cada lote sea independiente del anterior.
    """

    def __init__(self, profile: str, system: str) -> None:
        self.client = OpenAI(api_key=settings.llm_api_key)
        self.profile = profile
        self.system = system

    # ------------------------------------------ Helpers -------------------------------------------

    def _prompt(self, batch: list[Offer]) -> str:
        """
        Arma el mensaje del lote: el perfil una vez y las ofertas numeradas.
        Args:
            batch: Ofertas del lote, en orden.
        Returns:
            str: El mensaje de usuario listo para mandar.
        """
        blocks = [
            OFFER_BLOCK.format(
                index=index,
                title=card["title"],
                company=card["company"],
                location=card["location"],
                seniority=detail["criteria"].get("seniority", "no declarado"),
                employment_type=detail["criteria"].get(
                    "employment_type", "no declarado"
                ),
                applicants=detail["applicants"] or "no publicado",
                description=detail["description"],
            )
            for index, (card, detail) in enumerate(batch, 1)
        ]
        return TEMPLATE.format(
            count=len(batch), profile=self.profile, offers="\n\n".join(blocks)
        )

    def _complete(self, prompt: str) -> str:
        """
        Una llamada a OpenAI.
        Args:
            prompt: Mensaje del usuario ya armado.
        Returns:
            str: El texto que devolvió el modelo, sin interpretar.
        Raises:
            LabubotRateLimitError: Si el 429 sobrevivió a los reintentos del SDK.
            LabubotLLMError: Si el proveedor falla, corta la respuesta o contesta
            vacío.
        """
        try:
            response = self.client.responses.create(
                model=MODEL,
                instructions=self.system,
                input=prompt,
                reasoning={"effort": REASONING_EFFORT},
                text={"format": {"type": "json_object"}},
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )
        except RateLimitError as e:
            raise LabubotRateLimitError(f"OpenAI devolvió 429: {e}") from e
        except APIError as e:
            raise LabubotLLMError(f"OpenAI falló: {e}") from e

        # El razonamiento cuenta contra max_output_tokens: si se lo come todo, el
        # JSON viene truncado o no viene.
        if response.status == "incomplete":
            details = response.incomplete_details
            reason = details.reason if details and details.reason else "sin motivo"
            raise LabubotLLMError(f"OpenAI cortó la respuesta: {reason}")

        if not response.output_text:
            raise LabubotLLMError("OpenAI contestó vacío")

        return response.output_text

    # -------------------------------------------- API ---------------------------------------------

    def classify(self, offers: list[Offer]) -> list[Verdict | None]:
        """
        Un veredicto por oferta, en el mismo orden en que entraron.

        Va de a BATCH_SIZE para que el perfil y el system prompt viajen una vez
        por lote y no una vez por oferta. Si un lote se cae, se pierde ese lote y
        no la corrida: sus ofertas quedan en None y el caller las descarta.
        Args:
            offers: Tarjeta y detalle de cada oferta a evaluar.
        Returns:
            list[Verdict | None]: Un lugar por oferta; None si no se pudo evaluar.
        Raises:
            LabubotRateLimitError: Si se agotó la cuota del proveedor.
        """
        verdicts: list[Verdict | None] = []

        for start in range(0, len(offers), BATCH_SIZE):
            batch = offers[start : start + BATCH_SIZE]
            try:
                content = self._complete(self._prompt(batch))
                verdicts.extend(parse_verdicts(content, len(batch)))
            except LabubotLLMError as e:
                print(f"    lote de {len(batch)} sin evaluar: {e}")
                verdicts.extend([None] * len(batch))

        return verdicts
