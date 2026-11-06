# Declaración de uso de IA — Javier Ovelar

## Registro

| Integrante | Herramienta | Para qué la usó | Grado de intervención | Evidencia |
|---|---|---|---|---|
| Javier Ovelar | Claude Code (Anthropic), modelo Opus 5.5 | **Diagnóstico:** ubicar mi parte en el plan de trabajo, proponer los casos de prueba, armar la estructura de los documentos, resolver dudas sobre los resultados y revisar lo que redacté | **Medio.** La IA propuso los casos de prueba con el resultado esperado, armó las plantillas de los documentos (ubicación, evidencia y casos de cada hallazgo) y revisó mis correcciones. Yo ejecuté y capturé los casos, evalué cada resultado, redacté el análisis de la ficha (impacto, riesgo, prioridad y principio), el criterio de priorización y las conclusiones, y corregí los documentos a partir de la revisión | `anexo/ia/javier_claude_01_diagnostico.pdf` |
| Javier Ovelar | Claude Code (Anthropic), modelo Opus 5.5 | **Pruebas (Fase 2):** revisión de los tests, propuesta de verificaciones y de un caso adicional, y redacción del documento de resultados | **Medio.** Yo escribí los 8 tests de asignación y cambio de estado. La IA los revisó contra el plan y los tests de Cristian, y propuso comprobar el efecto en la base en cada test y agregar el test del caso 4 (PEND → ASIG sin responsable). Apliqué las propuestas, ejecuté la suite y capturé el resultado. La IA redactó el documento de resultados | `anexo/ia/javier_claude_02_pruebas.pdf` |

## Detalle

Usé Claude Code para el diagnóstico de mi parte: cambio de estado y asignación de responsable (líneas 251–318 de `main.py`). La IA identificó mi alcance a partir del plan de trabajo del grupo, propuso 19 casos de prueba en un orden que permite ejecutarlos sobre una base limpia, y antes de dármelos los corrió sobre una copia aislada del sistema para indicar el resultado esperado de cada uno.

Ejecuté y capturé los 19 casos desde Swagger UI, confirmé los resultados y evalué cada uno según el criterio de códigos HTTP del grupo. Durante la ejecución consulté dudas puntuales: qué código correspondía a un responsable inactivo (caso 8) y por qué se aceptaba un rechazo con motivo nulo (caso 15). La IA me explicó que la validación de la línea 270 no contempla `null`.

La IA armó la estructura de la ficha de smells con la ubicación, la evidencia y los casos de cada hallazgo. El impacto, el riesgo, la prioridad y el principio de cada uno, el criterio de priorización, el orden de resolución, la propuesta para la tabla grupal y las conclusiones de calidad externa los redacté yo. Después la IA revisó la tabla y la ficha, marcó inconsistencias (códigos HTTP mal asignados, justificaciones poco precisas y nombres de capturas que no coincidían) y las corregí.

También usé la IA para convertir la conversación exportada en el PDF del anexo.

Para las pruebas de mi parte, escribí 8 tests sobre los casos de la Fase 1 y usé Claude Code para revisarlos. La IA los comparó con el plan de trabajo y con los tests de Cristian, y propuso comprobar en cada test el efecto en la base con `GET /solicitudes/{id}` y agregar el test del caso 4, que cubre la regla que voy a tocar con el Move Method (hallazgo 3). Antes de pasarme las propuestas, las probó en una copia aparte. Apliqué los cambios, ejecuté la suite completa (22 tests en verde) y saqué la captura. La IA redactó el documento de resultados (`docs/pruebas/javier_resultados_fase2.md`) y convirtió la conversación en el PDF del anexo.
