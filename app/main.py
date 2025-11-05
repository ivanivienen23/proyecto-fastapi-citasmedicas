from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.engine import Connection
from sqlalchemy.sql import select, insert
from .database import engine, citas, create_db_and_tables, get_db
from .models import Cita, CitaCreate, CitaInDB
from typing import List
import uvicorn
from contextlib import asynccontextmanager

# --- NUEVO MÉTODO: LIFESPAN ---
# Esto reemplaza a los antiguos on_event("startup") y "shutdown"
# Es la forma moderna de gestionar el inicio y apagado de la app.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que se ejecuta ANTES de que la app empiece a recibir peticiones
    print("Iniciando aplicación y creando tablas de BD...")
    create_db_and_tables()
    yield
    # Código que se ejecuta DESPUÉS de que la app se apague
    print("Cerrando aplicación...")

# Pasamos el lifespan a la app principal
app = FastAPI(title="API de Citas Médicas", lifespan=lifespan)

# --- EL @app.on_event("startup") SE HA ELIMINADO ---

@app.post("/api/citas", response_model=CitaInDB, status_code=201)
def create_cita(cita: CitaCreate, conn: Connection = Depends(get_db)):
    """
    Crea una nueva cita.
    """
    try:
        stmt = insert(citas).values(**cita.model_dump())
        result = conn.execute(stmt)
        conn.commit()
        
        inserted_id = result.inserted_primary_key[0]
        select_stmt = select(citas).where(citas.c.id == inserted_id)
        new_cita = conn.execute(select_stmt).first()
        
        if new_cita:
            return new_cita
        else:
            raise HTTPException(status_code=500, detail="No se pudo crear la cita")
            
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear la cita: {e}")

@app.get("/api/citas", response_model=List[CitaInDB])
def get_citas(conn: Connection = Depends(get_db)):
    """
    Obtiene una lista de todas las citas.
    """
    try:
        select_stmt = select(citas).order_by(citas.c.fecha)
        result = conn.execute(select_stmt).fetchall()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer las citas: {e}")

@app.get("/api/citas/{cita_id}", response_model=CitaInDB)
def get_cita_by_id(cita_id: int, conn: Connection = Depends(get_db)):
    """
    Obtiene una cita específica por su ID.
    """
    try:
        select_stmt = select(citas).where(citas.c.id == cita_id)
        db_cita = conn.execute(select_stmt).first()
        
        # --- ESTA ES LA CORRECCIÓN CLAVE ---
        # Si la consulta no devuelve nada (None), lanzamos 404
        if db_cita is None:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        # --- FIN DE LA CORRECCIÓN ---
            
        return db_cita
    
    except HTTPException as http_ex:
        # Re-lanzamos la excepción HTTP (el 404) para que FastAPI la maneje
        raise http_ex
    except Exception as e:
        # Cualquier otro error inesperado se convierte en un 500
        raise HTTPException(status_code=500, detail=f"Error al buscar la cita: {e}")

# Para ejecutar directamente con `python app/main.py`
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)