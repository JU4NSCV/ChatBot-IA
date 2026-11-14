"""Normalización y tokenización en español para la búsqueda por palabras clave (BM25)."""

from __future__ import annotations

import re
import unicodedata

STOPWORDS = set(
    """
    a al algo algun alguna algunas alguno algunos ante antes aquel aquella aquellas aquellos aqui
    asi aun cada como con contra cual cuales cuando de del desde donde dos e el ella ellas ello
    ellos en entre era eran es esa esas ese eso esos esta estan estas este esto estos fue fueron
    ha han hasta hay la las le les lo los mas me mi mis mucho muy nada ni no nos o os otra otras
    otro otros para pero poco por porque que quien quienes se sea segun ser si sido sin sobre
    solo son su sus tal tambien tan te tiene tienen todo todos tu tus u un una unas uno unos
    usted ustedes y ya yo debo debe deben puedo puede pueden hacer hago dice dicen decir cual
    cuales
    """.split()
)
SYNONYMS = {"art": "articulo", "arts": "articulo", "inc": "inciso", "ia": "inteligencia artificial"}
STEM_LEN = 6  # truncar palabras largas: «transparencia» y «transparentar» → «transp»


def normalize(text: str) -> str:
    """Minúsculas y sin tildes."""
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in re.findall(r"[a-z0-9ñ]+", normalize(text)):
        for word in SYNONYMS.get(raw, raw).split():
            if word in STOPWORDS or (len(word) == 1 and not word.isdigit()):
                continue
            tokens.append(word[:STEM_LEN] if not word.isdigit() else word)
    return tokens


def terms(text: str) -> list[str]:
    """Términos para BM25: palabras + pares consecutivos (premia frases como «secreto fuentes»)."""
    words = tokenize(text)
    return words + [f"{a}_{b}" for a, b in zip(words, words[1:])]
