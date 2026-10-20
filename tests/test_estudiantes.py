from fastapi.testclient import TestClient


def buscar_estudiante(client, estudiante_id):
    """Busca un estudiante por su ID y devuelve el registro completo."""
    respuesta = client.get("/estudiantes")
    assert respuesta.status_code == 200

    return next((e for e in respuesta.json() if e["id"] == estudiante_id), None)


def cantidad_estudiantes(client):
    """Devuelve la cantidad de estudiantes registrados."""
    respuesta = client.get("/estudiantes")
    assert respuesta.status_code == 200
    return len(respuesta.json())


def test_crear_estudiante_valido(client):
    """Caso 1: alta válida."""
    datos = {
        "nombre": "Juan",
        "apellido": "Perez",
        "legajo": "TEST-9001",
        "email": "juan.perez@test.com",
        "carrera": "Sistemas",
    }

    respuesta = client.post("/estudiantes", json=datos)

    # Actual: 200. Esperado según el diagnóstico: 201.
    assert respuesta.status_code == 200

    resultado = respuesta.json()
    assert isinstance(resultado["id"], int)

    guardado = buscar_estudiante(client, resultado["id"])
    assert guardado is not None
    assert guardado == resultado


def test_crear_estudiante_sin_carrera_usa_default(client):
    """Sin carrera explícita, el sistema utiliza TUP."""
    datos = {
        "nombre": "Ana",
        "apellido": "Lopez",
        "legajo": "TEST-9002",
        "email": "ana.lopez@test.com",
    }

    respuesta = client.post("/estudiantes", json=datos)

    assert respuesta.status_code == 200

    resultado = respuesta.json()
    assert resultado["carrera"] == "TUP"

    guardado = buscar_estudiante(client, resultado["id"])
    assert guardado is not None
    assert guardado == resultado


def test_crear_estudiante_sin_apellido(client):
    """Caso 2: falta apellido."""
    datos = {"nombre": "Pedro", "legajo": "TEST-9003", "email": "pedro@test.com"}

    cantidad_antes = cantidad_estudiantes(client)

    respuesta = client.post("/estudiantes", json=datos)

    # Actual: 200. Esperado según el diagnóstico: 422.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error": "falta apellido"}

    cantidad_despues = cantidad_estudiantes(client)
    assert cantidad_despues == cantidad_antes


def test_crear_estudiante_acepta_email_invalido(client):
    """Caso 4: acepta un email inválido (hallazgos 4 y 5)."""
    datos = {
        "nombre": "Laura",
        "apellido": "Gomez",
        "legajo": "TEST-9004",
        "email": "@",
    }

    respuesta = client.post("/estudiantes", json=datos)

    # Actual: 200 y lo crea. Esperado: 422 y no lo crea.
    assert respuesta.status_code == 200

    resultado = respuesta.json()
    guardado = buscar_estudiante(client, resultado["id"])

    assert guardado is not None
    assert guardado["email"] == datos["email"]
    assert guardado == resultado


def test_crear_estudiante_acepta_apellido_nulo(client):
    """Caso 6: acepta un apellido nulo (hallazgos 5 y 11)."""
    datos = {
        "nombre": "Martin",
        "apellido": None,
        "legajo": "TEST-9006",
        "email": "martin@test.com",
    }

    respuesta = client.post("/estudiantes", json=datos)

    # Actual: 200 y lo crea. Esperado: 422 y no lo crea.
    assert respuesta.status_code == 200

    resultado = respuesta.json()
    guardado = buscar_estudiante(client, resultado["id"])

    assert guardado is not None
    assert guardado["apellido"] == datos["apellido"]
    assert guardado == resultado


def test_crear_estudiante_email_null(client):
    """Caso 10: email nulo provoca un error 500 (hallazgos 3, 4 y 5)."""
    datos = {
        "nombre": "Pedro",
        "apellido": "Perez",
        "legajo": "TEST-9010",
        "email": None,
    }

    cantidad_antes = cantidad_estudiantes(client)

    with TestClient(
        client.app, raise_server_exceptions=False
    ) as cliente_sin_excepciones:
        respuesta = cliente_sin_excepciones.post("/estudiantes", json=datos)

    # Actual: 500. Esperado tras corregir el defecto: 422.
    assert respuesta.status_code == 500

    cantidad_despues = cantidad_estudiantes(client)
    assert cantidad_despues == cantidad_antes
