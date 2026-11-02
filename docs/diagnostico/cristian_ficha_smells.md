# Fase 1 — Ficha de deuda técnica y code smells

**Integrante:** Cristian Morales
**Alcance:** líneas 1–111 de `main.py` (tag `estado-inicial`): conexión, creación de tablas, datos de prueba, estudiantes y responsables
**Evidencia de calidad externa:** [`cristian_resultados_fase1.md`](cristian_resultados_fase1.md) (los números de caso remiten a esa tabla)
**Uso de IA:** ver el registro de uso de IA del grupo

## Resumen

| # | Smell / hallazgo | Ubicación | Casos | Prioridad |
|---|---|---|---|---|
| 1 | Global State | Líneas 7–8 | — | Alta |
| 2 | Efectos secundarios al importar el módulo | Líneas 10–54 | — | Alta |
| 3 | Manejo de errores inconsistente | Líneas 62, 64, 66, 68, 71, 94, 96 y 98 | 2, 3, 5, 7, 10, 12 | Alta |
| 4 | Duplicated Code: validación de email | Líneas 67–68 y 97–98 | 4, 10 | Media |
| 5 | Falta de modelo de entrada | Líneas 60 y 92 | 4, 6, 10, 11a, 12 | Alta |
| 6 | Primitive Obsession | Líneas 95, 100 y 110 | — | Media |
| 7 | Violación de SRP en `crear_estudiante` | Líneas 59–76 | — | Media |
| 8 | Magic Numbers | Líneas 85 y 110 | — | Media |
| 9 | Duplicated Code: conversión de filas | Líneas 83–86 y 108–110 | — | Media |
| 10 | Duplicated Code: datos de prueba | Líneas 24–53 | — | Baja |
| 11 | Integridad de datos insuficiente | Líneas 10–18 y 69 | 6, 8b, 9b, 11a, 11b | Alta |
| 12 | Inconsistent Naming | Líneas 60, 80, 92 y 106 | — | Baja |
| 13 | Riesgo de Shotgun Surgery: áreas | Línea 95 (y `registrar`, líneas 167–174) | — | Media |

> Los hallazgos 2 y 11 son problemas de diseño, no smells con nombre propio del catálogo.

## Criterio de priorización

| Prioridad | Hallazgos | Criterio |
|---|---|---|
| Alta | 1, 2, 3, 5, 11 | Bloquean pruebas confiables (1 y 2) o tienen defectos comprobados (3, 5 y 11) |
| Media | 4, 6, 7, 8, 9, 13 | Dificultan el mantenimiento, sin una falla actual comprobada |
| Baja | 10, 12 | Legibilidad y mantenimiento de los datos de prueba |

**Orden de resolución propuesto:** primero 1 y 2, porque son transversales y desbloquean los tests del grupo; después 3, 5 y 11, que tienen defectos comprobados.

---

## Detalle

### 1. Global State
- **Ubicación:** líneas 7–8
- **Evidencia:** `conn = sqlite3.connect("solicitudes.db", check_same_thread=False)` y `c = conn.cursor()`, usados por todas las funciones
- **Casos:** —
- **Impacto:** dificulta probar con otra base de datos
- **Riesgo:** conflictos entre operaciones concurrentes
- **Prioridad:** alta, porque afecta a todo el sistema
- **Principio:** DIP

### 2. Efectos secundarios al importar el módulo
- **Ubicación:** líneas 10–54
- **Evidencia:** `CREATE TABLE` e `INSERT` sueltos a nivel de módulo, fuera de cualquier función
- **Casos:** —
- **Impacto:** importar el módulo modifica la base de datos y dificulta los tests
- **Riesgo:** los tests pueden modificar la base real y depender de datos de ejecuciones anteriores
- **Prioridad:** alta, porque bloquea pruebas confiables
- **Principio:** SRP / evitar efectos secundarios al importar

### 3. Manejo de errores inconsistente
- **Ubicación:** líneas 62, 64, 66, 68, 71, 94, 96 y 98
- **Evidencia:** `return {"error": "..."}` en lugar de lanzar una excepción HTTP
- **Casos:** 2, 3, 5, 7, 10, 12
- **Impacto:** el cliente recibe respuestas de error con estados HTTP incorrectos
- **Riesgo:** el frontend puede interpretar un fallo como una operación exitosa y las excepciones no controladas pueden generar errores 500
- **Prioridad:** alta, porque hay defectos comprobados
- **Principio:** manejo de errores

### 4. Duplicated Code: validación de email
- **Ubicación:** líneas 67–68 y 97–98
- **Evidencia:** `if "email" in data and "@" not in data["email"]:` repetido en los dos endpoints
- **Casos:** 4, 10
- **Impacto:** hay que modificar dos lugares para cambiar la validación del email
- **Riesgo:** que los endpoints validen de manera diferente
- **Prioridad:** media, porque duplica una regla de negocio
- **Principio:** DRY

### 5. Falta de modelo de entrada
- **Ubicación:** líneas 60 y 92
- **Evidencia:** `data: dict = Body(...)`, con validaciones manuales campo por campo
- **Casos:** 4, 6, 10, 11a, 12
- **Impacto:** las validaciones manuales aumentan el código y dificultan mantenerlo; favorecen la duplicación del hallazgo 4
- **Riesgo:** aceptar datos inválidos o generar errores inesperados
- **Prioridad:** alta, porque afecta la entrada de datos en varios endpoints
- **Principio:** Clean Code: validación y modelos explícitos

### 6. Primitive Obsession
- **Ubicación:** líneas 95, 100 y 110
- **Evidencia:** áreas como lista de strings; `activo` guardado como `1`/`0` y convertido con `r[4] == 1`
- **Casos:** —
- **Impacto:** cuesta entender qué representan los strings de áreas y los valores `1` y `0`
- **Riesgo:** errores al ampliar las áreas o interpretar el estado activo
- **Prioridad:** media, porque dificulta el mantenimiento
- **Principio:** Clean Code: tipos y nombres expresivos

### 7. Violación de SRP en `crear_estudiante`
- **Ubicación:** líneas 59–76
- **Evidencia:** la función valida campos, valida el email, verifica duplicados, inserta, hace commit y arma la respuesta
- **Casos:** —
- **Impacto:** cuesta modificar y probar por separado las tareas de la función
- **Riesgo:** un cambio en una responsabilidad puede afectar las demás
- **Prioridad:** media, porque dificulta el mantenimiento, pero no genera por sí sola un defecto comprobado
- **Principio:** SRP

### 8. Magic Numbers
- **Ubicación:** líneas 85 y 110
- **Evidencia:** `r[0]`, `r[1]` … `r[5]` para leer columnas
- **Casos:** —
- **Impacto:** cuesta entender qué columna representa cada índice
- **Riesgo:** intercambiar índices y devolver datos incorrectos al cambiar la consulta
- **Prioridad:** media, porque dificulta mantener los listados
- **Principio:** Clean Code: nombres expresivos

### 9. Duplicated Code: conversión de filas
- **Ubicación:** líneas 83–86 y 108–110
- **Evidencia:** el mismo bucle `for r in ...: res.append({...})` en los dos listados
- **Casos:** —
- **Impacto:** hay que mantener dos conversiones similares
- **Riesgo:** que los listados devuelvan formatos diferentes después de un cambio
- **Prioridad:** media, porque una función compartida simplificaría el mantenimiento
- **Principio:** DRY

### 10. Duplicated Code: datos de prueba
- **Ubicación:** líneas 24–53
- **Evidencia:** 30 `INSERT` casi idénticos con los valores escritos a mano
- **Casos:** —
- **Impacto:** cuesta editar y mantener los datos de prueba escritos manualmente
- **Riesgo:** inconsistencias o errores al modificar los registros
- **Prioridad:** baja, porque afecta principalmente al mantenimiento de los datos iniciales
- **Principio:** DRY

### 11. Integridad de datos insuficiente
- **Ubicación:** líneas 10–18 y 69
- **Evidencia:** las tablas no tienen `NOT NULL`, `UNIQUE` ni claves foráneas; `WHERE legajo = ?` no detecta `NULL`
- **Casos:** 6, 8b, 9b, 11a, 11b
- **Impacto:** la base permite datos incompletos, duplicados o relaciones inconsistentes
- **Riesgo:** que esos datos inválidos provoquen consultas incorrectas o errores en operaciones futuras
- **Prioridad:** alta, porque hay defectos comprobados
- **Principio:** diseño de base de datos: integridad de datos; práctica relacionada: fail fast

### 12. Inconsistent Naming
- **Ubicación:** líneas 60, 80, 92 y 106
- **Evidencia:** `crear_estudiante`, `listar_estudiantes`, `nuevoResponsable`, `get_resp`
- **Casos:** —
- **Impacto:** los nombres inconsistentes dificultan localizar y entender las funciones
- **Riesgo:** confusiones al usar o modificar endpoints
- **Prioridad:** baja, porque es principalmente un problema de legibilidad
- **Principio:** Clean Code: nombres consistentes

### 13. Riesgo de Shotgun Surgery: áreas
- **Ubicación:** línea 95 (y su uso en `registrar`, líneas 167–174)
- **Evidencia:** las áreas válidas están escritas en un lugar y el mapeo de tipo a área en otro
- **Casos:** —
- **Impacto:** para cambiar las áreas válidas hay que revisar varios lugares del código
- **Riesgo:** que el mapeo y la lista de áreas queden desincronizados
- **Prioridad:** media, porque complica los cambios relacionados
- **Principio:** OCP y DRY

---

## Para la puesta en común del grupo

- **Propuesta para la tabla grupal:** God Object. `main.py` concentra la API, la inicialización de la base, los datos de prueba y el acceso a datos de todo el sistema.
- **Hallazgos transversales:** 1 y 2. Afectan a todas las partes y conviene resolverlos antes que el resto de los refactorings.
- **Coordinación con Gaston:** el hallazgo 13 involucra el mapeo de tipo a área de `registrar` (líneas 167–174), que es parte de su código.
