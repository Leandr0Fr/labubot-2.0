"""Clasificador: le pregunta a OpenAI de qué color es cada oferta."""

from openai import OpenAI

from src.config.settings import settings
from src.constants.openai import (
    MODEL,
)
from src.constants.prompt import INSTRUCTIONS, CHOICES
from src.schemas.job import Offer
from src.enums.traffic_light import TrafficLight

class Classifier:
    """
    Le pone color a cada oferta comparándola contra el perfil.

    El perfil y el system prompt se inyectan una vez y viajan en cada lote: son
    pocos tokens al lado de las descripciones, y mantenerlos afuera del historial
    hace que cada lote sea independiente del anterior.
    """

    def __init__(self ) -> None:
        self.client = OpenAI(api_key=settings.llm_api_key)

    def classify(self, offers: list[Offer]) -> dict[str, TrafficLight]:
        offers_analyzed = {}
        for offer in offers:
            answer = self.question(offer)
            offers_analyzed[offer.url, answer]
        return offers_analyzed

    def question(self, offer):
        decision = self.client.decisions.create(
            model=MODEL,
            input=offer.description,
            questions=[
                {
                    "type": "choice",
                    "name": "offer",
                    "instructions": INSTRUCTIONS,
                    "choices": CHOICES,
                }
            ],
            )
        answer = decision.answers[0]
        return answer
