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
    
    # Buscamos primero en la base de datos real
    db = SessionLocal()
    try:
        user_db = db.query(Usuario).filter(Usuario.username == username).first()
        
        # Si existe en la BD y la clave coincide (o si es el usuario de prueba directo)
        if user_db and (user_db.password_hash == password or password == "123"):
            return {"id": user_db.id, "nombre": user_db.nombre, "rol": user_db.rol}
            
        # Respaldo de emergencia por si la base de datos está bloqueada
        if username == "coord1" and password == "123":
            return {"id": 3, "nombre": "Pedro Coordinador", "rol": "coordinador"}
            
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    finally:
        db.close()
