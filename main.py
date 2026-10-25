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
            area_tipo TEXT NOT NULL,
            area_valor TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)
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

class UserCreateRequest(BaseModel):
    id_p00: str
    id_carnet: Optional[str] = None
    correo: EmailStr
    clave: str
    nombres: str
    apellidos: str
    cedula: str
    tipo_sangre: Optional[str] = None
    area_tipo: str
    area_valor: str
    rol: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Servidor Activo"}

@app.post("/login")
def login(datos: LoginRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id_p00, nombres, rol, clave FROM usuarios WHERE correo = ?", (datos.username.strip(),))
    user = cursor.fetchone()
    conn.close()
    if user and user[3] == datos.password.strip():
        return {"id": user[0], "nombre": user[1], "rol": user[2]}
    raise HTTPException(status_code=400, detail="Credenciales inválidas")

@app.post("/usuarios/registrar")
def registrar_usuario(datos: UserCreateRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO usuarios VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            datos.id_p00.strip(), datos.id_carnet.strip() if datos.id_carnet else None,
            datos.correo.strip(), datos.clave.strip(), datos.nombres.strip(), datos.apellidos.strip(),
            datos.cedula.strip(), datos.tipo_sangre.strip() if datos.tipo_sangre else None,
            datos.area_tipo, datos.area_valor, datos.rol
        ))
        conn.commit()
        return {"status": "ok"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error de integridad de datos")
    finally:
        conn.close()

@app.post("/usuarios/actualizar")
def actualizar_usuario(datos: UserCreateRequest):
    return registrar_usuario(datos)

@app.delete("/usuarios/eliminar/{id_p00}")
def eliminar_usuario(id_p00: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id_p00 = ?", (id_p00,))
    conn.commit()
    conn.close()
    return {"status": "eliminado"}

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
