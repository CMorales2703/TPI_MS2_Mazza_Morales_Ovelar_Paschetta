# Decisión técnica 01 — Estructura del proyecto y conexión a la base

**Estado:** aplicada en la rama `refactor/conexion` (Fase 3, cambios transversales)
**Responsable:** Cristian Morales
**Hallazgos que la originan:** ver las fichas de `docs/diagnostico/` (C = Cristian, J = Javier, B = Bruno, G = Gaston)

## Problema

Todo el sistema estaba en `main.py`: conexión global, creación de tablas, datos de prueba y los diez endpoints. Eso generaba tres problemas:

- **Global State y efectos al importar (C1, C2):** `import main` abría la base, creaba las tablas y cargaba los datos de prueba. No se podía usar otra base sin trucos (los tests cambiaban de carpeta y reimportaban el módulo).
- **Un solo archivo para cuatro personas:** cualquier refactoring de un integrante chocaba con los de los demás en cada merge.
- **Responsabilidades mezcladas (SRP):** acceso a datos, reglas de negocio y endpoints en el mismo lugar.

## Decisión

### Estructura

```
main.py                  crea la aplicación (crear_app) y registra los routers
app/
  db.py                  conexión, creación de tablas y dependencia get_db
  seed.py                datos de prueba
  routers/
    estudiantes.py       Cristian
    responsables.py      Cristian
    solicitudes.py       Gaston  (registrar)
    estados.py           Javier  (cambio de estado y asignación)
    consultas.py         Bruno   (búsqueda, detalle y reporte)
```

Módulos previstos, que crea cada responsable en su refactoring cuando los necesite:

| Módulo | Para qué | Hallazgos |
|---|---|---|
| `app/dominio.py` | tipos, áreas, estados, transiciones y reglas por tipo | C6, C13, J2, J3, J10, G2, G6, B8 |
| `app/schemas.py` | modelos Pydantic de entrada | C4, C5, J5, G5 |
| `app/servicios/notificaciones.py` | historial y notificación al estudiante | J7, J8, G3, G7 |

### Conexión a la base

- `crear_app(ruta_db)` crea la aplicación sobre la base indicada. `main.app = crear_app()` usa `solicitudes.db`, así que `uvicorn main:app` funciona igual que antes.
- La base se prepara **al arrancar la aplicación** (`lifespan`): crea las tablas y, si la base está vacía, carga los datos de prueba. Importar `main` ya no toca la base.
- Cada request recibe su propia conexión con `Depends(get_db)`, que la cierra al terminar. Desaparecen las variables globales `conn` y `c`. Principio: **DIP** (los endpoints reciben la conexión en lugar de crearla).

### Tests

- El fixture `client` crea una aplicación por test con `crear_app(<base temporal>)`. Ya no hace falta reimportar `main`.
- Sigue cambiando a una carpeta temporal porque `notificaciones.log` se escribe en la carpeta actual. Se resuelve cuando se extraiga la notificación (J7, J8, G7).
- `conexion_db` da acceso directo a la base del test, para cargar datos que la API no permite (casos 17 y 18 de Bruno).

## Alternativas descartadas

- **Variable de entorno con la ruta de la base:** más simple, pero es otro estado global, implícito para quien lee el código.
- **`app.dependency_overrides[get_db]` en los tests:** reemplaza la conexión de los requests, pero no la del arranque, que seguiría usando `solicitudes.db`.
- **Dejar los endpoints en `main.py` hasta el refactor de cada uno:** los cuatro modificarían el mismo archivo en paralelo.

## Cómo se verificó

- Los 47 tests de la Fase 2 pasan después de cada commit, **sin cambiar ningún assert**. En los tests solo cambió la infraestructura: `conftest.py` y la forma de borrar datos en un test de `test_reporte.py`.
- `import main` en una carpeta vacía no crea ningún archivo.
- `uvicorn main:app` levanta el sistema, crea `solicitudes.db` con los datos de prueba y responde igual que antes.
- Al mover los endpoints a los routers, las líneas de código son las mismas (solo cambió el archivo donde están).

## Lo que no cambia todavía

El comportamiento de los endpoints es el mismo, incluidos los defectos documentados. Pasar los errores de 200 a 422 (C3, J1, G4) es una corrección de defecto, no refactoring: va en commits aparte, con el criterio de códigos HTTP unificado por el grupo.
