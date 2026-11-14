"""Índice del corpus y búsqueda híbrida: BM25 (palabras exactas, números de artículo) + vectores.

Los vectores son opcionales: si el índice se generó sin embeddings o Ollama no responde,
la búsqueda sigue funcionando solo con BM25.
"""

from __future__ import annotations

import json
import logging
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

from .text import normalize, terms

log = logging.getLogger(__name__)

CHUNKS_FILE = "chunks.jsonl"
EMBEDDINGS_FILE = "embeddings.npy"
META_FILE = "meta.json"

ARTICLE_QUERY_RE = re.compile(r"\bart(?:iculo|s)?\.?\s*(\d+)(?:\s*(bis|ter))?", re.IGNORECASE)
SOURCE_BOOST = 3.0
ARTICLE_BOOST = 6.0
RRF_K = 60


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.4, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.len = np.array([len(d) for d in docs], dtype=np.float32)
        self.avgdl = float(self.len.mean()) if len(docs) else 0.0
        df: Counter[str] = Counter()
        for d in self.tf:
            df.update(d.keys())
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: list[str]) -> np.ndarray:
        out = np.zeros(len(self.tf), dtype=np.float32)
        norm = self.k1 * (1 - self.b + self.b * self.len / (self.avgdl or 1.0))
        for term in set(query):
            idf = self.idf.get(term)
            if idf is None:
                continue
            tf = np.array([d.get(term, 0) for d in self.tf], dtype=np.float32)
            out += idf * tf * (self.k1 + 1) / (tf + norm)
        return out


@dataclass
class Hit:
    chunk: dict
    fuente: dict
    bm25: float
    coseno: float | None
    puntaje: float  # fusión RRF


@dataclass
class SearchResult:
    hits: list[Hit]
    max_bm25: float
    max_coseno: float | None
    uso_vectores: bool


class Index:
    def __init__(
        self,
        chunks: list[dict],
        fuentes: dict[str, dict],
        embeddings: np.ndarray | None = None,
        embed_model: str | None = None,
    ) -> None:
        self.chunks = chunks
        self.fuentes = fuentes
        self.embeddings = embeddings
        self.embed_model = embed_model
        self.bm25 = BM25([terms(self.index_text(c)) for c in chunks])
        self.aliases = {
            fid: [normalize(a) for a in f.get("alias", [])] for fid, f in fuentes.items()
        }

    def index_text(self, chunk: dict) -> str:
        fuente = self.fuentes.get(chunk["fuente_id"], {})
        return f"{fuente.get('titulo', '')} {chunk['cita']} {chunk['seccion']} {chunk['texto']}"

    @classmethod
    def load(cls, index_dir: Path, fuentes_path: Path) -> Index:
        chunks_path = index_dir / CHUNKS_FILE
        if not chunks_path.is_file():
            raise FileNotFoundError(
                f"No existe {chunks_path}. Genere el índice con: dilemabot-ingest"
            )
        chunks = [json.loads(line) for line in chunks_path.read_text(encoding="utf-8").splitlines()]
        meta_path = index_dir / META_FILE
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
        emb_path = index_dir / EMBEDDINGS_FILE
        embeddings = np.load(emb_path) if emb_path.is_file() else None
        if embeddings is not None and len(embeddings) != len(chunks):
            log.warning("embeddings.npy no coincide con chunks.jsonl; se ignoran los vectores")
            embeddings = None
        return cls(chunks, load_fuentes(fuentes_path), embeddings, meta.get("embed_model"))

    def search(
        self,
        query: str,
        query_vector: list[float] | None = None,
        top_k: int = 4,
        max_per_source: int = 2,
        pool: int = 50,
    ) -> SearchResult:
        bm = self.bm25.scores(terms(query)) + self._boosts(query)
        ranks: dict[int, float] = {}
        for rank, i in enumerate(np.argsort(-bm)[:pool]):
            if bm[i] > 0:
                ranks[int(i)] = ranks.get(int(i), 0.0) + 1 / (RRF_K + rank)

        cos = None
        if query_vector is not None and self.embeddings is not None:
            q = np.asarray(query_vector, dtype=np.float32)
            q /= np.linalg.norm(q) or 1.0
            cos = self.embeddings @ q
            for rank, i in enumerate(np.argsort(-cos)[:pool]):
                ranks[int(i)] = ranks.get(int(i), 0.0) + 1 / (RRF_K + rank)

        hits: list[Hit] = []
        per_source: Counter[str] = Counter()
        for i in sorted(ranks, key=ranks.get, reverse=True):
            chunk = self.chunks[i]
            if per_source[chunk["fuente_id"]] >= max_per_source:
                continue  # evita que la Ley 26.522 (más de la mitad del corpus) acapare la respuesta
            per_source[chunk["fuente_id"]] += 1
            hits.append(
                Hit(
                    chunk=chunk,
                    fuente=self.fuentes.get(chunk["fuente_id"], {}),
                    bm25=float(bm[i]),
                    coseno=float(cos[i]) if cos is not None else None,
                    puntaje=ranks[i],
                )
            )
            if len(hits) >= top_k:
                break

        return SearchResult(
            hits=hits,
            max_bm25=float(bm.max()) if len(bm) else 0.0,
            max_coseno=float(cos.max()) if cos is not None and len(cos) else None,
            uso_vectores=cos is not None,
        )

    def mentioned_sources(self, query: str) -> set[str]:
        q = normalize(query)
        return {fid for fid, aliases in self.aliases.items() if any(a and a in q for a in aliases)}

    def _boosts(self, query: str) -> np.ndarray:
        """Refuerza las fuentes nombradas en la pregunta y los artículos pedidos por número."""
        boost = np.zeros(len(self.chunks), dtype=np.float32)
        sources = self.mentioned_sources(query)
        articles = {
            m.group(1) + (f" {m.group(2).lower()}" if m.group(2) else "")
            for m in ARTICLE_QUERY_RE.finditer(normalize(query))
        }
        if not sources and not articles:
            return boost
        for i, chunk in enumerate(self.chunks):
            in_source = chunk["fuente_id"] in sources
            if in_source:
                boost[i] += SOURCE_BOOST
            if chunk.get("articulo") in articles and (in_source or not sources):
                boost[i] += ARTICLE_BOOST
        return boost


def load_fuentes(path: Path) -> dict[str, dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {f["id"]: f for f in data["fuentes"]}
