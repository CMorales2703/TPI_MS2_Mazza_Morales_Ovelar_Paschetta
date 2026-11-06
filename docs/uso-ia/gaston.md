# Declaración de uso de IA — Gaston Paschetta

## Registro

| Integrante | Herramienta | Para qué la usó | Grado de intervención | Evidencia |
|---|---|---|---|---|
| Gaston Paschetta | Claude Code | **Coordinación:** armado de la plantilla de la ficha de smells y de la tabla de deuda técnica (PR #6), a partir de la ficha de Cristian y del plan de trabajo | **Alto.** La IA redactó las dos plantillas. Yo definí qué campos sumar y las revisé antes del PR | [`anexo/ia/gaston_registro_ia.md`](../../anexo/ia/gaston_registro_ia.md), pedido 1 (la conversación no se conservó) |
| Gaston Paschetta | Claude Code (Anthropic) | **Diagnóstico:** proponer los casos de prueba de `POST /solicitudes` con el resultado esperado y armar el borrador de la ficha de smells y de la tabla de resultados | **Alto.** La IA propuso los casos y los corrió sobre una copia aislada del sistema para anticipar el resultado. Ejecuté y capturé los casos desde Swagger UI y confirmé los resultados.
| Gaston Paschetta | Claude Code (Anthropic) | **Pruebas (Fase 2):** pasar a tests automáticos los casos de `POST /solicitudes` que ejecuté en la Fase 1, correr la suite, redactar el documento de resultados y subir la rama | **Alto.** La IA escribió los 17 tests con el criterio de línea de base y el `conftest.py` del grupo, redactó `docs/pruebas/gaston_resultados_fase2.md` y, en mi PC, ejecutó la suite completa, sacó la captura e hizo el commit y el push. Los casos son los que ejecuté en la Fase 1. Yo abrí el PR | [`anexo/ia/gaston_registro_ia.md`](../../anexo/ia/gaston_registro_ia.md), pedido 3 |

## Detalle

Para el diagnóstico, la IA propuso 17 casos de prueba en un orden que permite ejecutarlos sobre una base limpia y los corrió antes sobre una copia aislada del sistema para indicar el resultado esperado. Ejecuté y capturé los casos desde Swagger UI y confirmé que los resultados coincidían.

Para las pruebas, le pedí a la IA que pasara a tests automáticos los 17 casos que ejecuté en la Fase 1. La IA escribió `tests/test_solicitudes.py` con el criterio de línea de base del grupo (cada test fija lo que el sistema hace hoy y deja el comportamiento esperado en un comentario), lo corrió junto con el resto de la suite y redactó `docs/pruebas/gaston_resultados_fase2.md`. Después, en mi PC, creó la rama `test/gaston` desde `dev`, ejecutó la suite completa con `.\run.bat test` (64 tests en verde), sacó la captura e hizo el commit y el push. Yo abrí el PR.
