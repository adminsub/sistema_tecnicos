from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Sistema de Control - Módulo Admin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ CADENA DE CONEXIÓN DE NEON.TECH
DB_URL = "postgresql://neondb_owner:npg_9lCoVdUr1Lqu@ep-floral-glitter-b5jqokc6-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DB_URL)

def init_db():
    conn = get_db_connection()
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
    cursor.close()
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
    return {"status": "ok", "message": "Servidor con PostgreSQL Activo"}

@app.post("/login")
def login(datos: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT id_p00, nombres, rol, clave FROM usuarios WHERE correo = %s", (datos.username.strip(),))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and user["clave"] == datos.password.strip():
        return {"id": user["id_p00"], "nombre": user["nombres"], "rol": user["rol"]}
    raise HTTPException(status_code=400, detail="Credenciales inválidas")

@app.post("/usuarios/registrar")
def registrar_usuario(datos: UserCreateRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_p00) DO UPDATE SET
            id_carnet=EXCLUDED.id_carnet, correo=EXCLUDED.correo, clave=EXCLUDED.clave,
            nombres=EXCLUDED.nombres, apellidos=EXCLUDED.apellidos, cedula=EXCLUDED.cedula,
            tipo_sangre=EXCLUDED.tipo_sangre, area_tipo=EXCLUDED.area_tipo,
            area_valor=EXCLUDED.area_valor, rol=EXCLUDED.rol
        """, (
            datos.id_p00.strip(), datos.id_carnet.strip() if datos.id_carnet else None,
            datos.correo.strip(), datos.clave.strip(), datos.nombres.strip(), datos.apellidos.strip(),
            datos.cedula.strip(), datos.tipo_sangre.strip() if datos.tipo_sangre else None,
            datos.area_tipo, datos.area_valor, datos.rol
        ))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/usuarios/actualizar")
def actualizar_usuario(datos: UserCreateRequest):
    return registrar_usuario(datos)

@app.delete("/usuarios/eliminar/{id_p00}")
def eliminar_usuario(id_p00: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id_p00 = %s", (id_p00,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "eliminado"}

@app.get("/usuarios/listar")
def listar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT id_p00, id_carnet, correo, nombres, apellidos, cedula, tipo_sangre, area_tipo, area_valor, rol FROM usuarios")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
