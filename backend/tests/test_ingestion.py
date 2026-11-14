from dilemabot.core.config import DOCS_DIR
from dilemabot.ingestion.segment import segment


def _chunks(fuentes, fid):
    f = fuentes[fid]
    return segment((DOCS_DIR / f["archivo"]).read_text(encoding="utf-8"), fid, f["titulo_corto"])


def _articles(chunks):
    return {c.articulo for c in chunks if c.articulo}


def test_constitucion_por_articulo(fuentes):
    chunks = _chunks(fuentes, "ar-constitucion")
    arts = _articles(chunks)
    assert {"14", "14 bis", "17", "32", "43", "75"} <= arts
    art43 = next(c for c in chunks if c.articulo == "43")
    assert art43.cita == "Constitución Nacional (Argentina), art. 43"
    assert "fuentes de información periodística" in art43.texto


def test_formatos_de_articulo_de_cada_ley(fuentes):
    assert {"10", "28", "29"} <= _articles(_chunks(fuentes, "ar-ley-11723"))  # «### Artículo 10»
    assert {"1", "20"} <= _articles(_chunks(fuentes, "ar-ley-25326"))  # «### ARTICULO 1° —»
    assert {"5", "49"} <= _articles(_chunks(fuentes, "ar-ley-12908"))  # «Art. 5º)–»
    assert {"45", "89"} <= _articles(_chunks(fuentes, "ar-ley-26522"))  # «**ARTICULO 45**»


def test_articulos_de_decretos_llevan_el_decreto_en_la_cita(fuentes):
    chunks = _chunks(fuentes, "ar-ley-26522")
    reglamentarios = [c for c in chunks if c.articulo and "Decreto 1225/2010" in c.cita]
    assert reglamentarios
    assert all(", art. " in c.cita for c in reglamentarios)


def test_descarta_articulos_sin_reglamentar(fuentes):
    chunks = _chunks(fuentes, "ar-ley-26522")
    assert not any(c.texto.rstrip(".").endswith("Sin reglamentar") and len(c.texto) < 40 for c in chunks)


def test_secciones_numeradas_de_la_guia(fuentes):
    citas = {c.cita for c in _chunks(fuentes, "adepa-guia-ia")}
    assert "Guía ADEPA para el uso de la IA, punto 02" in citas


def test_fragmentos_acotados_e_ids_unicos(index):
    assert all(len(c["texto"]) <= 1800 for c in index.chunks)
    ids = [c["id"] for c in index.chunks]
    assert len(ids) == len(set(ids))
