from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from database import crear_base_de_datos, SessionLocal, Usuario

# Forzar la creación de tablas limpias
crear_base_de_datos()

app = FastAPI(title="Sistema de Control de Técnicos de Campo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estructuras de datos estrictas
class LoginRequest(BaseModel):
    username: str
    password: str

class OrdenRequest(BaseModel):
    cliente: str
    direccion: str
    descripcion: str
    tecnico_id: Optional[int] = None

# Lista global en memoria activa para simular la base de datos sin fallos
DB_ORDENES = []
DB_USUARIOS = {
    "tecnico1": {"id": 1, "nombre": "Carlos Técnico", "rol": "tecnico", "clave": "123"},
    "super1": {"id": 2, "nombre": "Laura Supervisora", "rol": "supervisor", "clave": "123"},
    "coord1": {"id": 3, "nombre": "Pedro Coordinador", "rol": "coordinador", "clave": "123"},
    "gerente1": {"id": 4, "nombre": "Elena Gerente", "rol": "gerente", "clave": "123"}
}

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Servidor Activo"}

@app.post("/login")
def login(datos: LoginRequest):
    username = datos.username.strip()
    password = datos.password.strip()
    
    if username in DB_USUARIOS and DB_USUARIOS[username]["clave"] == password:
        return {
            "id": DB_USUARIOS[username]["id"],
            "nombre": DB_USUARIOS[username]["nombre"],
            "rol": DB_USUARIOS[username]["rol"]
        }
    raise HTTPException(status_code=400, detail="Credenciales inválidas")

# --- NUEVOS ENDPOINTS PARA LAS ÓRDENES DE TRABAJO ---
@app.get("/ordenes/")
def listar_ordenes(rol: Optional[str] = None, usuario_id: Optional[int] = None):
    # Retorna todas las órdenes guardadas en la memoria del servidor
    return DB_ORDENES

@app.post("/ordenes/")
def crear_orden(datos: OrdenRequest, creador_rol: Optional[str] = None):
    nueva_id = len(DB_ORDENES) + 1
    nueva_orden = {
        "id": nueva_id,
        "cliente": datos.cliente,
        "direccion": datos.direccion,
        "descripcion": datos.descripcion,
        "tecnico_id": datos.tecnico_id,
        "estado": "Pendiente",
        "latitud": None,
        "longitud": None
    }
    DB_ORDENES.append(nueva_orden)
    return {"status": "creada", "orden_id": nueva_id}
