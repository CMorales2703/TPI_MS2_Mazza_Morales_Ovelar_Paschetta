"""
Tests de GET /solicitudes (funcion buscar, lineas 201-233).

Los tests verifican el comportamiento ACTUAL del sistema, defectos incluidos.
Sirven como red de seguridad para el refactor: si un cambio altera lo que el
sistema hace hoy, estos tests lo detectan.

Los que documentan un defecto estan marcados con DEFECTO y deben actualizarse
cuando ese defecto se corrija en la Fase 3.
"""


# --- comportamiento correcto -------------------------------------------------

def test_sin_filtros_devuelve_todas(cliente):
    """Caso 1: sin filtros devuelve las 6 solicitudes de prueba."""
    r = cliente.get("/solicitudes")
    assert r.status_code == 200
    assert len(r.json()) == 6


def test_filtro_por_estado(cliente):
    """Caso 2: estado=PEND devuelve solo las pendientes."""
    r = cliente.get("/solicitudes", params={"estado": "PEND"})
    assert r.status_code == 200
    assert len(r.json()) == 2
    assert all(s["estado"] == "PEND" for s in r.json())


def test_filtro_por_prioridad(cliente):
    """Caso 3: prioridad=1 devuelve solo las de maxima prioridad."""
    r = cliente.get("/solicitudes", params={"prioridad": 1})
    assert r.status_code == 200
    assert len(r.json()) == 3
    assert all(s["prioridad"] == 1 for s in r.json())


def test_estado_inexistente_devuelve_lista_vacia(cliente):
    """Caso 4: un estado que no existe devuelve lista vacia, que es correcto."""
    r = cliente.get("/solicitudes", params={"estado": "XXXX"})
    assert r.status_code == 200
    assert r.json() == []


def test_orden_por_prioridad(cliente):
    """Caso 5: orden=prioridad pone primero las de prioridad 1."""
    r = cliente.get("/solicitudes", params={"orden": "prioridad"})
    assert r.status_code == 200
    prioridades = [s["prioridad"] for s in r.json()]
    assert prioridades == sorted(prioridades)


def test_orden_por_defecto_es_por_fecha(cliente):
    """Caso 1: sin indicar orden, devuelve de la mas nueva a la mas vieja."""
    fechas = [s["fecha_alta"] for s in cliente.get("/solicitudes").json()]
    assert fechas == sorted(fechas, reverse=True)


def test_prioridad_no_numerica_es_rechazada(cliente):
    """Caso 7: el tipo del parametro lo valida FastAPI antes de ejecutar."""
    r = cliente.get("/solicitudes", params={"prioridad": "alta"})
    assert r.status_code == 422


# --- defectos documentados ---------------------------------------------------

def test_DEFECTO_busqueda_distingue_mayusculas(cliente):
    """
    Caso 2b (hallazgo 11): 'pend' en minuscula no encuentra las solicitudes
    con estado 'PEND'. Devuelve lista vacia sin ningun aviso, igual que una
    busqueda legitima sin resultados.
    """
    r = cliente.get("/solicitudes", params={"estado": "pend"})
    assert r.status_code == 200
    assert r.json() == []


def test_DEFECTO_orden_invalido_se_ignora_en_silencio(cliente):
    """
    Caso 6 (hallazgo 9): un valor de orden inexistente no da error; el sistema
    usa el orden por defecto sin avisar que el parametro no se aplico.
    """
    r = cliente.get("/solicitudes", params={"orden": "zzz"})
    assert r.status_code == 200
    assert len(r.json()) == 6
    fechas = [s["fecha_alta"] for s in r.json()]
    assert fechas == sorted(fechas, reverse=True)


def test_DEFECTO_fecha_invalida_se_ignora_en_silencio(cliente):
    """
    Caso 8 (hallazgo 10): 'ayer' no es una fecha, pero el sistema la acepta
    y devuelve lista vacia en lugar de rechazar el parametro.
    """
    r = cliente.get("/solicitudes", params={"desde": "ayer"})
    assert r.status_code == 200
    assert r.json() == []


def test_DEFECTO_inyeccion_sql_evade_el_filtro(cliente):
    """
    Casos 9a y 9b (hallazgo 1): la consulta se arma concatenando texto, asi que
    un parametro puede alterarla. El filtro estado=RES devuelve 1 solicitud;
    con la inyeccion devuelve las 6.

    VULNERABILIDAD DE SEGURIDAD. Cuando se corrija usando consultas
    parametrizadas, este test debe pasar a esperar lista vacia.
    """
    control = cliente.get("/solicitudes", params={"estado": "RES"})
    assert len(control.json()) == 1

    inyeccion = cliente.get("/solicitudes", params={"estado": "' OR '1'='1"})
    assert inyeccion.status_code == 200
    assert len(inyeccion.json()) == 6


def test_DEFECTO_comilla_simple_rompe_el_servidor(cliente):
    """
    Caso 10 (hallazgo 1): una comilla suelta deja la consulta mal formada y
    SQLite lanza OperationalError en la linea 225. Un dato del cliente nunca
    deberia producir un 500.
    """
    r = cliente.get("/solicitudes", params={"texto": "'"})
    assert r.status_code == 500
