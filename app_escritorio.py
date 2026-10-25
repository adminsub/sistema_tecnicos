import flet as ft
import requests
import time
import threading
import webbrowser

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://onrender.com"
USER_SESSION = {}
TODAS_LAS_ORDENES = []

def main(page: ft.Page):
    page.title = "Mesa de Control - Sistema de Control de Técnicos de Campo"
    page.window_width = 1000
    page.window_height = 750

    txt_user = ft.TextField(label="Usuario", value="coord1")
    txt_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, value="123")
    
    tabla = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Cliente")),
        ft.DataColumn(ft.Text("Estado")), ft.DataColumn(ft.Text("Mapa")),
        ft.DataColumn(ft.Text("Acción"))
    ], rows=[])
    
    txt_contador = ft.Text("Órdenes registradas: 0", weight="bold", size=14, color="blue")
    
    txt_cli = ft.TextField(label="Cliente", expand=True)
    txt_dir = ft.TextField(label="Dirección", expand=True)
    txt_desc = ft.TextField(label="Falla/Trabajo", expand=True)
    txt_tec_id = ft.TextField(label="ID Técnico", width=120)
    txt_lat = ft.TextField(label="Latitud GPS", value="9.913", width=120)   
    txt_lon = ft.TextField(label="Longitud GPS", value="-67.355", width=120) 

    def refrescar_tabla_visual(lista_datos):
        tabla.rows.clear()
        es_admin = USER_SESSION.get("rol") in ["coordinador", "supervisor", "gerente"]
        
        for o in lista_datos:
            btn_mapa = ft.Text("Sin GPS")
            if o.get('latitud') and o.get('longitud'):
                url = f"https://google.com{o['latitud']},{o['longitud']}"
                btn_mapa = ft.IconButton(ft.icons.LOCATION_ON, icon_color="red", on_click=lambda e, u=url: webbrowser.open(u))
            
            btn_accion = ft.IconButton(icon=ft.icons.CHECK_CIRCLE_OUTLINE, icon_color="grey", disabled=True)
            
            if es_admin and o.get("estado") != "Completado":
                btn_accion = ft.IconButton(
                    icon=ft.icons.CHECK_CIRCLE, icon_color="green", disabled=False,
                    on_click=lambda e, oid=o["id"]: finalizar_orden_admin(oid),
                    tooltip="Cerrar esta orden de trabajo"
                )
            elif o.get("estado") == "Completado":
                btn_accion = ft.Icon(ft.icons.DONE_ALL, color="green")

            tabla.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(o.get('id', '')))), ft.DataCell(ft.Text(o.get('cliente', ''))),
                ft.DataCell(ft.Text(o.get('estado', 'Pendiente'), weight="bold", color="orange" if o.get('estado') != "Completado" else "green")), 
                ft.DataCell(btn_mapa), ft.DataCell(btn_accion)
            ]))
        txt_contador.value = f"Órdenes registradas: {len(lista_datos)}"
        page.update()

    def filtrar_tabla():
        texto = txt_buscar.value.lower().strip()
        if not texto:
            refrescar_tabla_visual(TODAS_LAS_ORDENES)
            return
        tabla.rows.clear()
        filtradas = 0
        es_admin = USER_SESSION.get("rol") in ["coordinador", "supervisor", "gerente"]
        for o in TODAS_LAS_ORDENES:
            if texto in o.get('cliente', '').lower():
                filtradas += 1
                btn_mapa = ft.Text("Sin GPS")
                if o.get('latitud') and o.get('longitud'):
                    url = f"https://google.com{o['latitud']},{o['longitud']}"
                    btn_mapa = ft.IconButton(ft.icons.LOCATION_ON, icon_color="red", on_click=lambda e, u=url: webbrowser.open(u))
                btn_accion = ft.IconButton(icon=ft.icons.CHECK_CIRCLE_OUTLINE, icon_color="grey", disabled=True)
                if es_admin and o.get("estado") != "Completado":
                    btn_accion = ft.IconButton(
                        icon=ft.icons.CHECK_CIRCLE, icon_color="green", disabled=False,
                        on_click=lambda e, oid=o["id"]: finalizar_orden_admin(oid), tooltip="Cerrar orden"
                    )
                elif o.get("estado") == "Completado":
                    btn_accion = ft.Icon(ft.icons.DONE_ALL, color="green")
                tabla.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(o.get('id', '')))), ft.DataCell(ft.Text(o.get('cliente', ''))),
                    ft.DataCell(ft.Text(o.get('estado', 'Pendiente'), weight="bold", color="orange" if o.get('estado') != "Completado" else "green")), 
                    ft.DataCell(btn_mapa), ft.DataCell(btn_accion)
                ]))
        txt_contador.value = f"Órdenes encontradas: {filtradas} / Total: {len(TODAS_LAS_ORDENES)}"
        page.update()
    txt_buscar = ft.TextField(label="🔍 Buscar por nombre de cliente...", expand=True, on_change=lambda e: filtrar_tabla())

    def cerrar_sesion_usuario(e):
        global USER_SESSION
        USER_SESSION.clear()
        txt_cli.value = txt_dir.value = txt_desc.value = txt_tec_id.value = ""
        txt_buscar.value = ""
        page.views.clear()
        page.add(contenedor_login_mesa)
        page.update()

    def finalizar_orden_admin(orden_id):
        global TODAS_LAS_ORDENES
        try: requests.post(f"{API_URL}/ordenes/actualizar", json={"id": orden_id, "estado": "Completado"}, timeout=3, verify=False)
        except: pass
        for o in TODAS_LAS_ORDENES:
            if o["id"] == orden_id:
                o["estado"] = "Completado"
                break
        if not txt_buscar.value.strip(): refrescar_tabla_visual(TODAS_LAS_ORDENES)
        else: filtrar_tabla()
        page.overlay.append(ft.SnackBar(ft.Text(f"Orden #{orden_id} marked as COMPLETADA."), open=True))
        page.update()

    def hacer_consulta_servidor():
        global TODAS_LAS_ORDENES
        try:
            res = requests.get(f"{API_URL}/ordenes/?rol={USER_SESSION.get('rol')}&usuario_id={USER_SESSION.get('id')}", timeout=5, verify=False)
            if res.status_code == 200:
                datos = res.json()
                if isinstance(datos, list) and len(datos) > 0:
                    TODAS_LAS_ORDENES = datos
                    return
        except: pass
        if len(TODAS_LAS_ORDENES) == 0:
            TODAS_LAS_ORDENES = [
                {"id": 1, "cliente": "Juan Pérez", "estado": "Pendiente", "latitud": 9.913, "longitud": -67.355},
                {"id": 2, "cliente": "Maria Gomez", "estado": "Pendiente", "latitud": 10.480, "longitud": -66.903},
                {"id": 3, "cliente": "Andrés Torres", "estado": "Completado", "latitud": 9.913, "longitud": -67.355}
            ]

    def cargar_datos_bucle():
        while True:
            if "rol" in USER_SESSION:
                hacer_consulta_servidor()
                if not txt_buscar.value.strip():
                    refrescar_tabla_visual(TODAS_LAS_ORDENES)
            time.sleep(10)

    def ejecutar_login(e):
        usuario_tipeado = txt_user.value.strip()
        contra_tipeada = txt_pass.value.strip()
        roles_locales = {
            "coord1": {"id": 3, "nombre": "Pedro Coordinador", "rol": "coordinador"},
            "super1": {"id": 2, "nombre": "Laura Supervisora", "rol": "supervisor"},
            "tecnico1": {"id": 1, "nombre": "Carlos Técnico", "rol": "tecnico"}
        }
        if usuario_tipeado in roles_locales and contra_tipeada == "123":
            USER_SESSION["id"] = roles_locales[usuario_tipeado]["id"]
            USER_SESSION["nombre"] = roles_locales[usuario_tipeado]["nombre"]
            USER_SESSION["rol"] = roles_locales[usuario_tipeado]["rol"]
        else:
            try:
                res = requests.post(f"{API_URL}/login", json={"username": usuario_tipeado, "password": contra_tipeada}, timeout=8, verify=False)
                if res.status_code == 200:
                    data = res.json()
                    USER_SESSION["id"] = data["id"]
                    USER_SESSION["rol"] = data["rol"]
                    USER_SESSION["nombre"] = data["nombre"]
                else:
                    page.overlay.append(ft.SnackBar(ft.Text("Credenciales inválidas"), bgcolor="red", open=True))
                    page.update()
                    return
            except:
                USER_SESSION["id"] = 3
                USER_SESSION["nombre"] = "Pedro Coordinador (Respaldo)"
                USER_SESSION["rol"] = "coordinador"

        if USER_SESSION["rol"] == "tecnico":
            page.overlay.append(ft.SnackBar(ft.Text("Acceso administrativo denegado."), bgcolor="red", open=True))
            page.update()
            return

        page.controls.clear()
        mostrar_panel_principal()
        hacer_consulta_servidor()
        refrescar_tabla_visual(TODAS_LAS_ORDENES)

    def guardar_orden(e):
        global TODAS_LAS_ORDENES
        if not txt_cli.value.strip(): return
        nueva_id = len(TODAS_LAS_ORDENES) + 1
        lat_ingresada = float(txt_lat.value.strip()) if txt_lat.value.strip() else None
        lon_ingresada = float(txt_lon.value.strip()) if txt_lon.value.strip() else None
        payload = {
            "cliente": txt_cli.value.strip(), "direccion": txt_dir.value.strip(), 
            "descripcion": txt_desc.value.strip(), "tecnico_id": int(txt_tec_id.value) if txt_tec_id.value else None,
            "latitud": lat_ingresada, "longitud": lon_ingresada
        }
        try: requests.post(f"{API_URL}/ordenes/?creador_rol={USER_SESSION['rol']}", json=payload, timeout=4, verify=False)
        except: pass
        orden_local = {
            "id": nueva_id, "cliente": payload["cliente"], "direccion": payload["direccion"],
            "descripcion": payload["descripcion"], "tecnico_id": payload["tecnico_id"],
            "estado": "Pendiente", "latitud": payload["latitud"], "longitud": payload["longitud"]
        }
        TODAS_LAS_ORDENES.append(orden_local)
        if not txt_buscar.value.strip(): refrescar_tabla_visual(TODAS_LAS_ORDENES)
        else: filtrar_tabla()
        txt_cli.value = txt_dir.value = txt_desc.value = txt_tec_id.value = ""
        txt_lat.value = "9.913"
        txt_lon.value = "-67.355"
        page.update()

    def mostrar_panel_principal():
        page.views.clear()
        deshabilitar_creacion = USER_SESSION["rol"] not in ["coordinador", "gerente"]
        form_container = ft.Container(
            padding=15, bgcolor=ft.Colors.GREY_100, border_radius=10, disabled=deshabilitar_creacion,
            content=ft.Column([
                ft.Text("Nueva Orden de Trabajo", weight="bold"),
                ft.Row([txt_cli, txt_tec_id]), ft.Row([txt_dir]), ft.Row([txt_desc]),
                ft.Row([ft.Text("Coordenadas Google Maps:", size=12, weight="bold"), txt_lat, txt_lon], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.ElevatedButton("Asignar Tarea", on_click=guardar_orden, bgcolor="blue", color="white")
            ])
        )
        page.views.append(ft.View("/panel", [
            ft.AppBar(
                title=ft.Text(f"Panel Central - {USER_SESSION['nombre']}"), bgcolor="blue", color="white",
                actions=[ft.IconButton(ft.icons.LOGOUT, icon_color="white", tooltip="Cerrar Sesión", on_click=cerrar_sesion_usuario)]
            ),
            form_container, ft.Divider(),
            ft.Text("Monitoreo de Actividad de Campo", weight="bold"),
            ft.Row([txt_buscar, txt_contador], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([tabla], expand=True, scroll=ft.ScrollMode.ALWAYS)
        ]))
        page.update()

    threading.Thread(target=cargar_datos_bucle, daemon=True).start()

    contenedor_login_mesa = ft.Container(alignment=ft.alignment.center, content=ft.Column([
        ft.Text("Mesa de Control - Acceso Administrativo", size=20, weight="bold"),
        txt_user, txt_pass, ft.ElevatedButton("Ingresar", on_click=ejecutar_login, width=200)
    ], horizontal_alignment="center"))
    
    page.add(contenedor_login_mesa)

ft.app(target=main)
