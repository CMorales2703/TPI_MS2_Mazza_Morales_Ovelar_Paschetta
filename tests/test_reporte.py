"""
Tests de GET /reporte (app/routers/consultas.py).
"""

from datetime import datetime, timedelta


def test_devuelve_todos_los_agrupamientos(client):
    """Caso 16: el reporte trae los conteos, el porcentaje y las vencidas."""
    r = client.get("/reporte")
    assert r.status_code == 200
    d = r.json()
    for campo in (
        "total",
        "por_estado",
        "por_tipo",
        "por_area",
        "porcentaje_resueltas",
        "vencidas",
    ):
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
    client_sin_excepciones, solicitud_con_fecha_invalida
):
    """
    Caso 17 (hallazgo 2): strptime en la linea 347 exige el formato
    '%Y-%m-%d %H:%M:%S'. Una sola solicitud con otro formato lanza ValueError
    y deja sin funcionar el reporte completo.
    """
    assert client_sin_excepciones.get("/reporte").status_code == 500


def test_DEFECTO_fecha_nula_rompe_el_reporte(
    client_sin_excepciones, solicitud_con_fecha_nula
):
    """
    Caso 18 (hallazgo 2): la misma linea lanza TypeError cuando no hay fecha.
    Dos errores distintos salen de la misma instruccion sin proteccion.
    """
    assert client_sin_excepciones.get("/reporte").status_code == 500


def test_DEFECTO_el_reporte_se_recupera_al_quitar_el_dato_malo(
    client_sin_excepciones, solicitud_con_fecha_invalida, conexion_db
):
    """
    El fallo viene del dato y no deja el sistema en un estado inconsistente:
    con la solicitud defectuosa el reporte devuelve 500, y al borrarla vuelve
    a responder 200 sin reiniciar nada.
    """
    assert client_sin_excepciones.get("/reporte").status_code == 500

    conexion_db.execute("DELETE FROM solicitudes WHERE descripcion LIKE 'Test - %'")
    conexion_db.commit()

    assert client_sin_excepciones.get("/reporte").status_code == 200


# --- cobertura del calculo de vencidas ---------------------------------------
# Estos casos faltaban: la suite no verificaba cual es el limite de dias de
# cada prioridad, asi que un error ahi no habria hecho fallar ningun test.

def _insertar_con_antiguedad(conn, dias, prioridad, estado="PEND"):
    """Inserta una solicitud con una antiguedad concreta y devuelve su id."""
    fecha = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.execute(
        "INSERT INTO solicitudes "
        "(estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, "
        "area, fecha_alta, fecha_mod, canal, obs) "
        "VALUES (1, 'CERT', 'Test - vencimiento', ?, ?, NULL, 'Alumnado', ?, ?, 'WEB', '')",
        (prioridad, estado, fecha, fecha),
    )
    conn.commit()
    return cur.lastrowid


def test_una_solicitud_abierta_y_vieja_figura_como_vencida(client, conexion_db):
    """Una solicitud de prioridad 3 con 15 dias abiertos supera el limite de 10."""
    id_nueva = _insertar_con_antiguedad(conexion_db, dias=15, prioridad=3)

    vencidas = client.get("/reporte").json()["vencidas"]
    fila = [v for v in vencidas if v["id"] == id_nueva]

    assert len(fila) == 1
    assert fila[0]["dias"] == 15
    assert fila[0]["prioridad"] == 3


def test_el_limite_de_vencimiento_depende_de_la_prioridad(client, conexion_db):
    """A los 7 dias, la prioridad 1 (limite 2) vencio y la prioridad 3 (limite 10) no."""
    urgente = _insertar_con_antiguedad(conexion_db, dias=7, prioridad=1)
    normal = _insertar_con_antiguedad(conexion_db, dias=7, prioridad=3)

    ids = [v["id"] for v in client.get("/reporte").json()["vencidas"]]

    assert urgente in ids
    assert normal not in ids


def test_una_solicitud_cerrada_nunca_figura_como_vencida(client, conexion_db):
    """El vencimiento solo corre para las solicitudes que siguen abiertas."""
    cerrada = _insertar_con_antiguedad(conexion_db, dias=90, prioridad=1, estado="RES")

    ids = [v["id"] for v in client.get("/reporte").json()["vencidas"]]

    assert cerrada not in ids