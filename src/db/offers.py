"""Las ofertas ya bajadas y lo que se le evaluó y mandó a cada usuario."""

import sqlite3

from src.db.database import now
from src.enums.traffic_light import TrafficLight
from src.schemas.job import Offer


class Offers:
    """Caché de descripciones: cada url se baja una sola vez, para todos."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get(self, url: str) -> sqlite3.Row | None:
        """
        Busca una oferta ya bajada.
        Args:
            url: URL de la oferta, sin query.
        Returns:
            sqlite3.Row | None: description y el portal que la bajó, o None si
            nunca se bajó.
        """
        return self.conn.execute(
            "SELECT description, portal FROM offers WHERE url = ?", (url,)
        ).fetchone()

    def add(self, offer: Offer, portal: str) -> None:
        """
        Guarda la oferta, o la reemplaza; con descripción '' si el portal no la dio.
        Args:
            offer: Título, descripción y url.
            portal: Nombre de la clase del portal que la trajo.
        """
        self.conn.execute(
            "INSERT OR REPLACE INTO offers (url, portal, title, description) "
            "VALUES (?, ?, ?, ?)",
            (offer["url"], portal, offer["title"], offer["description"]),
        )
        self.conn.commit()


class Deliveries:
    """Qué se evaluó para cada usuario, con qué color y palabra, y si ya le llegó."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def exists(self, chat_id: int, url: str) -> bool:
        """
        Dice si esa oferta ya se evaluó (o se importó) para ese usuario.
        Args:
            chat_id: Su chat privado con el bot.
            url: URL de la oferta, sin query.
        Returns:
            bool: True si ya tiene entrega.
        """
        row = self.conn.execute(
            "SELECT 1 FROM deliveries WHERE chat_id = ? AND url = ?", (chat_id, url)
        ).fetchone()
        return row is not None

    def add(
        self, chat_id: int, url: str, light: TrafficLight | None, term: str | None
    ) -> None:
        """
        Anota el veredicto y la palabra que la trajo.
        Args:
            chat_id: Su chat privado con el bot.
            url: URL de la oferta, sin query.
            light: El color; None = importada de vistas.txt.
            term: La palabra clave que la trajo; None = otros portales o importada.
        """
        self.conn.execute(
            "INSERT OR IGNORE INTO deliveries (chat_id, url, term, light, classified_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (chat_id, url, term, light, now()),
        )
        self.conn.commit()

    def mark_sent(self, chat_id: int, url: str) -> None:
        """
        Anota que el mensaje llegó a Telegram.
        Args:
            chat_id: Su chat privado con el bot.
            url: URL de la oferta, sin query.
        """
        self.conn.execute(
            "UPDATE deliveries SET sent_at = ? WHERE chat_id = ? AND url = ?",
            (now(), chat_id, url),
        )
        self.conn.commit()

    def pending(self, chat_id: int) -> list[sqlite3.Row]:
        """
        Sus verdes y amarillas que todavía no llegaron.
        Args:
            chat_id: Su chat privado con el bot.
        Returns:
            list[sqlite3.Row]: Con url, term, light y el title de offers, por
            orden de clasificación.
        """
        return self.conn.execute(
            "SELECT d.url, d.term, d.light, o.title "
            "FROM deliveries d "
            "JOIN offers o ON o.url = d.url "
            "WHERE d.chat_id = ? AND d.sent_at IS NULL "
            "AND d.light IN (?, ?) "
            "ORDER BY d.classified_at",
            (chat_id, TrafficLight.GREEN, TrafficLight.YELLOW),
        ).fetchall()
