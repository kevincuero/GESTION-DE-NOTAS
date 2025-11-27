# tests/test_docente.py
import pytest
from main import app  # Ajusta si tu app está en otro módulo

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_listado_alumnos_status(client):
    # Ajusta la ruta si en tu proyecto es otra (ej: "/docente/alumnos")
    resp = client.get('/alumnos')
    assert resp.status_code == 200

def test_buscar_alumno_por_nombre(client):
    # Ejemplo de búsqueda (ajusta el query param si corresponde)
    resp = client.get('/alumnos?search=pepito')
    assert resp.status_code == 200
    # Opcional: más aserciones (p. ej. comprobar JSON) si tu endpoint devuelve JSON.
