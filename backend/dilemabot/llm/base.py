"""Interfaz común para proveedores de modelos de lenguaje.

La lógica del chat solo conoce esta interfaz, así que cambiar Ollama por Claude u otra API
consiste en añadir una implementación nueva y elegirla con LLM_PROVIDER.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, TypedDict


class Message(TypedDict):
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMError(RuntimeError):
    """Error del proveedor (servicio caído, modelo ausente, respuesta inválida)."""


class LLMProvider(Protocol):
    name: str
    model: str

    def stream_chat(self, messages: list[Message]) -> AsyncIterator[str]:
        """Devuelve el texto de la respuesta en fragmentos, a medida que se genera."""
        ...

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Devuelve un vector por texto. Lanza LLMError si el proveedor no ofrece embeddings."""
        ...

    async def health(self) -> dict:
        """Estado del proveedor: {"ok": bool, "detalle": str, ...}."""
        ...
