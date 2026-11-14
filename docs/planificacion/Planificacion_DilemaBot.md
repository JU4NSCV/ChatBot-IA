# Planificación DilemaBot — estado por fase y preguntas abiertas

> Documento vivo. Se responde una fase a la vez; las respuestas se anotan debajo de cada pregunta (`**R:**`).
> Fuente de las fases: [README](../../README.md) · [Propuesta](../reto/Propuesta_Reto_DilemaBot_2026.md) · [Resumen del corpus](../../knowledge/resumen_documentos.md)

## Qué está claro

| Tema | Estado |
|---|---|
| Problema y pregunta del reto | ✅ Definidos |
| Capacidades A (conceptos), B (casos), C (analizar dilemas) | ✅ Definidas |
| 7 principios: veracidad, transparencia, autoría, privacidad, independencia, pluralismo, responsabilidad | ✅ Definidos (pero no mapeados al corpus) |
| Ruta de 7 fases / 16 semanas y producto de cada fase | ✅ Definida |
| Rúbrica de evaluación con pesos (F6) | ✅ Definida (sin indicadores detallados) |
| Criterios mínimos (fuentes, fuera de dominio, «no lo sé», interfaz web, pruebas reproducibles) | ✅ Definidos |
| Corpus normativo (7 documentos en Markdown + PDF) | ✅ Disponible, ~8.700 líneas |

## Vacíos detectados

1. **No hay banco de casos.** La capacidad B («explorar casos») y buena parte de la C dependen de casos de dilemas éticos, pero el corpus solo tiene normas y los dos documentos de ADEPA. El único caso explícito es «AMI vs Meta» y la demanda de Perfil contra OpenAI/Microsoft.
2. **Los principios no están mapeados al corpus.** Términos como *pluralismo*, *independencia* o *autoría* casi no aparecen en los documentos de IA; habrá que construir una taxonomía principio ↔ artículo/recomendación.
3. **Corpus 100 % argentino** para un reto de la UTPL (Ecuador) con alcance latinoamericano.
4. **Fuentes citadas pero ausentes:** Ley 26.032, Ley 27.078, Disposición 2/2023, Res. 161/2023 AAIP, política de IA de Chequeado y declaración de Todo Jujuy (corresponden a los números 2, 5, 8, 9, 10 que faltan en la carpeta).
5. **Vigencia no verificada:** ENACOM reemplazó a la AFSCA (DNU 267/2015) y el DNU 70/2023 afecta al Estatuto del Periodista.
6. **Volumen desbalanceado:** la Ley 26.522 ocupa ~5.000 de las ~8.700 líneas; puede dominar la recuperación (RAG) si no se pondera.
7. **Calendario:** el README dice oct 2026 – ene 2027 y la propuesta oct 2026 – feb 2027. Hoy (11-nov-2026) estaríamos cerca de la semana 5–6 si se empezó a inicios de octubre.

---

## F1 · Comprender el reto (S1–2) — Producto: ficha de comprensión del reto

- **P1.1** ¿En qué semana real estamos y cuál es la fecha de inicio de S1? ¿La entrega final es en enero o febrero de 2027?
  **R:** Actualmente estamos en la semana 6 se empezo desde Octubre y se debe entregar en febrero finales de las 16 semanas
- **P1.2** ¿Somos un equipo entre varios que compiten? ¿Cuántos integrantes y qué roles/habilidades hay (backend, frontend, datos/IA, documentación)?
  **R:** Si somo un equipo compitiendo contra otros, actualmente somos 4 integrantes, no se han asignado roles por el momento
- **P1.3** ¿Ya se entregó la ficha de comprensión del reto o hay que redactarla? ¿Existe una plantilla?
  **R:** Aun no se ah entregado nada, tenemos que tener listo los documentos, avances, documentos, etc. para una primera revicion
- **P1.4** Usuario principal del MVP: ¿estudiantes, periodistas o docentes? (cambia el tono y la profundidad de las respuestas)
  **R:** Va a estar para estudiantes, docentes y periodistas, el fin es dar a conocer la informacion a quien este interesado, que puedan realizar preguntas y recibir asesoramiento, va a llevar un tono educativo.
- **P1.5** ¿El dominio se limita a Argentina o el bot debe hablar de ética periodística en Latinoamérica en general (avisando que su evidencia es argentina)?
  **R:** Se ah planteado que sea para toda latinoamerica, que lo puedan entender y seguir sin que sea exclusivamente de argentina u Ecuador su dominio,

## F2 · Requerimientos y base de conocimiento (S3–4) — Producto: documento de requerimientos + BC v1

- **P2.1** ¿El equipo investigador entregará un **banco de casos** de dilemas éticos? ¿Cuándo? Si no, ¿podemos construirlos nosotros y quién los valida?
  **R:** Por el momento aun no se han entregado el banco de casos asi que podemos gestionar uno provicional hasta que llegue la informacion, esta es validada por quienes nos dan los caos para analizar.
- **P2.2** ¿Llegarán más documentos (las 6 fuentes faltantes, normativa ecuatoriana como la Ley Orgánica de Comunicación o la LOPDP, códigos deontológicos como FIP o FELAFACS)? ¿O el corpus está cerrado?
  **R:** Por el momento nos han proporcionado esos documentos de leyes y normativas, asi que quiero agregues las normas/regulaciones u estandares vigentes en Ecuador para poder sustendar y defendernos de cualquier tipo, tener el software funcional en base a normativas u estandares u ISOS es lo primordial
- **P2.3** ¿Se permite agregar fuentes por nuestra cuenta o solo el «corpus validado»?
  **R:** Por el momento se tomara esa informacion dada, en caso de necesitar mas funtes se puede aumentar siempre y cuando sea especificado que se ah agregado en base a que necesidad.
- **P2.4** ¿El equipo de Comunicación validará la taxonomía de principios y las preguntas frecuentes, o la definimos nosotros?
  **R:** Por el momento en la espera de que nos proporcionen mas informacion para el chatbot seran generadas por nosotros pero luego se deben validar con la informacion que nos den y corregir en caso de ser necesario
- **P2.5** Formato de la base de conocimiento: ¿hay preferencia (JSON/YAML por fichas, base de datos, solo documentos segmentados)?
  **R:** No existe preferencia se usara la mas optima posible
- **P2.6** ¿Cómo tratamos los textos posiblemente derogados o desactualizados: excluirlos, marcarlos con advertencia de vigencia, o usarlos tal cual?
  **R:** no tengo claro aun esta parte

## F3 · Arquitectura y diseño conversacional (S5–6) — Producto: arquitectura técnica + prototipo de interfaz

- **P3.1** ¿Hay presupuesto para APIs de modelos (Claude, OpenAI, etc.) o hay que usar modelos locales/gratuitos (Ollama, Llama, Mistral)?
  **R:** Por el momento para iniciar modelos locales gratuitos pero con la posibilidad de enlazar claude u otro mcp
- **P3.2** ¿Stack preferido o conocido por el equipo (Python/FastAPI, Node, React, Streamlit…)?
  **R:** De preferencia python
- **P3.3** ¿Dónde se ejecutará la demo: local, servidor de la UTPL o servicio gratuito en la nube? ¿Debe estar accesible por URL pública?
  **R:** Por el momento de forma local, para despues en caso de quedar como proyecto seleccionano migrar a los servicios de la UTPL o nube.
- **P3.4** Formato de cita deseado: ¿documento + artículo/sección, o también fragmento textual y enlace al PDF?
  **R:** documento + artículo/sección y enlace
- **P3.5** ¿Hay alguna restricción institucional sobre enviar datos a servicios externos o guardar conversaciones?
  **R:** Por el momento no se a mostrado nada o nos han establecido algo en concreto

## F4 · Desarrollo del MVP (S7–11) — Producto: versión alfa

- **P4.1** ¿Cuántos turnos de memoria conversacional se espera como «interacción básica de varios turnos»?
  **R:** no entiendo aun esta pregunta
- **P4.2** ¿Se requiere autenticación de usuarios o el bot es abierto?
  **R:** Por el moemnto el bot va a ser abierto, no se a mencionado de manejo de sesiones.
- **P4.3** ¿Hay revisiones o entregas intermedias con los docentes durante S7–11?
  **R:** Si hay revision se prepara un documento .md de resumen de lo realizado. A su vez cada que haya reunion sera comunicado un dia anterior
- **P4.4** ¿Idioma solo español?
  **R:** Si solo espanol

## F5 · Pruebas y control de respuestas (S12–13) — Producto: versión beta + informe de pruebas

- **P5.1** El «conjunto común de preguntas de prueba», ¿lo arma cada equipo o es compartido entre todos los equipos?
  **R:** Lo arma cada equipo
- **P5.2** ¿Quién califica la calidad de las respuestas: docentes, expertos de Comunicación, evaluación automática (p. ej. RAGAS / LLM como juez) o una combinación?
  **R:** Docentes
- **P5.3** ¿Hay métricas mínimas esperadas (tasa de alucinación, precisión de recuperación, tiempo de respuesta)?
  **R:** No existen exactamente

## F6 · Evaluación comparativa (S14) — Producto: matriz comparativa

- **P6.1** ¿Existen indicadores detallados por criterio de la rúbrica (p. ej., qué significa 20/20 en «funcionamiento técnico»)?
  **R:** no lo tomes en cuenta por ahora
- **P6.2** ¿Participan usuarios reales (estudiantes/periodistas) en la evaluación de experiencia de usuario?
  **R:** Si, para la prueba final es con estudiantes y preiodistas

## F7 · Demo final y selección (S15–16) — Producto: prototipo final, documentación, presentación

- **P7.1** Formato y duración de la demo; ¿presencial o virtual?
  **R:** va a ser presencial la prueba del producto
- **P7.2** ¿Licencia del código y propiedad del prototipo (equipo, UTPL, proyecto de investigación)?
  **R:** Del equipo
- **P7.3** ¿Formato esperado del manual de uso y la documentación técnica (Markdown en el repo, PDF, wiki)?
  **R:** Markdown en el repo