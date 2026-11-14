"""Flujo de una respuesta: buscar evidencia → decidir si hay suficiente → generar → verificar citas.

`answer()` produce eventos (diccionarios) que la API envía al navegador como SSE:
    {"type": "fuentes", "fuentes": [...]}   fragmentos recuperados, numerados como en las citas
    {"type": "token", "text": "..."}         texto de la respuesta a medida que se genera
    {"type": "fin", ...}                     resultado de la verificación de citas
    {"type": "error", "mensaje": "..."}      fallo del proveedor LLM
"""

from __future__ import annotations

import logging
import re
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass

from ..core.config import Settings
from ..llm import LLMError, LLMProvider, Message
from ..retrieval import Hit, Index, SearchResult
from .guardrails import has_evidence, strip_citations, verify_citations
from .prompts import GREETING, NO_EVIDENCE, SYSTEM_PROMPT, THANKS, user_prompt

log = logging.getLogger(__name__)

GREETING_RE = re.compile(
    r"^\W*(hola|buen(os|as)\s+(d[ií]as|tardes|noches)|hey|saludos|qu[eé]\s+tal)\W*$", re.I
)
THANKS_RE = re.compile(r"^\W*(muchas\s+)?gracias(\s+\w+)?\W*$|^\W*(chao|adi[oó]s)\W*$", re.I)
# Señales de que la pregunta depende de la anterior: «¿y eso?», «¿por qué?», «esa ley…».
FOLLOWUP_RE = re.compile(
    r"^\W*(y|pero|entonces|tambi[eé]n)\b"
    r"|\b(eso|esto|ese|esa|esos|esas|ello|aquello|anterior|lo mismo|dicho|dicha)\b"
    r"|^\W*(por\s*qu[eé]|c[oó]mo\s+as[ií]|en\s+qu[eé]\s+sentido)\W*$",
    re.I,
)


@dataclass
class Turn:
    rol: str  # "usuario" | "bot"
    contenido: str


def _fuente_payload(n: int, hit: Hit) -> dict:
    fuente = hit.fuente
    pdf = fuente.get("pdf")
    return {
        "n": n,
        "cita": hit.chunk["cita"],
        "fuente_id": hit.chunk["fuente_id"],
        "titulo": fuente.get("titulo", ""),
        "pais": fuente.get("pais", ""),
        "seccion": hit.chunk["seccion"],
        "vigencia": fuente.get("vigencia", "por_verificar"),
        "nota_vigencia": " ".join(str(fuente.get("nota_vigencia", "")).split()),
        "url": fuente.get("url") or None,
        "pdf_url": f"/corpus/pdf/{pdf}" if pdf else None,
        "extracto": hit.chunk["texto"][:320],
    }


def _history_messages(history: list[Turn], turns: int, max_chars: int) -> list[Message]:
    messages: list[Message] = []
    for turn in history[-turns * 2 :] if turns > 0 else []:
        role = "user" if turn.rol == "usuario" else "assistant"
        content = turn.contenido[:max_chars]
        if role == "assistant":
            content = strip_citations(content)  # los números de cita antiguos ya no aplican
        messages.append({"role": role, "content": content})
    return messages


def _followup_query(question: str, history: list[Turn]) -> str | None:
    """Si la pregunta parece de seguimiento, la combina con la pregunta anterior del usuario."""
    if not FOLLOWUP_RE.search(question):
        return None
    previous = next((t.contenido for t in reversed(history) if t.rol == "usuario"), None)
    return f"{previous} {question}" if previous else None


async def answer(
    question: str,
    history: list[Turn],
    index: Index,
    provider: LLMProvider,
    settings: Settings,
) -> AsyncIterator[dict]:
    question = question.strip()
    if GREETING_RE.match(question) or THANKS_RE.match(question):
        yield {"type": "fuentes", "fuentes": []}
        yield {"type": "token", "text": GREETING if GREETING_RE.match(question) else THANKS}
        yield {"type": "fin", "citadas": [], "citas_invalidas": [], "sin_citas": False, "motivo": "saludo"}
        return

    started = time.perf_counter()
    avisos: list[str] = []
    embed_model = getattr(provider, "embed_model", None)
    use_vectors = index.embeddings is not None and index.embed_model == embed_model

    async def search(query: str) -> tuple[SearchResult, bool]:
        query_vector = None
        if use_vectors:
            try:
                query_vector = (await provider.embed([query]))[0]
            except LLMError as exc:
                log.warning("Sin vectores para esta consulta: %s", exc)
                if not avisos:
                    avisos.append("Búsqueda solo por palabras clave (embeddings no disponibles).")
        result = index.search(
            query,
            query_vector=query_vector,
            top_k=settings.retrieval_top_k,
            max_per_source=settings.retrieval_max_per_source,
        )
        return result, has_evidence(result, settings)

    # Primero la pregunta sola: así una pregunta nueva fuera de dominio no hereda la evidencia
    # de la anterior. Solo si no hay evidencia y suena a seguimiento se busca con el contexto.
    result, enough = await search(question)
    if not enough and (followup := _followup_query(question, history)):
        result, enough = await search(followup)

    # Solo métricas, nunca el texto del usuario (privacidad).
    log.info(
        "consulta chars=%d bm25=%.2f coseno=%s evidencia=%s",
        len(question),
        result.max_bm25,
        f"{result.max_coseno:.3f}" if result.max_coseno is not None else "-",
        enough,
    )

    if not enough:
        yield {"type": "fuentes", "fuentes": [], "avisos": avisos}
        yield {"type": "token", "text": NO_EVIDENCE}
        yield {"type": "fin", "citadas": [], "citas_invalidas": [], "sin_citas": False, "motivo": "sin_evidencia"}
        return

    hits = result.hits
    yield {
        "type": "fuentes",
        "fuentes": [_fuente_payload(i + 1, h) for i, h in enumerate(hits)],
        "avisos": avisos,
    }

    messages: list[Message] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += _history_messages(history, settings.history_turns, settings.max_message_chars)
    messages.append({"role": "user", "content": user_prompt(question, hits)})

    full = []
    try:
        async for token in provider.stream_chat(messages):
            full.append(token)
            yield {"type": "token", "text": token}
    except LLMError as exc:
        log.error("Error del proveedor LLM: %s", exc)
        yield {"type": "error", "mensaje": str(exc)}
        return

    check = verify_citations("".join(full), len(hits))
    log.info(
        "respuesta en %.1f s, citas=%s inválidas=%s",
        time.perf_counter() - started,
        check["citadas"],
        check["citas_invalidas"],
    )
    yield {"type": "fin", **check, "motivo": "respuesta"}
