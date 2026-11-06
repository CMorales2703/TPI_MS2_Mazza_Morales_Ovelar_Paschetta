# Declaración de uso de IA — Gaston Paschetta

## Registro

| Integrante | Herramienta | Para qué la usó | Grado de intervención | Evidencia |
|---|---|---|---|---|
| Gaston Paschetta | Claude Code | **Coordinación:** armado de la plantilla de la ficha de smells y de la tabla de deuda técnica (PR #6), a partir de la ficha de Cristian y del plan de trabajo | **Alto.** La IA redactó las dos plantillas. Yo definí qué campos sumar y las revisé antes del PR | [`anexo/ia/gaston_registro_ia.md`](../../anexo/ia/gaston_registro_ia.md), pedido 1 (la conversación no se conservó) |
| Gaston Paschetta | Claude Code (Anthropic) | **Diagnóstico:** proponer los casos de prueba de `POST /solicitudes` con el resultado esperado y armar el borrador de la ficha de smells y de la tabla de resultados | **Alto.** La IA propuso los casos y los corrió sobre una copia aislada del sistema para anticipar el resultado. Ejecuté y capturé los casos desde Swagger UI y confirmé los resultados.
| Gaston Paschetta | Claude Code (Anthropic) | **Pruebas (Fase 2):** pasar a tests automáticos los 17 casos de `POST /solicitudes` que ejecuté y validé en la Fase 1, siguiendo el criterio de línea de base y el `conftest.py` común que ya había definido el grupo | **Alto en la escritura del código.** La IA tradujo cada caso a un test sin agregar casos ni cambiar resultados esperados, redactó `docs/pruebas/gaston_resultados_fase2.md` y corrió la suite en mi PC. Los casos, sus resultados y el criterio vienen de la Fase 1 y del plan del grupo. Revisé el resultado, hice el commit y el push, y abrí el PR | [`anexo/ia/gaston_registro_ia.md`](../../anexo/ia/gaston_registro_ia.md), pedido 3 |

## Detalle

Para el diagnóstico, la IA propuso 17 casos de prueba en un orden que permite ejecutarlos sobre una base limpia y los corrió antes sobre una copia aislada del sistema para indicar el resultado esperado. Ejecuté y capturé los casos desde Swagger UI y confirmé que los resultados coincidían.

Para las pruebas seguí la metodología que el grupo ya venía aplicando: cada integrante pasa a tests automáticos los casos de su Fase 1, con el criterio de línea de base (cada test fija lo que el sistema hace hoy y deja el comportamiento esperado en un comentario) y los fixtures del `conftest.py` común. Con esa base definida, le pedí a la IA que tradujera a tests los 17 casos que ejecuté en la Fase 1, sin agregar casos nuevos ni cambiar los resultados esperados. La IA escribió `tests/test_solicitudes.py` y `docs/pruebas/gaston_resultados_fase2.md`. Después corrió la suite completa en mi PC con `.\run.bat test` (64 tests en verde, con `main.py` sin cambios respecto de `estado-inicial`) y sacó la captura. Revisé el resultado, subí la rama `test/gaston` y abrí el PR.
