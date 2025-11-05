from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.engine import Connection

# Usamos una base de datos SQLite basada en archivo
DATABASE_URL = "sqlite:///./citas.db"

# connect_args={"check_same_thread": False} es necesario solo para SQLite
# para permitir que sea usado en múltiples hilos (como lo hace FastAPI)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Metadata es un contenedor para las definiciones de las tablas
metadata = MetaData()

# Definición de la tabla 'citas'
citas = Table(
    "citas",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("paciente", String(100), nullable=False),
    Column("fecha", DateTime, nullable=False),
    Column("motivo", String, default="Consulta"),
)


def create_db_and_tables():
    """
    Crea todas las tablas definidas en la metadata.
    """
    metadata.create_all(bind=engine)


def get_db() -> Connection:
    """
    Dependencia de FastAPI para obtener una conexión a la base de datos.
    Asegura que la conexión se cierre después de usarla.
    """
    with engine.connect() as conn:
        try:
            yield conn
        finally:
            conn.close()  # Se cierra la conexión al finalizar la petición
