"""La pregunta que compara una oferta contra el CV."""

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
5. Excluyentes duros: cualquiera de estos, pedido como requisito, descarta la
   oferta aunque el resto encaje:
   - Idioma por encima del nivel del perfil ("fluent", "advanced", "business
     level", "strong communication in English", "intermediate required", B2+),
     o un trabajo que en sí se hace en inglés (escribir feedback, documentación
     o reportes en inglés, equipo o cliente angloparlante) aunque no diga nivel.
   - Años de experiencia o seniority muy por encima de los del perfil (Senior,
     Lead, Principal, 4+ años).
   - Un stack sin Python: el rol exige solo otros lenguajes (Java, Go, Kotlin,
     etc.). Si Python está entre los lenguajes exigidos, que pida además otros
     no descarta por sí solo; el resto de estas reglas se sigue aplicando igual.
     Excepción: un lenguaje que el perfil declara con un nivel acotado se acepta
     solo dentro de ese nivel (ej. Node junior sí; Node con años de experiencia,
     no).
   - Lo que el perfil marca como "Lo que NO quiero".
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
    {
        "value": TrafficLight.GREEN,
        "description": "Encaja de verdad: el stack coincide y cumple TODOS los excluyentes. Vale postularse ya.",
    },
    {
        "value": TrafficLight.YELLOW,
        "description": "Encaja a medias: cumple todos los excluyentes duros, pero le falta algo salvable con una buena carta o el aviso es ambiguo sobre un excluyente.",
    },
    {
        "value": TrafficLight.RED,
        "description": "No encaja: pide un excluyente que no tiene, o es de otra especialidad aunque mencione su stack al pasar.",
    },
]
