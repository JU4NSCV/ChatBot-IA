"""Capa de modelos de lenguaje: proveedores intercambiables detrás de `LLMProvider`."""

from ..core.config import Settings
from .base import LLMError, LLMProvider, Message
from .ollama import OllamaProvider

__all__ = ["LLMError", "LLMProvider", "Message", "OllamaProvider", "get_provider"]


def get_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "ollama":
        return OllamaProvider(
            host=settings.ollama_host,
            model=settings.ollama_model,
            embed_model=settings.ollama_embed_model,
            temperature=settings.llm_temperature,
            num_ctx=settings.llm_num_ctx,
            timeout_s=settings.llm_timeout_s,
            num_thread=settings.ollama_num_thread,
        )
    # El proveedor Claude se añade en S11 implementando la misma interfaz.
    raise ValueError(f"Proveedor LLM no soportado todavía: {settings.llm_provider!r}")
