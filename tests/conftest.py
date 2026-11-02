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
