# Sistema de Gestión de Solicitudes Académicas

API para registrar y gestionar solicitudes de estudiantes (certificados, equivalencias, mesas especiales, reclamos y bajas).

> Versión inicial del sistema base (tag `estado-inicial`). Datos de prueba sintéticos.

## Requisitos

- Python 3.10 o superior

## Instalación y uso

```bash
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Abrir http://127.0.0.1:8000/docs para probar los endpoints.

La base `solicitudes.db` se crea sola con datos de prueba la primera vez. Para volver al estado inicial, borrar `solicitudes.db` y `notificaciones.log` y reiniciar.

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

## Tecnologías

- FastAPI
- SQLite
