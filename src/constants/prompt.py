"""
Instructions que compara un lote de ofertas contra el CV.
"""
from src.enums.traffic_light import TrafficLight

INSTRUCTIONS = """\
Decidí si a esta persona le conviene invertir tiempo en postularse a la oferta
laboral que llega como input.

<REGLAS>
1. Fuente única: usá SOLO el perfil de abajo y el texto de la oferta. Nada de
   conocimiento previo sobre la empresa, su reputación, sueldos o proceso de
   selección.
2. Nunca inventes requisitos: si el aviso no dice explícitamente una tecnología,
   años de experiencia, modalidad, sueldo o nivel de idioma, NO es requisito. Un
   dato ausente es ausente; no lo completes con lo que suele pedirse.
3. Excluyente vs. deseable: lo marcado como "requisito", "imprescindible",
   "excluyente" o derivados es lo esencial; lo "deseable", "es un plus", "valoramos",
   o derivados es algo adicional.
4. Especialidad: si el rol es de otra especialidad y solo menciona el stack del
   perfil de pasada, no encaja. EJ: FastAPI y es una oferta de Frontend.
</REGLAS>

<PERFIL>
{cv}
</PERFIL>\
"""

OFFER_BLOCK = """\
<OFERTA>
Título: {title}

{description}
</OFERTA>\
"""

CHOICES = [
    {"value": TrafficLight.GREEN,  "description": "Encaja de verdad: el stack coincide y cumple TODOS los excluyentes. Vale postularse ya."},
    {"value": TrafficLight.YELLOW, "description": "Encaja a medias: le falta algo salvable con una buena carta, o el aviso es ambiguo sobre un excluyente."},
    {"value": TrafficLight.RED,    "description": "No encaja: pide un excluyente que no tiene, o es de otra especialidad aunque mencione su stack al pasar."},
]