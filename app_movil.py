import flet as ft
import requests

API_URL = "https://pythonanywhere.com"
TECNICO_SESSION = {}

def main(page: ft.Page):
    page.title = "Módulo de Campo - Técnicos"
    txt_user = ft.TextField(label="Usuario Técnico")
    txt_pass = ft.TextField(label="Contraseña", password=True)
    lista_container = ft.ListView(expand=True, spacing=10)
    
    geolocator = ft.Geolocator()
    page.overlay.append(geolocator)

    def obtener_gps():
        try:
            if not geolocator.has_permission(): geolocator.request_permission()
            pos = geolocator.get_current_position()
            if pos: return pos.latitude, pos.longitude
        except: pass
        return None, None

    def cambiar_estado(orden_id, estado_nuevo):
        lat, lon = obtener_gps()
        url = f"{API_URL}/ordenes/{orden_id}/estado?nuevo_estado={estado_nuevo}"
        if lat and lon: url += f"&lat={lat}&lon={lon}"
        requests.patch(url)
        cargar_agenda_tecnico()

    def cargar_agenda_tecnico():
        lista_container.controls.clear()
        res = requests.get(f"{API_URL}/ordenes/?rol=tecnico&usuario_id={TECNICO_SESSION['id']}")
        if res.status_code == 200:
            for o in res.json():
                btn = ft.Text("Completado")
                if o['estado'] == 'Pendiente':
                    btn = ft.ElevatedButton("Iniciar Ruta 🚗", on_click=lambda e, id=o['id']: cambiar_estado(id, "En Ruta"), bgcolor="blue", color="white")
                elif o['estado'] == 'En Ruta':
                    btn = ft.ElevatedButton("Llegué al Sitio 📍", on_click=lambda e, id=o['id']: cambiar_estado(id, "En Sitio"), bgcolor="orange", color="white")
                elif o['estado'] == 'En Sitio':
                    btn = ft.ElevatedButton("Terminar Trabajo ✅", on_click=lambda e, id=o['id']: cambiar_estado(id, "Completado"), bgcolor="green", color="white")
                
                lista_container.controls.append(ft.Card(content=ft.Container(padding=15, content=ft.Column([
                    ft.Text(f"OT #{o['id']} - {o['cliente']}", weight="bold"),
                    ft.Text(f"Dirección: {o['direccion']}"),
                    ft.Text(f"Estado actual: {o['estado']}"),
                    btn
                ]))))
        page.update()

    def login_tecnico(e):
        res = requests.post(f"{API_URL}/login", json={"username": txt_user.value, "password": txt_pass.value})
        if res.status_code == 200 and res.json()["rol"] == "tecnico":
            TECNICO_SESSION["id"] = res.json()["id"]
            page.views.clear()
            page.views.append(ft.View("/agenda", [
                ft.AppBar(title=ft.Text("Mi Agenda de Trabajo"), bgcolor="green"),
                lista_container
            ]))
            cargar_agenda_tecnico()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Acceso exclusivo para Técnicos"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    page.add(ft.Column([
        ft.Text("Acceso Técnicos de Campo", size=18, weight="bold"),
        txt_user, txt_pass, ft.ElevatedButton("Ingresar", on_click=login_tecnico)
    ], horizontal_alignment="center"))

ft.main(target=main)

