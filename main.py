from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import sqlite3

app = FastAPI(title="Sistema de Control - Módulo Admin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "sistema.db"

def init_db():
    """Crea la tabla de usuarios real y persistente con los nuevos campos"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_p00 TEXT PRIMARY KEY,
            id_carnet TEXT,
            correo TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            cedula TEXT NOT NULL,
            tipo_sangre TEXT,
            area_tipo TEXT NOT NULL, -- 'numero' o 'estadal'
            area_valor TEXT NOT NULL, -- '1' al '10' o 'TODAS'
            rol TEXT NOT NULL -- 'admin', 'coordinador', 'supervisor', 'tecnico'
        )
    """)
    # Insertar el usuario administrador maestro por defecto si la base está vacía
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE id_p00 = 'P001'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO usuarios VALUES (
                'P001', 'C-ADMIN-01', 'admin@sistema.com', 'admin123',
                'Administrador', 'General', 'V-00000000', 'O+',
                'estadal', 'TODAS', 'admin'
            )
        """)
    conn.commit()
    conn.close()

init_db()

# Modelos de datos estrictos (Pydantic)
class UserCreateRequest(BaseModel):
    id_p00: str
    id_carnet: Optional[str] = None
    correo: EmailStr
    clave: str
    nombres: str
    apellidos: str
    cedula: str
    tipo_sangre: Optional[str] = None
    area_tipo: str # 'numero' o 'estadal'
    area_valor: str # '1'...'10' o 'TODAS'
    rol: str

class LoginRequest(BaseModel):
    username: str # Será el correo
    password: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Servidor con Módulo Admin Activo"}

@app.post("/login")
def login(datos: LoginRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id_p00, nombres, rol, clave FROM usuarios WHERE correo = ?", (datos.username.strip(),))
    user = cursor.fetchone()
    conn.close()
    
    if user and user[3] == datos.password.strip():
        return {"id": user[0], "nombre": f"{user[1]}", "rol": user[2]}
    raise HTTPException(status_code=400, detail="Credenciales inválidas")

@app.post("/usuarios/registrar")
def registrar_usuario(datos: UserCreateRequest):
    # Validaciones de reglas de negocio
    if datos.area_tipo == "numero" and datos.area_valor not in [str(i) for i in range(1, 11)]:
        raise HTTPException(status_code=400, detail="El área por número debe ser del 1 al 10")
    if datos.area_tipo == "estadal" and datos.area_valor != "TODAS":
        raise HTTPException(status_code=400, detail="Los usuarios estadales ven 'TODAS' las áreas")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            datos.id_p00.strip(), datos.id_carnet.strip() if datos.id_carnet else None,
            datos.correo.strip(), datos.clave.strip(), datos.nombres.strip(), datos.apellidos.strip(),
            datos.cedula.strip(), datos.tipo_sangre.strip() if datos.tipo_sangre else None,
            datos.area_tipo, datos.area_valor, datos.rol
        ))
        conn.commit()
        return {"status": "creado", "id_p00": datos.id_p00}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El ID P00 o el Correo ya se encuentran registrados")
    finally:
        conn.close()

@app.get("/usuarios/listar")
def listar_usuarios():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id_p00, id_carnet, correo, nombres, apellidos, cedula, tipo_sangre, area_tipo, area_valor, rol FROM usuarios")
    rows = cursor.fetchall()
    conn.close()
    
    resultado = []
    for r in rows:
        resultado.append({
            "id_p00": r[0], "id_carnet": r[1], "correo": r[2], "nombres": r[3],
            "apellidos": r[4], "cedula": r[5], "tipo_sangre": r[6], "area_tipo": r[7],
            "area_valor": r[8], "rol": r[9]
        })
    return resultado
