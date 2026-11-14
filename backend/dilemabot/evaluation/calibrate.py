"""Mide los puntajes de búsqueda para preguntas dentro y fuera del dominio y sugiere umbrales.

Uso:  dilemabot-calibrar

Requiere el índice con vectores (dilemabot-ingest) y Ollama en ejecución.
Repetir cada vez que cambie el corpus o el modelo de embeddings.
"""

from __future__ import annotations

import asyncio

from ..chat import has_evidence
from ..core.config import FUENTES_PATH, load_settings
from ..llm import get_provider
from ..retrieval import Index, SearchResult

DENTRO = [
    "¿Debo avisar a la audiencia si una nota se redactó con IA?",
    "¿Qué protege la Constitución argentina sobre el secreto de las fuentes periodísticas?",
    "¿Qué dice el artículo 20 de la ley 25.326?",
    "¿Cuántas palabras puedo citar de una obra con fines didácticos?",
    "¿Puede un algoritmo decidir sobre una persona con un perfil automatizado?",
    "límite de licencias de radio y concentración de medios",
    "¿Qué es el principio de pluralismo?",
    "¿Qué es la transparencia en el periodismo?",
    "¿Quién es dueño de una nota firmada por un colaborador?",
    "¿Se puede usar IA para entrenar modelos con contenido de los medios?",
    "¿Un periodista puede perder su carnet por sus opiniones?",
    "¿Cómo deben supervisar los humanos el contenido generado por IA en una redacción?",
    "¿Es ético publicar la foto de una persona sin su consentimiento?",
    "¿Qué riesgos tiene usar IA generativa para redactar noticias?",
    "¿Qué hacen los medios argentinos para capacitar a sus periodistas en IA?",
]

FUERA = [
    "receta de pizza napolitana",
    "¿Quién ganó el mundial de fútbol 2022?",
    "¿Cómo configuro mi router wifi?",
    "dame consejos para bajar de peso",
    "¿Cuál es la capital de Francia?",
    "Escribe un poema sobre el mar",
    "¿Cómo se resuelve una ecuación de segundo grado?",
    "¿Qué tiempo hará mañana en Loja?",
    "Recomiéndame una película de terror",
    "¿Cuánto cuesta un pasaje a Madrid?",
]


async def medir(index: Index, provider, preguntas: list[str]) -> list[tuple[float, float, str]]:
    filas = []
    for q in preguntas:
        vec = (await provider.embed([q]))[0]
        r = index.search(q, query_vector=vec)
        filas.append((r.max_bm25, r.max_coseno or 0.0, q))
    return filas


def imprimir(titulo: str, filas) -> None:
    print(f"\n{titulo}")
    for bm, cos, q in sorted(filas, key=lambda f: f[1]):
        print(f"  bm25={bm:6.2f}  coseno={cos:.3f}  {q}")


async def main() -> None:
    settings = load_settings()
    index = Index.load(settings.index_dir, FUENTES_PATH)
    if index.embeddings is None:
        raise SystemExit("El índice no tiene vectores. Ejecute: dilemabot-ingest")
    provider = get_provider(settings)

    dentro = await medir(index, provider, DENTRO)
    fuera = await medir(index, provider, FUERA)
    imprimir("DENTRO DEL DOMINIO", dentro)
    imprimir("FUERA DEL DOMINIO", fuera)

    for nombre, i in (("BM25", 0), ("coseno", 1)):
        min_dentro = min(f[i] for f in dentro)
        max_fuera = max(f[i] for f in fuera)
        estado = "separa" if min_dentro > max_fuera else "SE SOLAPAN"
        print(f"\n{nombre}: mínimo dentro={min_dentro:.3f} · máximo fuera={max_fuera:.3f} → {estado}")

    s = settings

    def acepta(bm: float, cos: float) -> bool:  # misma regla que usa el chat
        return has_evidence(SearchResult([None], bm, cos, True), s)

    rechazos = [q for bm, cos, q in dentro if not acepta(bm, cos)]
    falsos = [q for bm, cos, q in fuera if acepta(bm, cos)]
    print(
        f"\nCon los umbrales actuales (coseno ≥ {s.evidence_min_cosine}, o BM25 ≥ "
        f"{s.evidence_min_bm25} y coseno ≥ {s.evidence_min_cosine_bm25}):"
    )
    print(f"  preguntas válidas rechazadas: {len(rechazos)} {rechazos}")
    print(f"  preguntas ajenas aceptadas:   {len(falsos)} {falsos}")


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
