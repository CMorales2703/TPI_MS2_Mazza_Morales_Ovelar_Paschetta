"""
Tests de GET /reporte (funcion reporte, lineas 323-361).
"""


def test_devuelve_todos_los_agrupamientos(client):
    """Caso 16: el reporte trae los conteos, el porcentaje y las vencidas."""
    r = client.get("/reporte")
    assert r.status_code == 200
    d = r.json()
    for campo in ("total", "por_estado", "por_tipo", "por_area",
                  "porcentaje_resueltas", "vencidas"):
        assert campo in d


def test_el_total_coincide_con_el_listado(client):
    """El total del reporte es la misma cantidad que devuelve el listado."""
    total = client.get("/reporte").json()["total"]
    assert total == len(client.get("/solicitudes").json())


def test_los_conteos_suman_el_total(client):
    """Cada agrupamiento reparte el total sin perder ni duplicar solicitudes."""
    d = client.get("/reporte").json()
    assert sum(d["por_estado"].values()) == d["total"]
    assert sum(d["por_tipo"].values()) == d["total"]
    assert sum(d["por_area"].values()) == d["total"]


def test_el_porcentaje_de_resueltas_es_coherente(client):
    """El porcentaje corresponde a las solicitudes en estado RES."""
    d = client.get("/reporte").json()
    resueltas = d["por_estado"].get("RES", 0)
    esperado = round(resueltas * 100 / d["total"], 2)
    assert d["porcentaje_resueltas"] == esperado


def test_DEFECTO_fecha_con_otro_formato_rompe_el_reporte(
        client_sin_excepciones, solicitud_con_fecha_invalida):
    """
    Caso 17 (hallazgo 2): strptime en la linea 347 exige el formato
    '%Y-%m-%d %H:%M:%S'. Una sola solicitud con otro formato lanza ValueError
    y deja sin funcionar el reporte completo.
    """
    assert client_sin_excepciones.get("/reporte").status_code == 500


def test_DEFECTO_fecha_nula_rompe_el_reporte(
        client_sin_excepciones, solicitud_con_fecha_nula):
    """
    Caso 18 (hallazgo 2): la misma linea lanza TypeError cuando no hay fecha.
    Dos errores distintos salen de la misma instruccion sin proteccion.
    """
    assert client_sin_excepciones.get("/reporte").status_code == 500


def test_DEFECTO_el_reporte_se_recupera_al_quitar_el_dato_malo(
        client_sin_excepciones, solicitud_con_fecha_invalida):
    """
    El fallo viene del dato y no deja el sistema en un estado inconsistente:
    con la solicitud defectuosa el reporte devuelve 500, y al borrarla vuelve
    a responder 200 sin reiniciar nada.
    """
    import sys

    assert client_sin_excepciones.get("/reporte").status_code == 500

    main = sys.modules["main"]
    main.c.execute("DELETE FROM solicitudes WHERE descripcion LIKE 'Test - %'")
    main.conn.commit()

    assert client_sin_excepciones.get("/reporte").status_code == 200
