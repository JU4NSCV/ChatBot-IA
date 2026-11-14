"""Capa de recuperación: encuentra en el corpus los fragmentos que respaldan una respuesta."""

from .index import CHUNKS_FILE, EMBEDDINGS_FILE, META_FILE, Hit, Index, SearchResult, load_fuentes
from .text import normalize, terms, tokenize

__all__ = [
    "CHUNKS_FILE",
    "EMBEDDINGS_FILE",
    "META_FILE",
    "Hit",
    "Index",
    "SearchResult",
    "load_fuentes",
    "normalize",
    "terms",
    "tokenize",
]
