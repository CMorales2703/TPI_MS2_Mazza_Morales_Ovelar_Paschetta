# Fase 1 — Ficha de deuda técnica y code smells

**Integrante:** Bruno Maza
**Alcance:** líneas 201–248 y 323–361 de `main.py` (tag `estado-inicial`): búsqueda, detalle de solicitud y reporte
**Evidencia de calidad externa:** [`bruno_resultados_fase1.md`](bruno_resultados_fase1.md) (los números de caso remiten a esa tabla)
**Uso de IA:** ver [`../uso-ia/bruno.md`](../uso-ia/bruno.md)

## Resumen

| # | Smell / hallazgo | Ubicación | Casos | Prioridad |
|---|---|---|---|---|
| 1 | Inyección SQL por concatenación de parámetros | Líneas 205–222 | 9a, 9b, 10 | Alta |
| 2 | Fallo del reporte por fecha no parseable | Línea 347 | 17, 18 | Alta |
| 3 | Duplicated Code: conversión de fila a diccionario | Líneas 229–231 y 244–246 | — | Alta |
| 4 | Índices posicionales sin nombre | Líneas 229–231, 244–246 y 333–352 | — | Alta |
| 5 | Long Method / violación de SRP en `reporte` | Líneas 324–361 | 16 | Media |
| 6 | Duplicated Code: patrón de conteo repetido | Líneas 333–344 | — | Media |
| 7 | Long Parameter List en `buscar` | Líneas 202–203 | — | Media |
| 8 | Magic Numbers y Magic Strings en `reporte` | Líneas 346, 348–353 | — | Media |
| 9 | Parámetro `orden` inválido ignorado en silencio | Líneas 221–224 | 6 | Media |
| 10 | Falta de validación de fechas en `buscar` | Líneas 217–220 | 8 | Media |
| 11 | Búsqueda sensible a mayúsculas sin aviso | Líneas 205–216 | 2b, 4 | Media |
| 12 | Inconsistent Naming | Líneas 205, 227–228, 237–247, 332–356 | — | Baja |
| 13 | Mensaje de error poco informativo | Línea 240 | 12, 14 | Baja |

> El hallazgo 1 es una vulnerabilidad de seguridad, no un smell del catálogo. El 2 es un defecto de robustez. El 11 surgió de la ejecución de los casos, no del análisis del código.

## Criterio de priorización

| Prioridad | Hallazgos | Criterio |
|---|---|---|
| Alta | 1, 2, 3, 4 | Vulnerabilidad de seguridad (1), defectos comprobados (1, 2) o duplicación que multiplica el costo de cualquier cambio de esquema (3, 4) |
| Media | 5, 6, 7, 8, 9, 10, 11 | Dificultan el mantenimiento o degradan la experiencia del usuario, sin comprometer la seguridad |
| Baja | 12, 13 | Legibilidad y calidad de los mensajes |

**Orden de resolución propuesto:** primero el 1, por ser una vulnerabilidad con defecto comprobado; después el 3 y el 4, que se resuelven con un mismo Extract Method y habilitan el resto; luego el 2 y el 5.

**Relación con el reparto del grupo:** el hallazgo 3 es el que resuelvo con la técnica **Extract Method** que me toca garantizar. El hallazgo 7 corresponde a **Introduce Parameter Object**, la técnica que garantiza Gastón. El hallazgo 3 también fue detectado por Cristian en su parte (su hallazgo 9), de modo que el refactor es transversal y debe coordinarse antes de la Fase 3.

**Familia de fallas silenciosas:** los hallazgos 9, 10 y 11 comparten el mismo efecto: el sistema responde 200 y un resultado aparentemente válido, pero el parámetro enviado no se aplicó. Conviene resolverlos juntos con un criterio único de validación.

---

## Detalle

### 1. Inyección SQL por concatenación de parámetros
- **Ubicación:** líneas 205–222, en `buscar`
- **Evidencia:** `q += " AND estado = '" + estado + "'"` y siete concatenaciones equivalentes. La consulta se arma pegando texto que viene del cliente
- **Casos:** 9a, 9b, 10
- **Impacto:** un parámetro puede modificar la consulta que se ejecuta. Con `estado=RES` el filtro devuelve 1 solicitud; con `estado=' OR '1'='1` devuelve las 6, porque la condición resultante (`AND estado = '' OR '1'='1'`) es verdadera para todas las filas. Con `texto='` la consulta queda mal formada y el servidor responde 500
- **Riesgo:** acceso a datos que el filtro debía excluir y, en un sistema con permisos por área, lectura de solicitudes ajenas. El mismo mecanismo permite ejecutar consultas no previstas
- **Prioridad:** alta, por ser una vulnerabilidad de seguridad con defecto comprobado
- **Principio:** manejo seguro de entradas (Clean Code: límites y validación). La corrección es usar consultas parametrizadas, como ya hace `getSolicitud` en la línea 237
- **Observación:** en el mismo archivo conviven las dos formas. `getSolicitud` usa `c.execute("SELECT * FROM solicitudes WHERE id = ?", (id,))`, que es la correcta, mientras que `buscar` concatena. La inconsistencia hace más probable que el error se repita al agregar filtros

### 2. Fallo del reporte por fecha no parseable
- **Ubicación:** línea 347, en `reporte`
- **Evidencia:** `fa = datetime.strptime(s[8], "%Y-%m-%d %H:%M:%S")` sin control de formato ni de valor nulo
- **Casos:** 17, 18
- **Impacto:** una sola solicitud con `fecha_alta` en otro formato lanza `ValueError`; con `fecha_alta` nula lanza `TypeError`. En ambos casos `/reporte` responde 500 para todo el conjunto
- **Riesgo:** el reporte deja de funcionar por completo por un único registro mal cargado, y el error aparece lejos del lugar donde se originó el dato
- **Prioridad:** alta, por ser un defecto comprobado que inutiliza un endpoint entero
- **Principio:** manejo de errores. La función debería contemplar el dato inválido en lugar de asumir que el formato siempre es correcto

### 3. Duplicated Code: conversión de fila a diccionario
- **Ubicación:** líneas 229–231 (en `buscar`) y 244–246 (en `getSolicitud`)
- **Evidencia:** el mismo diccionario de doce campos, `{"id": r[0], "estudiante_id": r[1], ...}`, escrito dos veces
- **Casos:** —
- **Impacto:** agregar, quitar o reordenar una columna de la tabla obliga a modificar los dos lugares
- **Riesgo:** si se corrige uno solo, los dos endpoints devuelven estructuras distintas para la misma entidad, y el error no se detecta hasta que alguien compara las dos respuestas
- **Prioridad:** alta, porque multiplica el costo de cualquier cambio de esquema
- **Principio:** DRY. Se resuelve con **Extract Method**: una función que reciba la fila y devuelva el diccionario

### 4. Índices posicionales sin nombre
- **Ubicación:** líneas 229–231, 244–246 y 333–352
- **Evidencia:** `r[0]`, `r[4]`, `s[5]`, `s[8]`, `x[2]` y similares, sin ninguna indicación de qué columna representan
- **Casos:** —
- **Impacto:** para saber qué significa `s[5]` hay que volver al `CREATE TABLE` de la línea 15 y contar las columnas
- **Riesgo:** si se agrega una columna en el medio de la tabla, todos los índices posteriores se desplazan y el código sigue ejecutándose, devolviendo datos en campos equivocados sin dar error
- **Prioridad:** alta, por el tipo de error silencioso que habilita
- **Principio:** nombres claros y evitar la desinformación (Clean Code). Se corrige junto con el hallazgo 3

### 5. Long Method / violación de SRP en `reporte`
- **Ubicación:** líneas 324–361
- **Evidencia:** la función recorre las solicitudes y, en el mismo bucle, cuenta por estado, cuenta por tipo, cuenta por área, determina si cada solicitud está vencida y arma la lista de vencidas; después calcula el porcentaje de resueltas
- **Casos:** 16
- **Impacto:** cinco responsabilidades en una sola función de 38 líneas, imposible de probar por partes
- **Riesgo:** cualquier cambio en una de las reglas, por ejemplo los plazos de vencimiento, obliga a tocar una función que también calcula los otros cuatro valores
- **Prioridad:** media, porque hoy funciona correctamente
- **Principio:** SRP y funciones pequeñas (Clean Code)

### 6. Duplicated Code: patrón de conteo repetido
- **Ubicación:** líneas 333–344
- **Evidencia:** el bloque `if s[5] in por_estado: por_estado[s[5]] = por_estado[s[5]] + 1 else: por_estado[s[5]] = 1` aparece tres veces, cambiando solo el índice y el diccionario
- **Casos:** —
- **Impacto:** doce líneas que expresan una sola idea repetida tres veces
- **Riesgo:** bajo en cuanto a defectos, pero agregar un cuarto agrupamiento significa copiar el bloque una vez más
- **Prioridad:** media
- **Principio:** DRY

### 7. Long Parameter List en `buscar`
- **Ubicación:** líneas 202–203
- **Evidencia:** nueve parámetros: `estado`, `tipo`, `prioridad`, `area`, `estudiante_id`, `texto`, `desde`, `hasta` y `orden`
- **Casos:** —
- **Impacto:** la firma ocupa dos líneas y es difícil de leer; agregar un filtro nuevo la alarga y modifica a todos los que la usan
- **Riesgo:** los parámetros son opcionales y de tipos repetidos, de modo que un error en el orden al invocarla no se detecta
- **Prioridad:** media
- **Principio:** Long Parameter List. Se resuelve con **Introduce Parameter Object**, agrupando los criterios de búsqueda en un objeto

### 8. Magic Numbers y Magic Strings en `reporte`
- **Ubicación:** líneas 346 y 348–353
- **Evidencia:** `if s[5] not in ["RES", "RECH", "CANC"]` y los plazos `dias = 2`, `dias = 5`, `dias = 10` según la prioridad
- **Casos:** —
- **Impacto:** las reglas de negocio (qué estados se consideran cerrados y cuántos días tiene cada prioridad) están escritas dentro del cálculo, sin nombre que las explique
- **Riesgo:** si cambian los plazos, hay que encontrarlos dentro de la función; y los estados cerrados pueden quedar desalineados con los que usa `proc_estado`
- **Prioridad:** media
- **Principio:** evitar números y textos mágicos (Clean Code)

### 9. Parámetro `orden` inválido ignorado en silencio
- **Ubicación:** líneas 221–224
- **Evidencia:** `if orden == "prioridad": ... else: ...`, sin validar que el valor recibido sea uno de los admitidos
- **Casos:** 6
- **Impacto:** `orden=zzz` devuelve 200 con el orden por defecto, sin avisar que el parámetro no se aplicó
- **Riesgo:** un error de tipeo en el cliente pasa inadvertido y el usuario cree que ordenó cuando no lo hizo
- **Prioridad:** media
- **Principio:** manejo de errores: fallar de forma visible en lugar de silenciosa

### 10. Falta de validación de fechas en `buscar`
- **Ubicación:** líneas 217–220
- **Evidencia:** `desde` y `hasta` se concatenan a la consulta sin verificar que sean fechas válidas
- **Casos:** 8
- **Impacto:** `desde=ayer` devuelve una lista vacía, indistinguible de una búsqueda sin resultados
- **Riesgo:** el usuario interpreta que no hay solicitudes en ese rango cuando en realidad el filtro era inválido
- **Prioridad:** media
- **Principio:** validación de entradas

### 11. Búsqueda sensible a mayúsculas sin aviso
- **Ubicación:** líneas 205–216, en `buscar`
- **Evidencia:** los filtros de texto se comparan con `=` en SQL, que distingue mayúsculas de minúsculas. Las columnas se crearon sin `COLLATE NOCASE` (línea 15)
- **Casos:** 2b, 4
- **Impacto:** `estado=pend` devuelve lista vacía aunque existan dos solicitudes con estado `PEND`. El sistema responde exactamente igual que ante un estado inexistente (caso 4), de modo que el usuario no puede distinguir un error de tipeo de una búsqueda sin resultados
- **Riesgo:** quien consulte puede concluir que no hay solicitudes pendientes cuando en realidad las hay. En un sistema de gestión académica, una consulta que devuelve vacío por un problema de mayúsculas puede derivar en que un trámite quede sin atender
- **Prioridad:** media, por el impacto sobre la confiabilidad de las consultas
- **Principio:** principio de mínima sorpresa y validación de entradas. Se corrige normalizando el valor recibido antes de comparar, o declarando las columnas como insensibles a mayúsculas
- **Observación:** este hallazgo no surgió del análisis del código sino de la ejecución del caso 2, al escribir el estado en minúscula por error. Es un ejemplo de defecto que solo aparece al probar el sistema

### 12. Inconsistent Naming
- **Ubicación:** líneas 205, 227–228, 237–247 y 332–356
- **Evidencia:** variables de una letra (`q`, `r`, `d`, `h`, `x`, `s`), abreviaturas (`fa`, `porc`, `res`) y nombres de función en estilos distintos: `buscar` y `reporte` en minúscula, `getSolicitud` en camelCase
- **Casos:** —
- **Impacto:** obliga a reconstruir el significado de cada variable leyendo su uso
- **Riesgo:** bajo, pero aumenta el tiempo de comprensión antes de cualquier modificación
- **Prioridad:** baja
- **Principio:** nombres claros y del dominio (Clean Code)

### 13. Mensaje de error poco informativo
- **Ubicación:** línea 240
- **Evidencia:** `raise HTTPException(status_code=404, detail="no existe")`
- **Casos:** 12, 14
- **Impacto:** el mensaje no indica qué no existe ni con qué id se buscó
- **Riesgo:** dificulta el diagnóstico desde el cliente y desde los registros
- **Prioridad:** baja
- **Principio:** mensajes de error informativos (Clean Code)
