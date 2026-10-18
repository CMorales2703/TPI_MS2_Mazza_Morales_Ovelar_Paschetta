# Sistema de Gestión de Solicitudes Académicas

API para registrar y gestionar solicitudes de estudiantes (certificados, equivalencias, mesas especiales, reclamos y bajas).

Trabajo Práctico Integrador — Metodología de Sistemas II — Tecnicatura Universitaria en Programación a Distancia (UTN).

> Los datos de prueba son sintéticos.

## Integrantes

| Integrante | Usuario de GitHub |
|---|---|
| Mazza | |
| Cristian Morales | [@CMorales2703](https://github.com/CMorales2703) |
| Ovelar | |
| Paschetta | |

## Requisitos

- Python 3.10 o superior
- Git

## Uso rápido

Los scripts crean el entorno virtual e instalan las dependencias la primera vez (y cuando cambian los `requirements`). Después solo levantan el sistema.

| Acción | Windows | Linux / macOS |
|---|---|---|
| Levantar el sistema | `.\run.bat` (o doble clic) | `./run.sh` |
| Correr los tests | `.\run.bat test` | `./run.sh test` |
| Volver a los datos iniciales | `.\run.bat reset` | `./run.sh reset` |

En Windows también se puede usar `.\run.ps1` si PowerShell tiene habilitados los scripts.

Si se prefiere hacerlo a mano, los pasos están abajo.

## Instalación manual

### 1. Clonar el repositorio

```bash
git clone https://github.com/CMorales2703/TPI_MS2_Mazza_Morales_Ovelar_Paschetta.git
cd TPI_MS2_Mazza_Morales_Ovelar_Paschetta
```

### 2. Crear y activar el entorno virtual

**Windows (PowerShell)**

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

**Windows (CMD)**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Cuando el entorno está activo, la terminal muestra `(.venv)` al principio de la línea.

### 3. Instalar dependencias

Para correr el sistema:

```bash
pip install -r requirements.txt
```

Para desarrollar y correr los tests:

```bash
pip install -r requirements-dev.txt
```

## Uso

```bash
uvicorn main:app --reload
```

Abrir http://127.0.0.1:8000/docs para probar los endpoints.

La base `solicitudes.db` se crea sola con datos de prueba la primera vez. Para volver al estado inicial, borrar `solicitudes.db` y `notificaciones.log` y reiniciar.

## Tests

```bash
pytest
```

## Funcionalidades

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/estudiantes` | Alta de estudiante |
| GET | `/estudiantes` | Listado de estudiantes |
| POST | `/responsables` | Alta de responsable |
| GET | `/responsables` | Listado de responsables |
| POST | `/solicitudes` | Registrar solicitud |
| GET | `/solicitudes` | Buscar / filtrar solicitudes |
| GET | `/solicitudes/{id}` | Detalle con historial |
| PUT | `/solicitudes/{id}/estado` | Cambiar estado |
| PUT | `/solicitudes/{id}/responsable` | Asignar responsable |
| GET | `/reporte` | Reporte resumido |

### Estados

`PEND` → `ASIG` → `EN_PROC` → `RES` / `RECH`. Una solicitud `PEND` o `ASIG` puede pasar a `CANC`.

### Ejemplo: registrar solicitud

```json
{
  "estudiante_id": 1,
  "tipo": "MESA",
  "descripcion": "Solicito mesa especial por viaje laboral",
  "canal": "WEB"
}
```

Tipos válidos: `CERT`, `EQUIV`, `MESA`, `RECLAMO`, `BAJA`.

## Forma de trabajo

- Ramas principales:
  - `main`: versión estable. Contiene el sistema base y, al cierre, la versión refactorizada final.
  - `dev`: rama de trabajo (rama por defecto durante el desarrollo).
- `main` y `dev` están protegidas: todo cambio entra por **Pull Request** con al menos **una aprobación** de otro integrante.
- Cada cambio se hace en una rama creada desde `dev` y vuelve a `dev` por Pull Request. Al terminar, `dev` se integra a `main` con un último Pull Request.
- Ramas por tipo de cambio: `test/<tema>`, `refactor/<tema>`, `docs/<tema>`, `chore/<tema>`.
- Commits con prefijo: `refactor:`, `test:`, `docs:`, `chore:`, `fix:`.
- Tags del trabajo:

| Tag | Marca |
|---|---|
| `estado-inicial` | Sistema base sin modificar |
| `etapa-diagnostico` | Cierre del diagnóstico |
| `etapa-refactoring` | Cierre de los refactorings |
| `etapa-pruebas` | Cierre de la verificación |
| `etapa-docs` | Cierre de la documentación |
| `estadorefactorizado` | Versión final |

Los tags de etapa se crean sobre `dev`; el tag `estadorefactorizado` se crea sobre `main` una vez integrada la versión final.

El checklist de code review, las decisiones técnicas y las evidencias están en la carpeta [`docs/`](docs/).

## Tecnologías

- Python
- FastAPI
- SQLite
- pytest
