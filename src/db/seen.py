"""Las urls de ofertas ya leídas, una por línea en un .txt."""

from pathlib import Path


class SeenUrls:
    """Recuerda qué ofertas ya se leyeron, para no volver a pedir su detalle."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.urls: set[str] = set()
        if path.exists():
            self.urls = set(path.read_text(encoding="utf-8").splitlines())

    def exists(self, url: str) -> bool:
        """
        Dice si la oferta ya se leyó.
        Args:
            url: URL de la oferta.
        Returns:
            bool: True si ya está guardada.
        """
        return url in self.urls

    def add(self, url: str) -> None:
        """
        Marca la oferta como leída, en memoria hasta el `save()`.
        Args:
            url: URL de la oferta.
        """
        self.urls.add(url)

    def save(self) -> None:
        """Escribe todas las urls al .txt, las de antes y las nuevas."""
        self.path.write_text("\n".join(self.urls), encoding="utf-8")
