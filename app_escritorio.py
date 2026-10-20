import flet as ft
import requests
import time
import threading
import webbrowser

API_URL = "https://onrender.com"

USER_SESSION = {}

def main(page: ft.Page):
    page.title = "Mesa de Control - Sistema de Control de Técnicos de Campo"
    page.window_width = 950
    page.window_height = 700
    
    txt_user = ft.TextField(label="Usuario")
    txt_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
    
    tabla = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Cliente")),
        ft.DataColumn(ft.Text("Estado")), ft.DataColumn(ft.Text("Mapa"))
    ], rows=[])
    
    txt_cli = ft.TextField(label="Cliente", expand=True)
    txt_dir = ft.TextField(label="Dirección", expand=True)
    txt_desc = ft.TextField(label="Falla/Trabajo", expand=True)
    txt_tec_id = ft.TextField(label="ID Técnico", width=120)
    
    def cargar_datos_bucle():
        while True:
            if "rol" in USER_SESSION:
                try:
                    res = requests.get(f"{API_URL}/ordenes/?rol={USER_SESSION['rol']}&usuario_id={USER_SESSION['id']}")
                    if res.status_code == 200:
                        tabla.rows.clear()
                        for o in res.json():
                            btn_mapa = ft.Text("Sin GPS")
                            if o['latitud'] and o['longitud']:
                                url = f"https://google.com{o['latitud']},{o['longitud']}"
                                btn_mapa = ft.IconButton(ft.icons.LOCATION_ON, icon_color="red", on_click=lambda e, u=url: webbrowser.open(u))
                            tabla.rows.append(ft.DataRow(cells=[
                                ft.DataCell(ft.Text(str(o['id']))), ft.DataCell(ft.Text(o['cliente'])),
                                ft.DataCell(ft.Text(o['estado'], weight="bold")), ft.DataCell(btn_mapa)
                            ]))
                        page.update()
                except: pass
            time.sleep(10)

    def ejecutar_login(e):
        try:
            res = requests.post(f"{API_URL}/login", json={"username": txt_user.value, "password": txt_pass.value})
            if res.status_code == 200:
                data = res.json()
                USER_SESSION["id"], USER_SESSION["rol"], USER_SESSION["nombre"] = data["id"], data["rol"], data["nombre"]
                if USER_SESSION["rol"] == "tecnico":
                    page.snack_bar = ft.SnackBar(ft.Text("Los técnicos deben usar la App Móvil"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
                    return
                mostrar_panel_principal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Credenciales inválidas o usuario incorrecto"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
        except Exception as error:
            print(f"⚠️ DETALLE DEL ERROR: {error}")
            page.snack_bar = ft.SnackBar(ft.Text("No se pudo conectar con el servidor de internet"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()

    def guardar_orden(e):
        payload = {"cliente": txt_cli.value, "direccion": txt_dir.value, "descripcion": txt_desc.value, "tecnico_id": int(txt_tec_id.value) if txt_tec_id.value else None}
        requests.post(f"{API_URL}/ordenes/?creador_rol={USER_SESSION['rol']}", json=payload)
        txt_cli.value = txt_dir.value = txt_desc.value = txt_tec_id.value = ""
        page.update()

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
        
        page.views.append(ft.View("/panel", [
            ft.AppBar(title=ft.Text(f"Panel Central - {USER_SESSION['nombre']} ({USER_SESSION['rol'].upper()})"), bgcolor="blue"),
            form_container,
            ft.Text("Monitoreo de Actividad de Campo", weight="bold"),
            ft.Container(content=tabla, expand=True, scroll=ft.ScrollMode.ALWAYS)
        ]))
        page.update()

    threading.Thread(target=cargar_datos_bucle, daemon=True).start()

    page.add(ft.Container(alignment=ft.alignment.center, content=ft.Column([
        ft.Text("Mesa de Control - Acceso Administrativo", size=20, weight="bold"),
        txt_user, txt_pass, ft.ElevatedButton("Entrar al Sistema", on_click=ejecutar_login, width=200)
    ], horizontal_alignment="center")))

ft.app(target=main)
