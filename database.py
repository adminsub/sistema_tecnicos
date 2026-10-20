from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

DATABASE_URL = "sqlite:///./sistema_tecnicos.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, nullable=False) # tecnico, supervisor, coordinador, gerente

class OrdenTrabajo(Base):
    __tablename__ = "ordenes_trabajo"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    estado = Column(String, default="Pendiente") # Pendiente, En Ruta, En Sitio, Completado
    fecha_creacion = Column(DateTime, default=datetime.datetime.now)
    fecha_completado = Column(DateTime, nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    tecnico_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    coordinador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

def crear_base_de_datos():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
if __name__ == "__main__":
    crear_base_de_datos()
    print("¡Base de datos 'sistema_tecnicos.db' creada con éxito!")
