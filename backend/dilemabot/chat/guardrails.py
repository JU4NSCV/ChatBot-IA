"""Control de respuestas: decidir si hay evidencia suficiente y verificar las citas del modelo."""

from __future__ import annotations

import re

from ..core.config import Settings
from ..retrieval import SearchResult

CITATION_RE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
NO_SE_RE = re.compile(r"no lo s[eé]", re.I)


def has_evidence(result: SearchResult, settings: Settings) -> bool:
    """¿Alcanzan los fragmentos recuperados para responder?

    Con vectores, el significado manda: una coincidencia de palabras (p. ej. «grado» en
    «ecuación de segundo grado») no basta si el coseno es bajo. Sin vectores, solo BM25.
    """
    if not result.hits:
        return False
    bm25_ok = result.max_bm25 >= settings.evidence_min_bm25
    if result.max_coseno is None:
        return bm25_ok
    return result.max_coseno >= settings.evidence_min_cosine or (
        bm25_ok and result.max_coseno >= settings.evidence_min_cosine_bm25
    )


def verify_citations(text: str, available: int) -> dict:
    """Separa las citas [n] válidas de las que apuntan a fragmentos que no se enviaron."""
    cited: set[int] = set()
    for group in CITATION_RE.findall(text):
        cited.update(int(x) for x in re.split(r"\s*,\s*", group))
    valid = sorted(n for n in cited if 1 <= n <= available)
    invalid = sorted(n for n in cited if not 1 <= n <= available)
    return {
        "citadas": valid,
        "citas_invalidas": invalid,
        "sin_citas": not valid and not NO_SE_RE.search(text),
    }


def strip_citations(text: str) -> str:
    return CITATION_RE.sub("", text)
