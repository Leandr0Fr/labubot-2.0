"""
Migración única de la versión de un chat a labubot.db.

perfil.md, vistas.txt y sus listas de búsqueda pasan a ser del admin.
"""

import logging
from pathlib import Path

from src.config.settings import settings
from src.db.database import connect
from src.db.offers import Deliveries
from src.db.users import Users
from src.enums.user_status import UserStatus

PROFILE_PATH = Path("perfil.md")
SEEN_PATH = Path("vistas.txt")

ADMIN_TERMS = [
    "python",
    "fastapi",
    "desarrollador python",
    "python developer",
    "backend",
    "desarrollador backend",
    "backend developer",
    "desarrollador",
    "programador",
    "developer",
    "software engineer",
    "ingeniero de software",
    "analista programador",
    "desarrollador jr",
    "desarrollador junior",
    "programador jr",
    "programador junior",
    "junior developer",
    "desarrollador semi senior",
    "ssr developer",
    "web scraping",
    "integraciones",
]
ADMIN_BLOCKED_WORDS = [
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
    "frontend",
    "front-end",
    "front end",
    "angular",
    "vue",
    "director",
    "head of",
    "manager",
    "lead",
    "líder",
    "lider",
    "jefe",
    "soporte",
    "support",
    "helpdesk",
    "mesa de ayuda",
]

logger = logging.getLogger(__name__)


def migrate() -> None:
    """
    Crea al admin con perfil.md y sus listas, e importa vistas.txt como sus deliveries.

    Queda como "admin" y sin @ hasta que su primer /start trae los de Telegram.
    """
    admin_chat_id = settings.admin_chat_id
    conn = connect()
    users = Users(conn)
    users.register(admin_chat_id, None, "admin")
    users.set_status(admin_chat_id, UserStatus.ACTIVE)
    users.set_profile(admin_chat_id, PROFILE_PATH.read_text(encoding="utf-8"))
    users.add_terms(admin_chat_id, ADMIN_TERMS)
    users.add_blocked_words(admin_chat_id, ADMIN_BLOCKED_WORDS)

    deliveries = Deliveries(conn)
    urls = SEEN_PATH.read_text(encoding="utf-8").splitlines()
    for url in urls:
        deliveries.add(admin_chat_id, url, None, None)
    conn.close()
    logger.info(
        f"Migración: admin {admin_chat_id} activo y {len(urls)} urls de vistas.txt"
    )


if __name__ == "__main__":
    migrate()
