# Declaración de uso de IA — Gaston Paschetta

## Registro

| Integrante | Herramienta | Para qué la usó | Grado de intervención | Evidencia |
|---|---|---|---|---|
| Gaston Paschetta | Claude Code | **Coordinación:** armado de la plantilla de la ficha de smells y de la tabla de deuda técnica (PR #6), a partir de la ficha de Cristian y del plan de trabajo | **Alto.** La IA redactó las dos plantillas. Yo definí qué campos sumar y las revisé antes del PR | [`anexo/ia/gaston_registro_ia.md`](../../anexo/ia/gaston_registro_ia.md), pedido 1 (la conversación no se conservó) |
| Gaston Paschetta | Claude Code (Anthropic) | **Diagnóstico:** proponer los casos de prueba de `POST /solicitudes` con el resultado esperado y armar el borrador de la ficha de smells y de la tabla de resultados | **Alto.** La IA propuso los casos y los corrió sobre una copia aislada del sistema para anticipar el resultado. Ejecuté y capturé los casos desde Swagger UI y confirmé los resultados.
## Detalle

Para el diagnóstico, la IA propuso 17 casos de prueba en un orden que permite ejecutarlos sobre una base limpia y los corrió antes sobre una copia aislada del sistema para indicar el resultado esperado. Ejecuté y capturé los casos desde Swagger UI y confirmé que los resultados coincidían.