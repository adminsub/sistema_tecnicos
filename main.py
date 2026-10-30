from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI(title="Sistema de Control - Módulo Admin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ REEMPLAZA ESTA CADENA POR LA TUYA DE NEON.TECH (Asegúrate de mantener el connect_timeout)
DB_URL = "postgresql://tu_usuario:tu_clave@tu_servidor.neon.tech/neondb?sslmode=require&connect_timeout=10"

def get_db_connection():
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        print(f"❌ ERROR CRÍTICO DE CONEXIÓN A LA BASE DE DATOS: {str(e)}")
        raise e

def init_db():
    try:
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
        print("✅ Base de datos PostgreSQL inicializada con éxito en la nube.")
    except Exception as e:
        print(f"❌ No se pudo inicializar la tabla en Neon: {str(e)}")

# Forzar inicialización al arrancar
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
    return {"status": "ok", "database": "PostgreSQL Conectada"}

@app.post("/login")
def login(datos: LoginRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id_p00, nombres, rol, clave FROM usuarios WHERE correo = %s", (datos.username.strip(),))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and user["clave"] == datos.password.strip():
            return {"id": user["id_p00"], "nombre": user["nombres"], "rol": user["rol"]}
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor de datos: {str(e)}")

@app.post("/usuarios/registrar")
def registrar_usuario(datos: UserCreateRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (id_p00, id_carnet, correo, clave, nombres, apellidos, cedula, tipo_sangre, area_tipo, area_valor, rol)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al escribir en la nube: {str(e)}")

@app.post("/usuarios/actualizar")
def actualizar_usuario(datos: UserCreateRequest):
    return registrar_usuario(datos)

@app.delete("/usuarios/eliminar/{id_p00}")
def eliminar_usuario(id_p00: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_p00 = %s", (id_p00,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/usuarios/listar")
def listar_usuarios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id_p00, id_carnet, correo, nombres, apellidos, cedula, tipo_sangre, area_tipo, area_valor, rol FROM usuarios ORDER BY id_p00 ASC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"❌ Error al listar usuarios: {str(e)}")
        return []
