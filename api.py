"""
API que recibe los updates de Telegram por webhook. Se levanta con `uvicorn api:app`.

Sin /docs ni /openapi.json: detrás del túnel, todo lo que expone queda público.
"""

from fastapi import FastAPI

from src.telegram.webhook import router

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(router)
