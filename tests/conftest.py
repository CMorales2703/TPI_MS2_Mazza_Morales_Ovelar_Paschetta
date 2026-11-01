"""
Configuracion comun de los tests.

main.py abre la base de datos, crea las tablas e inserta los datos de prueba
en el momento en que se lo importa (lineas 7 a 54), fuera de cualquier funcion.
Por eso, antes de importarlo, este archivo se para en una carpeta temporal:
asi el sistema crea su propia base de prueba y la base real (solicitudes.db)
no se toca.

Cuando se refactorice ese acoplamiento, este rodeo se puede simplificar.
"""

import os
import shutil
import sys
import tempfile

import pytest

# --- preparacion previa a importar el sistema --------------------------------

RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_carpeta_temporal = tempfile.mkdtemp(prefix="tpi_tests_")

os.chdir(_carpeta_temporal)          # la base se crea aca, no en el proyecto
sys.path.insert(0, RAIZ_PROYECTO)    # para poder importar main

import main                                      # noqa: E402
from fastapi.testclient import TestClient        # noqa: E402


@pytest.fixture(scope="session")
def cliente():
    """
    Cliente HTTP que llama a los endpoints sin levantar el servidor.

    raise_server_exceptions=False hace que un error interno devuelva un 500
    en lugar de cortar el test. Es necesario para poder verificar los casos
    que hoy rompen el sistema (casos 10, 17 y 18 del diagnostico).
    """
    return TestClient(main.app, raise_server_exceptions=False)


@pytest.fixture
def solicitud_con_fecha_invalida():
    """
    Inserta una solicitud con fecha_alta en un formato que el reporte no puede
    interpretar, y la borra al terminar el test. Reproduce el caso 17.
    """
    _insertar_solicitud("Test - fecha sin hora", "2026-11-01")
    yield
    _borrar_solicitudes_de_prueba()


@pytest.fixture
def solicitud_con_fecha_nula():
    """
    Inserta una solicitud con fecha_alta nula y la borra al terminar.
    Reproduce el caso 18.
    """
    _insertar_solicitud("Test - fecha nula", None)
    yield
    _borrar_solicitudes_de_prueba()


def _insertar_solicitud(descripcion, fecha_alta):
    main.c.execute(
        "INSERT INTO solicitudes "
        "(estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, "
        "area, fecha_alta, fecha_mod, canal, obs) "
        "VALUES (1, 'CERT', ?, 3, 'PEND', NULL, 'Alumnado', ?, ?, 'WEB', '')",
        (descripcion, fecha_alta, fecha_alta),
    )
    main.conn.commit()


def _borrar_solicitudes_de_prueba():
    main.c.execute("DELETE FROM solicitudes WHERE descripcion LIKE 'Test - %'")
    main.conn.commit()


def pytest_sessionfinish(session, exitstatus):
    """Borra la carpeta temporal cuando termina la corrida."""
    os.chdir(RAIZ_PROYECTO)
    shutil.rmtree(_carpeta_temporal, ignore_errors=True)
