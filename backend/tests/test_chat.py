import asyncio
import json

from fastapi.testclient import TestClient

from dilemabot import main as main_module
from dilemabot.core.config import Settings
from dilemabot.chat import Turn, answer, verify_citations
from dilemabot.chat.prompts import NO_EVIDENCE

from .conftest import FakeProvider


def _run(question, index, provider, settings, history=None):
    async def collect():
        return [e async for e in answer(question, history or [], index, provider, settings)]

    return asyncio.run(collect())


def test_verificacion_de_citas():
    assert verify_citations("Hecho [1][2] y otro [2, 7].", available=3) == {
        "citadas": [1, 2],
        "citas_invalidas": [7],
        "sin_citas": False,
    }
    assert verify_citations("Sin respaldo.", 3)["sin_citas"] is True
    assert verify_citations("No lo sé con la evidencia disponible.", 3)["sin_citas"] is False


def _result(bm25, coseno):
    from dilemabot.retrieval import SearchResult

    return SearchResult(hits=[object()], max_bm25=bm25, max_coseno=coseno, uso_vectores=coseno is not None)


def test_regla_de_evidencia(settings):
    from dilemabot.chat import has_evidence

    assert has_evidence(_result(8.0, None), settings)  # sin vectores: solo BM25
    assert not has_evidence(_result(6.0, None), settings)
    assert has_evidence(_result(2.0, 0.60), settings)  # el significado basta
    assert has_evidence(_result(39.9, 0.52), settings)  # «artículo 20 de la ley 25.326»
    assert not has_evidence(_result(15.6, 0.435), settings)  # «ecuación de segundo grado»
    assert not has_evidence(_result(5.4, 0.509), settings)  # «router wifi»


def test_respuesta_con_fuentes_y_citas_invalidas(index, settings):
    provider = FakeProvider()
    events = _run("¿Debo avisar a la audiencia si una nota se redactó con IA?", index, provider, settings)
    types = [e["type"] for e in events]
    assert types[0] == "fuentes" and types[-1] == "fin" and "token" in types
    fuentes = events[0]["fuentes"]
    assert [f["n"] for f in fuentes] == list(range(1, len(fuentes) + 1))
    assert all(f["cita"] and f["pais"] == "Argentina" for f in fuentes)
    assert events[-1]["citadas"] == [1]
    assert events[-1]["citas_invalidas"] == [9]

    system, *_, user = provider.calls[0]
    assert system["role"] == "system" and "Responde SOLO" in system["content"]
    assert "FRAGMENTOS" in user["content"] and "[1]" in user["content"]


def test_sin_evidencia_no_llama_al_modelo(index, settings):
    provider = FakeProvider()
    events = _run("receta de pizza napolitana", index, provider, settings)
    assert provider.calls == []
    assert events[1]["text"] == NO_EVIDENCE
    assert events[-1]["motivo"] == "sin_evidencia"


def test_saludo_sin_busqueda(index, settings):
    provider = FakeProvider()
    events = _run("¡Hola!", index, provider, settings)
    assert provider.calls == [] and events[-1]["motivo"] == "saludo"


def test_advertencia_de_vigencia_en_el_prompt(index, settings):
    provider = FakeProvider()
    _run("límite de licencias de radio y concentración de medios", index, provider, settings)
    assert "Advertencia de vigencia (modificada)" in provider.calls[0][-1]["content"]


def test_historial_y_pregunta_de_seguimiento(index, settings):
    provider = FakeProvider()
    history = [
        Turn("usuario", "¿Qué dice la ley 11.723 sobre citar obras con fines didácticos?"),
        Turn("bot", "Permite citar hasta mil palabras [1]."),
    ]
    events = _run("¿Y eso por qué?", index, provider, settings, history)
    assert events[-1]["motivo"] == "respuesta"  # el seguimiento se busca junto a la pregunta anterior
    roles = [m["role"] for m in provider.calls[0]]
    assert roles == ["system", "user", "assistant", "user"]
    assert "[1]" not in provider.calls[0][2]["content"]  # citas antiguas eliminadas


def test_pregunta_nueva_fuera_de_dominio_no_hereda_evidencia(index, settings):
    provider = FakeProvider()
    history = [
        Turn("usuario", "¿Qué protege la Constitución sobre el secreto de las fuentes periodísticas?"),
        Turn("bot", "Lo protege el art. 43 [1]."),
    ]
    events = _run("¿Cuál es la capital de Francia?", index, provider, settings, history)
    assert provider.calls == [] and events[-1]["motivo"] == "sin_evidencia"


def test_error_del_proveedor(index, settings):
    events = _run("¿Qué dice el art. 43 de la Constitución?", index, FakeProvider(fail=True), settings)
    assert events[-1] == {"type": "error", "mensaje": "Ollama caído"}


def test_api_chat_sse(index_dir, monkeypatch):
    monkeypatch.setattr(main_module, "get_provider", lambda s: FakeProvider())
    monkeypatch.setattr(main_module, "load_settings", lambda: Settings(index_dir=index_dir))
    with TestClient(main_module.app) as client:
        salud = client.get("/api/salud").json()
        assert salud["indice"]["cargado"] and salud["llm"]["ok"]

        resp = client.post("/api/chat", json={"mensaje": "¿Qué dice el art. 43 de la Constitución?"})
        assert resp.status_code == 200
        events = [json.loads(line[6:]) for line in resp.text.splitlines() if line.startswith("data: ")]
        assert events[0]["fuentes"][0]["cita"] == "Constitución Nacional (Argentina), art. 43"
        assert events[-1]["type"] == "fin"

        assert client.post("/api/chat", json={"mensaje": ""}).status_code == 422
        assert client.post("/api/chat", json={"mensaje": "x" * 2001}).status_code == 422
        assert client.get("/").status_code == 200

