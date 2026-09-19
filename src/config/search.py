"""
Qué buscar y qué descartar antes de gastar una llamada al LLM.

Dos listas y nada más. El criterio de si una oferta sirve o no lo pone el LLM
leyendo tu CV: acá no hay pesos, puntajes ni reglas.
"""

TERMS: list[str] = ["python"]

BLOCKED_TITLE_WORDS: list[str] = [
    "sap",
    "abap",
    "salesforce",
    "cobol",
    "sharepoint",
    ".net",
    "c#",
    "php",
    "recruiter",
    "reclutador",
    "comercial",
    "ventas",
    "vendedor",
    "marketing",
    "contable",
    "rrhh",
]
