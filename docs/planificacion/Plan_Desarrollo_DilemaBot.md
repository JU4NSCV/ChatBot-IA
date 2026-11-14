# Plan de desarrollo — DilemaBot

> Versión 0.1 · 13-nov-2026 · Semana 6 de 16
> Basado en: [README](../../README.md) · [Propuesta](../reto/Propuesta_Reto_DilemaBot_2026.md) · [Respuestas de planificación](Planificacion_DilemaBot.md) · [Diseño](../diseno/DESIGN.md)

## 1. Qué se entrega

Una **aplicación web local** con dos partes:

1. **Landing** (diseño de `docs/diseno/`): explica qué es DilemaBot, para qué sirve y **cómo funciona**.
2. **Chat integrado**: el usuario pregunta en español y el bot responde con un tono educativo, citando **documento + artículo/sección + enlace**, o dice «no lo sé» cuando no hay evidencia.

Además: repositorio, base de conocimiento, documentación técnica y manual de uso en Markdown, informe de pruebas y un resumen `.md` para cada revisión con docentes.

## 2. Situación actual y prioridad

Estamos en la **S6** sin entregas, así que F1, F2 y F3 se juntan en un **sprint de recuperación (S6–S7)** para llegar a la primera revisión con documentos y un esqueleto funcionando. El calendario de 16 semanas termina a **finales de febrero de 2027**, lo que implica pausas (vacaciones); se trabaja por número de semana, no por fecha.

## 3. Decisiones propuestas sobre los puntos abiertos

| Tema | Propuesta |
|---|---|
| **P2.6 Textos desactualizados** | No se excluyen. Cada fuente lleva un campo `vigencia` (`vigente`, `modificada`, `derogada`, `por_verificar`). Si el bot cita una fuente que no está vigente, añade una advertencia («Esta norma fue modificada por…»). Así se conserva el valor histórico y la respuesta sigue siendo honesta. |
| **P4.1 Memoria conversacional** | Es cuántos mensajes anteriores «recuerda» el bot dentro de una misma conversación. Ejemplo: el usuario pregunta por transparencia y luego «¿y qué dice la ley de Ecuador sobre *eso*?». Propuesta: recordar los **últimos 6 turnos** y reescribir la pregunta de seguimiento antes de buscar. Sin cuentas: la conversación vive solo en el navegador. |
| **Alcance latinoamericano** | El bot habla de ética periodística en general y cita normas de cada país; aclara de qué país es cada norma. Los principios (veracidad, transparencia…) son transversales. |
| **Fuentes nuevas (P2.3)** | Todas se registran en `knowledge/fuentes.yaml` con el campo `motivo_inclusion` y quién la agregó. |
| **Casos provisionales (P2.1)** | Se redactan casos marcados `estado: provisional`; cuando el equipo investigador entregue los suyos, se reemplazan o validan (`estado: validado`). El bot muestra esa etiqueta. |

## 4. Ampliación del corpus (Ecuador, regional y estándares)

Candidatas a incorporar en F2. **Todas deben verificarse en fuente oficial** (vigencia y última reforma) antes de entrar al corpus.

**Ecuador**
- Constitución de la República del Ecuador (2008): derechos de comunicación (arts. 16–20, 384), protección de datos (art. 66 num. 19).
- Ley Orgánica de Comunicación (2013, reformada en 2019).
- Ley Orgánica de Protección de Datos Personales (2021) y su Reglamento.
- Código Orgánico de la Economía Social de los Conocimientos (Código Ingenios): propiedad intelectual.
- Ley Orgánica de Transparencia y Acceso a la Información Pública (2023).
- Proyectos de ley sobre IA en la Asamblea: solo como contexto, marcados `por_verificar`; no hay ley de IA aprobada que conozcamos.

**Regional e internacional (ética)**
- Convención Americana sobre Derechos Humanos, art. 13, y Declaración de Principios sobre Libertad de Expresión de la CIDH.
- Recomendación de la UNESCO sobre la Ética de la IA (2021).
- Carta Mundial de Ética para Periodistas de la FIP (2019).
- Carta de París sobre IA y Periodismo (RSF, 2023).

**Estándares para el software** (respaldan los requerimientos no funcionales; no son corpus del bot)

| Estándar | Para qué lo usamos |
|---|---|
| ISO/IEC/IEEE 29148 | Estructura del documento de requerimientos |
| ISO/IEC 25010 y 25059 | Atributos de calidad del software y de sistemas con IA |
| ISO/IEC 23894 · NIST AI RMF + perfil de IA generativa | Análisis de riesgos (alucinación, sesgo, privacidad) |
| ISO/IEC 42001 | Referencia de gestión responsable de IA (sin certificación) |
| OWASP Top 10 para aplicaciones LLM | Seguridad: inyección de prompts, fuga de datos |
| WCAG 2.2 nivel AA | Accesibilidad de la interfaz |
| ISO 9241-210 | Diseño centrado en el usuario para las pruebas con estudiantes y periodistas |

## 5. Arquitectura propuesta

```
Navegador (landing + chat)
     │  HTTP / SSE (respuesta en streaming)
     ▼
FastAPI (Python)
 ├─ Clasificador de intención ─► A concepto · B caso · C dilema · fuera de dominio · saludo
 ├─ Reescritura de la pregunta con historial (últimos 6 turnos)
 ├─ Recuperación híbrida: BM25 (palabras exactas, «art. 43») + vectores (significado)
 ├─ Umbral de evidencia ─► si no hay fragmentos relevantes: «no lo sé» + sugerencias
 ├─ Generación con prompt que obliga a citar [id] de los fragmentos recuperados
 └─ Verificación: cada cita debe existir en lo recuperado; si no, se elimina o se responde «no lo sé»
     │
     ├─ Proveedor LLM intercambiable (variable de entorno)
     │    ├─ Ollama local (por defecto)
     │    └─ Claude u otra API (opcional)
     └─ Índice local: ChromaDB + metadatos
```

| Capa | Elección | Motivo |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Preferencia del equipo; streaming sencillo |
| LLM local | Ollama, comparando 2–3 modelos de 7–8B con buen español (familias Qwen, Llama, Gemma) | Gratis y local; se elige con una prueba corta en F3 según el hardware del equipo |
| LLM externo | Interfaz `LLMProvider` con implementación para Claude | Cambiar de proveedor sin tocar la lógica |
| Embeddings | Modelo multilingüe (p. ej. `bge-m3` o `multilingual-e5`) | Calidad en español |
| Búsqueda | Híbrida BM25 + vectores, opcional *reranker* | Las preguntas mezclan conceptos y números de artículo |
| Vector DB | ChromaDB embebida | Sin servidor extra; migrable a Qdrant o pgvector si se escala |
| Frontend | HTML del diseño + JavaScript sin framework, Tailwind compilado con su CLI independiente | Reutiliza `docs/diseno/code.html`; sin Node ni CDN en producción |
| Pruebas | pytest + script de evaluación con preguntas de prueba | Protocolo reproducible (criterio mínimo) |

**Equilibrio del corpus:** la Ley 26.522 es más de la mitad del texto. Se segmenta por artículo y se limita cuántos fragmentos de un mismo documento entran en cada respuesta, para que no domine.

## 6. Base de conocimiento

```
knowledge/
├─ fuentes.yaml        # registro: id, título, país, tipo, url, vigencia, motivo_inclusion
├─ principios.yaml     # 7 principios: definición, preguntas guía, artículos relacionados
├─ casos/*.yaml        # casos: situación, principios en tensión, normas, preguntas de análisis, estado
├─ faq.yaml            # preguntas frecuentes con respuesta y citas
├─ documentos/         # normas y guías en Markdown (lo que se ingiere)
├─ pdf/                # originales en PDF (se enlazan en las citas)
└─ indice/             # fragmentos por artículo/sección + embeddings (generados por dilemabot-ingest)
```

Cada fragmento lleva: `fuente_id`, `pais`, `articulo/seccion`, `url` (con ancla o página del PDF), `vigencia` y `principios[]`. Ese mapeo principio ↔ artículo resuelve que los principios no aparezcan literalmente en las normas.

**Meta de la versión 1 (S7):** 7 principios con fichas completas, **15 casos provisionales** (al menos 2 por principio), **30 preguntas frecuentes** y el corpus actual + Ecuador ingerido.

## 7. Diseño: qué se reutiliza y qué falta

Se reutilizan la paleta, la tipografía (Plus Jakarta Sans, Inter, JetBrains Mono), las secciones de la landing y la ventana de chat del hero.

Ajustes necesarios:
1. **Falta diseñar la pantalla de chat completa.** `DESIGN.md` describe un diseño de 7 columnas para la conversación y 5 para un **panel de evidencia** con las fuentes, pero `code.html` solo tiene la landing. Hay que diseñarla (pide el mismo tipo de prompt que se usó para la landing).
2. **Logo roto:** la imagen viene de un enlace externo de Google; se reemplaza por un SVG propio.
3. **Icono de usuario** en la barra: sugiere cuentas, y el bot es abierto. Se quita.
4. **«Cómo funciona»** hoy apunta a la sección «Con qué fin». Como el entregable debe mostrar *cómo trabaja* el bot, se propone una sección real con el flujo en 4 pasos: pregunta → busca en el corpus → responde citando → o dice «no lo sé».
5. **Tailwind por CDN** y la etiqueta «V1.4»: se reemplazan por CSS compilado y la versión real.
6. Verificar contraste (WCAG AA) del texto gris sobre fondos oscuros.

## 8. Roles sugeridos (4 integrantes)

| Rol | Responsabilidades |
|---|---|
| **R1 · Backend y RAG** | API, ingesta, recuperación, prompts, proveedores LLM |
| **R2 · Conocimiento** | Corpus, fuentes, principios, casos y FAQ; enlace con el equipo de Comunicación |
| **R3 · Frontend y UX** | Landing, chat, panel de evidencia, accesibilidad, pruebas con usuarios |
| **R4 · Calidad y gestión** | Preguntas de prueba, script de evaluación, informes, resúmenes de revisión, manual |

Todos revisan código de otros (pull requests) y rotan en la redacción de documentos.

## 9. Cronograma por fase

| Semanas | Fase | Tareas | Entregable |
|---|---|---|---|
| **S6–S7** | **Recuperación F1+F2+F3** | Ficha de comprensión del reto · Documento de requerimientos (ISO 29148) · `fuentes.yaml` y corpus de Ecuador · principios, 15 casos y 30 FAQ · Arquitectura · Diseño de la pantalla de chat · Esqueleto FastAPI + ingesta | Resumen de revisión 1, ficha, requerimientos, BC v1, arquitectura |
| **S8** | F4 · Iteración 1 | Ingesta y segmentación por artículo · Búsqueda híbrida · Respuestas con citas · Chat básico en la web | Responde conceptos (A) con citas |
| **S9** | F4 · Iteración 2 | Clasificador de intención · Casos (B) · Fuera de dominio y «no lo sé» · Verificación de citas | Responde A y B; rechaza fuera de dominio |
| **S10** | F4 · Iteración 3 | Análisis de dilemas (C) · Memoria de 6 turnos · Panel de evidencia · Advertencias de vigencia | Las tres capacidades funcionando |
| **S11** | F4 · Cierre | Proveedor Claude opcional · Landing completa con «Cómo funciona» · Manual v0 | **Versión alfa** + resumen de revisión |
| **S12** | F5 | 80–100 preguntas de prueba (directas, ambiguas, casos, fuera de dominio, inducción a error, inyección de prompts) · Registro de errores | Informe de pruebas v1 |
| **S13** | F5 | Correcciones · Prueba piloto con 3–5 usuarios | **Versión beta** + informe de pruebas |
| **S14** | F6 | Autoevaluación con la rúbrica · Ajustes finales | Matriz de autoevaluación |
| **S15–S16** | F7 | Documentación final · Ensayo de la demo presencial · Instalación probada en un equipo limpio | Prototipo final, documentación, presentación |

## 10. Cobertura de la rúbrica

| Criterio (peso) | Cómo lo cubrimos |
|---|---|
| Funcionamiento técnico (20 %) | Instalación con un comando, pruebas automáticas, demo ensayada |
| Calidad de respuestas (20 %) | Prompts por intención, tono educativo, revisión de casos con Comunicación |
| Recuperación y trazabilidad (15 %) | Búsqueda híbrida, citas verificadas, panel de evidencia con enlaces |
| Fuera de dominio (10 %) | Clasificador + umbral de evidencia + «no lo sé» con sugerencias |
| Experiencia de usuario (10 %) | Diseño de `docs/diseno/`, streaming, pruebas piloto, WCAG AA |
| Arquitectura y código (10 %) | Capas separadas, proveedor LLM intercambiable, tipado y linters |
| Seguridad (5 %) | OWASP LLM Top 10, sin datos personales en registros, aviso de privacidad |
| Documentación (5 %) | Markdown en el repo: arquitectura, manual, decisiones |
| Innovación (5 %) | Panel de evidencia, advertencias de vigencia, comparación entre países |

## 11. Riesgos

| Riesgo | Mitigación |
|---|---|
| Los casos oficiales llegan tarde | Casos provisionales con formato ya definido; reemplazo sin tocar código |
| El modelo local responde mal en español o es lento | Prueba de modelos en S7; Claude como alternativa configurable |
| El hardware del equipo no soporta modelos de 7–8B | Modelos más pequeños (3–4B) o API externa para la demo |
| Alucinaciones o citas inventadas | Verificación de citas y umbral de evidencia |
| Normas desactualizadas | Campo `vigencia` y advertencias |
| Atraso acumulado (S6 sin entregas) | Sprint de recuperación y esqueleto funcional en S7 |

## 12. Preguntas pendientes

1. ¿Qué hardware tiene el equipo (RAM y GPU)? Define el tamaño del modelo local.
2. ¿Cuándo es la primera revisión con docentes?
3. ¿Quién del equipo de Comunicación será el contacto para validar casos y FAQ?
4. ¿Se diseña la pantalla de chat en Stitch, igual que la landing, o la construimos directamente siguiendo `DESIGN.md`?
