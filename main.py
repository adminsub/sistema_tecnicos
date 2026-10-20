import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import crear_base_de_datos, SessionLocal, Usuario

# 1. Asegurar creación de base de datos
crear_base_de_datos()

app = FastAPI(title="Sistema de Control de Técnicos")

# 2. Permisos de conexión abiertos para tu PC
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Inyectar usuarios directamente a la base de datos limpia de Render
db = SessionLocal()
try:
    usuarios_iniciales = [
        {"nombre": "Carlos Técnico", "username": "tecnico1", "password_hash": "123", "rol": "tecnico"},
        {"nombre": "Laura Supervisora", "username": "super1", "password_hash": "123", "rol": "supervisor"},
        {"nombre": "Pedro Coordinador", "username": "coord1", "password_hash": "123", "rol": "coordinador"},
        {"nombre": "Elena Gerente", "username": "gerente1", "password_hash": "123", "rol": "gerente"}
    ]
    for u in usuarios_iniciales:
        existe = db.query(Usuario).filter(Usuario.username == u["username"]).first()
        if not existe:
            nuevo_usuario = Usuario(**u)
            db.add(nuevo_usuario)
    db.commit()
finally:
    db.close()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Servidor Activo"}

# 4. EL LOGIN DEFINITIVO CORREGIDO
@app.post("/login")
def login(datos: dict):
    username = datos.get("username")
    password = datos.get("password")
    
    # Lista de respaldo directa para pruebas en internet
    usuarios_dict = {
        "tecnico1": {"id": 1, "nombre": "Carlos Técnico", "rol": "tecnico", "clave": "123"},
        "super1": {"id": 2, "nombre": "Laura Supervisora", "rol": "supervisor", "clave": "123"},
        "coord1": {"id": 3, "nombre": "Pedro Coordinador", "rol": "coordinador", "clave": "123"},
        "gerente1": {"id": 4, "nombre": "Elena Gerente", "rol": "gerente", "clave": "123"}
    }
    
    if username in usuarios_dict and usuarios_dict[username]["clave"] == password:
        return {
            "id": usuarios_dict[username]["id"],
            "nombre": usuarios_dict[username]["nombre"],
            "rol": usuarios_dict[username]["rol"]
        }
    
    from fastapi import HTTPException
    raise HTTPException(status_code=400, detail="Credenciales inválidas")
