"""Clasificador: le pregunta a Gemini de qué color es cada oferta."""

from google import genai
from google.genai import errors

from src.config.settings import settings
from src.constants.gemini import (
    BATCH_SIZE,
    MAX_TOKENS,
    MODEL,
    TEMPERATURE,
    THINKING_LEVEL,
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
        self.client = genai.Client(api_key=settings.llm_api_key)
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
        Una llamada a Gemini.
        Args:
            prompt: Mensaje del usuario ya armado.
        Returns:
            str: El texto que devolvió el modelo, sin interpretar.
        Raises:
            LabubotRateLimitError: Si se agotó la cuota del free tier.
            LabubotLLMError: Si el proveedor falla o contesta vacío.
        """
        try:
            interaction = self.client.interactions.create(
                model=MODEL,
                input=prompt,
                system_instruction=self.system,
                generation_config={
                    "temperature": TEMPERATURE,
                    "max_output_tokens": MAX_TOKENS,
                    "thinking_level": THINKING_LEVEL,
                    "response_mime_type": "application/json",
                },
            )
        except errors.APIError as e:
            if getattr(e, "code", None) == 429:
                raise LabubotRateLimitError("Gemini agotó la cuota") from e
            raise LabubotLLMError(f"Gemini falló: {e}") from e

        if not interaction.output_text:
            raise LabubotLLMError("Gemini contestó vacío")

        return interaction.output_text

    # -------------------------------------------- API ---------------------------------------------

    def classify(self, offers: list[Offer]) -> list[Verdict | None]:
        """
        Un veredicto por oferta, en el mismo orden en que entraron.

        Va de a BATCH_SIZE porque en el free tier ata el RPM, no los tokens. Si un
        lote se cae, se pierde ese lote y no la corrida: sus ofertas quedan en
        None y el caller las descarta.
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
