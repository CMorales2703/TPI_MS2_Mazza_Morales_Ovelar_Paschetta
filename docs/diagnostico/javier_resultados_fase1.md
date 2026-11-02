# Fase 1 — Calidad externa: resultados observados

**Integrante:** Javier Ovelar
**Alcance:** `PUT /solicitudes/{id}/estado`, `PUT /solicitudes/{id}/responsable` (líneas 251–318 de `main.py`, tag `estado-inicial`)
**Fecha de ejecución:** 24/10/2026
**Entorno:** base limpia (`run.bat reset`), pruebas manuales desde Swagger UI (`/docs`), casos ejecutados en orden

## Criterio de evaluación de códigos HTTP

| Situación | Código esperado |
|---|---|
| Operación exitosa | 200 OK |
| Dato inválido o faltante | 422 Unprocessable Entity |
| Choca con el estado actual del recurso (transición no permitida, solicitud cerrada) | 409 Conflict |
| El recurso no existe | 404 Not Found |
| Falla interna | 500, nunca por un dato enviado por el cliente |

## Datos iniciales relevantes

| Solicitud | Estado | Área | Responsable |
|---|---|---|---|
| 1 | PEND | Alumnado | — |
| 2 | ASIG | Departamento Academico | 3 (Paula Diaz) |
| 3 | EN_PROC | Bedelia | 4 (Hector Ruiz) |
| 4 | RES | Coordinacion | 5 (Marina Sosa) |
| 6 | PEND | Alumnado | — |

Responsables: 1 Graciela Molina (Alumnado, activa), 2 Ruben Castro (Alumnado, **inactivo**), 3 Paula Diaz (Departamento Academico), 4 Hector Ruiz (Bedelia), 5 Marina Sosa (Coordinacion).

## Resultados

| #   | Qué se probó                              | Endpoint / id               | Body enviado                                                                        | HTTP | Qué respondió                                                                               | ¿Está bien? | ¿Por qué?                                                                                                                                    | Evidencia                                                |
| --- | ----------------------------------------- | --------------------------- | ----------------------------------------------------------------------------------- | ---- | ------------------------------------------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| 1   | Cambio de estado de solicitud inexistente | estado / 999                | `{"estado":"ASIG"}`                                                                 | 404  | `{"detail":"no existe"}`                                                                    | Sí          | El mensaje es el correcto                                                                                                                    | `caso01_estado_no_existe.png`                            |
| 2   | Asignar en solicitud inexistente          | responsable / 999           | `{"responsable_id":1}`                                                              | 200  | `{"error":"solicitud no existe"}`                                                           | Parcial     | El código debería ser 404                                                                                                                    | `caso02_asignar_no_existe.png`                           |
| 3   | Cambio de estado sin campo `estado`       | estado / 1                  | `{}`                                                                                | 200  | `{"error":"transicion no permitida de PEND a None"}`                                        | Parcial     | El código debería ser 422                                                                                                                    | `caso03_estado_falta.png`                                |
| 4   | PEND → ASIG sin responsable               | estado / 1                  | `{"estado":"ASIG"}`                                                                 | 200  | `{"error":"no tiene responsable"}`                                                          | Parcial     | Mensaje bien pero el código debería ser 409                                                                                                  | `caso04_asig_sin_responsable.png`                        |
| 5   | Transición no permitida PEND → RES        | estado / 1                  | `{"estado":"RES"}`                                                                  | 200  | `{"error":"transicion no permitida de PEND a RES"}`                                         | Parcial     | Mensaje indica error correcto, no se puede saltar de Pendiente a resuelto, pero el código está mal, debería ser 409                          | `caso05_transicion_invalida.png`                         |
| 6   | Asignar sin campo `responsable_id`        | responsable / 1             | `{}`                                                                                | 200  | `{"error":"responsable no existe"}`                                                         | No          | Código error incorrecto, debe ser 422. El mensaje está mal porque el responsable no se envió                                                 | `caso06_responsable_falta.png`                           |
| 7   | Asignar responsable inexistente           | responsable / 1             | `{"responsable_id":99}`                                                             | 200  | `{"error":"responsable no existe"}`                                                         | Parcial     | El mensaje es el correcto, pero no el código, que tiene que ser 404                                                                          | `caso07_responsable_no_existe.png`                       |
| 8   | Asignar responsable inactivo              | responsable / 1             | `{"responsable_id":2}`                                                              | 200  | `{"error":"responsable inactivo"}`                                                          | Parcial     | Mensaje correcto, código inválido, tiene que ser 409                                                                                         | `caso08_responsable_inactivo.png`                        |
| 9   | Asignar responsable de otra área          | responsable / 1             | `{"responsable_id":4}`                                                              | 200  | `{"error":"el responsable no pertenece al area Alumnado"}`                                  | Parcial     | El código tiene que ser 409                                                                                                                  | `caso09_responsable_otra_area.png`                       |
| 10  | Asignación válida                         | responsable / 1             | `{"responsable_id":1}`                                                              | 200  | `{"id":1,"responsable_id":1,"responsable":"Graciela Molina","estado":"ASIG"}`; sin línea nueva en `notificaciones.log` | Sí          | Se modificó la solicitud con éxito.                                                                                                          | `caso10_asignacion_ok.png`, `caso10_notificaciones_log.png` |
| 11  | Asignar en solicitud cerrada              | responsable / 4             | `{"responsable_id":5}`                                                              | 200  | `{"error":"la solicitud esta cerrada"}`                                                     | Parcial     | El mensaje está bien pero el código está mal, debería ser 409                                                                                | `caso11_solicitud_cerrada.png`                           |
| 12a | Alta de responsable para reasignar        | `POST /responsables`        | `{"nombre":"Laura Gil","area":"Departamento Academico","email":"lgil@ejemplo.com"}` | 200  | Responsable creado (`id` 6)                                                                 | Sí          | Agregó un nuevo responsable, código 200.                                                                                                     | `caso12a_responsable_alta.png`                           |
| 12b | Reasignación en estado ASIG               | responsable / 2             | `{"responsable_id":6}`                                                              | 200  | `{"id":2,"responsable_id":6,"responsable":"Laura Gil","estado":"ASIG"}`                     | Sí          | Se realizó la reasignación                                                                                                                   | `caso12b_reasignacion.png`                               |
| 12c | Historial después de reasignar            | `GET /solicitudes/2`        | —                                                                                   | 200  | `responsable_id: 6`, pero el historial sigue diciendo solo "asignada a Paula Diaz"          | Parcial     | El código está bien (200), pero no el mensaje. Al realizar el cambio de asignación falta la persona anterior. Falla trazabilidad             | `caso12c_historial_sin_reasignacion.png`                 |
| 13  | Transición válida ASIG → EN_PROC          | estado / 2                  | `{"estado":"EN_PROC"}`                                                              | 200  | `{"id":2,"estado":"EN_PROC","estado_anterior":"ASIG"}`; línea nueva en `notificaciones.log` | Sí          | La transición fue válida, hay registro en el log que lo indica (notificación)                                                                | `caso13_en_proc_ok.png`, `caso13_notificaciones_log.png` |
| 14  | Rechazo sin motivo                        | estado / 2                  | `{"estado":"RECH"}`                                                                 | 200  | `{"error":"para rechazar hay que poner motivo"}`                                            | Parcial     | Mensaje correcto, no así el código, falta dato (422)                                                                                         | `caso14_rech_sin_motivo.png`                             |
| 15  | Rechazo con motivo nulo                   | estado / 2                  | `{"estado":"RECH","comentario":null}`                                               | 200  | `{"id":2,"estado":"RECH","estado_anterior":"EN_PROC"}`                                      | No          | Aceptó la solicitud con el campo "comentario" nulo. Falló validación o es débil                                                              | `caso15_rech_motivo_null.png`                            |
| 16  | Rechazo con motivo en blanco              | estado / 3                  | `{"estado":"RECH","comentario":"   "}`                                              | 200  | `{"id":3,"estado":"RECH","estado_anterior":"EN_PROC"}`                                      | No          | Acepta la solicitud pero el campo comentario solo posee espacios en blanco, no informa nada.                                                 | `caso16_rech_motivo_blanco.png`                          |
| 17  | Historial de los rechazos                 | `GET /solicitudes/2` y `/3` | —                                                                                   | 200  | Rechazos con comentario `null` (2) y `"   "` (3)                                            | No          | En ambas consultas, en el campo "comentario" se muestran valores inútiles: Un comentario debe informar, no permanecer en blanco y/o ser null | `caso17_historial_2.png`, `caso17_historial_3.png`       |
| 18  | Comentario que no es texto                | estado / 1                  | `{"estado":"CANC","comentario":123}`                                                | 200  | `{"id":1,"estado":"CANC","estado_anterior":"ASIG"}`; el historial guarda `"123"`            | No          | Acepta un comentario numérico y no String. Falla en validación/modelo de entrada                                                             | `caso18_comentario_numero.png`                           |
| 19  | Body que no es un objeto                  | estado / 6                  | `[1, 2]`                                                                            | 422  | `"Input should be a valid dictionary"` (formato `detail`)                                   | Parcial     | Código correcto, pero el mensaje es poco claro.                                                                                              | `caso19_body_lista_422.png`                              |

## Conclusiones de calidad externa

- **Funciona con datos válidos:** asignar, reasignar y cambiar de estado andan bien (casos 10, 12b y 13).
- **Los errores responden 200:** el cliente no distingue un éxito de un error por el código HTTP, y la misma situación da 404 en un endpoint y 200 en el otro (casos 1 y 2).
- **Se guardan datos inválidos:** se aceptan rechazos sin motivo real y comentarios que no son texto (casos 15, 16 y 18).
- **Se pierde información:** las reasignaciones no quedan en el historial y asignar no notifica al estudiante (casos 12c y 10).

## Vínculo con la ficha de smells

| Hallazgo de la ficha | Casos que lo evidencian |
|---|---|
| Manejo de errores inconsistente | 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 14, 19 |
| Lógica de estados repartida entre dos funciones | 4, 10 |
| Validación débil del motivo de rechazo | 15, 16, 17 |
| Falta de modelo de entrada (`data: dict`) | 3, 6, 18, 19 |
| Pérdida de trazabilidad en reasignaciones | 12b, 12c |
