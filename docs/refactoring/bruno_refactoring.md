# Fase 3 — Refactoring: búsqueda, detalle y reporte

**Integrante:** Bruno Maza
**Alcance:** `app/routers/consultas.py` (`GET /solicitudes`, `GET /solicitudes/{id}`, `GET /reporte`)
**Rama:** `refactor/bruno-consultas`
**Técnica principal:** Extract Method
**Verificación:** la suite completa pasa después de cada commit (64 tests al empezar, 67 con los 3 nuevos), sin cambiar ningún assert de la Fase 2

## Resumen

| # | Refactoring | Técnica | Hallazgos | Principio |
|---|---|---|---|---|
| T | Tests del cálculo de vencidas (antes de B3) | — | — | — |
| B1 | Conversión de fila a diccionario en un solo lugar | Extract Method | 3, 4 (parcial) | DRY |
| B2 | El conteo por clave, una sola vez | Extract Method | 6 | DRY |
| B3 | Las reglas de vencimiento con nombre | Extract Method | 8 | Clean Code: evitar números y textos mágicos |
| B4 | El porcentaje fuera del cuerpo de `reporte` | Extract Method | 5 | SRP |

Los hallazgos 1, 2, 7, 9, 10, 11, 12 y 13 no se resuelven acá: ver [Hallazgos que quedan fuera](#hallazgos-que-quedan-fuera).

## T — Tests del cálculo de vencidas

Antes de tocar las reglas de vencimiento se comprobó qué las protegía: se cambió `dias_limite` para que devolviera 999 en lugar de 2 y se corrió la suite. **Los 64 tests siguieron en verde.**

El contenido de `vencidas` no estaba cubierto por ninguna prueba. Los siete tests de `reporte` de la Fase 2 verificaban los conteos y el porcentaje, pero ninguno miraba qué hay adentro de esa lista. Un error en el cálculo de plazos habría pasado inadvertido, justo en la parte que este refactor iba a modificar.

**Antes:** ningún test fijaba el plazo de cada prioridad, ni qué estados vencen, ni la cantidad de días que se informa.

**Después:** 3 tests nuevos en `tests/test_reporte.py`, con el mismo criterio de línea de base de la Fase 2.

```python
def test_una_solicitud_abierta_y_vieja_figura_como_vencida(client, conexion_db):
    """Una solicitud de prioridad 3 con 15 dias abiertos supera el limite de 10."""

def test_el_limite_de_vencimiento_depende_de_la_prioridad(client, conexion_db):
    """A los 7 dias, la prioridad 1 (limite 2) vencio y la prioridad 3 (limite 10) no."""

def test_una_solicitud_cerrada_nunca_figura_como_vencida(client, conexion_db):
    """El vencimiento solo corre para las solicitudes que siguen abiertas."""
```

Los tres insertan solicitudes con una antigüedad calculada en el momento (`datetime.now() - timedelta(days=n)`), no con fechas fijas, para que no caduquen con el paso del tiempo.

Los tres pasan sobre el código sin refactorizar — se verificó antes de aplicar las extracciones, y es lo que los convierte en tests de caracterización y no en tests escritos para que el código nuevo dé bien. Van en un commit aparte, anterior al del refactor. Repetida la mutación, ahora falla `test_el_limite_de_vencimiento_depende_de_la_prioridad`.

## B1 — Extract Method, conversión de fila a diccionario (hallazgos 3 y 4)

**Antes:** el mismo diccionario de doce campos, escrito dos veces. Agregar una columna a la tabla obligaba a modificar los dos lugares; corregir uno solo dejaba el listado y el detalle devolviendo estructuras distintas para la misma entidad, sin ningún error que lo señalara.

En `buscar`:

```python
res = []
for r in rows:
    res.append({"id": r[0], "estudiante_id": r[1], "tipo": r[2], "descripcion": r[3], "prioridad": r[4],
                "estado": r[5], "responsable_id": r[6], "area": r[7], "fecha_alta": r[8], "fecha_mod": r[9],
                "canal": r[10], "obs": r[11]})
return res
```

En `getSolicitud`:

```python
d = {"id": r[0], "estudiante_id": r[1], "tipo": r[2], "descripcion": r[3], "prioridad": r[4], "estado": r[5],
     "responsable_id": r[6], "area": r[7], "fecha_alta": r[8], "fecha_mod": r[9], "canal": r[10], "obs": r[11]}
```

**Después:** una sola definición y dos usos de una línea cada uno.

```python
def fila_a_solicitud(fila):
    """Convierte una fila de la tabla solicitudes en un diccionario."""
    return {
        "id": fila[0],
        "estudiante_id": fila[1],
        "tipo": fila[2],
        "descripcion": fila[3],
        "prioridad": fila[4],
        "estado": fila[5],
        "responsable_id": fila[6],
        "area": fila[7],
        "fecha_alta": fila[8],
        "fecha_mod": fila[9],
        "canal": fila[10],
        "obs": fila[11],
    }
```

```python
return [fila_a_solicitud(r) for r in rows]
```

```python
d = fila_a_solicitud(r)
```

Del hallazgo 4 resuelve la parte que corresponde a esta duplicación: los doce índices posicionales quedan en un único lugar, de modo que un cambio en el orden de las columnas se corrige una vez. Los índices que `reporte` usa sobre la misma tabla (`s[2]`, `s[4]`, `s[5]`, `s[7]`, `s[8]`) siguen siendo posicionales; eliminarlos requiere `row_factory`, que es el camino que tomaron Cristian y Gastón en sus partes.

## B2 — Extract Method, el conteo por clave (hallazgo 6)

**Antes:** el mismo bloque de cuatro líneas, tres veces, cambiando solo el índice y el diccionario.

```python
if s[5] in por_estado:
    por_estado[s[5]] = por_estado[s[5]] + 1
else:
    por_estado[s[5]] = 1
if s[2] in por_tipo:
    por_tipo[s[2]] = por_tipo[s[2]] + 1
else:
    por_tipo[s[2]] = 1
if s[7] in por_area:
    por_area[s[7]] = por_area[s[7]] + 1
else:
    por_area[s[7]] = 1
```

**Después:**

```python
def contar(conteos, clave):
    """Suma uno al contador de esa clave."""
    conteos[clave] = conteos.get(clave, 0) + 1
```

```python
contar(por_estado, s[5])
contar(por_tipo, s[2])
contar(por_area, s[7])
```

Doce líneas pasan a tres. Agregar un cuarto agrupamiento es una línea más, no copiar el bloque otra vez.

## B3 — Extract Method, las reglas de vencimiento (hallazgo 8)

**Antes:** qué estados se consideran cerrados y cuántos días tiene cada prioridad estaban escritos dentro del cálculo, sin nombre. Además, la antigüedad se calculaba dos veces en el mismo `if`.

```python
if s[5] not in ["RES", "RECH", "CANC"]:
    fa = datetime.strptime(s[8], "%Y-%m-%d %H:%M:%S")
    if s[4] == 1:
        dias = 2
    elif s[4] == 2:
        dias = 5
    else:
        dias = 10
    if (hoy - fa).days > dias:
        vencidas.append({"id": s[0], "tipo": s[2], "prioridad": s[4], "dias": (hoy - fa).days})
```

**Después:** tres funciones con nombre y el cálculo de antigüedad una sola vez.

```python
def esta_cerrada(estado):
    """Una solicitud cerrada ya no puede vencer."""
    return estado in ("RES", "RECH", "CANC")


def dias_limite(prioridad):
    """Dias que una solicitud puede permanecer abierta segun su prioridad."""
    if prioridad == 1:
        return 2
    if prioridad == 2:
        return 5
    return 10


def dias_abierta(fecha_alta, hoy):
    """Dias transcurridos desde el alta de la solicitud."""
    return (hoy - datetime.strptime(fecha_alta, "%Y-%m-%d %H:%M:%S")).days
```

```python
if not esta_cerrada(s[5]):
    dias = dias_abierta(s[8], hoy)
    if dias > dias_limite(s[4]):
        vencidas.append({"id": s[0], "tipo": s[2], "prioridad": s[4], "dias": dias})
```

Las tres reglas de negocio ahora tienen nombre y se pueden leer sin reconstruir el algoritmo. `dias_limite` queda además como el lugar único donde cambiar un plazo.

## B4 — Extract Method, el porcentaje (hallazgo 5)

**Antes:** el cálculo final, con su guarda contra la división por cero, ocupaba cuatro líneas del cuerpo de `reporte`.

```python
resueltas = por_estado.get("RES", 0)
porc = 0
if total > 0:
    porc = round(resueltas * 100 / total, 2)
return {"total": total, "por_estado": por_estado, "por_tipo": por_tipo, "por_area": por_area,
        "porcentaje_resueltas": porc, "vencidas": vencidas}
```

**Después:**

```python
def porcentaje_resueltas(por_estado, total):
    """Porcentaje de solicitudes en estado RES sobre el total."""
    if total == 0:
        return 0
    return round(por_estado.get("RES", 0) * 100 / total, 2)
```

```python
return {
    "total": total,
    "por_estado": por_estado,
    "por_tipo": por_tipo,
    "por_area": por_area,
    "porcentaje_resueltas": porcentaje_resueltas(por_estado, total),
    "vencidas": vencidas,
}
```

Con las cuatro extracciones juntas, el bucle de `reporte` pasa de 25 líneas a 7 y se lee casi como la frase que describe lo que hace. Es lo que atiende el hallazgo 5: la función seguía teniendo una sola responsabilidad de cara afuera, pero mezclaba cuatro niveles de detalle en el mismo cuerpo.

## Decisiones de diseño

| Pregunta | Decisión | Por qué | Alternativa descartada |
|---|---|---|---|
| ¿Dónde viven las funciones extraídas? | En `app/routers/consultas.py`, a nivel de módulo | Las usan solo estos tres endpoints; moverlas a `app/dominio.py` sin un segundo consumidor sería anticipar | Llevarlas a `app/dominio.py` junto con `AREAS` y `REGLAS_POR_TIPO` |
| ¿`fila_a_solicitud` o `row_factory`? | La función | `row_factory` cambia el tipo de todas las filas del cursor y toca también el historial, que tiene su propia forma; era un cambio más grande del que esta rama necesitaba | `conn.row_factory = sqlite3.Row`, como en R2 de Cristian y G5 de Gastón |
| ¿Se corrige la inyección SQL acá? | No | Cambia el comportamiento a propósito y haría fallar dos tests de la Fase 2; corresponde a un PR de tipo `fix`, no `refactor` | Parametrizar la consulta en el mismo PR |
| ¿`dias_limite` con `if` o con un diccionario? | Con `if` | Es la traslación literal del bloque original, que es lo que corresponde a una extracción: mover el código, no reescribirlo | `{1: 2, 2: 5}` con `.get(prioridad, 10)` |
| ¿`esta_cerrada` o una constante? | Función | Deja el punto único donde después se puede unificar con los estados que usa `proc_estado`, que es el riesgo que señalaba el hallazgo 8 | `ESTADOS_CERRADOS = ("RES", "RECH", "CANC")` a nivel de módulo |
| ¿Se extrae también el armado de la consulta de `buscar`? | No | Es el mismo código que hay que reescribir al parametrizar; extraerlo ahora obligaría a rehacerlo en el PR de corrección | `armar_consulta(...)` con los nueve filtros |
| ¿Los tests nuevos van en este PR? | Sí, en un commit anterior al del refactor | Sin ellos el refactor de B3 no estaba cubierto; el orden de los commits deja ver que la cobertura vino primero | Un PR separado de tipo `test` antes de este |

## Hallazgos que quedan fuera

| Hallazgo | Por qué no va en esta rama | Dónde va |
|---|---|---|
| 1. Inyección SQL por concatenación | Parametrizar la consulta cambia el comportamiento: los tests `DEFECTO` de inyección y de la comilla simple pasan a fallar, que es lo esperado | PR de tipo `fix`, con los dos tests actualizados en el mismo cambio |
| 2. Fallo del reporte por fecha no parseable | Ídem: contemplar el dato inválido cambia el 500 por un 200 | PR de tipo `fix`, con los tres tests del reporte actualizados |
| 7. Long Parameter List en `buscar` | Introduce Parameter Object sobre los nueve filtros toca la firma del endpoint y, con FastAPI, la forma en que se declaran los query params | Junto con el modelo de entrada que Cristian y Gastón dejaron para `app/schemas.py` |
| 9. Orden inválido ignorado en silencio | Devolver 422 es corrección de defecto | PR de tipo `fix` |
| 10. Falta de validación de fechas | Ídem | PR de tipo `fix`, previsiblemente con el mismo modelo de entrada del hallazgo 7 |
| 11. Búsqueda sensible a mayúsculas | Ídem | PR de tipo `fix` |
| 12. Inconsistent Naming (`getSolicitud`) | Renombrar la función no cambia la ruta ni la respuesta, así que entraría en un refactor; se deja afuera para no mezclar un cambio de nombre público con las extracciones | Cambio transversal de nombres, acordado con el grupo |
| 13. Mensaje de error poco informativo | Cambia el cuerpo de la respuesta | PR de tipo `fix` |

## Cómo se verificó

- Suite completa después de cada commit: 67 passed. Ningún assert de la Fase 2 cambió.
- Prueba de mutación sobre cada extracción: alterar `contar` para que sume dos hace fallar `test_los_conteos_suman_el_total`; alterar `dias_limite` hace fallar `test_el_limite_de_vencimiento_depende_de_la_prioridad`. Las dos fallas confirman que los tests son sensibles a los cambios en el código extraído.
- Los tres tests nuevos pasan también sobre el código sin refactorizar.
- Evidencia: `docs/evidencias/fase3/bruno/bruno_fase3_01_suite_completa.png`.

El warning `StarletteDeprecationWarning` sobre `httpx` viene de las versiones de las librerías, no del código del sistema. No afecta los resultados.
