import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import crear_base_de_datos, SessionLocal, Usuario

# Asegurar la creación de las tablas en la nube
crear_base_de_datos()

app = FastAPI(title="Sistema de Control de Técnicos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Servidor Activo"}

# --- EL LOGIN CON RESPALDO ABSOLUTO PARA EVITAR EL REBOTE ---
@app.post("/login")
def login(datos: dict):
    username = datos.get("username")
    password = datos.get("password")
    
    # 1. Respaldo directo en memoria (Si esto coincide, pasas SÍ O SÍ)
    usuarios_prueba = {
        "tecnico1": {"id": 1, "nombre": "Carlos Técnico", "rol": "tecnico", "clave": "123"},
        "super1": {"id": 2, "nombre": "Laura Supervisora", "rol": "supervisor", "clave": "123"},
        "coord1": {"id": 3, "nombre": "Pedro Coordinador", "rol": "coordinador", "clave": "123"},
        "gerente1": {"id": 4, "nombre": "Elena Gerente", "rol": "gerente", "clave": "123"}
    }
    
    if username in usuarios_prueba and usuarios_prueba[username]["clave"] == password:
        return {
            "id": usuarios_prueba[username]["id"],
            "nombre": usuarios_prueba[username]["nombre"],
            "rol": usuarios_prueba[username]["rol"]
        }
        
    # 2. Si no es de prueba, buscar en la base de datos física
    db = SessionLocal()
    try:
        user_db = db.query(Usuario).filter(Usuario.username == username).first()
        if user_db and user_db.password_hash == password:
            return {"id": user_db.id, "nombre": user_db.nombre, "rol": user_db.rol}
    finally:
        db.close()
        
    raise HTTPException(status_code=400, detail="Credenciales inválidas")
