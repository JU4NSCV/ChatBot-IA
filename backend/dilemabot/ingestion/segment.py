"""Segmentación del corpus Markdown en fragmentos citables (por artículo o por sección)."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# Cubre los formatos del corpus: «ARTÍCULO 14 bis.-», «### Artículo 1º», «**ARTICULO 1º** —»,
# «### ARTICULO 1° — (Objeto).» y «Art. 1º)–».
ARTICLE_RE = re.compile(
    r"^(?:#{1,6}\s*)?(?:\*\*)?\s*(?:ART[IÍ]CULO|Art\.)\s*(\d+)\s*[°º]?\s*(bis|ter|quater)?\b",
    re.IGNORECASE,
)
NOISE_RE = re.compile(r"^(sin reglamentar|derogado|vetado|observado)\.?$", re.IGNORECASE)
CONTEXT_HEADING_RE = re.compile(r"^(decreto|anexo)\b", re.IGNORECASE)

MAX_CHARS = 1800
MIN_BODY_CHARS = 40


@dataclass
class Chunk:
    id: str
    fuente_id: str
    seccion: str  # ruta de encabezados, p. ej. «TITULO II › CAPITULO I»
    articulo: str | None  # «43», «14 bis» o None
    cita: str  # texto de la cita, p. ej. «Ley 26.522 (Argentina), art. 45»
    texto: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class _Block:
    path: list[str]
    articulo: str | None
    lines: list[str]


def _clean_heading(text: str) -> str:
    return re.sub(r"[*_`\\]", "", text).strip()


def _blocks(markdown: str) -> list[_Block]:
    levels: dict[int, str] = {}
    current = _Block(path=[], articulo=None, lines=[])
    blocks = [current]

    def path() -> list[str]:
        # El nivel 1 es el título del documento: no aporta a la ruta.
        return [levels[k] for k in sorted(levels) if k > 1]

    for line in markdown.splitlines():
        art = ARTICLE_RE.match(line)
        head = HEADING_RE.match(line)
        if art:
            numero = art.group(1) + (f" {art.group(2).lower()}" if art.group(2) else "")
            current = _Block(path=path(), articulo=numero, lines=[line.lstrip("# ").strip()])
            blocks.append(current)
        elif head:
            level = len(head.group(1))
            levels[level] = _clean_heading(head.group(2))
            for deeper in [k for k in levels if k > level]:
                del levels[deeper]
            current = _Block(path=path(), articulo=None, lines=[])
            blocks.append(current)
        else:
            current.lines.append(line)
    return blocks


def _body(block: _Block) -> str:
    text = "\n".join(block.lines).strip()
    return re.sub(r"\n{3,}", "\n\n", text)


def _is_noise(block: _Block, text: str) -> bool:
    if block.articulo:
        rest = ARTICLE_RE.sub("", text, count=1).lstrip(" *.-—–)°º:").strip()
        return len(rest) < 3 or bool(NOISE_RE.match(rest))
    return len(text) < MIN_BODY_CHARS


def _split_long(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """Agrupa párrafos hasta max_chars; si un párrafo es enorme, corta por líneas y oraciones."""
    if len(text) <= max_chars:
        return [text]
    pieces: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        if len(para) <= max_chars:
            pieces.append(para)
            continue
        for line in para.splitlines():
            if len(line) <= max_chars:
                pieces.append(line)
            else:
                pieces.extend(s for s in re.split(r"(?<=[.;:])\s+", line) if s)
    parts: list[str] = []
    buf = ""
    for piece in pieces:
        if buf and len(buf) + len(piece) + 2 > max_chars:
            parts.append(buf.strip())
            buf = ""
        buf = f"{buf}\n\n{piece}" if buf else piece
    if buf.strip():
        parts.append(buf.strip())
    return parts


def _cita(titulo_corto: str, block: _Block) -> str:
    if block.articulo:
        context = next((p for p in reversed(block.path) if CONTEXT_HEADING_RE.match(p)), None)
        prefix = f"{titulo_corto} — {context}" if context else titulo_corto
        return f"{prefix}, art. {block.articulo}"
    if block.path:
        last = block.path[-1]
        if last.isdigit():  # secciones numeradas, p. ej. las recomendaciones «01»…«08» de ADEPA
            return f"{titulo_corto}, punto {last}"
        return f"{titulo_corto}, «{last[:90]}»"
    return titulo_corto


def segment(markdown: str, fuente_id: str, titulo_corto: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    for block in _blocks(markdown):
        text = _body(block)
        if not text or _is_noise(block, text):
            continue
        parts = _split_long(text)
        for i, part in enumerate(parts):
            cita = _cita(titulo_corto, block)
            if len(parts) > 1:
                cita = f"{cita} (parte {i + 1}/{len(parts)})"
            chunks.append(
                Chunk(
                    id=f"{fuente_id}-{len(chunks):04d}",
                    fuente_id=fuente_id,
                    seccion=" › ".join(block.path),
                    articulo=block.articulo,
                    cita=cita,
                    texto=part,
                )
            )
    return chunks
