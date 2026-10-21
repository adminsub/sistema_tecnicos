from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# 1. RUTA DE BIENVENIDA (Solo responde si entras a la raíz)
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Servidor Activo"}

# 2. RUTA DE ACCESO REAL (Separada para recibir los datos de Flet)
@app.post("/login")
def login(datos: dict):
    username = datos.get("username")
    password = datos.get("password")
    
    # Lista de usuarios fija en memoria para acceso directo sin fallos de BD
    usuarios_maestros = {
        "tecnico1": {"id": 1, "nombre": "Carlos Técnico", "rol": "tecnico", "clave": "123"},
        "super1": {"id": 2, "nombre": "Laura Supervisora", "rol": "supervisor", "clave": "123"},
        "coord1": {"id": 3, "nombre": "Pedro Coordinador", "rol": "coordinador", "clave": "123"},
        "gerente1": {"id": 4, "nombre": "Elena Gerente", "rol": "gerente", "clave": "123"}
    }
    
    if username in usuarios_maestros and usuarios_maestros[username]["clave"] == password:
        return {
            "id": usuarios_maestros[username]["id"],
            "nombre": usuarios_maestros[username]["nombre"],
            "rol": usuarios_maestros[username]["rol"]
        }
        
    raise HTTPException(status_code=400, detail="Credenciales inválidas")
