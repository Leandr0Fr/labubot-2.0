"""Conexión a labubot.db, la base que comparten la api y el worker."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from src.config.settings import settings

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect() -> sqlite3.Connection:
    """
    Abre la base de DB_PATH, en WAL y con foreign keys, y crea las tablas que falten.

    Las foreign keys se prenden en cada conexión: SQLite no las guarda en la base.
    Returns:
        sqlite3.Connection: Con las filas como sqlite3.Row, por nombre de columna.
    """
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return conn


def now() -> str:
    """
    La fecha y hora actual como se guarda en la base.
    Returns:
        str: ISO 8601 en UTC, con "T" y sin fracciones de segundo.
    """
    return datetime.now(UTC).isoformat(timespec="seconds")
