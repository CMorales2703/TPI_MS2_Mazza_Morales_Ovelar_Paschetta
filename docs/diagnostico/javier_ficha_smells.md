# Fase 1 — Ficha de deuda técnica y code smells

**Integrante:** Javier Ovelar
**Alcance:** líneas 251–318 de `main.py` (tag `estado-inicial`): cambio de estado y asignación de responsable
**Evidencia de calidad externa:** [`javier_resultados_fase1.md`](javier_resultados_fase1.md) (los números de caso remiten a esa tabla)
**Uso de IA:** ver el registro de uso de IA del grupo

## Resumen

| # | Smell / hallazgo | Ubicación | Casos | Prioridad |
|---|---|---|---|---|
| 1 | Manejo de errores inconsistente | Líneas 256, 267, 269, 271, 296, 298, 302, 304 y 306 | 1–9, 11, 14, 19 | Alta |
| 2 | Switch Statements: transiciones hardcodeadas | Líneas 259–266 | 3, 5 | Media |
| 3 | Lógica de estados repartida (riesgo de Shotgun Surgery) | Líneas 309–311 (y 259–266) | 4, 10 | Alta |
| 4 | Validación débil del motivo de rechazo | Línea 270 | 15, 16, 17 | Alta |
| 5 | Falta de modelo de entrada | Líneas 252 y 292 | 3, 6, 18, 19 | Alta |
| 6 | Pérdida de trazabilidad en reasignaciones | Líneas 312–316 | 12b, 12c | Alta |
| 7 | Excepción silenciada (`except:` sin tipo) | Líneas 282–286 | — | Media |
| 8 | Duplicated Code: historial, notificación y fecha | Líneas 273–286, 308 y 315–316 (y 180–194) | 13 | Media |
| 9 | Magic Numbers: índices de columnas | Líneas 258, 268, 280, 284, 297, 303, 305, 309–316 | — | Media |
| 10 | Primitive Obsession: estados como strings | Líneas 260–265 y 297 | — | Media |
| 11 | Long Method / violación de SRP en `proc_estado` | Líneas 251–288 | — | Media |
| 12 | Nombres poco expresivos | Líneas 252, 254, 258, 292, 300 | — | Baja |

> Los hallazgos 4 y 6 son defectos de reglas de negocio, no smells con nombre propio del catálogo.

## Criterio de priorización

| Prioridad | Hallazgos | Criterio |
|---|---|---|
| Alta | 1, 3, 4, 5, 6 | Defectos comprobados con los casos de prueba |
| Media | 2, 7, 8, 9, 10, 11 | Dificultan el mantenimiento, sin una falla actual comprobada |
| Baja | 12 | Legibilidad |

**Orden de resolución propuesto:** primero el 1, porque es transversal (es el mismo problema que el hallazgo 3 de Cristian); después 4, 5 y 6, que tienen defectos comprobados; por último 2, 3 y 10 juntos, moviendo las transiciones a un módulo de estados (Move Method).

---

## Detalle

### 1. Manejo de errores inconsistente
- **Ubicación:** líneas 256, 267, 269, 271, 296, 298, 302, 304 y 306
- **Evidencia:** `proc_estado` responde 404 con `HTTPException` si la solicitud no existe (línea 256), pero `asignar` responde 200 con `{"error": "solicitud no existe"}` en la misma situación (línea 296). El resto de los errores son `return {"error": ...}` con 200, y FastAPI responde 422 con otro formato (`detail`).
- **Casos:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 14, 19
- **Impacto:** el cliente no puede distinguir un éxito de un error por el código HTTP
- **Riesgo:** un cliente que confía en el código da por hecha una operación que falló
- **Prioridad:** alta, comprobado en 12 casos
- **Principio:** Clean Code: manejo de errores consistente

### 2. Switch Statements: transiciones hardcodeadas
- **Ubicación:** líneas 259–266
- **Evidencia:** las transiciones permitidas se calculan con tres `if` que activan una bandera `ok`, en lugar de una tabla de transiciones
- **Casos:** 3, 5
- **Impacto:** agregar o cambiar una transición obliga a modificar los `if` de `proc_estado`
- **Riesgo:** olvidar una combinación y permitir o bloquear una transición por error
- **Prioridad:** media, sin falla actual comprobada
- **Principio:** OCP

### 3. Lógica de estados repartida (riesgo de Shotgun Surgery)
- **Ubicación:** líneas 309–311 de `asignar` (y 259–266 de `proc_estado`)
- **Evidencia:** `asignar` cambia PEND → ASIG por su cuenta, sin pasar por las reglas de `proc_estado`. Como toda asignación sobre una solicitud PEND la pasa a ASIG, no puede existir una solicitud PEND con responsable, y la transición PEND → ASIG por `/estado` nunca tiene éxito usando la API.
- **Casos:** 4, 10
- **Impacto:** las reglas de estado están en dos funciones que se comportan distinto (una notifica y la otra no)
- **Riesgo:** cambiar una regla en un lugar y no en el otro; hoy PEND → ASIG por `/estado` nunca puede tener éxito
- **Prioridad:** alta, comprobado en el caso 4 (el 10 muestra que asignar cambia el estado por su cuenta)
- **Principio:** DRY: las transiciones deberían tener una sola fuente de verdad

### 4. Validación débil del motivo de rechazo
- **Ubicación:** línea 270
- **Evidencia:** `"comentario" not in data or data["comentario"] == ""` deja pasar `null` y textos en blanco (`"   "`)
- **Casos:** 15, 16, 17
- **Impacto:** se guardan rechazos sin un motivo útil
- **Riesgo:** no poder explicar después por qué se rechazó una solicitud
- **Prioridad:** alta, comprobado en los casos 15, 16 y 17
- **Principio:** Clean Code: validar la entrada

### 5. Falta de modelo de entrada
- **Ubicación:** líneas 252 y 292
- **Evidencia:** `data: dict = Body(...)` con lecturas sueltas (`data.get("estado")`, `data.get("responsable_id")`, `data.get("comentario", "")`), sin validar presencia ni tipo
- **Casos:** 3, 6, 18, 19
- **Impacto:** cada función valida a mano, y un dato faltante o de otro tipo se confunde con otro error
- **Riesgo:** se guardan en la base datos de tipo incorrecto
- **Prioridad:** alta, comprobado en los casos 3, 6 y 18
- **Principio:** Clean Code: validar la entrada

### 6. Pérdida de trazabilidad en reasignaciones
- **Ubicación:** líneas 312–316
- **Evidencia:** el historial solo se escribe `if nuevo_estado != s[5]`; reasignar una solicitud ASIG o EN_PROC cambia `responsable_id` sin dejar registro
- **Casos:** 12b, 12c
- **Impacto:** el historial no refleja quién tuvo la solicitud a cargo
- **Riesgo:** pérdida de información ante un reclamo o una auditoría
- **Prioridad:** alta, comprobado en el caso 12c
- **Principio:** integridad de datos (regla de negocio, no un principio SOLID)

### 7. Excepción silenciada (`except:` sin tipo)
- **Ubicación:** líneas 282–286
- **Evidencia:** `except: pass` atrapa cualquier error de la notificación, incluido un `TypeError` si el estudiante no existe (`est` es `None`) o no tiene email
- **Casos:** — (detectado leyendo el código)
- **Impacto:** si la notificación falla, nadie se entera
- **Riesgo:** estudiantes sin notificar sin que quede rastro del error
- **Prioridad:** media, detectado leyendo el código, sin falla comprobada
- **Principio:** Clean Code: no silenciar excepciones

### 8. Duplicated Code: historial, notificación y fecha
- **Ubicación:** líneas 273–286, 308 y 315–316 (y en `registrar`, líneas 180–194)
- **Evidencia:** el `INSERT INTO historial` aparece en las líneas 183, 275 y 315; el bloque de notificación en 190–194 y 282–286; `datetime.now().strftime("%Y-%m-%d %H:%M:%S")` en 180, 273 y 308
- **Casos:** 13
- **Impacto:** un cambio en el historial, la notificación o el formato de fecha hay que repetirlo en tres lugares
- **Riesgo:** que los lugares queden desalineados
- **Prioridad:** media, sin falla actual comprobada
- **Principio:** DRY

### 9. Magic Numbers: índices de columnas
- **Ubicación:** líneas 258, 268, 280, 284, 297, 303, 305 y 309–316
- **Evidencia:** `s[1]`, `s[5]`, `s[6]`, `s[7]`, `r[0]`, `r[1]`, `r[2]`, `r[4]`, `est[4]` para leer columnas
- **Casos:** —
- **Impacto:** hay que mirar el `CREATE TABLE` para entender qué es `s[5]` o `r[4]`
- **Riesgo:** agregar o reordenar una columna rompe el código sin un error visible
- **Prioridad:** media, sin falla actual comprobada
- **Principio:** Clean Code: nombres expresivos

### 10. Primitive Obsession: estados como strings
- **Ubicación:** líneas 260–265 y 297
- **Evidencia:** los estados son strings sueltos (`"PEND"`, `"ASIG"`, `"EN_PROC"`, `"RES"`, `"RECH"`, `"CANC"`) y la lista de estados cerrados `["RES", "RECH", "CANC"]` está escrita a mano (se repite en `reporte`, línea 346)
- **Casos:** —
- **Impacto:** los estados válidos no están definidos en un solo lugar
- **Riesgo:** un error de tipeo en un estado no se detecta
- **Prioridad:** media, sin falla actual comprobada
- **Principio:** Clean Code: evitar valores mágicos

### 11. Long Method / violación de SRP en `proc_estado`
- **Ubicación:** líneas 251–288
- **Evidencia:** la función busca la solicitud, valida la transición y las reglas de negocio, actualiza el estado, escribe el historial, busca al estudiante, notifica y arma la respuesta
- **Casos:** —
- **Impacto:** no se puede probar la validación, el guardado o la notificación por separado
- **Riesgo:** un cambio en una responsabilidad puede romper otra
- **Prioridad:** media, sin falla actual comprobada
- **Principio:** SRP

### 12. Nombres poco expresivos
- **Ubicación:** líneas 252, 254, 258, 292 y 300
- **Evidencia:** `proc_estado`, `asignar`, variables `s`, `r`, `act`, `f`, y el parámetro `id`, que tapa la función `id()` de Python
- **Casos:** —
- **Impacto:** hay que leer el código completo para entender cada variable
- **Riesgo:** confusiones al modificar; `id` tapa la función `id()` de Python
- **Prioridad:** baja, solo legibilidad
- **Principio:** Clean Code: nombres

---

## Para la puesta en común del grupo

- **Propuesta para la tabla grupal:** llevar los de prioridad alta (1, 3, 4, 5 y 6) y el 2. Unificar el 1 con el hallazgo 3 de Cristian y el 5 con su hallazgo 5 (falta de modelo de entrada).
- **Coordinación con Gaston:** el hallazgo 8 comparte el insert de historial, la notificación y el formato de fecha con `registrar` (líneas 180–194).
- **Coordinación con Bruno:** la lista de estados cerrados del hallazgo 10 se repite en `reporte` (línea 346).
- **Coordinación con Cristian:** el hallazgo 1 es el mismo problema que su hallazgo 3; conviene acordar un único criterio de errores para todo el sistema.
- **Fase 3 (Move Method):** candidatos naturales son las transiciones (hallazgos 2, 3 y 10) hacia un módulo de estados y la notificación (hallazgo 8) hacia un servicio propio.
