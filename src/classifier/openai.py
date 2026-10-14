"""Clasificador: le pregunta a OpenAI de qué color es cada oferta."""

from openai import OpenAI

from src.config.settings import settings
from src.constants.openai import MODEL
from src.constants.prompt import CHOICES, INSTRUCTIONS, OFFER_BLOCK
from src.enums.traffic_light import TrafficLight
from src.schemas.job import Offer


class Classifier:
    """Le pone color a cada oferta comparándola contra el CV, una por llamada."""

    def __init__(self, cv: str) -> None:
        """
        Arma las instructions una sola vez con el CV adentro.
        Args:
            cv: El perfil de la persona, tal como está en perfil.md.
        """
        self.client = OpenAI(api_key=settings.llm_api_key)
        self.instructions = INSTRUCTIONS.format(cv=cv)

    def classify(self, offers: list[Offer]) -> dict[str, TrafficLight]:
        """
        Un color por oferta, indexado por url.
        Args:
            offers: Ofertas a evaluar.
        Returns:
            dict[str, TrafficLight]: url de la oferta → color que le dio el modelo.
        """
        offers_results: dict[str, TrafficLight] = {}
        for offer in offers:
            offers_results[offer["url"]] = self._decide(offer)
        return offers_results

    def _decide(self, offer: Offer) -> TrafficLight:
        """
        Una llamada a Decisions para una oferta.
        Args:
            offer: Título, descripción y url de la oferta.
        Returns:
            TrafficLight: El color que eligió el modelo.
        """
        job = OFFER_BLOCK.format(title=offer["title"], description=offer["description"])
        decision = self.client.decisions.create(
            model=MODEL,
            input=job,
            questions=[
                {
                    "type": "choice",
                    "name": "light",
                    "instructions": self.instructions,
                    "choices": CHOICES,
                }
            ],
        )
        return TrafficLight(decision.answers[0].choice)
