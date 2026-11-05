# Fase 2 — Pruebas automatizadas: línea de base

**Integrante:** Javier Ovelar
**Alcance:** `PUT /solicitudes/{id}/estado`, `PUT /solicitudes/{id}/responsable` (líneas 251–318 de `main.py`, tag `estado-inicial`)
**Herramientas:** pytest + `TestClient` de FastAPI
**Archivos:** `tests/test_asignacion.py`, `tests/test_estado.py` (usan el fixture `client` de `tests/conftest.py`)
**Cómo se ejecuta:** `.\run.bat test`
**Resultado:** 9 tests, 9 en verde (suite completa: 22 tests, 22 en verde)

## Criterio: línea de base

Se sigue el mismo criterio que en `cristian_resultados_fase2.md`: cada test verifica lo que el sistema hace **hoy**, aunque sea incorrecto, y el comportamiento esperado queda escrito en un comentario (`# Actual: ... Esperado: ...`), con el criterio de códigos HTTP de la Fase 1.

Los tests de casos que el sistema acepta y no debería llevan en el nombre lo que pasa hoy (`rechazar_acepta_motivo_nulo`, `reasignar_no_registra_historial`).

## Qué verifica cada test

Además del código HTTP y la respuesta, cada test comprueba el efecto en la base con `GET /solicitudes/{id}`:

- **Casos correctos:** el estado, el responsable y la última fila del historial quedaron guardados.
- **Errores:** la solicitud es la misma antes y después del `PUT`. En los casos con id 999 no se comprueba, porque la solicitud no existe.
- **Reasignación:** cambia el `responsable_id` y el historial es el mismo antes y después.

## Tests y casos

### `PUT /solicitudes/{id}/responsable` (`test_asignacion.py`)

| Caso Fase 1 | Test | Actual | Esperado | Hallazgos |
|---|---|---|---|---|
| 10 | `test_asignar_responsable_valido` | 200, pasa a `ASIG` y agrega "asignada a Graciela Molina" al historial | 200 | — |
| 2 | `test_asignar_solicitud_inexistente` | 200 con error | 404 | 1 |
| 8 | `test_asignar_responsable_inactivo` | 200 con error, no cambia la solicitud | 409 | 1 |
| 12a–12c | `test_reasignar_no_registra_historial` | 200, cambia el responsable y el historial queda igual | Una fila nueva en el historial con la reasignación | 6 |

### `PUT /solicitudes/{id}/estado` (`test_estado.py`)

| Caso Fase 1 | Test | Actual | Esperado | Hallazgos |
|---|---|---|---|---|
| 13 | `test_cambiar_estado_asig_a_en_proc` | 200, pasa a `EN_PROC` y agrega la fila al historial | 200 | — |
| 1 | `test_cambiar_estado_solicitud_inexistente` | 404 con formato `detail` | 404 con formato `error` | 1 |
| 5 | `test_cambiar_estado_transicion_no_permitida` | 200 con error, no cambia la solicitud | 409 | 1, 2 |
| 15 | `test_rechazar_acepta_motivo_nulo` | 200, rechaza y el historial guarda el comentario `null` | 422 sin cambiar el estado | 4 |
| 4 | `test_cambiar_estado_a_asig_sin_responsable` | 200 con error, no cambia la solicitud | 409 | 1, 3 |

## Evidencia

`docs/evidencias/fase2/javier/prueba_antes.png`: ejecución de la suite completa sobre la rama `test/javier`, con `main.py` sin cambios respecto de `estado-inicial`. Resultado: 22 passed.

El warning `StarletteDeprecationWarning` sobre `httpx` viene de las versiones de las librerías, no del código del sistema. No afecta los resultados.
