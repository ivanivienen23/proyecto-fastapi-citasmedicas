from pydantic import BaseModel, ConfigDict
from datetime import datetime


# Modelo base con los campos comunes
class CitaBase(BaseModel):
    paciente: str
    fecha: datetime
    motivo: str


# Modelo para la creación (lo que esperamos en el POST)
class CitaCreate(CitaBase):
    pass


# Modelo para la lectura (lo que devolvemos de la DB)
class CitaInDB(CitaBase):
    id: int

    # Configuración para que Pydantic pueda leer desde objetos (atributos)
    # y no solo desde diccionarios. Útil para SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)


# Modelo público (sin el ID, aunque para este caso CitaInDB es suficiente)
class Cita(CitaBase):
    pass
