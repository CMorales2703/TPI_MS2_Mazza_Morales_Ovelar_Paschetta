# Decisión técnica 02 — Defectos que quedan como deuda técnica

**Estado:** aceptada por el grupo al cierre de la Fase 3
**Hallazgos:** fichas de `docs/diagnostico/` (C = Cristian, G = Gaston, J = Javier, B = Bruno) y la sección "Hallazgos que quedan fuera" de cada documento de `docs/refactoring/`

## Decisión

Los defectos comprobados en el diagnóstico **no se corrigen en este trabajo**: quedan registrados como deuda técnica para una etapa posterior.

La Fase 3 se limitó a refactorings, es decir, a cambios que no alteran el comportamiento. Corregir estos defectos cambia lo que responde el sistema (códigos HTTP, datos que se aceptan o se rechazan), así que obliga a modificar asserts de los tests de línea de base. Mezclarlo con el refactoring impediría demostrar que el refactoring fue seguro.

Los tests de la Fase 2 ya documentan cada defecto: los que verifican el comportamiento actual llevan un comentario `Actual: ... Esperado: ...` o el prefijo `DEFECTO` en el nombre. Cuando se corrija un defecto, esos tests se actualizan en el mismo commit, y el cambio queda trazable.

## Deuda registrada

Ordenada por prioridad, con el criterio del grupo: **Alta** = defecto comprobado en la Fase 1.

| # | Tema | Hallazgos | Prioridad | Corrección propuesta | Tests que cambian |
|---|---|---|---|---|---|
| 1 | Inyección SQL en la búsqueda | B1 | **Alta** | Consulta parametrizada en `buscar` | `test_DEFECTO_inyeccion_sql_evade_el_filtro`, `test_DEFECTO_comilla_simple_rompe_el_servidor` |
| 2 | Errores 500 por datos de entrada | C5, G5, J5 (casos C10, G con `descripcion` nula o numérica) | **Alta** | Modelos Pydantic en `app/schemas.py`: 422 en lugar de 500 | `test_crear_estudiante_email_null`, `test_registrar_descripcion_null`, `test_registrar_descripcion_numerica` |
| 3 | Reporte roto por fechas inválidas | B2 | **Alta** | Contemplar la fecha no interpretable en `reporte` | `test_DEFECTO_fecha_con_otro_formato_rompe_el_reporte`, `test_DEFECTO_fecha_nula_rompe_el_reporte`, `test_DEFECTO_el_reporte_se_recupera_al_quitar_el_dato_malo` |
| 4 | Errores con HTTP 200 | C3, G4, J1, B13 | **Alta** | Unificar códigos: 422 validación, 404 inexistente, 409 duplicado, 201 alta | todos los que tienen `Actual: 200` en el comentario |
| 5 | Integridad de datos | C11 | **Alta** | `NOT NULL` y `UNIQUE` en la base, y rechazo con 422/409 | casos 6, 8b y 11 de estudiantes y responsables |
| 6 | Historial y estados | J3 (en parte), J4, J6 | **Alta** | Historial en las reasignaciones; motivo obligatorio al rechazar; `asignar_responsable` usando `transicion_permitida` | `test_reasignar_no_registra_historial`, `test_rechazar_acepta_motivo_nulo` |
| 7 | Filtros ignorados en la búsqueda | B9, B10, B11 | Media | Rechazar orden y fechas inválidos; búsqueda sin distinguir mayúsculas | `test_DEFECTO_orden_invalido...`, `test_DEFECTO_fecha_invalida...`, `test_DEFECTO_busqueda_distingue_mayusculas` |
| 8 | Notificaciones | G7, J7, J8 (en parte) | Media | Servicio `app/servicios/notificaciones.py` compartido; capturar solo `OSError` | ninguno de la línea de base |
| 9 | Mejoras de estructura pendientes | B7, B12, J10 (en parte), J12 (en parte) | Baja | Parameter Object en `buscar` (con los modelos del punto 2); renombrar `getSolicitud`; usar `ESTADOS_CERRADOS` en `consultas.py`; nombre del parámetro `id` | ninguno (son refactorings) |

## Criterios a acordar antes de corregir

1. **Recurso del body que no existe:** Gaston usa **422** (estudiante inexistente) y Javier **404** (responsable inexistente). Hay que elegir uno para el punto 4.
2. **Body que no es un objeto** (`[1, 2]`): Cristian y Gaston lo evaluaron como correcto y Javier como parcial. Los tres coinciden en que el problema es el formato `detail`, distinto del `error` del resto.

## Orden sugerido para la etapa posterior

1. **Inyección SQL (punto 1):** es un riesgo de seguridad y se resuelve sin depender de nada más.
2. **Criterios y códigos HTTP (punto 4)**, junto con los **modelos de entrada (punto 2)**: resuelven la mayor cantidad de hallazgos y eliminan los 500.
3. El resto, por área.

Cada corrección va en un commit `fix:` aparte, que actualiza los tests afectados y cita el hallazgo.
