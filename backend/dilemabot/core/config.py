"""Configuración leída de variables de entorno (y de un archivo .env opcional)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# backend/dilemabot/core/config.py → raíz del repositorio
ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_DIR = ROOT / "knowledge"
DOCS_DIR = KNOWLEDGE_DIR / "documentos"  # corpus en Markdown (lo que se ingiere)
PDF_DIR = KNOWLEDGE_DIR / "pdf"  # originales, se sirven en /corpus/pdf/
FUENTES_PATH = KNOWLEDGE_DIR / "fuentes.yaml"
INDEX_DIR = KNOWLEDGE_DIR / "indice"  # generado por dilemabot-ingest
FRONTEND_DIR = ROOT / "frontend"


def _load_dotenv(path: Path) -> None:
    """Carga KEY=VALUE de .env sin pisar variables ya definidas en el entorno."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    llm_provider: str = "ollama"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_embed_model: str = "bge-m3"
    llm_temperature: float = 0.2
    llm_num_ctx: int = 8192
    llm_timeout_s: float = 180.0
    ollama_num_thread: int = 0  # 0 = lo decide Ollama

    retrieval_top_k: int = 4
    retrieval_max_per_source: int = 2
    evidence_min_bm25: float = 7.0
    evidence_min_cosine: float = 0.55  # basta por sí solo
    evidence_min_cosine_bm25: float = 0.45  # mínimo cuando BM25 ya supera su umbral

    history_turns: int = 6
    max_message_chars: int = 2000

    index_dir: Path = field(default=INDEX_DIR)


def load_settings() -> Settings:
    _load_dotenv(ROOT / ".env")
    return Settings(
        llm_provider=_env("LLM_PROVIDER", "ollama").lower(),
        ollama_host=_env("OLLAMA_HOST", "http://localhost:11434").rstrip("/"),
        ollama_model=_env("OLLAMA_MODEL", "qwen2.5:7b"),
        ollama_embed_model=_env("OLLAMA_EMBED_MODEL", "bge-m3"),
        llm_temperature=float(_env("LLM_TEMPERATURE", "0.2")),
        llm_num_ctx=int(_env("LLM_NUM_CTX", "8192")),
        llm_timeout_s=float(_env("LLM_TIMEOUT_S", "180")),
        ollama_num_thread=int(_env("OLLAMA_NUM_THREAD", "0")),
        retrieval_top_k=int(_env("RETRIEVAL_TOP_K", "4")),
        retrieval_max_per_source=int(_env("RETRIEVAL_MAX_PER_SOURCE", "2")),
        evidence_min_bm25=float(_env("EVIDENCE_MIN_BM25", "7.0")),
        evidence_min_cosine=float(_env("EVIDENCE_MIN_COSINE", "0.55")),
        evidence_min_cosine_bm25=float(_env("EVIDENCE_MIN_COSINE_BM25", "0.45")),
        history_turns=int(_env("HISTORY_TURNS", "6")),
    )
