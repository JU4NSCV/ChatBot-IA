"""Punto de entrada de DilemaBot: arma la aplicación web.

Ejecutar:  uvicorn dilemabot.main:app --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import router
from .core.config import FRONTEND_DIR, FUENTES_PATH, PDF_DIR, load_settings
from .llm import get_provider
from .retrieval import Index

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("dilemabot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    app.state.settings = settings
    app.state.provider = get_provider(settings)
    try:
        app.state.index = Index.load(settings.index_dir, FUENTES_PATH)
        log.info(
            "Índice cargado: %d fragmentos, vectores=%s",
            len(app.state.index.chunks),
            app.state.index.embeddings is not None,
        )
    except FileNotFoundError as exc:
        app.state.index = None
        log.warning("%s", exc)
    log.info("Proveedor LLM: %s · %s", app.state.provider.name, app.state.provider.model)
    yield


app = FastAPI(title="DilemaBot", version="0.1.0", lifespan=lifespan)
app.include_router(router)
app.mount("/corpus/pdf", StaticFiles(directory=PDF_DIR), name="pdf")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
