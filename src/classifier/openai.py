"""Clasificador: le pregunta a OpenAI de qué color es cada oferta."""

import logging

from openai import OpenAI

from src.config.settings import settings
from src.constants.openai import MODEL
from src.constants.prompt import CHOICES, INSTRUCTIONS, OFFER_BLOCK
from src.enums.traffic_light import TrafficLight
from src.schemas.job import Offer


logger = logging.getLogger(__name__)


class Classifier:
    """Le pone color a cada oferta comparándola contra el CV, una por llamada."""

    def __init__(self, cv: str) -> None:
        """
        Arma las instructions una sola vez con el CV adentro.
        Args:
            cv: El perfil del usuario, tal como lo cargó en el bot.
        """
        self.client = OpenAI(api_key=settings.llm_api_key)
        self.instructions = INSTRUCTIONS.format(cv=cv)

    def classify(self, offer: Offer) -> TrafficLight:
        """
        Le pregunta al modelo, por la Decisions API, de qué color es una oferta.
        Args:
            offer: Título, descripción y url de la oferta.
        Returns:
            TrafficLight: El color que eligió el modelo.
        """
        offer_block = OFFER_BLOCK.format(
            title=offer["title"], description=offer["description"]
        )
        decision = self.client.decisions.create(
            model=MODEL,
            input=offer_block,
            questions=[
                {
                    "type": "choice",
                    "name": "light",
                    "instructions": self.instructions,
                    "choices": CHOICES,
                }
            ],
        )
        light = TrafficLight(decision.answers[0].choice)
        logger.debug(f"{light}: {offer['title']}")
        return light
