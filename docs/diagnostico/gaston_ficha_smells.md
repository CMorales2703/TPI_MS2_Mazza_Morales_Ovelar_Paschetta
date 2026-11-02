# Fase 1 — Ficha de deuda técnica y code smells

**Integrante:** Gaston Paschetta
**Alcance:** líneas 114–198 de `main.py` (tag `estado-inicial`): `guardar_solicitud`, `calcular_prioridad` y `registrar`
**Endpoints:** `POST /solicitudes`
**Evidencia de calidad externa:** [`gaston_resultados_fase1.md`](gaston_resultados_fase1.md) (los números de caso remiten a esa tabla)
**Uso de IA:** [`docs/uso-ia/gaston.md`](../uso-ia/gaston.md)

## Resumen

| # | Smell / hallazgo | Ubicación | Casos | Prioridad | Transversal | Refactoring propuesto |
|---|---|---|---|---|---|---|
| 1 | Long Parameter List en `guardar_solicitud` | Líneas 116–119 y 181–182 | — | Media | No | Introduce Parameter Object |
| 2 | Duplicated Code / Dead Code: cálculo de prioridad | Líneas 124–130 y 148–161 | 3 | Media | No | Usar `calcular_prioridad` en `registrar` (sumando la regla de "urgente") y borrar la copia |
| 3 | Long Method / violación de SRP en `registrar` | Líneas 133–198 | — | Media | Sí | Extract Method |
| 4 | Manejo de errores inconsistente | Líneas 137, 141, 143, 145 y 164 | 5–10, 12, 13, 16 | Alta | Sí | Reemplazar los `return {"error": ...}` por `HTTPException` con el código correcto |
| 5 | Falta de modelo de entrada y validación inconsistente | Líneas 134, 142–145, 163 y 176–178 | 9, 10, 11, 13, 14, 15 | Alta | Sí | Modelo de entrada con Pydantic |
| 6 | Switch Statements: área y prioridad según el tipo | Líneas 142, 150–159 y 167–174 | — | Media | Sí | Una tabla de configuración por tipo (tipo → área y prioridad) |
| 7 | Excepción silenciada (`except:` sin tipo) | Líneas 190–194 | 17 | Media | Sí | Extract Method `notificar_estudiante` y capturar solo el error de archivo |
| 8 | Magic Numbers: índice de columna | Línea 192 | — | Media | Sí | Acceder a las columnas por nombre (`sqlite3.Row`) |
| 9 | Nombres poco expresivos y código comentado | Líneas 148, 168–174, 180–181 y 186–187 | — | Baja | Sí | Rename Variable y borrar el código comentado |

> El hallazgo 5 mezcla un smell (falta de modelo de entrada) con un defecto comprobado (validación que deja pasar datos inválidos o los cambia sin avisar).

## Criterio de priorización

| Prioridad | Hallazgos | Por qué |
|---|---|---|
| Alta | 4, 5 | Tienen defectos comprobados en las pruebas: errores con 200, dos errores 500 y datos inválidos guardados |
| Media | 1, 2, 3, 6, 7, 8 | Complican cambiar el código o pueden provocar fallas en un cambio futuro, pero hoy no se comprobó una falla |
| Baja | 9 | Afecta principalmente la legibilidad |

**Orden de resolución propuesto:** primero 4 y 5, porque se repiten en las partes de Cristian y Javier y conviene resolverlos una sola vez como cambio transversal. Después 1 junto con 3, porque al separar `registrar` en funciones más chicas también se simplifica la llamada a `guardar_solicitud`. El 2 y el 6 se pueden resolver juntos, porque los dos salen de las reglas por tipo.

---

## Detalle

### 1. Long Parameter List en `guardar_solicitud`
- **Ubicación:** `guardar_solicitud`, líneas 116–119, y su única llamada en `registrar`, líneas 181–182
- **Evidencia:** `def guardar_solicitud(estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs):`
- **Casos:** —
- **Impacto:** para guardar una solicitud hay que pasar 11 valores sueltos en el orden exacto. En la llamada de la línea 181 van `f, f` seguidos para las dos fechas y `None` para el responsable, y no se ve a qué campo corresponde cada uno sin volver a la definición.
- **Riesgo de mantenimiento:** si se invierten dos argumentos del mismo tipo (por ejemplo `canal` y `obs`, o las dos fechas) Python no avisa y el dato queda mal guardado. Agregar un campo a la solicitud obliga a tocar la firma, el `INSERT`, la llamada y la respuesta de las líneas 196–198.
- **Prioridad:** media, porque complica cada cambio en la tabla de solicitudes, aunque hoy no se comprobó una falla.
- **Principio:** Clean Code, funciones con pocos argumentos.
- **Transversal:** No. Solo la usa `registrar`.
- **Refactoring propuesto:** Introduce Parameter Object: una clase `Solicitud` (o `NuevaSolicitud`) que agrupe los datos y se pase entera a `guardar_solicitud`.

### 2. Duplicated Code / Dead Code: cálculo de prioridad
- **Ubicación:** `calcular_prioridad`, líneas 124–130, y el bloque de prioridad de `registrar`, líneas 148–161
- **Evidencia:** `# TODO: usar esto en registrar` en la línea 125, mientras `registrar` repite la misma regla con `if data["tipo"] == "MESA": p = 1 ...`
- **Casos:** 3
- **Impacto:** la regla de prioridad por tipo está escrita dos veces y las dos versiones no son iguales: la de `registrar` sube a 1 las descripciones con "urgente" (caso 3) y la de `calcular_prioridad` no. Quien lea `calcular_prioridad` cree que esa es la regla del sistema, pero no se usa en ningún lado.
- **Riesgo de mantenimiento:** si alguien cambia la regla en `calcular_prioridad` no cambia nada. Si alguien cumple el TODO y la empieza a usar, se pierde sin querer la regla de "urgente".
- **Prioridad:** media, porque hoy el comportamiento es correcto, pero es muy fácil romperlo en un cambio.
- **Principio:** DRY y Clean Code (no dejar código muerto ni TODOs sin resolver).
- **Transversal:** No.
- **Refactoring propuesto:** pasar la regla de "urgente" a `calcular_prioridad`, usarla desde `registrar` y borrar el bloque repetido.

### 3. Long Method / violación de SRP en `registrar`
- **Ubicación:** `registrar`, líneas 133–198
- **Evidencia:** en una sola función de 66 líneas: validaciones (136–145), cálculo de prioridad (148–164), área según tipo (167–174), canal (176–178), guardado (181–182), historial (183–185), notificación (190–194) y armado de la respuesta (196–198)
- **Casos:** —
- **Impacto:** para cambiar una sola regla (por ejemplo, el área de un tipo) hay que leer y entender toda la función. No se puede probar la regla de prioridad o de área por separado: hay que pasar por el endpoint y por la base.
- **Riesgo de mantenimiento:** cada cambio toca la misma función, lo que aumenta la chance de romper otra parte sin darse cuenta.
- **Prioridad:** media, porque complica el mantenimiento y los tests, aunque hoy funciona con datos válidos.
- **Principio:** SRP.
- **Transversal:** Sí. El registro en historial y la notificación (183–194) se repiten en `proc_estado` y `asignar` (hallazgo 8 de Javier).
- **Refactoring propuesto:** Extract Method: `validar_solicitud`, `calcular_prioridad`, `determinar_area`, `registrar_historial` y `notificar_estudiante`.

### 4. Manejo de errores inconsistente
- **Ubicación:** `registrar`, líneas 137, 141, 143, 145 y 164
- **Evidencia:** `return {"error": "falta estudiante"}` en lugar de `raise HTTPException(...)`
- **Casos:** 5, 6, 7, 8, 12 y 13 (errores con 200), 9 y 10 (500), 16 (422 con otro formato)
- **Impacto:** el cliente recibe 200 tanto si la solicitud se creó como si no, y tiene que leer el body para darse cuenta. Hay además dos formatos de error distintos (`error` y `detail`).
- **Riesgo de mantenimiento:** un frontend o un test que solo mire el código HTTP va a tomar un error como un alta correcta.
- **Prioridad:** alta, porque hay defectos comprobados en las pruebas.
- **Principio:** Clean Code, usar excepciones en lugar de devolver códigos de error.
- **Transversal:** Sí. Es el mismo hallazgo que el 3 de Cristian y el 1 de Javier.
- **Refactoring propuesto:** reemplazar cada `return {"error": ...}` por `HTTPException` con 422 (o el código que se acuerde en el grupo) y responder 201 en el alta.

### 5. Falta de modelo de entrada y validación inconsistente
- **Ubicación:** `registrar`, líneas 134 (`data: dict`), 142–145, 163 y 176–178
- **Evidencia:** `if "descripcion" not in data or len(data["descripcion"]) < 10:` y `if p not in [1, 2, 3]:`
- **Casos:** 9, 10, 11, 13, 14 y 15
- **Impacto:** como el body es un `dict` sin tipos, cada campo se valida a mano y de forma incompleta: una descripción `null` o numérica rompe el servidor (casos 9 y 10), una descripción en blanco se acepta (caso 11) y acepta `true` como prioridad (caso 14). Además el criterio cambia según el campo: la prioridad inválida se rechaza pero el canal inválido se cambia a `WEB` sin avisar (caso 15).
- **Riesgo de mantenimiento:** cada campo nuevo necesita su validación manual y es fácil olvidar un caso. Se guardan datos que después pueden romper otras partes (búsqueda, reporte).
- **Prioridad:** alta, porque hay defectos comprobados (dos errores 500 y datos inválidos guardados).
- **Principio:** Clean Code (manejo de errores) y SRP: el endpoint valida, además de registrar.
- **Transversal:** Sí. Es el mismo hallazgo que el 5 de Cristian y el 5 de Javier.
- **Refactoring propuesto:** un modelo de entrada con Pydantic (`SolicitudIn`) con tipos, `Literal` para tipo y canal, y longitud mínima sin contar espacios.

### 6. Switch Statements: área y prioridad según el tipo
- **Ubicación:** `registrar`, líneas 142 (lista de tipos), 150–159 (prioridad) y 167–174 (área)
- **Evidencia:** `if data["tipo"] == "CERT" or data["tipo"] == "BAJA": a = "Alumnado" elif ...`
- **Casos:** —
- **Impacto:** la información de cada tipo (si es válido, su prioridad y su área) está repartida en tres cadenas de `if` distintas, más `calcular_prioridad`.
- **Riesgo de mantenimiento:** agregar un tipo nuevo obliga a tocar al menos tres lugares de `registrar`, `calcular_prioridad` y la lista de áreas de `crear_responsable`. Si se olvida uno, el tipo nuevo cae en el `else` y queda en Coordinación con prioridad 2 sin que nadie lo note.
- **Prioridad:** media, porque complica la evolución del sistema, aunque hoy funciona.
- **Principio:** OCP.
- **Transversal:** Sí. Se cruza con el hallazgo 13 de Cristian (áreas).
- **Refactoring propuesto:** un diccionario de configuración por tipo (tipo → área y prioridad por defecto) que usen la validación, la prioridad y el área.

### 7. Excepción silenciada (`except:` sin tipo)
- **Ubicación:** `registrar`, líneas 190–194
- **Evidencia:** `except:` seguido de `pass`
- **Casos:** 17
- **Impacto:** cualquier error al notificar se pierde sin dejar rastro, no solo los errores de archivo. Por ejemplo, si `est[4]` llegara a ser `None`, la concatenación de la línea 192 fallaría con `TypeError` y nadie se enteraría de que no se notificó. Tampoco se controla que haya a quién notificar: con un estudiante sin email se registra "Se envio mail a :" como si se hubiera enviado (caso 17).
- **Riesgo de mantenimiento:** los errores de programación en la notificación quedan ocultos y son muy difíciles de encontrar.
- **Prioridad:** media. El caso 17 muestra que la notificación no se controla, pero el `except` en sí no se pudo provocar desde la API.
- **Principio:** Clean Code, manejo de errores (no silenciar excepciones).
- **Transversal:** Sí. Es el mismo patrón que el hallazgo 7 de Javier.
- **Refactoring propuesto:** Extract Method `notificar_estudiante`, capturar solo `OSError` y registrar el error en lugar de ignorarlo.

### 8. Magic Numbers: índice de columna
- **Ubicación:** `registrar`, línea 192
- **Evidencia:** `est[4]`
- **Casos:** —
- **Impacto:** para saber que `est[4]` es el email hay que ir a la creación de la tabla `estudiantes` y contar columnas.
- **Riesgo de mantenimiento:** si se agrega o reordena una columna de `estudiantes`, la notificación se manda a otro dato sin ningún error.
- **Prioridad:** media, porque un cambio en la tabla rompería la notificación sin avisar.
- **Principio:** Clean Code, nombres significativos (evitar números mágicos).
- **Transversal:** Sí. Se cruza con el hallazgo 8 de Cristian y el 9 de Javier.
- **Refactoring propuesto:** usar `sqlite3.Row` como `row_factory` y acceder por nombre (`est["email"]`).

### 9. Nombres poco expresivos y código comentado
- **Ubicación:** `registrar`, líneas 148 (`p`), 168–174 (`a`), 180 (`f`), 181 (`id`) y 186–187
- **Evidencia:** `id = guardar_solicitud(...)` y `# c.execute("UPDATE estudiantes SET carrera = 'TUP' WHERE id = ?", ...)`
- **Casos:** —
- **Impacto:** `p`, `a` y `f` no dicen qué guardan, e `id` tapa la función `id()` de Python. El código comentado no se sabe si se puede borrar o si alguien lo necesita.
- **Riesgo de mantenimiento:** confunde a quien lee y mantiene el código.
- **Prioridad:** baja, porque afecta principalmente la legibilidad.
- **Principio:** Clean Code, nombres significativos y no dejar código comentado.
- **Transversal:** Sí, en cuanto a nombres. Se cruza con el hallazgo 12 de Cristian y el 12 de Javier.
- **Refactoring propuesto:** Rename Variable (`prioridad`, `area`, `fecha`, `solicitud_id`) y borrar las líneas 186–187.

---

## Para la puesta en común del grupo

- **Hallazgos transversales:** 3 (historial y notificación, con Javier), 4 (manejo de errores, con Cristian y Javier), 5 (modelo de entrada, con Cristian y Javier), 6 (reglas por tipo y áreas, con Cristian), 7 (excepción silenciada, con Javier), 8 (índices de columna, con Cristian y Javier) y 9 (nombres, con todos).
- **Coordinación con otros integrantes:** el 4 y el 5 conviene resolverlos como cambio transversal antes de los refactors individuales (lo coordina Cristian). El 3 y el 7 se pueden resolver con una sola función de historial y notificación que usen `registrar`, `proc_estado` y `asignar`.
- **Propuestas para la tabla grupal:** manejo de errores inconsistente, falta de modelo de entrada, excepciones silenciadas y acceso a columnas por índice, porque aparecen en todo `main.py`.
- **Refactoring obligatorio que garantizo:** Introduce Parameter Object, con el hallazgo 1.
