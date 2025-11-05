import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool, select
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import metadata, get_db, citas
from datetime import datetime
import os

# --- Configuración de la Base de Datos de Prueba (En Memoria) ---

# Usamos una DB SQLite en memoria para las pruebas
TEST_DATABASE_URL = "sqlite:///:memory:"

# Creamos un motor de DB específico para pruebas
# StaticPool previene que se cierren las conexiones en memoria
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# Creamos una función 'override' para la dependencia get_db
def override_get_db():
    """
    Sobrescribe la dependencia get_db para usar la base de datos en memoria
    durante las pruebas.
    """
    with engine.connect() as conn:
        try:
            yield conn
        finally:
            conn.close()


# Aplicamos el 'override' a nuestra app de FastAPI
app.dependency_overrides[get_db] = override_get_db

# Creamos un cliente de prueba
client = TestClient(app)

# --- Fixture de Pytest ---


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """
    Fixture que se ejecuta antes de CADA prueba.
    Crea las tablas, permite que la prueba se ejecute (yield),
    y luego borra las tablas.
    """
    # Crear tablas
    metadata.create_all(bind=engine)
    yield
    # Borrar tablas
    metadata.drop_all(bind=engine)


# --- Tests de Integración (Endpoints) ---


def test_get_citas_vacia():
    """
    Test (Integración): Verifica que GET /api/citas devuelve una lista vacía
    cuando la base de datos está vacía.
    """
    response = client.get("/api/citas")
    assert response.status_code == 200
    assert response.json() == []


def test_create_cita():
    """
    Test (Integración): Verifica que POST /api/citas crea una cita
    correctamente y la devuelve.
    """
    test_fecha = datetime.now().isoformat()
    response = client.post(
        "/api/citas",
        json={
            "paciente": "Paciente de Prueba",
            "fecha": test_fecha,
            "motivo": "Test Motivo",
        },
    )
    # Verificar el código de estado (201 Created)
    assert response.status_code == 201

    # Verificar los datos devueltos
    data = response.json()
    assert data["paciente"] == "Paciente de Prueba"
    assert data["motivo"] == "Test Motivo"
    assert "id" in data
    assert data["id"] == 1


def test_get_citas_con_datos():
    """
    Test (Integración): Verifica que GET /api/citas devuelve los datos
    después de haber creado una cita.
    """
    # 1. Crear una cita primero
    test_fecha = datetime.now().isoformat()
    client.post(
        "/api/citas",
        json={"paciente": "Paciente 1", "fecha": test_fecha, "motivo": "Test 1"},
    )

    # 2. Obtener la lista de citas
    response = client.get("/api/citas")
    assert response.status_code == 200
    data = response.json()

    # Verificar que los datos están en la lista
    assert len(data) == 1
    assert data[0]["paciente"] == "Paciente 1"
    assert data[0]["id"] == 1


def test_get_cita_by_id_existente():
    """
    Test (Integración): Verifica que se puede obtener una cita por su ID.
    """
    test_fecha = datetime.now().isoformat()
    post_response = client.post(
        "/api/citas",
        json={"paciente": "Paciente ID", "fecha": test_fecha, "motivo": "Test ID"},
    )
    cita_id = post_response.json()["id"]

    get_response = client.get(f"/api/citas/{cita_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["paciente"] == "Paciente ID"
    assert data["id"] == cita_id


def test_get_cita_by_id_no_existente():
    """
    Test (Integración): Verifica que devuelve 404 si la cita no existe.
    """
    response = client.get("/api/citas/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Cita no encontrada"}


# --- Test Unitario (Ejemplo) ---

# (En este proyecto, la lógica está muy ligada a los endpoints,
# pero si tuviéramos una función de utilidad, la probaríamos así)


def mi_funcion_utilidad(a, b):
    return a + b


def test_mi_funcion_utilidad():
    """
    Test (Unitario): Verifica una función simple de forma aislada.
    """
    assert mi_funcion_utilidad(2, 3) == 5
    assert mi_funcion_utilidad(-1, 1) == 0
