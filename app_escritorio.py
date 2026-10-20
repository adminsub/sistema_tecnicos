import tkinter as tk
from tkinter import messagebox, ttk
import requests

# 1. Dirección única y directa a tu servidor en la nube (Render)
API_URL = "https://onrender.com"

# Variables globales para almacenar los datos del usuario que inicia sesión
usuario_actual = None

def abrir_panel_central_azul(datos_usuario):
    """Abre la ventana principal del sistema (Panel Administrativo Azul)"""
    global usuario_actual
    usuario_actual = datos_usuario

    # Crear ventana del Panel Principal
    ventana_panel = tk.Tk()
    ventana_panel.title("Mesa de Control - Sistema de Gestión de Técnicos")
    ventana_panel.geometry("900x600")
    ventana_panel.configure(bg="#1e3a8a")  # Color azul administrativo

    # --- ENCABEZADO ---
    frame_header = tk.Frame(ventana_panel, bg="#111827", height=70)
    frame_header.pack(fill="x")
    frame_header.pack_propagate(False)

    lbl_titulo = tk.Label(
        frame_header, 
        text="PANEL CENTRAL DE CONTROL DE OPERACIONES", 
        fg="white", 
        bg="#111827", 
        font=("Arial", 16, "bold")
    )
    lbl_titulo.pack(side="left", padx=20, pady=15)

    lbl_user = tk.Label(
        frame_header, 
        text=f"Sesión: {datos_usuario['nombre']} ({datos_usuario['rol'].upper()})", 
        fg="#60a5fa", 
        bg="#111827", 
        font=("Arial", 10, "bold")
    )
    lbl_user.pack(side="right", padx=20, pady=20)

    # --- CONTENIDO / TABLA DE ÓRDENES ---
    frame_cuerpo = tk.Frame(ventana_panel, bg="#1e3a8a")
    frame_cuerpo.pack(fill="both", expand=True, padx=30, pady=30)

    lbl_sub = tk.Label(
        frame_cuerpo, 
        text="Órdenes de Trabajo en Campo", 
        fg="white", 
        bg="#1e3a8a", 
        font=("Arial", 14, "bold")
    )
    lbl_sub.pack(anchor="w", pady=(0, 10))

    # Estilo para la tabla de datos
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#ffffff", foreground="#000000", rowheight=25, fieldbackground="#ffffff")
    style.configure("Treeview.Heading", background="#f3f4f6", foreground="#111827", font=("Arial", 10, "bold"))

    # Crear tabla (Treeview)
    columnas = ("id", "cliente", "tecnico", "estado", "fecha")
    tabla = ttk.Treeview(frame_cuerpo, columns=columnas, show="headings", height=12)
    
    tabla.heading("id", text="N° Orden")
    tabla.heading("cliente", text="Cliente / Dirección")
    tabla.heading("tecnico", text="Técnico Asignado")
    tabla.heading("estado", text="Estado")
    tabla.heading("fecha", text="Fecha Creación")

    tabla.column("id", width=80, anchor="center")
    tabla.column("cliente", width=300, anchor="w")
    tabla.column("tecnico", width=180, anchor="w")
    tabla.column("estado", width=120, anchor="center")
    tabla.column("fecha", width=120, anchor="center")
    
    tabla.pack(fill="both", expand=True)

    # Insertar datos simulados iniciales para que no se vea vacío el panel azul
    tabla.insert("", "end", values=("101", "Distribuidora San Juan - Av. Bolívar", "Carlos Técnico", "Asignado", "19/10/2026"))
    tabla.insert("", "end", values=("102", "Residencias El Faro - Apto 4B", "Pendiente", "Abierta", "19/10/2026"))

    # --- BOTONES DE ACCIÓN ---
    frame_botones = tk.Frame(frame_cuerpo, bg="#1e3a8a")
    frame_botones.pack(fill="x", pady=(20, 0))

    btn_nueva = tk.Button(
        frame_botones, text="+ Crear Nueva Orden", bg="#10b981", fg="white", 
        font=("Arial", 10, "bold"), padx=15, pady=8, bd=0, cursor="hand2"
    )
    btn_nueva.pack(side="left", padx=(0, 10))

    btn_actualizar = tk.Button(
        frame_botones, text="🔄 Refrescar Datos", bg="#3b82f6", fg="white", 
        font=("Arial", 10, "bold"), padx=15, pady=8, bd=0, cursor="hand2"
    )
    btn_actualizar.pack(side="left")

    ventana_panel.mainloop()


def verificar_ingreso():
    """Valida los datos contra el servidor en la nube de Render"""
    user = entrada_usuario.get().strip()
    pas = entrada_contra.get().strip()

    if not user or not pas:
        messagebox.showwarning("Campos Vacíos", "Por favor ingresa tu usuario y contraseña.")
        return

    try:
        # Enviamos las credenciales en formato JSON plano directo al endpoint de login
        datos_enviar = {"username": user, "password": pas}
        respuesta = requests.post(f"{API_URL}/login", json=datos_enviar, timeout=10)

        if respuesta.status_code == 200:
            datos_usuario = respuesta.json()
            messagebox.showinfo("Acceso Concedido", f"¡Bienvenido al sistema, {datos_usuario['nombre']}!")
            
            # Cerrar la ventana de Login y abrir el panel administrativo azul
            ventana_login.destroy()
            abrir_panel_central_azul(datos_usuario)
        else:
            messagebox.showerror("Error de Credenciales", "Usuario o contraseña incorrectos. Verifica e intenta de nuevo.")
            
    except requests.exceptions.Timeout:
        messagebox.showerror("Error de Tiempo", "El servidor de Render está despertando (demora un minuto en el plan gratuito). Por favor, intenta de nuevo en unos segundos.")
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor de Render:\n{e}")


# ==========================================
# INTERFAZ VISUAL DE LOGIN (Tkinter)
# ==========================================
ventana_login = tk.Tk()
ventana_login.title("Inicio de Sesión - Mesa de Control")
ventana_login.geometry("400x450")
ventana_login.configure(bg="#f3f4f6")
ventana_login.resizable(False, False)

# Contenedor central blanco
frame_login = tk.Frame(ventana_login, bg="white", padx=30, pady=30, bd=1, relief="solid")
frame_login.place(relx=0.5, rely=0.5, anchor="center", width=340, height=380)

lbl_login_tit = tk.Label(frame_login, text="SISTEMA DE GESTIÓN", font=("Arial", 14, "bold"), bg="white", fg="#111827")
lbl_login_tit.pack(pady=(0, 5))
lbl_login_sub = tk.Label(frame_login, text="Inicia sesión para continuar", font=("Arial", 9), bg="white", fg="#6b7280")
lbl_login_sub.pack(pady=(0, 25))

# Campo: Usuario
lbl_u = tk.Label(frame_login, text="Usuario:", font=("Arial", 10, "bold"), bg="white", anchor="w")
lbl_u.pack(fill="x")
entrada_usuario = tk.Entry(frame_login, font=("Arial", 11), bd=1, relief="solid", bg="#f9fafb")
entrada_usuario.pack(fill="x", ipady=4, pady=(5, 15))
entrada_usuario.insert(0, "coord1")  # Usuario predeterminado para pruebas rápidas

# Campo: Contraseña
lbl_p = tk.Label(frame_login, text="Contraseña:", font=("Arial", 10, "bold"), bg="white", anchor="w")
lbl_p.pack(fill="x")
entrada_contra = tk.Entry(frame_login, font=("Arial", 11), show="*", bd=1, relief="solid", bg="#f9fafb")
entrada_contra.pack(fill="x", ipady=4, pady=(5, 25))
entrada_contra.insert(0, "123")  # Contraseña predeterminada para pruebas rápidas

# Botón Entrar
btn_entrar = tk.Button(
    frame_login, 
    text="Entrar al Sistema", 
    bg="#2563eb", 
    fg="white", 
    font=("Arial", 11, "bold"), 
    bd=0, 
    command=verificar_ingreso,
    cursor="hand2"
)
btn_entrar.pack(fill="x", ipady=6)

# Ejecutar el programa
ventana_login.mainloop()
