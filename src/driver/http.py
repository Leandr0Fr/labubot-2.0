"""Driver HTTP: el único que toca httpx. Pide y devuelve crudo."""

import httpx

from src.constants.http import (
    ACCEPT_LANGUAGE,
    HTTP_TIMEOUT,
    USER_AGENT,
)
from src.exceptions.exceptions import LabubotRateLimitError, LabubotRequestError


class Driver:
    """
    Pide páginas y endpoints públicos, de a uno.

    No sabe con quién habla: recibe una URL y devuelve lo que vuelve.
    """

    def __init__(self) -> None:
        self.http = httpx.Client(
            timeout=HTTP_TIMEOUT,
            headers={
                "Accept-Language": ACCEPT_LANGUAGE,
                "User-Agent": USER_AGENT,
            },
            follow_redirects=True,
        )

    def close(self) -> None:
        """Cierra el cliente httpx y su pool de conexiones."""
        self.http.close()

    def _send(self, request: httpx.Request, subject: str) -> httpx.Response:
        """
        Manda el request y devuelve la respuesta cruda.

        Args:
            request: Request ya armado por el cliente.
            subject: Cómo nombrar el recurso dentro del mensaje de error.
        Returns:
            httpx.Response: La respuesta, con el status que haya venido.
        Raises:
            LabubotRateLimitError: Si el sitio contestó 429.
            LabubotRequestError: Si la red falló.
        """
        try:
            response = self.http.send(request)
        except httpx.HTTPError as error:
            raise LabubotRequestError(f"Falló la red al obtener {subject}") from error

        if response.status_code == httpx.codes.TOO_MANY_REQUESTS:
            raise LabubotRateLimitError(f"Respondió 429 al obtener {subject}")

        return response

    def get(self, url: str, subject: str, params: dict[str, str] | None = None) -> str:
        """
        Trae el texto de una URL.
        Args:
            url: URL completa a pedir.
            subject: Cómo nombrar el recurso dentro del mensaje de error.
            params: Query string, si el endpoint la lleva.
        Returns:
            str: El cuerpo crudo, que puede ser un fragmento y no una página
            entera. Vacío si el recurso ya no existe (404 o 410).
        Raises:
            LabubotRateLimitError: Si el sitio contestó 429.
            LabubotRequestError: Si la red falla o el sitio contesta otra cosa.
        """
        request = self.http.build_request("GET", url, params=params)
        response = self._send(request, subject)

        if response.status_code == httpx.codes.OK:
            return response.text

        if response.status_code in (httpx.codes.NOT_FOUND, httpx.codes.GONE):
            return ""

        raise LabubotRequestError(
            f"Respondió {response.status_code} al obtener {subject}"
        )
