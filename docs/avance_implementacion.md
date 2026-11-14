# Avance de implementación — DilemaBot

> 13-nov-2026 · Semana 6 · Basado en el [Plan de desarrollo](planificacion/Plan_Desarrollo_DilemaBot.md)

## Qué funciona

| Plan | Estado | Detalle |
|---|---|---|
| Esqueleto FastAPI (S6–S7) | ✅ | `GET /api/salud`, `GET /api/fuentes`, `POST /api/chat` con respuesta en streaming (SSE) |
| Proveedor LLM intercambiable | ✅ | Interfaz `LLMProvider`; implementaciones Ollama (chat + embeddings) y Claude (chat con el SDK `anthropic`; embeddings vía Ollama). Se elige con `LLM_PROVIDER` |
| Ingesta y segmentación (S8) | ✅ | 8 documentos → 1.172 fragmentos. Cada artículo es un fragmento; los artículos de decretos reglamentarios llevan el decreto en la cita. Se descartan los «Sin reglamentar» |
| Registro de fuentes | ✅ | `knowledge/fuentes.yaml` con país, enlace, PDF, vigencia, nota de vigencia y motivo de inclusión |
| Búsqueda híbrida (S8) | ✅ | BM25 con pares de palabras + vectores `bge-m3` (fusión RRF). Refuerza la fuente y el artículo nombrados («art. 43 de la Constitución»). Máximo 2 fragmentos por fuente para que la Ley 26.522 no domine |
| Respuestas con citas (S8) | ✅ | El prompt numera los fragmentos y obliga a citar `[n]` |
| «No lo sé» (S9, adelantado) | ✅ | Si la mejor coincidencia no supera el umbral, responde «No lo sé» con sugerencias **sin llamar al modelo** |
| Verificación de citas (S9, adelantado) | ✅ | Las citas a fragmentos inexistentes se eliminan y se avisa; si no hay citas, se advierte |
| Advertencias de vigencia (S10, adelantado) | ✅ | El prompt incluye la nota de vigencia; la interfaz marca «Modificada» / «Vigencia por verificar» |
| Memoria conversacional (S10, parcial) | 🟡 | Se envían los últimos 6 turnos. Las preguntas de seguimiento («¿y eso?») se buscan junto a la anterior; falta la reescritura con el modelo |
| Chat web básico (S8) | ✅ | Tema oscuro según `docs/diseno/DESIGN.md`, citas clicables, fuentes con enlace original y PDF |
| Pruebas automáticas | ✅ | 36 pruebas con pytest (segmentación, búsqueda, flujo del chat con un LLM simulado, API) |

## Decisiones tomadas al implementar

- **Embeddings en NumPy en lugar de ChromaDB.** Con ~1.200 fragmentos, un producto matricial tarda menos de 1 ms y evita una dependencia. Si el corpus crece a decenas de miles de fragmentos, se migra a ChromaDB o Qdrant sin cambiar la interfaz `Index.search`.
- **Modelo por defecto `qwen2.5:7b`** y embeddings `bge-m3`, ambos configurables en `.env`. La comparación de modelos (Qwen, Llama, Gemma) sigue pendiente para S7.
- **Regla de evidencia** (calibrada con `bge-m3` real, `dilemabot-calibrar`): hay evidencia si el coseno ≥ 0,55, o si BM25 ≥ 7,0 y coseno ≥ 0,45. Con 15 preguntas del dominio y 10 ajenas: 0 rechazos indebidos y 0 aceptaciones indebidas. BM25 sola no basta: «¿Cómo se resuelve una ecuación de segundo grado?» obtiene 15,6 por la palabra «grado» en la Ley 26.522. El margen del coseno es estrecho (mínimo válido 0,522 frente a 0,509 de «router wifi»); hay que ampliar el conjunto de preguntas en S12.
- **Ollama en Docker** (`docker-compose.yml`). En Intel Core Ultra, Ollama solo usaba 2 hilos (núcleos P); `OLLAMA_NUM_THREAD=10` aprovecha también los núcleos E.
- **4 fragmentos por respuesta** (antes 6). Medido con `qwen2.5:7b` en CPU (Core Ultra 7 155U): primer token en ~40 s y respuesta completa en ~52 s, frente a ~73 s y ~84 s con 6. Casi todo el tiempo se va en leer el prompt, no en escribir.
- **Privacidad:** el servidor registra solo métricas (longitud, puntajes, tiempos), nunca el texto de las preguntas. La conversación vive en el navegador.

## Pendiente

1. **Latencia:** ~40 s hasta el primer token sigue siendo mucho para la demo. Opciones: comparar `qwen2.5:3b` (S7), fragmentos más cortos, o un proveedor externo para la demo.
2. **Calidad de las respuestas:** las primeras pruebas con `qwen2.5:7b` citan bien (p. ej. art. 29 de la Ley 11.723 para notas firmadas por colaboradores), pero falta el banco de 80–100 preguntas de S12.
3. Clasificador de intención A/B/C (S9), banco de casos y fichas de principios (BC v1), reescritura de preguntas de seguimiento (S10), panel de evidencia lateral (S10), landing con «Cómo funciona» (S11).
4. Las fuentes web de Google Fonts se cargan por CDN; el plan pide servirlas localmente antes de la demo.
