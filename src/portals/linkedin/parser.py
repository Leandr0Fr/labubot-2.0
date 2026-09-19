"""
Parsea el HTML que devuelve el endpoint jobs-guest de LinkedIn.

Todo el conocimiento del DOM de LinkedIn vive acá y en constants.py. Si LinkedIn
cambia el markup —y lo cambia seguido— estos son los únicos dos archivos que hay
que tocar: el driver pide páginas y no sabe nada de clases CSS.
"""

from selectolax.lexbor import LexborHTMLParser

from src.portals.linkedin.constants import (
    JOB_URL,
    LABELS,
    SEL_APPLICANTS,
    SEL_CARD,
    SEL_COMPANY,
    SEL_CRITERION,
    SEL_CRITERION_LABEL,
    SEL_CRITERION_VALUE,
    SEL_DATE,
    SEL_DESCRIPTION,
    SEL_DESCRIPTION_ALT,
    SEL_LINK,
    SEL_LOCATION,
    SEL_TITLE,
    URN_PREFIX,
)
from src.schemas.job import Criteria, JobCard, JobDetail
from src.utils.text import first_int, normalize, text


def parse_cards(html: str) -> list[JobCard]:
    """
    Extrae las ofertas de un fragmento del listado.

    La respuesta es una lista de <li> suelta, sin <html> ni <body>: selectolax la
    envuelve solo, así que se parsea igual que una página entera.
    Args:
        html: Fragmento devuelto por seeMoreJobPostings/search.
    Returns:
        list[JobCard]: Una por oferta; vacía si el fragmento no traía ninguna.
    """
    tree = LexborHTMLParser(html)
    cards: list[JobCard] = []

    for node in tree.css(SEL_CARD):
        urn = node.attributes.get("data-entity-urn") or ""
        job_id = urn.removeprefix(URN_PREFIX)
        title = text(node.css_first(SEL_TITLE))
        # Sin id o sin título la fila no sirve para nada aguas abajo.
        if not job_id or not title:
            continue

        link = node.css_first(SEL_LINK)
        href = (link.attributes.get("href") or "") if link else ""
        date = node.css_first(SEL_DATE)

        cards.append(
            JobCard(
                id=job_id,
                title=title,
                company=text(node.css_first(SEL_COMPANY)),
                location=text(node.css_first(SEL_LOCATION)),
                date=(date.attributes.get("datetime") or "") if date else "",
                # El href trae parámetros de tracking; el link limpio es más corto
                # y no delata de dónde salió.
                url=href.split("?")[0] or JOB_URL.format(job_id=job_id),
            )
        )

    return cards


def parse_criteria(tree: LexborHTMLParser) -> Criteria:
    """
    Lee los campos que la empresa cargó en el formulario de la vacante.

    Esto es dato declarado, no inferido: `seniority` acá vale mucho más que
    adivinar "Senior" desde el título, que se equivoca en los dos sentidos.
    Args:
        tree: DOM del detalle ya parseado.
    Returns:
        Criteria: Solo las claves que la oferta realmente publicó.
    """
    criteria: Criteria = {}
    for item in tree.css(SEL_CRITERION):
        label = normalize(text(item.css_first(SEL_CRITERION_LABEL)))
        key = LABELS.get(label)
        if key is None:
            continue
        value = text(item.css_first(SEL_CRITERION_VALUE))
        if value:
            criteria[key] = value  # type: ignore[literal-required]
    return criteria


def parse_detail(html: str) -> JobDetail:
    """
    Extrae descripción, criterios y competencia de la página de una oferta.

    La descripción es lo que hace falta para cazar el aviso que dice "Developer"
    en el título y Python en el cuerpo: la tarjeta del listado nunca lo muestra.
    Args:
        html: HTML devuelto por jobPosting/{id}.
    Returns:
        JobDetail: Descripción en texto plano, criterios y cantidad de postulantes
        (None si la oferta no la publica, que pasa seguido).
    """
    tree = LexborHTMLParser(html)

    body = tree.css_first(SEL_DESCRIPTION) or tree.css_first(SEL_DESCRIPTION_ALT)
    applicants = tree.css_first(SEL_APPLICANTS)

    return JobDetail(
        description=text(body),
        criteria=parse_criteria(tree),
        # "33 solicitudes" en español, "33 applicants" en inglés: sacamos el número
        # y listo, en vez de mantener un regex por idioma.
        applicants=first_int(text(applicants)) if applicants else None,
    )
