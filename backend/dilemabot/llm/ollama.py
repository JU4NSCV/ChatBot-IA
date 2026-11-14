"""Proveedor Ollama (modelos locales). API: https://github.com/ollama/ollama/blob/main/docs/api.md"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from .base import LLMError, Message


class OllamaProvider:
    name = "ollama"

    def __init__(
        self,
        host: str,
        model: str,
        embed_model: str,
        temperature: float = 0.2,
        num_ctx: int = 8192,
        timeout_s: float = 180.0,
        num_thread: int = 0,
    ) -> None:
        self.host = host.rstrip("/")
        self.model = model
        self.embed_model = embed_model
        self.temperature = temperature
        self.num_ctx = num_ctx
        self.num_thread = num_thread
        # Conexión rápida para detectar que Ollama no está corriendo; lectura larga porque
        # en CPU el primer token puede tardar.
        self.timeout = httpx.Timeout(timeout_s, connect=5.0)

    def _options(self, **extra) -> dict:
        if self.num_thread > 0:
            extra["num_thread"] = self.num_thread
        return extra

    async def stream_chat(self, messages: list[Message]) -> AsyncIterator[str]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": self._options(temperature=self.temperature, num_ctx=self.num_ctx),
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{self.host}/api/chat", json=payload) as resp:
                    if resp.status_code != 200:
                        body = (await resp.aread()).decode("utf-8", "replace")
                        raise LLMError(_explain(resp.status_code, body, self.model))
                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        if "error" in data:
                            raise LLMError(f"Ollama: {data['error']}")
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            yield chunk
                        if data.get("done"):
                            break
        except httpx.ConnectError as exc:
            raise LLMError(
                f"No se pudo conectar con Ollama en {self.host}. ¿Está en ejecución (`ollama serve`)?"
            ) from exc
        except httpx.TimeoutException as exc:
            raise LLMError("Ollama tardó demasiado en responder.") from exc

    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.host}/api/embed",
                    json={"model": self.embed_model, "input": texts, "options": self._options()},
                )
        except httpx.ConnectError as exc:
            raise LLMError(f"No se pudo conectar con Ollama en {self.host}.") from exc
        except httpx.TimeoutException as exc:
            raise LLMError("Ollama tardó demasiado en calcular embeddings.") from exc
        if resp.status_code != 200:
            raise LLMError(_explain(resp.status_code, resp.text, self.embed_model))
        embeddings = resp.json().get("embeddings")
        if not embeddings or len(embeddings) != len(texts):
            raise LLMError("Ollama devolvió embeddings vacíos o incompletos.")
        return embeddings

    async def health(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                resp = await client.get(f"{self.host}/api/tags")
            resp.raise_for_status()
        except httpx.HTTPError:
            return {
                "ok": False,
                "proveedor": self.name,
                "modelo": self.model,
                "detalle": f"Ollama no responde en {self.host}",
            }
        installed = {m.get("name", "") for m in resp.json().get("models", [])}
        missing = [m for m in (self.model, self.embed_model) if not _has_model(installed, m)]
        return {
            "ok": self.model not in missing,
            "proveedor": self.name,
            "modelo": self.model,
            "modelo_embeddings": self.embed_model,
            "faltan": missing,
            "detalle": "listo" if not missing else f"Faltan modelos: {', '.join(missing)} (ollama pull …)",
        }


def _has_model(installed: set[str], name: str) -> bool:
    # «bge-m3» equivale a «bge-m3:latest».
    return name in installed or f"{name}:latest" in installed


def _explain(status: int, body: str, model: str) -> str:
    if status == 404 or "not found" in body.lower():
        return f"El modelo «{model}» no está descargado en Ollama. Ejecute: ollama pull {model}"
    return f"Ollama respondió {status}: {body[:300]}"
