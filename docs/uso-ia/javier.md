# Declaración de uso de IA — Javier Ovelar

## Registro

| Integrante | Herramienta | Para qué la usó | Grado de intervención | Evidencia |
|---|---|---|---|---|
| Javier Ovelar | Claude Code (Anthropic), modelo Opus 5.5 | **Diagnóstico:** ubicar mi parte en el plan de trabajo, proponer los casos de prueba, armar la estructura de los documentos, resolver dudas sobre los resultados y revisar lo que redacté | **Medio.** La IA propuso los casos de prueba con el resultado esperado, armó las plantillas de los documentos (ubicación, evidencia y casos de cada hallazgo) y revisó mis correcciones. Yo ejecuté y capturé los casos, evalué cada resultado, redacté el análisis de la ficha (impacto, riesgo, prioridad y principio), el criterio de priorización y las conclusiones, y corregí los documentos a partir de la revisión | `anexo/ia/javier_claude_01_diagnostico.pdf` |

## Detalle

Usé Claude Code para el diagnóstico de mi parte: cambio de estado y asignación de responsable (líneas 251–318 de `main.py`). La IA identificó mi alcance a partir del plan de trabajo del grupo, propuso 19 casos de prueba en un orden que permite ejecutarlos sobre una base limpia, y antes de dármelos los corrió sobre una copia aislada del sistema para indicar el resultado esperado de cada uno.

Ejecuté y capturé los 19 casos desde Swagger UI, confirmé los resultados y evalué cada uno según el criterio de códigos HTTP del grupo. Durante la ejecución consulté dudas puntuales: qué código correspondía a un responsable inactivo (caso 8) y por qué se aceptaba un rechazo con motivo nulo (caso 15). La IA me explicó que la validación de la línea 270 no contempla `null`.

La IA armó la estructura de la ficha de smells con la ubicación, la evidencia y los casos de cada hallazgo. El impacto, el riesgo, la prioridad y el principio de cada uno, el criterio de priorización, el orden de resolución, la propuesta para la tabla grupal y las conclusiones de calidad externa los redacté yo. Después la IA revisó la tabla y la ficha, marcó inconsistencias (códigos HTTP mal asignados, justificaciones poco precisas y nombres de capturas que no coincidían) y las corregí.

También usé la IA para convertir la conversación exportada en el PDF del anexo.
