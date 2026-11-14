"""Genera el índice del corpus.

Uso:
    dilemabot-ingest                 # fragmentos + embeddings (si Ollama está disponible)
    dilemabot-ingest --sin-vectores  # solo fragmentos (búsqueda BM25)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time

import numpy as np

from ..core.config import DOCS_DIR, FUENTES_PATH, load_settings
from ..llm import LLMError, get_provider
from ..retrieval import CHUNKS_FILE, EMBEDDINGS_FILE, META_FILE, load_fuentes
from .segment import segment

BATCH = 16


async def _embed_all(provider, texts: list[str]) -> np.ndarray:
    vectors: list[list[float]] = []
    for start in range(0, len(texts), BATCH):
        vectors.extend(await provider.embed(texts[start : start + BATCH]))
        print(f"\r  embeddings {min(start + BATCH, len(texts))}/{len(texts)}", end="", flush=True)
    print()
    arr = np.asarray(vectors, dtype=np.float32)
    arr /= np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    return arr


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dilemabot-ingest", description="Genera el índice de DilemaBot")
    parser.add_argument("--sin-vectores", action="store_true", help="no calcular embeddings")
    args = parser.parse_args(argv)

    settings = load_settings()
    fuentes = load_fuentes(FUENTES_PATH)
    chunks: list[dict] = []
    for fuente in fuentes.values():
        path = DOCS_DIR / fuente["archivo"]
        if not path.is_file():
            print(f"  ! falta {path}, se omite {fuente['id']}", file=sys.stderr)
            continue
        found = segment(path.read_text(encoding="utf-8"), fuente["id"], fuente["titulo_corto"])
        chunks.extend(c.to_dict() for c in found)
        print(f"  {fuente['id']:24} {len(found):4} fragmentos")

    out = settings.index_dir
    out.mkdir(parents=True, exist_ok=True)
    with (out / CHUNKS_FILE).open("w", encoding="utf-8") as fh:
        for chunk in chunks:
            fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"Total: {len(chunks)} fragmentos → {out / CHUNKS_FILE}")

    meta = {"generado": time.strftime("%Y-%m-%dT%H:%M:%S"), "fragmentos": len(chunks)}
    emb_path = out / EMBEDDINGS_FILE
    if args.sin_vectores:
        emb_path.unlink(missing_ok=True)
        print("Sin vectores: la búsqueda usará solo BM25.")
    else:
        provider = get_provider(settings)
        texts = [f"{c['cita']}\n{c['texto']}" for c in chunks]
        print(f"Calculando embeddings con {settings.ollama_embed_model}…")
        t0 = time.time()
        try:
            np.save(emb_path, asyncio.run(_embed_all(provider, texts)))
            meta["embed_model"] = settings.ollama_embed_model
            print(f"Embeddings listos en {time.time() - t0:.0f} s → {emb_path}")
        except LLMError as exc:
            emb_path.unlink(missing_ok=True)
            print(f"\n  ! No se calcularon embeddings: {exc}\n  La búsqueda usará solo BM25.")
    (out / META_FILE).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
