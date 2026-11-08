"""Los comandos del bot, sin la barra."""

from enum import StrEnum


class Command(StrEnum):
    """
    Lo que el usuario escribe después de "/".
    START: Pedir acceso o buscar ofertas ya.
    SETTINGS: El panel de términos, bloqueadas y perfil.
    PROFILE: Ver o reemplazar el CV.
    ALLOW: Sumar términos de búsqueda: /permitido python, django.
    BLOCK: Sumar palabras bloqueadas: /bloquear php, wordpress.
    TEMPLATE: La plantilla para armar el CV.
    PAUSE / RESUME: Pausar o volver a recibir alertas.
    CLEAR: Borrar los mensajes del chat.
    HELP: Qué hace el bot.
    USERS: Los usuarios y su estado; solo el admin.
    """

    START = "start"
    SETTINGS = "settings"
    PROFILE = "perfil"
    ALLOW = "permitido"
    BLOCK = "bloquear"
    TEMPLATE = "template"
    PAUSE = "pausa"
    RESUME = "reanudar"
    CLEAR = "clear"
    HELP = "ayuda"
    USERS = "usuarios"
