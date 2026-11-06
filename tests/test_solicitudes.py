from pathlib import Path


DESCRIPCION = "Solicito mesa especial de Algoritmos por superposicion"


def cantidad_solicitudes(client):
    """Devuelve la cantidad de solicitudes registradas."""
    respuesta = client.get("/solicitudes")
    assert respuesta.status_code == 200
    return len(respuesta.json())


def buscar_solicitud(client, solicitud_id):
    """Devuelve la solicitud guardada, con su historial."""
    respuesta = client.get(f"/solicitudes/{solicitud_id}")
    assert respuesta.status_code == 200
    return respuesta.json()


def lineas_notificaciones():
    """Lee el log de notificaciones de la carpeta del test."""
    return Path("notificaciones.log").read_text().splitlines()


def test_registrar_solicitud_valida(client):
    """Caso 1: alta válida de tipo MESA (estudiante 3)."""
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 3, "tipo": "MESA", "descripcion": DESCRIPCION})

    # Actual: 200. Esperado: 201.
    assert respuesta.status_code == 200
    resultado = respuesta.json()
    assert resultado["prioridad"] == 1
    assert resultado["area"] == "Bedelia"
    assert resultado["estado"] == "PEND"
    assert resultado["canal"] == "WEB"

    guardada = buscar_solicitud(client, resultado["id"])
    historial = guardada.pop("historial")
    assert guardada == resultado
    assert historial == [{"estado_anterior": None, "estado_nuevo": "PEND",
                          "fecha": resultado["fecha_alta"], "comentario": "alta de solicitud"}]


def test_registrar_solicitud_notifica_al_estudiante(client):
    """Caso 2: el alta deja una línea en notificaciones.log."""
    resultado = client.post("/solicitudes", json={
        "estudiante_id": 3, "tipo": "MESA", "descripcion": DESCRIPCION}).json()

    # Actual: notifica a sofia.aranda. Esperado: lo mismo.
    assert lineas_notificaciones()[-1].endswith(
        f"Se envio mail a sofia.aranda@ejemplo.com: su solicitud {resultado['id']} fue registrada")


def test_registrar_cert_urgente_sube_prioridad(client):
    """Caso 3: un CERT con "urgente" en la descripción queda con prioridad 1 (hallazgo 2)."""
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 1, "tipo": "CERT",
        "descripcion": "Necesito el certificado analitico, es urgente"})

    # Actual: 200, prioridad 1 (un CERT normal es 3). Esperado: 201, prioridad 1.
    assert respuesta.status_code == 200
    assert respuesta.json()["prioridad"] == 1
    assert respuesta.json()["area"] == "Alumnado"


def test_registrar_respeta_prioridad_enviada(client):
    """Caso 4: la prioridad enviada por el cliente reemplaza la del tipo."""
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 2, "tipo": "MESA", "descripcion": DESCRIPCION, "prioridad": 3})

    # Actual: 200, prioridad 3. Esperado: 201, prioridad 3.
    assert respuesta.status_code == 200
    resultado = respuesta.json()
    assert resultado["prioridad"] == 3
    assert buscar_solicitud(client, resultado["id"])["prioridad"] == 3


def test_registrar_sin_estudiante(client):
    """Caso 5: falta estudiante_id (hallazgo 4)."""
    antes = cantidad_solicitudes(client)
    respuesta = client.post("/solicitudes", json={"tipo": "MESA", "descripcion": DESCRIPCION})

    # Actual: 200 con error. Esperado: 422.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error": "falta estudiante"}
    assert cantidad_solicitudes(client) == antes


def test_registrar_estudiante_inexistente(client):
    """Caso 6: estudiante 999 (hallazgo 4)."""
    antes = cantidad_solicitudes(client)
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 999, "tipo": "MESA", "descripcion": DESCRIPCION})

    # Actual: 200 con error. Esperado: 422.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error": "estudiante no existe"}
    assert cantidad_solicitudes(client) == antes


def test_registrar_tipo_invalido(client):
    """Caso 7: tipo BECA (hallazgo 4)."""
    antes = cantidad_solicitudes(client)
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 1, "tipo": "BECA", "descripcion": DESCRIPCION})

    # Actual: 200 con error. Esperado: 422.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error": "tipo invalido"}
    assert cantidad_solicitudes(client) == antes


def test_registrar_descripcion_corta(client):
    """Caso 8: descripción de menos de 10 caracteres (hallazgo 4)."""
    antes = cantidad_solicitudes(client)
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 1, "tipo": "MESA", "descripcion": "mesa"})

    # Actual: 200 con error. Esperado: 422.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error": "descripcion muy corta"}
    assert cantidad_solicitudes(client) == antes


def test_registrar_descripcion_null(client_sin_excepciones):
    """Caso 9: descripción null rompe el servidor (hallazgos 4 y 5)."""
    antes = cantidad_solicitudes(client_sin_excepciones)
    respuesta = client_sin_excepciones.post("/solicitudes", json={
        "estudiante_id": 1, "tipo": "MESA", "descripcion": None})

    # Actual: 500 (TypeError en la línea 144). Esperado: 422.
    assert respuesta.status_code == 500
    assert cantidad_solicitudes(client_sin_excepciones) == antes


def test_registrar_descripcion_numerica(client_sin_excepciones):
    """Caso 10: descripción numérica rompe el servidor (hallazgos 4 y 5)."""
    antes = cantidad_solicitudes(client_sin_excepciones)
    respuesta = client_sin_excepciones.post("/solicitudes", json={
        "estudiante_id": 1, "tipo": "MESA", "descripcion": 12345678901})

    # Actual: 500 (TypeError en la línea 144). Esperado: 422.
    assert respuesta.status_code == 500
    assert cantidad_solicitudes(client_sin_excepciones) == antes


def test_registrar_acepta_descripcion_en_blanco(client):
    """Caso 11: una descripción de 12 espacios se guarda (hallazgo 5)."""
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 1, "tipo": "MESA", "descripcion": " " * 12})

    # Actual: 200, la crea en blanco. Esperado: 422.
    assert respuesta.status_code == 200
    resultado = respuesta.json()
    assert buscar_solicitud(client, resultado["id"])["descripcion"] == " " * 12


def test_registrar_prioridad_fuera_de_rango(client):
    """Caso 12: prioridad 7 (hallazgo 4)."""
    antes = cantidad_solicitudes(client)
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 1, "tipo": "MESA", "descripcion": DESCRIPCION, "prioridad": 7})

    # Actual: 200 con error. Esperado: 422.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error": "prioridad invalida"}
    assert cantidad_solicitudes(client) == antes


def test_registrar_prioridad_como_texto(client):
    """Caso 13: prioridad "1" como texto (hallazgos 4 y 5)."""
    antes = cantidad_solicitudes(client)
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 1, "tipo": "MESA", "descripcion": DESCRIPCION, "prioridad": "1"})

    # Actual: 200 con error. Esperado: 422.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error": "prioridad invalida"}
    assert cantidad_solicitudes(client) == antes


def test_registrar_acepta_prioridad_booleana(client):
    """Caso 14: prioridad true pasa la validación porque True == 1 (hallazgo 5)."""
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 1, "tipo": "MESA", "descripcion": DESCRIPCION, "prioridad": True})

    # Actual: 200, responde true y guarda 1. Esperado: 422.
    assert respuesta.status_code == 200
    resultado = respuesta.json()
    assert resultado["prioridad"] is True
    assert buscar_solicitud(client, resultado["id"])["prioridad"] == 1


def test_registrar_canal_invalido_se_guarda_como_web(client):
    """Caso 15: canal FAX se cambia a WEB sin avisar (hallazgo 5)."""
    respuesta = client.post("/solicitudes", json={
        "estudiante_id": 4, "tipo": "EQUIV",
        "descripcion": "Pido equivalencia de Ingles I", "canal": "FAX"})

    # Actual: 200, la crea con canal WEB. Esperado: 422.
    assert respuesta.status_code == 200
    resultado = respuesta.json()
    assert resultado["canal"] == "WEB"
    assert resultado["area"] == "Departamento Academico"
    assert buscar_solicitud(client, resultado["id"])["canal"] == "WEB"


def test_registrar_body_lista_responde_otro_formato(client):
    """Caso 16: body que no es un objeto (hallazgo 4)."""
    antes = cantidad_solicitudes(client)
    respuesta = client.post("/solicitudes", json=[1, 2])

    # Actual: 422 con formato "detail". Esperado: 422 con formato "error".
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["msg"] == "Input should be a valid dictionary"
    assert cantidad_solicitudes(client) == antes


def test_registrar_notifica_a_estudiante_sin_email(client):
    """Caso 17: se registra un mail enviado sin destinatario (hallazgo 7)."""
    estudiante = client.post("/estudiantes", json={
        "nombre": "Ana", "apellido": "Paz", "legajo": "TUP-3001"}).json()
    resultado = client.post("/solicitudes", json={
        "estudiante_id": estudiante["id"], "tipo": "MESA",
        "descripcion": "Solicito mesa especial por viaje"}).json()

    # Actual: "Se envio mail a : ...". Esperado: avisar que no se pudo notificar.
    assert lineas_notificaciones()[-1].endswith(
        f"Se envio mail a : su solicitud {resultado['id']} fue registrada")
