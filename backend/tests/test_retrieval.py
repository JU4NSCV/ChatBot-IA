import pytest

from dilemabot.retrieval import tokenize

EVIDENCE_MIN_BM25 = 7.0


def _top_citas(index, query, n=3):
    return [h.chunk["cita"] for h in index.search(query).hits[:n]]


def test_tokenize_quita_tildes_stopwords_y_trunca():
    assert tokenize("¿Qué es la Transparencia?") == ["transp"]
    assert tokenize("art. 43") == ["articu", "43"]


def test_articulo_pedido_por_numero_y_fuente(index):
    assert _top_citas(index, "¿Qué dice el art. 43 de la Constitución?")[0] == (
        "Constitución Nacional (Argentina), art. 43"
    )
    assert _top_citas(index, "¿Qué dice el artículo 20 de la ley 25.326?")[0] == (
        "Ley 25.326 (Argentina), art. 20"
    )


@pytest.mark.parametrize(
    "query, expected",
    [
        ("¿Cuántas palabras puedo citar de una obra con fines didácticos?", "Ley 11.723 (Argentina), art. 10"),
        ("¿Quién es dueño de una nota firmada por un colaborador?", "Ley 11.723 (Argentina), art. 29"),
        ("secreto de las fuentes periodísticas", "Constitución Nacional (Argentina), art. 43"),
        ("¿Debo avisar a la audiencia si una nota se redactó con IA?", "Guía ADEPA para el uso de la IA, punto 05"),
    ],
)
def test_recupera_el_fragmento_esperado(index, query, expected):
    assert expected in [h.chunk["cita"] for h in index.search(query).hits]


def test_limite_de_fragmentos_por_fuente(index):
    hits = index.search("licencias de radio y televisión", top_k=6, max_per_source=2).hits
    per_source = {}
    for h in hits:
        per_source[h.chunk["fuente_id"]] = per_source.get(h.chunk["fuente_id"], 0) + 1
    assert max(per_source.values()) <= 2


@pytest.mark.parametrize(
    "query",
    [
        "receta de pizza napolitana",
        "¿Quién ganó el mundial de fútbol 2022?",
        "¿Cómo configuro mi router wifi?",
        "dame consejos para bajar de peso",
    ],
)
def test_fuera_de_dominio_bajo_el_umbral(index, query):
    assert index.search(query).max_bm25 < EVIDENCE_MIN_BM25


@pytest.mark.parametrize(
    "query",
    [
        "¿Qué es la transparencia en el periodismo?",
        "¿Puede un algoritmo decidir sobre una persona con un perfil automatizado?",
        "límite de licencias de radio y concentración de medios",
    ],
)
def test_dentro_del_dominio_sobre_el_umbral(index, query):
    assert index.search(query).max_bm25 >= EVIDENCE_MIN_BM25
