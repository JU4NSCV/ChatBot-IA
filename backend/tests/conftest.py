from __future__ import annotations

import json

import pytest

from dilemabot.core.config import DOCS_DIR, FUENTES_PATH, Settings
from dilemabot.llm import LLMError
from dilemabot.retrieval import Index, load_fuentes
from dilemabot.ingestion.segment import segment


class FakeProvider:
    """Proveedor LLM de prueba: devuelve una respuesta fija y registra lo que recibió."""

    name = "fake"
    model = "fake-model"
    embed_model = None

    def __init__(self, reply: str = "Respuesta [1] con cita inventada [9].", fail: bool = False):
        self.reply = reply
        self.fail = fail
        self.calls: list[list[dict]] = []

    async def stream_chat(self, messages):
        self.calls.append(messages)
        if self.fail:
            raise LLMError("Ollama caído")
        for word in self.reply.split(" "):
            yield word + " "

    async def embed(self, texts):
        raise LLMError("sin embeddings")

    async def health(self):
        return {"ok": True, "proveedor": self.name, "modelo": self.model, "detalle": "listo"}


@pytest.fixture(scope="session")
def fuentes() -> dict[str, dict]:
    return load_fuentes(FUENTES_PATH)


@pytest.fixture(scope="session")
def index(fuentes) -> Index:
    chunks = []
    for f in fuentes.values():
        text = (DOCS_DIR / f["archivo"]).read_text(encoding="utf-8")
        chunks += [c.to_dict() for c in segment(text, f["id"], f["titulo_corto"])]
    return Index(chunks, fuentes)


@pytest.fixture()
def settings(tmp_path) -> Settings:
    return Settings(index_dir=tmp_path)


@pytest.fixture()
def index_dir(tmp_path, index):
    with (tmp_path / "chunks.jsonl").open("w", encoding="utf-8") as fh:
        for c in index.chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    return tmp_path
