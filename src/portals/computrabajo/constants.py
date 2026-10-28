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
# Sin el :not toma el puntaje de la empresa, que va en el mismo párrafo.
SEL_JOB_LOCATION = "p.fs16.fc_base.mt5:not(.dFlex) > span.mr10"
# "Presencial y remoto" es otro ícono (i_home_office): cuenta como presencial.
SEL_JOB_REMOTE = "span.icon.i_home"

# La ubicación es "Ciudad, Provincia". "Buenos Aires" suma el interior
# bonaerense; ese lo descarta el LLM.
AMBA_PROVINCES = ("Capital Federal", "Buenos Aires-GBA", "Buenos Aires")

SEL_DESCRIPTION = 'div[div-link="oferta"] > :is(div.mbB, p.mbB:not(.fc_aux), ul.disc)'
# Viene como "Empresa - Ciudad, Provincia".
SEL_DETAIL_LOCATION = "h1 + p.fs16"
COMPANY_SEPARATOR = " - "
