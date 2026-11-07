"""API: recibe los updates de Telegram por webhook. Se levanta con `uvicorn api:app`."""

from fastapi import FastAPI

from src.telegram.webhook import router

# Sin /docs ni /openapi.json: detrás de un túnel, todo lo de la app queda público.
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(router)
