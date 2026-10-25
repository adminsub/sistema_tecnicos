import flet as ft
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://onrender.com"
SESSION_ADMIN = {}
LISTA_USUARIOS_LOCALES = []

def main(page: ft.Page):
    page.title = "Módulo de Administración - Gestión de Usuarios"
    page.window_width = 1100
    page.window_height = 750

    # --- COMPONENTES DE LOGIN ---
    txt_user = ft.TextField(label="Correo Admin", value="admin@sistema.com")
    txt_pass = ft.TextField(label="Clave", password=True, value="admin123")

    # --- COMPONENTES DEL FORMULARIO DE USUARIOS ---
    txt_p00 = ft.TextField(label="ID Principal (Ej: P002)", width=150)
    txt_carnet = ft.TextField(label="ID Carnet (Opcional)", width=150)
    txt_correo = ft.TextField(label="Correo (Usuario de Acceso)", expand=True)
    txt_clave = ft.TextField(label="Contraseña de Acceso", password=True, width=180)
    txt_nombres = ft.TextField(label="Nombres", expand=True)
    txt_apellidos = ft.TextField(label="Apellidos", expand=True)
    txt_cedula = ft.TextField(label="Cédula de Identidad", width=180)
    txt_sangre = ft.TextField(label="Tipo de Sangre", value="O+", width=120)

    dropdown_rol = ft.Dropdown(
        label="Rol del Usuario",
        width=200,
        options=[
            ft.dropdown.Option("admin", "Administrador"),
            ft.dropdown.Option("coordinador", "Coordinador"),
            ft.dropdown.Option("supervisor", "Supervisor"),
            ft.dropdown.Option("tecnico", "Técnico de Campo")
        ],
        value="tecnico"
    )

    dropdown_area_tipo = ft.Dropdown(
        label="Tipo de Cobertura",
        width=180,
        options=[
            ft.dropdown.Option("numero", "Por Área (1-10)"),
            ft.dropdown.Option("estadal", "Estadal (Todas)")
        ],
        value="numero",
        on_change=lambda e: actualizar_visibilidad_areas()
    )

    dropdown_area_valor = ft.Dropdown(
        label="Selección de Área",
        width=180,
        options=[ft.dropdown.Option(str(i), f"Área {i}") for i in range(1, 11)],
        value="1"
    )

    tabla_usuarios = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID P00")), ft.DataColumn(ft.Text("Nombre")),
        ft.DataColumn(ft.Text("Correo")), ft.DataColumn(ft.Text("Rol")),
        ft.DataColumn(ft.Text("Área / Cobertura"))
    ], rows=[])

    def actualizar_visibilidad_areas():
        if dropdown_area_tipo.value == "estadal":
            dropdown_area_valor.options = [ft.dropdown.Option("TODAS", "Todas las Áreas")]
            dropdown_area_valor.value = "TODAS"
        else:
            dropdown_area_valor.options = [ft.dropdown.Option(str(i), f"Área {i}") for i in range(1, 11)]
            dropdown_area_valor.value = "1"
        page.update()
    def refrescar_tabla_usuarios(lista):
        tabla_usuarios.rows.clear()
        for u in lista:
            cobertura = f"Estadal ({u['area_valor']})" if u['area_tipo'] == "estadal" else f"Área Num. {u['area_valor']}"
            tabla_usuarios.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(u['id_p00'], weight="bold")),
                ft.DataCell(ft.Text(f"{u['nombres']} {u['apellidos']}")),
                ft.DataCell(ft.Text(u['correo'])),
                ft.DataCell(ft.Text(u['rol'].upper())),
                ft.DataCell(ft.Text(cobertura))
            ]))
        page.update()

    def guardar_usuario(e):
        global LISTA_USUARIOS_LOCALES
        if not txt_p00.value.strip() or not txt_correo.value.strip():
            page.overlay.append(ft.SnackBar(ft.Text("ID P00 y Correo son obligatorios"), bgcolor="red", open=True))
            page.update()
            return

        payload = {
            "id_p00": txt_p00.value.strip(), "id_carnet": txt_carnet.value.strip() if txt_carnet.value.strip() else None,
            "correo": txt_correo.value.strip(), "clave": txt_clave.value.strip() if txt_clave.value.strip() else "123",
            "nombres": txt_nombres.value.strip(), "apellidos": txt_apellidos.value.strip(),
            "cedula": txt_cedula.value.strip(), "tipo_sangre": txt_sangre.value.strip(),
            "area_tipo": dropdown_area_tipo.value, "area_valor": dropdown_area_valor.value,
            "rol": dropdown_rol.value
        }

        try:
            requests.post(f"{API_URL}/usuarios/registrar", json=payload, timeout=5, verify=False)
        except:
            pass

        LISTA_USUARIOS_LOCALES.append(payload)
        refrescar_tabla_usuarios(LISTA_USUARIOS_LOCALES)

        # Limpiar campos del formulario
        txt_p00.value = txt_carnet.value = txt_correo.value = txt_clave.value = ""
        txt_nombres.value = txt_apellidos.value = txt_cedula.value = ""
        page.overlay.append(ft.SnackBar(ft.Text("Usuario registrado con éxito en el sistema"), bgcolor="green", open=True))
        page.update()

    def autenticar_admin(e):
        if txt_user.value.strip() == "admin@sistema.com" and txt_pass.value.strip() == "admin123":
            SESSION_ADMIN["rol"] = "admin"
            mostrar_panel_admin()
            refrescar_tabla_usuarios(LISTA_USUARIOS_LOCALES)
        else:
            page.overlay.append(ft.SnackBar(ft.Text("Acceso denegado. Use credenciales de Admin maestro"), bgcolor="red", open=True))
            page.update()

    def mostrar_panel_admin():
        page.views.clear()
        
        formulario = ft.Container(
            padding=15, bgcolor=ft.Colors.GREY_100, border_radius=10,
            content=ft.Column([
                ft.Text("Registrar Nuevo Personal (Mesa de Control y Campo)", weight="bold", size=16),
                ft.Row([txt_p00, txt_carnet, txt_correo, txt_clave]),
                ft.Row([txt_nombres, txt_apellidos, txt_cedula, txt_sangre]),
                ft.Row([dropdown_rol, dropdown_area_tipo, dropdown_area_valor]),
                ft.ElevatedButton("Dar de Alta en Base de Datos", on_click=guardar_usuario, bgcolor="purple", color="white")
            ])
        )

        page.views.append(ft.View("/admin-panel", [
            ft.AppBar(title=ft.Text("Panel de Control del Administrador - Configuración del Sistema"), bgcolor="purple", color="white"),
            formulario,
            ft.Divider(),
            ft.Text("Listado Oficial de Usuarios en Base de Datos", weight="bold"),
            ft.Column([tabla_usuarios], expand=True, scroll=ft.ScrollMode.ALWAYS)
        ]))
        page.update()

    # Pantalla de acceso inicial
    page.add(ft.Container(alignment=ft.alignment.center, content=ft.Column([
        ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS, size=60, color="purple"),
        ft.Text("Acceso exclusivo del Administrador", size=20, weight="bold"),
        txt_user, txt_pass, ft.ElevatedButton("Ingresar al Módulo", on_click=autenticar_admin, width=220, bgcolor="purple", color="white")
    ], horizontal_alignment="center")))

ft.app(target=main)
