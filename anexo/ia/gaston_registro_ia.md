# Registro de interacciones con IA — Gaston Paschetta

**Herramienta:** Claude Code
**Fases:** 1 — Diagnóstico y 2 — Pruebas
**Qué es este documento:** un resumen de los pedidos técnicos hechos a la IA, lo que devolvió y lo hecho con eso.

## Pedidos

| # | Fecha | Pedido (resumido) | Qué devolvió la IA | Qué hice yo |
|---|---|---|---|---|
| 1 | 23/10/2026 | Armar la plantilla de la ficha de smells y de la tabla grupal a partir de la ficha de Cristian y del plan de trabajo | Las dos plantillas del PR #6 | Las revisé y abrí el PR #6. |
| 2 | 28/10/2026 | Cómo se reparte el trabajo y en qué estado está cada integrante | Un panorama de las fases, los entregables y lo que me toca en cada etapa | Lo usé para ordenar lo que me queda |
| 3 | 06/11/2026 | Pasar a tests automáticos mis 17 casos de la Fase 1 de `POST /solicitudes` con el criterio de línea de base del grupo y correr la suite | `tests/test_solicitudes.py` (un test por caso), `docs/pruebas/gaston_resultados_fase2.md` y la captura de la ejecución en mi PC | Revisé que cada test correspondiera a su caso y a su resultado de la Fase 1, hice el commit y el push de la rama `test/gaston` y abrí el PR |
