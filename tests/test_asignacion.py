def test_asignar_responsable_valido(client):
    """Caso 10: asigna a Graciela Molina (1) la solicitud 1 (PEND -> ASIG)."""
    respuesta = client.put("/solicitudes/1/responsable", json={"responsable_id": 1})

    # Actual: 200. Esperado: 200.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"id":1,"responsable_id":1,"responsable":"Graciela Molina","estado":"ASIG"}
    solicitud = client.get("/solicitudes/1").json()                                     
    assert solicitud["estado"] == "ASIG"                                                
    assert solicitud["responsable_id"] == 1                                             
    assert solicitud["historial"][-1]["comentario"] == "asignada a Graciela Molina"     



def test_asignar_solicitud_inexistente(client):
    """Caso 2: solicitud inexistente responde 200 (hallazgo 1)."""
    respuesta = client.put("/solicitudes/999/responsable", json={"responsable_id": 1})

    # Actual: 200 {"error": "solicitud no existe"}. Esperado: 404.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error":"solicitud no existe"}


def test_asignar_responsable_inactivo(client):
    """Caso 8: responsable inactivo (Ruben Castro, 2) (hallazgo 1)."""
    antes = client.get("/solicitudes/1").json()                                         
    respuesta = client.put("/solicitudes/1/responsable", json={"responsable_id": 2})

    # Actual: 200 con error. Esperado: 409.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error":"responsable inactivo"}
    assert client.get("/solicitudes/1").json() == antes                                 


def test_reasignar_no_registra_historial(client):
    """Casos 12a-12c: reasignar la solicitud 2 no deja registro (hallazgo 6)."""
    antes = client.get("/solicitudes/2").json()                                         
    nuevo = client.post("/responsables", json={
        "nombre": "Laura Gil", "area": "Departamento Academico",
        "email": "lgil@ejemplo.com"}).json()

    respuesta = client.put("/solicitudes/2/responsable",
                           json={"responsable_id": nuevo["id"]})

    # Actual: 200, cambia responsable_id y el historial queda igual.
    # Esperado: una fila nueva en el historial con la reasignación.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": 2, "responsable_id": 6, "responsable": "Laura Gil", "estado": "ASIG"}
    solicitud = client.get("/solicitudes/2").json()                                     
    assert solicitud["responsable_id"] == 6                                             
    assert solicitud["historial"] == antes["historial"]                                 