# Tabla de deuda técnica y code smells

Tabla única del grupo. Reúne los hallazgos de las fichas individuales sin repetidos y es la base de la Fase 3. La coordina Gaston Paschetta.

**Líneas:** las del tag `estado-inicial`.

**Fichas de origen:**

| Integrante | Parte del código | Ficha |
|---|---|---|
| Cristian Morales | Conexión, tablas, datos de prueba, estudiantes y responsables (líneas 1–111) | [`cristian_ficha_smells.md`](cristian_ficha_smells.md) |
| Gaston Paschetta | `guardar_solicitud`, `calcular_prioridad`, `registrar` (líneas 114–198) | Pendiente |
| Bruno Maza | `buscar`, `getSolicitud`, `reporte` (líneas 201–248 y 321–361) | Pendiente |
| Javier Ovelar | `proc_estado`, `asignar` (líneas 251–318) | Pendiente |

## Cómo se unifica

- **Código:** cada hallazgo de la tabla lleva un código `S-01`, `S-02`, etc. La columna **Origen** dice de qué ficha viene (por ejemplo, `Cristian 3`).
- **Repetidos:** si el mismo smell aparece en varias partes (por ejemplo, devolver errores con estado 200), queda una sola fila con todas las ubicaciones y todos los orígenes.
- **Prioridad:** se usa el criterio común de la [plantilla](plantilla_ficha_smells.md#criterio-común-de-prioridad). Si dos fichas le dan distinta prioridad al mismo smell, queda la más alta y se explica por qué.
- **Refactoring:** todo hallazgo de prioridad alta o media tiene un refactoring asociado y un responsable. Si no se resuelve en este trabajo, queda como `mejora futura`, con el motivo.
- **Transversales:** se resuelven primero, en la Fase 3, y se mergean antes de que cada uno empiece su refactor.
- **Estado:** `Pendiente`, `En curso` (con el PR abierto) o `Resuelto` (con el PR mergeado).

## Resumen

| Código | Smell / hallazgo | Ubicación | Origen | Prioridad | Transversal | Refactoring asociado | Responsable | Estado |
|---|---|---|---|---|---|---|---|---|
| S-01 | | Líneas | | | | | | Pendiente |
| S-02 | | Líneas | | | | | | Pendiente |
| S-03 | | Líneas | | | | | | Pendiente |
| S-04 | | Líneas | | | | | | Pendiente |
| S-05 | | Líneas | | | | | | Pendiente |
| S-06 | | Líneas | | | | | | Pendiente |
| S-07 | | Líneas | | | | | | Pendiente |
| S-08 | | Líneas | | | | | | Pendiente |

## Refactorings obligatorios

Cada uno de estos tipos tiene que aparecer al menos una vez en el trabajo final.

| Refactoring | Lo garantiza | Hallazgos que resuelve | PR |
|---|---|---|---|
| Introduce Parameter Object | Gaston | | |
| Move Method | Javier | | |
| Extract Method | Bruno | | |
| Cambios transversales | Cristian | | |

## Orden de resolución

1. <transversales, en el orden acordado>
2. <prioridad alta de cada parte>
3. <prioridad media de cada parte>

---

## Detalle

### S-01. <Nombre del smell>
- **Origen:** <integrante y número en su ficha>
- **Ubicación:** <función>, líneas <desde>–<hasta>
- **Evidencia:** `<fragmento de código>`
- **Casos:** <ficha de resultados y números de caso, o —>
- **Impacto:**
- **Riesgo de mantenimiento:**
- **Prioridad:** <alta / media / baja>, porque <justificación>
- **Principio:**
- **Transversal:** <Sí / No>
- **Refactoring asociado:** <técnica, o mejora futura con el motivo>
- **Responsable:**
- **Estado:** Pendiente

---

## Control del coordinador

Antes de crear el tag `etapa-diagnostico`:

- [ ] Están las fichas de los 4 integrantes
- [ ] No hay hallazgos repetidos
- [ ] Hay 8 o más hallazgos
- [ ] Cada hallazgo tiene completos los 6 campos de la consigna: nombre, evidencia, ubicación, impacto, riesgo de mantenimiento y prioridad con justificación
- [ ] Cada hallazgo tiene el principio que viola
- [ ] Cada hallazgo de prioridad alta o media tiene un refactoring asociado o figura como mejora futura con el motivo
- [ ] Los cuatro refactorings obligatorios tienen al menos un hallazgo asignado
- [ ] Los transversales están identificados y tienen un orden acordado
