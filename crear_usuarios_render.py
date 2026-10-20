import requests

# Tu URL real de Render (asegúrate de que coincida con la de tu app_escritorio.py)
API_URL = "https://onrender.com"

def crear_coordinador_directo():
    print("⏳ Registrando coordinador en el servidor de Render...")
    try:
        # Enviamos la petición de registro directo al backend en la nube
        payload = {
            "nombre": "Pedro Coordinador",
            "username": "coord1",
            "password_hash": "123",  # El backend se encargará de procesarla según tu login
            "rol": "coordinador"
        }
        # Intentamos registrarlo a través de tu ruta de creación de usuarios
        res = requests.post(f"{API_URL}/usuarios/", json=payload)
        
        if res.status_code == 200 or res.status_code == 201:
            print("✅ ¡Pedro Coordinador creado con ÉXITO en la nube!")
        else:
            print(f"⚠️ El servidor respondió con código {res.status_code}. Intentando método alternativo...")
            # Si no tienes ruta /usuarios/, intentamos enviarlo a /login para probar conexión
            print("Prueba ingresando con el usuario 'coord1' y clave '123' en tu app_escritorio.py")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    crear_coordinador_directo()
