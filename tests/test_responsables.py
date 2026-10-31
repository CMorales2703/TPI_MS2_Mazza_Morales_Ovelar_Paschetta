def buscar_responsable(client, responsable_id):
    """Busca un responsable por su ID y devuelve el registro completo."""
    respuesta = client.get("/responsables")
    assert respuesta.status_code == 200

    return next(
        (r for r in respuesta.json() if r["id"] == responsable_id),
        None,
    )


def cantidad_responsables(client):
    """Devuelve la cantidad de responsables registrados."""
    respuesta = client.get("/responsables")
    assert respuesta.status_code == 200
    return len(respuesta.json())


def test_crear_responsable_area_invalida(client):
    """Caso 7: área inexistente (hallazgos 3 y 6)."""
    datos = {"nombre": "Laura Gil", "area": "Sistemas"}

    cantidad_antes = cantidad_responsables(client)

    respuesta = client.post("/responsables", json=datos)

    # Actual: 200. Esperado según el diagnóstico: 422.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error": "area invalida"}

    cantidad_despues = cantidad_responsables(client)
    assert cantidad_despues == cantidad_antes


def test_crear_responsable_valido(client):
    """Caso 8a: alta válida de responsable."""
    datos = {"nombre": "Laura Gil", "area": "Bedelia"}

    respuesta = client.post("/responsables", json=datos)

    # Actual: 200. Esperado según el diagnóstico: 201.
    assert respuesta.status_code == 200

    resultado = respuesta.json()
    assert isinstance(resultado["id"], int)
    assert resultado["activo"] is True

    guardado = buscar_responsable(client, resultado["id"])
    assert guardado is not None
    assert guardado == resultado


def test_crear_responsable_acepta_duplicado(client):
    """Caso 8b: acepta un responsable repetido (hallazgo 11)."""
    datos = {"nombre": "Laura Gil", "area": "Bedelia"}

    cantidad_antes = cantidad_responsables(client)

    primera_respuesta = client.post("/responsables", json=datos)
    segunda_respuesta = client.post("/responsables", json=datos)

    # Actual: 200 en los dos y crea ambos.
    # Esperado: el segundo debería responder 409 Conflict.
    assert primera_respuesta.status_code == 200
    assert segunda_respuesta.status_code == 200

    primero = primera_respuesta.json()
    segundo = segunda_respuesta.json()

    # Son dos registros distintos con los mismos datos.
    assert primero["id"] != segundo["id"]

    for resultado in (primero, segundo):
        guardado = buscar_responsable(client, resultado["id"])
        assert guardado is not None
        assert guardado == resultado

    cantidad_despues = cantidad_responsables(client)
    assert cantidad_despues == cantidad_antes + 2
