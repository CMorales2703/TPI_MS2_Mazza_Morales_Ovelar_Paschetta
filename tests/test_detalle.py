"""
Tests de GET /solicitudes/{id} (funcion getSolicitud, lineas 235-248).

A diferencia de buscar, esta funcion usa una consulta parametrizada
(linea 237: "WHERE id = ?"), por eso no es vulnerable a inyeccion.
"""


def test_devuelve_la_solicitud_con_su_historial(cliente):
    """Caso 11: el detalle incluye un campo historial que el listado no trae."""
    r = cliente.get("/solicitudes/1")
    assert r.status_code == 200
    d = r.json()
    assert d["id"] == 1
    assert "historial" in d
    assert isinstance(d["historial"], list)


def test_id_inexistente_devuelve_404(cliente):
    """Caso 12: un id que no existe devuelve 404."""
    r = cliente.get("/solicitudes/99999")
    assert r.status_code == 404
    assert r.json()["detail"] == "no existe"


def test_id_cero_devuelve_404(cliente):
    """Caso 13."""
    assert cliente.get("/solicitudes/0").status_code == 404


def test_id_no_numerico_es_rechazado(cliente):
    """Caso 15: el tipo del parametro lo valida FastAPI."""
    assert cliente.get("/solicitudes/abc").status_code == 422


def test_DEFECTO_id_negativo_devuelve_404_en_lugar_de_422(cliente):
    """
    Caso 14: un id negativo no es un dato inexistente sino imposible.
    Corresponderia 422 (dato invalido) y no 404 (no encontrado). El sistema
    no distingue los dos casos.
    """
    r = cliente.get("/solicitudes/-5")
    assert r.status_code == 404


def test_el_detalle_no_es_vulnerable_a_inyeccion(cliente):
    """
    Contraste con buscar: aca el id viaja como parametro, no concatenado,
    asi que un texto malicioso es rechazado por tipo antes de llegar al SQL.
    """
    assert cliente.get("/solicitudes/1 OR 1=1").status_code == 422
