"""Capa conversacional: orquesta búsqueda, control de evidencia, generación y verificación."""

from .guardrails import has_evidence, verify_citations
from .pipeline import Turn, answer

__all__ = ["Turn", "answer", "has_evidence", "verify_citations"]
