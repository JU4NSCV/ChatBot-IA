"""Proveedor Claude con un cliente simulado (no usa la API real ni una API key)."""

import asyncio
from types import SimpleNamespace

import anthropic
import pytest

from dilemabot.core.config import Settings
from dilemabot.llm import LLMError, get_provider
from dilemabot.llm.claude import FALLBACK_BETA, ClaudeProvider

from .conftest import FakeProvider


class FakeStream:
    def __init__(self, chunks, stop_reason="end_turn", model="claude-opus-5-5"):
        self.chunks = chunks
        self.final = SimpleNamespace(
            stop_reason=stop_reason,
            model=model,
            usage=SimpleNamespace(input_tokens=100, output_tokens=20),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    @property
    async def text_stream(self):
        for chunk in self.chunks:
            yield chunk

    async def get_final_message(self):
        return self.final


class FakeClient:
    def __init__(self, stream=None, error=None):
        self.requests = []
        self._stream, self._error = stream, error
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._open))

    def _open(self, **request):
        self.requests.append(request)
        if self._error:
            raise self._error
        return self._stream


def _provider(client, model="claude-opus-5-5"):
    provider = ClaudeProvider(model=model, embedder=FakeProvider())
    provider._client = client
    return provider


def _collect(provider, messages):
    async def run():
        return [t async for t in provider.stream_chat(messages)]

    return asyncio.run(run())


MESSAGES = [
    {"role": "system", "content": "Reglas de DilemaBot"},
    {"role": "user", "content": "¿Qué dice el art. 43?"},
]


def test_separa_el_sistema_y_activa_fallbacks():
    client = FakeClient(FakeStream(["Hola ", "[1]"]))
    assert _collect(_provider(client), MESSAGES) == ["Hola ", "[1]"]
    request = client.requests[0]
    assert request["system"] == "Reglas de DilemaBot"
    assert request["messages"] == [{"role": "user", "content": "¿Qué dice el art. 43?"}]
    assert request["model"] == "claude-opus-5-5"
    assert request["output_config"] == {"effort": "medium"}
    assert request["betas"] == [FALLBACK_BETA] and request["fallbacks"] == "default"
    assert "temperature" not in request  # los modelos actuales la rechazan


def test_sin_fallbacks_en_modelos_que_no_los_admiten():
    client = FakeClient(FakeStream(["ok"]))
    _collect(_provider(client, model="claude-haiku-5-5"), MESSAGES)
    assert "fallbacks" not in client.requests[0] and "betas" not in client.requests[0]


def test_rechazo_se_informa_como_error():
    client = FakeClient(FakeStream([], stop_reason="refusal"))
    with pytest.raises(LLMError, match="declinó"):
        _collect(_provider(client), MESSAGES)


def test_error_de_conexion_se_traduce():
    error = anthropic.APIConnectionError(request=SimpleNamespace(method="POST", url="x"))
    with pytest.raises(LLMError, match="conectar"):
        _collect(_provider(FakeClient(error=error)), MESSAGES)


def test_sin_api_key_se_explica():
    error = TypeError('"Could not resolve authentication method. Expected one of api_key..."')
    with pytest.raises(LLMError, match="ANTHROPIC_API_KEY"):
        _collect(_provider(FakeClient(error=error)), MESSAGES)


def test_fabrica_usa_ollama_para_embeddings():
    provider = get_provider(Settings(llm_provider="claude"))
    assert isinstance(provider, ClaudeProvider)
    assert provider.embed_model == "bge-m3" and provider.embedder.name == "ollama"
