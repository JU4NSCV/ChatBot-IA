"""Capa de modelos de lenguaje: proveedores intercambiables detrás de `LLMProvider`."""

from ..core.config import Settings
from .base import LLMError, LLMProvider, Message
from .ollama import OllamaProvider

__all__ = ["LLMError", "LLMProvider", "Message", "OllamaProvider", "get_provider"]


def _ollama(settings: Settings) -> OllamaProvider:
    return OllamaProvider(
        host=settings.ollama_host,
        model=settings.ollama_model,
        embed_model=settings.ollama_embed_model,
        temperature=settings.llm_temperature,
        num_ctx=settings.llm_num_ctx,
        timeout_s=settings.llm_timeout_s,
        num_thread=settings.ollama_num_thread,
    )


def get_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "ollama":
        return _ollama(settings)
    if settings.llm_provider == "claude":
        from .claude import ClaudeProvider  # importa el SDK solo si se usa

        # Claude redacta; Ollama sigue calculando los embeddings de la búsqueda.
        return ClaudeProvider(
            model=settings.claude_model,
            embedder=_ollama(settings),
            effort=settings.claude_effort,
            max_tokens=settings.claude_max_tokens,
            timeout_s=settings.llm_timeout_s,
        )
    raise ValueError(f"Proveedor LLM no soportado: {settings.llm_provider!r} (use ollama o claude)")
