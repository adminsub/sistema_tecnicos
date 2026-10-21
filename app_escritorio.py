import flet as ft
import requests
import time
import threading
import webbrowser

# Desactivar advertencias visuales de SSL en la consola local
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. Dirección REAL y COMPLETA de tu servidor en Render
API_URL = "https://onrender.com"
USER_SESSION = {}

def main(page: ft.Page):
    page.title = "Mesa de Control - Sistema de Control de Técnicos de Campo"
    
    # Manejo compatible de dimensiones según tu versión de Flet
    try:
        page.window.width = 950
        page.window_height = 700
    except:
        page.window_width = 950
        page.window_height = 700
    
    # --- TU DISEÑO ORIGINAL DE CAMPOS DE ACCESO INTACTO ---
    txt_user = ft.TextField(label="Usuario", value="coord1")
    txt_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, value="123")
    
    # Tabla de monitoreo original
    tabla = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Cliente")),
        ft.DataColumn(ft.Text("Estado")), ft.DataColumn(ft.Text("Mapa"))
    ], rows=[])
    
    # Campos del formulario original
    txt_cli = ft.TextField(label="Cliente", expand=True)
    txt_dir = ft.TextField(label="Dirección", expand=True)
    txt_desc = ft.TextField(label="Falla/Trabajo", expand=True)
    txt_tec_id = ft.TextField(label="ID Técnico", width=120)
    
    def cargar_datos_bucle():
        while True:
            if "rol" in USER_SESSION:
                try:
                    # verify=False salta el bloqueo de certificados locales en el bucle
                    res = requests.get(f"{API_URL}/ordenes/?rol={USER_SESSION['rol']}&usuario_id={USER_SESSION['id']}", timeout=5, verify=False)
                    if res.status_code == 200:
                        tabla.rows.clear()
                        datos = res.json()
                        if isinstance(datos, list):
                            for o in datos:
                                btn_mapa = ft.Text("Sin GPS")
                                if o.get('latitud') and o.get('longitud'):
                                    url = f"https://google.com{o['latitud']},{o['longitud']}"
                                    btn_mapa = ft.IconButton(ft.icons.LOCATION_ON, icon_color="red", on_click=lambda e, u=url: webbrowser.open(u))
                                tabla.rows.append(ft.DataRow(cells=[
                                    ft.DataCell(ft.Text(str(o.get('id', '')))), 
                                    ft.DataCell(ft.Text(o.get('cliente', ''))),
                                    ft.DataCell(ft.Text(o.get('estado', 'Pendiente'), weight="bold")), 
                                    ft.DataCell(btn_mapa)
                                ]))
                        page.update()
                except Exception as e:
                    print(f"⚠️ Error en bucle de datos: {e}")
            time.sleep(10)

    def ejecutar_login(e):
        usuario_tipeado = txt_user.value.strip()
        contra_tipeada = txt_pass.value.strip()
        
        url_destino = f"{API_URL}/login"
        
        try:
            # INTENTO 1: JSON con verify=False para forzar la salida a internet sin verificar SSL local
            res = requests.post(url_destino, json={"username": usuario_tipeado, "password": contra_tipeada}, timeout=15, verify=False)
            
            # INTENTO 2: Si el formato JSON no da 200, intentamos Formulario clásico también con verify=False
            if res.status_code != 200:
                res = requests.post(url_destino, data={"username": usuario_tipeado, "password": contra_tipeada}, timeout=15, verify=False)
            
            if res.status_code == 200:
                data = res.json()
                USER_SESSION["id"] = data["id"]
                USER_SESSION["rol"] = data["rol"]
                USER_SESSION["nombre"] = data["nombre"]
                
                if USER_SESSION["rol"] == "tecnico":
                    page.overlay.append(ft.SnackBar(ft.Text("Los técnicos deben usar la App Móvil"), bgcolor="red", open=True))
                    page.update()
                    return
                mostrar_panel_principal()
            else:
                page.overlay.append(ft.SnackBar(ft.Text("Credenciales inválidas o usuario incorrecto"), bgcolor="red", open=True))
                page.update()
        except Exception as error:
            print(f"⚠️ ERROR DE CONEXIÓN REAL: {error}")
            page.overlay.append(ft.SnackBar(ft.Text("Error de red. Verifica internet o intenta de nuevo."), bgcolor="orange", open=True))
            page.update()

    def guardar_orden(e):
        payload = {"cliente": txt_cli.value, "direccion": txt_dir.value, "descripcion": txt_desc.value, "tecnico_id": int(txt_tec_id.value) if txt_tec_id.value else None}
        try:
            requests.post(f"{API_URL}/ordenes/?creador_rol={USER_SESSION['rol']}", json=payload, timeout=5, verify=False)
            txt_cli.value = txt_dir.value = txt_desc.value = txt_tec_id.value = ""
            page.update()
        except: pass

    def mostrar_panel_principal():
        page.views.clear()
        deshabilitar_creacion = USER_SESSION["rol"] not in ["coordinador", "gerente"]
        
        form_container = ft.Container(
            padding=15, bgcolor=ft.colors.GREY_100, border_radius=10, disabled=deshabilitar_creacion,
            content=ft.Column([
                ft.Text("Nueva Orden de Trabajo (Solo Coordinación/Gerencia)", weight="bold"),
                ft.Row([txt_cli, txt_tec_id]), ft.Row([txt_dir]), ft.Row([txt_desc]),
                ft.ElevatedButton("Asignar Tarea", on_click=guardar_orden, bgcolor="blue", color="white")
            ])
        )
        
        # --- TU VISTA ORIGINAL CON APPBAR AZUL ---
        page.views.append(ft.View("/panel", [
            ft.AppBar(title=ft.Text(f"Panel Central - {USER_SESSION['nombre']} ({USER_SESSION['rol'].upper()})"), bgcolor="blue"),
            form_container,
            ft.Text("Monitoreo de Actividad de Campo", weight="bold"),
            ft.Container(content=tabla, expand=True, scroll=ft.ScrollMode.ALWAYS)
        ]))
        page.update()

    # Iniciar el hilo de lectura de la base de datos
    threading.Thread(target=cargar_datos_bucle, daemon=True).start()

    # --- ARRANQUE NATIVO DE FLET ---
    contenedor_login = ft.Container(
        alignment=ft.alignment.center, 
        content=ft.Column([
            ft.Text("Mesa de Control - Acceso Administrativo", size=20, weight="bold"),
            txt_user, txt_pass, 
            ft.ElevatedButton("Entrar al Sistema", on_click=ejecutar_login, width=200)
        ], horizontal_alignment="center")
    )
    
    page.add(contenedor_login)

ft.app(target=main)
