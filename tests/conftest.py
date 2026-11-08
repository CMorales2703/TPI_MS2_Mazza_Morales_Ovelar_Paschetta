"""Configuración común de los tests.

Cada test usa una aplicación creada sobre su propia base temporal, cargada con
los datos de prueba al arrancar: 4 estudiantes, 5 responsables y 6 solicitudes.
"""

import pytest
from fastapi.testclient import TestClient

from app.db import conectar
from main import crear_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Cliente sobre una aplicación con una base nueva para este test."""
    # notificaciones.log se escribe en la carpeta actual: que quede en la temporal
    monkeypatch.chdir(tmp_path)

    app = crear_app(tmp_path / "solicitudes_test.db")
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client_sin_excepciones(client):
    """Mismo sistema y misma base que client, pero un error interno
    devuelve 500 en lugar de cortar el test."""
    with TestClient(client.app, raise_server_exceptions=False) as c:
        yield c


# --- datos que reproducen los defectos del reporte ---------------------------


@pytest.fixture
def conexion_db(client):
    """Conexión directa a la base del test, para preparar datos que la API no permite cargar."""
    conn = conectar(client.app.state.ruta_db)
    yield conn
    conn.close()


def _insertar_solicitud(conn, descripcion, fecha_alta):
    """Inserta una solicitud en la base del test en curso."""
    conn.execute(
        "INSERT INTO solicitudes "
        "(estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, "
        "area, fecha_alta, fecha_mod, canal, obs) "
        "VALUES (1, 'CERT', ?, 3, 'PEND', NULL, 'Alumnado', ?, ?, 'WEB', '')",
        (descripcion, fecha_alta, fecha_alta),
    )
    conn.commit()


@pytest.fixture
def solicitud_con_fecha_invalida(conexion_db):
    """Solicitud con fecha_alta en un formato que el reporte no interpreta.
    Reproduce el caso 17 del diagnostico."""
    _insertar_solicitud(conexion_db, "Test - fecha sin hora", "2026-11-01")


@pytest.fixture
def solicitud_con_fecha_nula(conexion_db):
    """Solicitud con fecha_alta nula. Reproduce el caso 18."""
    _insertar_solicitud(conexion_db, "Test - fecha nula", None)
