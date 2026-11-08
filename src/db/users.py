"""Los usuarios: estado, perfil, términos, palabras bloqueadas y búsquedas pedidas."""

import sqlite3

from src.db.database import now
from src.enums.chat_state import ChatState
from src.enums.user_status import UserStatus
from src.schemas.user import User


class Users:
    """Lee y escribe users, user_terms, user_blocked_words y search_requests."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        """
        Trabaja sobre una conexión ya abierta.
        Args:
            conn: La de connect().
        """
        self.conn = conn

    def get(self, chat_id: int) -> User | None:
        """
        Busca un usuario.
        Args:
            chat_id: Su chat privado con el bot.
        Returns:
            User | None: El usuario, o None si nunca escribió.
        """
        row = self.conn.execute(
            "SELECT * FROM users WHERE chat_id = ?", (chat_id,)
        ).fetchone()
        if row is None:
            return None
        return User(**row)

    def register(self, chat_id: int, username: str | None, first_name: str) -> None:
        """
        Lo da de alta en pending, o le actualiza nombre y @ si ya existe.
        Args:
            chat_id: Su chat privado con el bot.
            username: El @, sin la arroba; None si no tiene.
            first_name: Nombre que muestra Telegram.
        """
        self.conn.execute(
            "INSERT INTO users (chat_id, username, first_name, created_at) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT (chat_id) DO UPDATE SET "
            "username = excluded.username, first_name = excluded.first_name",
            (chat_id, username, first_name, now()),
        )
        self.conn.commit()

    def set_status(self, chat_id: int, status: UserStatus) -> None:
        """
        Cambia el estado.
        Args:
            chat_id: Su chat privado con el bot.
            status: El estado nuevo.
        """
        self.conn.execute(
            "UPDATE users SET status = ? WHERE chat_id = ?", (status, chat_id)
        )
        self.conn.commit()

    def set_profile(self, chat_id: int, profile: str) -> None:
        """
        Reemplaza el CV.
        Args:
            chat_id: Su chat privado con el bot.
            profile: El CV, en texto.
        """
        self.conn.execute(
            "UPDATE users SET profile = ? WHERE chat_id = ?", (profile, chat_id)
        )
        self.conn.commit()

    def set_state(self, chat_id: int, state: ChatState) -> None:
        """
        Anota qué espera el bot del próximo mensaje.
        Args:
            chat_id: Su chat privado con el bot.
            state: Lo que espera; IDLE = nada.
        """
        self.conn.execute(
            "UPDATE users SET state = ? WHERE chat_id = ?", (state, chat_id)
        )
        self.conn.commit()

    def active(self) -> list[User]:
        """
        Los usuarios a los que la corrida les busca ofertas.
        Returns:
            list[User]: Los que están en active y ya cargaron el perfil, por
            orden de alta.
        """
        rows = self.conn.execute(
            "SELECT * FROM users WHERE status = ? AND profile != '' "
            "ORDER BY created_at, chat_id",
            (UserStatus.ACTIVE,),
        ).fetchall()
        users = []
        for row in rows:
            users.append(User(**row))
        return users

    def all(self) -> list[User]:
        """
        Todos los usuarios, para /usuarios.
        Returns:
            list[User]: Por orden de alta.
        """
        rows = self.conn.execute(
            "SELECT * FROM users ORDER BY created_at, chat_id"
        ).fetchall()
        users = []
        for row in rows:
            users.append(User(**row))
        return users

    def request_search(self, chat_id: int) -> None:
        """
        Le pide al worker una búsqueda para este usuario.
        Args:
            chat_id: Su chat privado con el bot.
        """
        self.conn.execute(
            "INSERT OR REPLACE INTO search_requests (chat_id, requested_at) "
            "VALUES (?, ?)",
            (chat_id, now()),
        )
        self.conn.commit()

    def take_search_requests(self) -> list[int]:
        """
        Saca las búsquedas pedidas, para que el worker las corra.
        Returns:
            list[int]: Los chat_id que pidieron búsqueda; quedan borrados.
        """
        # En una sola sentencia: un pedido que entra mientras tanto no se pierde.
        rows = self.conn.execute(
            "DELETE FROM search_requests RETURNING chat_id"
        ).fetchall()
        self.conn.commit()
        chat_ids = []
        for row in rows:
            chat_ids.append(row["chat_id"])
        return chat_ids

    def remove_search_request(self, chat_id: int) -> None:
        """
        Borra la búsqueda pedida por un usuario, si había una.
        Args:
            chat_id: Su chat privado con el bot.
        """
        self.conn.execute("DELETE FROM search_requests WHERE chat_id = ?", (chat_id,))
        self.conn.commit()

    def terms(self, chat_id: int) -> list[str]:
        """
        Sus términos de búsqueda.
        Args:
            chat_id: Su chat privado con el bot.
        Returns:
            list[str]: En orden alfabético: de ese orden sale la palabra de cada oferta.
        """
        rows = self.conn.execute(
            "SELECT term FROM user_terms WHERE chat_id = ? ORDER BY term", (chat_id,)
        ).fetchall()
        terms = []
        for row in rows:
            terms.append(row["term"])
        return terms

    def add_terms(self, chat_id: int, terms: list[str]) -> list[str]:
        """
        Suma términos en minúsculas y sin espacios de más.
        Args:
            chat_id: Su chat privado con el bot.
            terms: Los términos, tal como los escribió.
        Returns:
            list[str]: Los que no tenía.
        """
        added = []
        for item in terms:
            term = item.strip().lower()
            if not term:
                continue
            cursor = self.conn.execute(
                "INSERT OR IGNORE INTO user_terms (chat_id, term) VALUES (?, ?)",
                (chat_id, term),
            )
            if cursor.rowcount:
                added.append(term)
        self.conn.commit()
        return added

    def remove_terms(self, chat_id: int, terms: list[str]) -> list[str]:
        """
        Quita términos.
        Args:
            chat_id: Su chat privado con el bot.
            terms: Los términos, tal como los escribió.
        Returns:
            list[str]: Los que tenía.
        """
        removed = []
        for item in terms:
            term = item.strip().lower()
            if not term:
                continue
            cursor = self.conn.execute(
                "DELETE FROM user_terms WHERE chat_id = ? AND term = ?",
                (chat_id, term),
            )
            if cursor.rowcount:
                removed.append(term)
        self.conn.commit()
        return removed

    def blocked_words(self, chat_id: int) -> list[str]:
        """
        Sus palabras bloqueadas.
        Args:
            chat_id: Su chat privado con el bot.
        Returns:
            list[str]: En orden alfabético.
        """
        rows = self.conn.execute(
            "SELECT word FROM user_blocked_words WHERE chat_id = ? ORDER BY word",
            (chat_id,),
        ).fetchall()
        words = []
        for row in rows:
            words.append(row["word"])
        return words

    def add_blocked_words(self, chat_id: int, words: list[str]) -> list[str]:
        """
        Suma palabras bloqueadas en minúsculas y sin espacios de más.
        Args:
            chat_id: Su chat privado con el bot.
            words: Las palabras, tal como las escribió.
        Returns:
            list[str]: Las que no tenía.
        """
        added = []
        for item in words:
            word = item.strip().lower()
            if not word:
                continue
            cursor = self.conn.execute(
                "INSERT OR IGNORE INTO user_blocked_words (chat_id, word) VALUES (?, ?)",
                (chat_id, word),
            )
            if cursor.rowcount:
                added.append(word)
        self.conn.commit()
        return added

    def remove_blocked_words(self, chat_id: int, words: list[str]) -> list[str]:
        """
        Quita palabras bloqueadas.
        Args:
            chat_id: Su chat privado con el bot.
            words: Las palabras, tal como las escribió.
        Returns:
            list[str]: Las que tenía.
        """
        removed = []
        for item in words:
            word = item.strip().lower()
            if not word:
                continue
            cursor = self.conn.execute(
                "DELETE FROM user_blocked_words WHERE chat_id = ? AND word = ?",
                (chat_id, word),
            )
            if cursor.rowcount:
                removed.append(word)
        self.conn.commit()
        return removed
