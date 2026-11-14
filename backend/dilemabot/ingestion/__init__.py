"""Capa de ingesta: convierte el corpus en fragmentos citables y genera el índice."""

from .segment import Chunk, segment

__all__ = ["Chunk", "segment"]
