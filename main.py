import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import crear_base_de_datos, SessionLocal, Usuario

# 1. Asegurar la creación de la base de datos al arrancar
crear_base_de_datos()

# 2. Inicializar la aplicación con el nombre exacto que busca Render
app = FastAPI(title="Sistema de Control de Técnicos de Campo")

# 3. Habilitar permisos CORS para que tu PC pueda conectarse sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Crear los usuarios de prueba si la base de datos está vacía
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

# 5. Ruta de prueba para verificar que el servidor esté vivo
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Servidor de Técnicos activo en Render"}

# Incluye aquí abajo tus rutas existentes de @app.post("/login") y @app.get("/ordenes/") si las tienes
