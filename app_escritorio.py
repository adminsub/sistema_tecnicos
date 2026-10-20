import tkinter as tk
from tkinter import messagebox, ttk
import requests

# 1. Dirección de tu servidor en Render
API_URL = "https://onrender.com"

def verificar_ingreso():
    user = entrada_usuario.get().strip()
    pas = entrada_contra.get().strip()
    
    if not user or not pas:
        messagebox.showwarning("Campos Vacíos", "Por favor ingresa usuario y contraseña.")
        return

    try:
        # Sincronizado en formato JSON para el servidor
        datos_enviar = {"username": user, "password": pas}
        respuesta = requests.post(f"{API_URL}/login", json=datos_enviar, timeout=10)
        
        if respuesta.status_code == 200:
            datos_usuario = respuesta.json()
            messagebox.showinfo("Éxito", f"¡Bienvenido {datos_usuario['nombre']}!")
            ventana_login.destroy()
            abrir_panel_central_azul(datos_usuario)
        else:
            messagebox.showerror("Error", "Credenciales inválidas o usuario incorrecto.")
            
    except requests.exceptions.Timeout:
        messagebox.showerror("Error de Tiempo", "El servidor está despertando. Por favor, intenta de nuevo en unos segundos.")
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor: {e}")

def abrir_panel_central_azul(datos_usuario):
    # Ventana Principal con tu diseño original
    ventana_panel = tk.Tk()
    ventana_panel.title("Mesa de Control")
    ventana_panel.geometry("900x550")
    ventana_panel.configure(bg="#1e3a8a")

    # Barra superior gris oscura original
    frame_superior = tk.Frame(ventana_panel, bg="#1f2937", height=50)
    frame_superior.pack(fill="x")
    frame_superior.pack_propagate(False)

    lbl_barra = tk.Label(
        frame_superior, 
        text=f"Panel de Control  |  Usuario: {datos_usuario['nombre']}", 
        fg="white", 
        bg="#1f2937", 
        font=("Arial", 11)
    )
    lbl_barra.pack(side="left", padx=15, pady=12)

    # Contenedor de la tabla
    frame_tabla = tk.Frame(ventana_panel, bg="#1e3a8a")
    frame_tabla.pack(fill="both", expand=True, padx=25, pady=25)

    # Configuración visual de la tabla
    style = ttk.Style()
    style.theme_use("clam")
    
    columnas = ("id", "cliente", "tecnico", "estado")
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
    
    tabla.heading("id", text="ID Orden")
    tabla.heading("cliente", text="Cliente")
    tabla.heading("tecnico", text="Técnico")
    tabla.heading("estado", text="Estado")

    tabla.column("id", width=100, anchor="center")
    tabla.column("cliente", width=350, anchor="w")
    tabla.column("tecnico", width=200, anchor="w")
    tabla.column("estado", width=150, anchor="center")
    
    tabla.pack(fill="both", expand=True)

    # Simulación de datos iniciales en la tabla
    tabla.insert("", "end", values=("1", "Clínica Metropolitana - Revisión de Aire", "Carlos Técnico", "Asignado"))
    tabla.insert("", "end", values=("2", "Banco Central - Falla de Planta Eléctrica", "Pendiente", "Abierta"))

    ventana_panel.mainloop()

# ==========================================
# INTERFAZ DE LOGIN ORIGINAL
# ==========================================
ventana_login = tk.Tk()
ventana_login.title("Login - Sistema Técnicos")
ventana_login.geometry("350x400")
ventana_login.configure(bg="#f3f4f6")

lbl_tit = tk.Label(ventana_login, text="MESA DE CONTROL", font=("Arial", 14, "bold"), bg="#f3f4f6", fg="#1f2937")
lbl_tit.pack(pady=30)

lbl_u = tk.Label(ventana_login, text="Usuario:", font=("Arial", 10), bg="#f3f4f6")
lbl_u.pack(anchor="w", padx=40)
entrada_usuario = tk.Entry(ventana_login, font=("Arial", 11))
entrada_usuario.pack(fill="x", padx=40, pady=5)
entrada_usuario.insert(0, "coord1")

lbl_p = tk.Label(ventana_login, text="Contraseña:", font=("Arial", 10), bg="#f3f4f6")
lbl_p.pack(anchor="w", padx=40, pady=(10, 0))
entrada_contra = tk.Entry(ventana_login, font=("Arial", 11), show="*")
entrada_contra.pack(fill="x", padx=40, pady=5)
entrada_contra.insert(0, "123")

btn_entrar = tk.Button(
    ventana_login, 
    text="Entrar al Sistema", 
    bg="#1f2937", 
    fg="white", 
    font=("Arial", 11, "bold"),
    command=verificar_ingreso,
    cursor="hand2"
)
btn_entrar.pack(fill="x", padx=40, pady=30, ipady=5)

ventana_login.mainloop()
