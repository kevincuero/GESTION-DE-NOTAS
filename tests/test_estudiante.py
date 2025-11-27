# tests/test_estudiante.py
import pytest
from main import app  # Ajusta si tu app está en otro módulo

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_pagina_horario(client):
    # Simular login
    with client.session_transaction() as sess:
        sess['usuario'] = {"id": 1, "tipo": "estudiante"}
    
    response = client.get('/estudiante/horario')
    assert response.status_code == 200


def test_ver_calificaciones(client):
    with client.session_transaction() as sess:
        sess['usuario'] = {"id": 1, "tipo": "estudiante"}

    response = client.get('/estudiante/calificaciones')
    assert response.status_code == 200

