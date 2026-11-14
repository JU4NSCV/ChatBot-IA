"""Endpoints HTTP de DilemaBot."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from ..chat import Turn, answer
from ..core.config import FUENTES_PATH
from ..retrieval import Index, load_fuentes
from .schemas import ChatRequest

router = APIRouter(prefix="/api")


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


@router.get("/salud")
async def salud(request: Request) -> dict:
    """Estado del modelo de lenguaje y del índice."""
    index: Index | None = request.app.state.index
    return {
        "llm": await request.app.state.provider.health(),
        "indice": {
            "cargado": index is not None,
            "fragmentos": len(index.chunks) if index else 0,
            "vectores": bool(index is not None and index.embeddings is not None),
        },
    }


@router.get("/fuentes")
async def fuentes() -> list[dict]:
    """Fuentes del corpus con su país, enlace y vigencia."""
    keys = ("id", "titulo", "titulo_corto", "pais", "tipo", "url", "vigencia", "nota_vigencia")
    return [{k: f.get(k) for k in keys} for f in load_fuentes(FUENTES_PATH).values()]


@router.post("/chat")
async def chat(body: ChatRequest, request: Request) -> StreamingResponse:
    """Responde en streaming (Server-Sent Events). Ver `chat.pipeline` para los tipos de evento."""
    if not body.mensaje.strip():
        raise HTTPException(422, "El mensaje está vacío.")
    index: Index | None = request.app.state.index
    if index is None:
        raise HTTPException(503, "El índice no está generado. Ejecute: dilemabot-ingest")

    history = [Turn(h.rol, h.contenido) for h in body.historial]
    state = request.app.state

    async def events() -> AsyncIterator[str]:
        async for event in answer(body.mensaje, history, index, state.provider, state.settings):
            yield _sse(event)

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
