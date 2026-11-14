"""Contratos de entrada de la API (validación con Pydantic)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

MAX_HISTORY_ITEMS = 40


class HistoryItem(BaseModel):
    rol: Literal["usuario", "bot"]
    contenido: str = Field(max_length=8000)


class ChatRequest(BaseModel):
    mensaje: str = Field(min_length=1, max_length=2000)
    historial: list[HistoryItem] = Field(default_factory=list, max_length=MAX_HISTORY_ITEMS)
