"""Proveedor Claude (API de Anthropic) con el SDK oficial `anthropic`.

La API de Claude no ofrece embeddings: la búsqueda por significado sigue usando el modelo de
embeddings de Ollama (`embedder`), así el índice y los umbrales calibrados no cambian.

Credenciales: el SDK lee ANTHROPIC_API_KEY del entorno (o del archivo .env del proyecto).
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator

import anthropic

from .base import LLMError, LLMProvider, Message

log = logging.getLogger(__name__)

# Si un clasificador de seguridad declina la consulta, la API la reintenta en otro modelo
# dentro de la misma llamada. Solo algunos modelos lo admiten.
FALLBACK_BETA = "server-side-fallback-2026-07-01"
FALLBACK_MODELS = {
    "claude-opus-5-5",
    "claude-opus-5",
    "claude-sonnet-5-5",
    "claude-fable-5-1",
    "claude-fable-5-2",
}


MISSING_KEY = "Falta la API key de Claude: defina ANTHROPIC_API_KEY en el archivo .env."


def _is_missing_credentials(exc: TypeError) -> bool:
    # El SDK detecta la falta de credenciales al armar la petición, no al crear el cliente.
    return "authentication method" in str(exc)


class ClaudeProvider:
    name = "claude"

    def __init__(
        self,
        model: str,
        embedder: LLMProvider,
        effort: str = "medium",
        max_tokens: int = 64000,
        timeout_s: float = 180.0,
    ) -> None:
        self.model = model
        self.embedder = embedder
        self.embed_model = getattr(embedder, "embed_model", None)
        self.effort = effort
        self.max_tokens = max_tokens
        self.timeout_s = timeout_s
        self.fallbacks = model in FALLBACK_MODELS
        self._client: anthropic.AsyncAnthropic | None = None

    def _get_client(self) -> anthropic.AsyncAnthropic:
        if self._client is None:
            try:
                self._client = anthropic.AsyncAnthropic(timeout=self.timeout_s)
            except anthropic.AnthropicError as exc:
                raise LLMError(MISSING_KEY) from exc
        return self._client

    def _request(self, messages: list[Message]) -> dict:
        # La API recibe las instrucciones de sistema aparte de la conversación.
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        conversation = [
            {"role": m["role"], "content": m["content"]} for m in messages if m["role"] != "system"
        ]
        request = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": conversation,
            "output_config": {"effort": self.effort},
        }
        if self.fallbacks:
            request["betas"] = [FALLBACK_BETA]
            request["fallbacks"] = "default"
        return request

    async def stream_chat(self, messages: list[Message]) -> AsyncIterator[str]:
        client = self._get_client()
        try:
            async with client.beta.messages.stream(**self._request(messages)) as stream:
                async for text in stream.text_stream:
                    yield text
                final = await stream.get_final_message()
        except TypeError as exc:
            if _is_missing_credentials(exc):
                raise LLMError(MISSING_KEY) from exc
            raise
        except anthropic.AuthenticationError as exc:
            raise LLMError("La API key de Claude no es válida (ANTHROPIC_API_KEY).") from exc
        except anthropic.PermissionDeniedError as exc:
            raise LLMError("La API key no tiene permiso para usar este modelo.") from exc
        except anthropic.NotFoundError as exc:
            raise LLMError(f"Modelo de Claude no encontrado: {self.model}") from exc
        except anthropic.RateLimitError as exc:
            raise LLMError("Límite de uso de la API de Claude alcanzado; intente en un momento.") from exc
        except anthropic.BadRequestError as exc:
            # El caso más común: cuenta sin crédito.
            raise LLMError(f"Claude rechazó la solicitud: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            raise LLMError("No se pudo conectar con la API de Claude (¿hay internet?).") from exc
        except anthropic.APIStatusError as exc:
            raise LLMError(f"Error de la API de Claude ({exc.status_code}).") from exc

        if final.model != self.model:
            log.info("Claude respondió con el modelo de respaldo %s", final.model)
        if final.stop_reason == "refusal":
            raise LLMError("Claude declinó responder esta consulta.")
        if final.stop_reason == "max_tokens":
            log.warning("Respuesta de Claude cortada por max_tokens")
        log.info(
            "Claude tokens: entrada=%s salida=%s", final.usage.input_tokens, final.usage.output_tokens
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self.embedder.embed(texts)

    async def health(self) -> dict:
        status = {"proveedor": self.name, "modelo": self.model}
        try:
            # Consulta el modelo sin generar texto (no consume tokens).
            await self._get_client().models.retrieve(self.model)
        except LLMError as exc:
            return {**status, "ok": False, "detalle": str(exc)}
        except TypeError as exc:
            if not _is_missing_credentials(exc):
                raise
            return {**status, "ok": False, "detalle": MISSING_KEY}
        except anthropic.AuthenticationError:
            return {**status, "ok": False, "detalle": "API key de Claude inválida"}
        except anthropic.NotFoundError:
            return {**status, "ok": False, "detalle": f"Modelo no disponible: {self.model}"}
        except anthropic.APIError as exc:
            return {**status, "ok": False, "detalle": f"API de Claude no responde: {exc}"}
        embed = await self.embedder.health()
        detalle = "listo" if not embed.get("faltan") else f"embeddings: {embed['detalle']}"
        return {**status, "ok": True, "modelo_embeddings": self.embed_model, "detalle": detalle}
