"""Constantes de Computrabajo Argentina: páginas HTML renderizadas en el server."""

BASE_URL = "https://ar.computrabajo.com"

SEARCH_URL = f"{BASE_URL}/trabajo-de-{{slug}}"

# Sin "1": es "Hoy", desde la medianoche, y no cubre una ventana de 24 h.
RECENCY_BUCKETS = {
    72: "3",
    168: "7",
    360: "15",
    720: "30",
}

SEL_JOB_CARD = "article.box_offer"
SEL_JOB_LINK = "h2 a.js-o-link"

SEL_DESCRIPTION = 'div[div-link="oferta"] > :is(div.mbB, p.mbB:not(.fc_aux), ul.disc)'
