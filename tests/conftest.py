# PROVISORIO: armado por Cristian para la Fase 2.
# Coordinar con Bruno antes de mergear.

import sys
import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Crea una base temporal por test, inicializada con datos de prueba.

    Al importar main se cargan 4 estudiantes, 5 responsables y 6 solicitudes.
    """
    # (1) Pararse en una carpeta temporal vacía
    monkeypatch.chdir(tmp_path)

    # (2) Asegurar que main se importe de cero
    sys.modules.pop("main", None)

    # (3) Importar main
    main = importlib.import_module("main")

    # (4) Entregar el cliente al test y, al terminar, limpiar
    try:
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.conn.close()
        sys.modules.pop("main", None)


@pytest.fixture
def client_sin_excepciones(client):
    """Mismo sistema y misma base que client, pero un error interno
    devuelve 500 en lugar de cortar el test."""
    with TestClient(client.app, raise_server_exceptions=False) as c:
        yield c


# --- datos que reproducen los defectos del reporte ---------------------------

def _insertar_solicitud(descripcion, fecha_alta):
    """Inserta una solicitud en la base del test en curso."""
    main = sys.modules["main"]
    main.c.execute(
        "INSERT INTO solicitudes "
        "(estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, "
        "area, fecha_alta, fecha_mod, canal, obs) "
        "VALUES (1, 'CERT', ?, 3, 'PEND', NULL, 'Alumnado', ?, ?, 'WEB', '')",
        (descripcion, fecha_alta, fecha_alta),
    )
    main.conn.commit()


@pytest.fixture
def solicitud_con_fecha_invalida(client):
    """Solicitud con fecha_alta en un formato que el reporte no interpreta.
    Reproduce el caso 17 del diagnostico."""
    _insertar_solicitud("Test - fecha sin hora", "2026-11-01")


@pytest.fixture
def solicitud_con_fecha_nula(client):
    """Solicitud con fecha_alta nula. Reproduce el caso 18."""
    _insertar_solicitud("Test - fecha nula", None)
