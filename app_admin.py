import flet as ft
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://onrender.com"
SESSION_ADMIN = {}
LISTA_USUARIOS_LOCALES = []
USUARIO_SELECCIONADO_ID = None

def main(page: ft.Page):
    page.title = "Módulo de Administración - Gestión de Usuarios"
    page.window_width = 1100
    page.window_height = 750

    # --- ESTILOS DE ENTRADA ALTA VISIBILIDAD (AZUL MARINO) ---
    # Fondo blanco puro, texto negro intenso y etiquetas en azul marino para máxima comodidad visual
    def crear_campo_texto(label, expand=False, width=None, password=False, value=""):
        return ft.TextField(
            label=label,
            value=value,
            password=password,
            expand=expand,
            width=width,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.WHITE,
            border_color=ft.Colors.BLUE_900,
            label_style=ft.TextStyle(color=ft.Colors.BLUE_900, weight="bold"),
            focused_border_color=ft.Colors.BLUE_ACCENT_700
        )

    # --- COMPONENTES DE LOGIN ---
    txt_user = crear_campo_texto("Correo Admin", value="admin@sistema.com")
    txt_pass = crear_campo_texto("Clave", password=True, value="admin123")

    # --- COMPONENTES DEL FORMULARIO DE USUARIOS ---
    txt_p00 = crear_campo_texto("ID Principal (Ej: P002)", width=150)
    txt_carnet = crear_campo_texto("ID Carnet (Opcional)", width=150)
    txt_correo = crear_campo_texto("Correo (Usuario de Acceso)", expand=True)
    txt_clave = crear_campo_texto("Contraseña de Acceso", password=True, width=180)
    txt_nombres = crear_campo_texto("Nombres", expand=True)
    txt_apellidos = crear_campo_texto("Apellidos", expand=True)
    txt_cedula = crear_campo_texto("Cédula de Identidad", width=180)
    txt_sangre = crear_campo_texto("Tipo de Sangre", value="O+", width=120)

    dropdown_rol = ft.Dropdown(
        label="Rol del Usuario", width=200,
        color=ft.Colors.BLACK, bgcolor=ft.Colors.WHITE,
        border_color=ft.Colors.BLUE_900,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_900, weight="bold"),
        options=[
            ft.dropdown.Option("admin", "Administrador"),
            ft.dropdown.Option("coordinador", "Coordinador"),
            ft.dropdown.Option("supervisor", "Supervisor"),
            ft.dropdown.Option("tecnico", "Técnico de Campo")
        ], value="tecnico"
    )

    dropdown_area_tipo = ft.Dropdown(
        label="Tipo de Cobertura", width=180,
        color=ft.Colors.BLACK, bgcolor=ft.Colors.WHITE,
        border_color=ft.Colors.BLUE_900,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_900, weight="bold"),
        options=[
            ft.dropdown.Option("numero", "Por Área (1-10)"),
            ft.dropdown.Option("estadal", "Estadal (Todas)")
        ], value="numero",
        on_change=lambda e: actualizar_visibilidad_areas()
    )

    dropdown_area_valor = ft.Dropdown(
        label="Selección de Área", width=180,
        color=ft.Colors.BLACK, bgcolor=ft.Colors.WHITE,
        border_color=ft.Colors.BLUE_900,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_900, weight="bold"),
        options=[ft.dropdown.Option(str(i), f"Área {i}") for i in range(1, 11)],
        value="1"
    )

    btn_guardar = ft.ElevatedButton("Guardar", bgcolor="purple", color="white")
    btn_eliminar = ft.ElevatedButton("Eliminar Usuario", bgcolor="red", color="white", visible=False)
    btn_cancelar = ft.TextButton("Cancelar Edición", visible=False)

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

    def seleccionar_usuario_para_editar(u):
        global USUARIO_SELECCIONADO_ID
        USUARIO_SELECCIONADO_ID = u['id_p00']
        txt_p00.value = u['id_p00']
        txt_p00.disabled = True
        txt_carnet.value = u.get('id_carnet', '') if u.get('id_carnet') else ""
        txt_correo.value = u['correo']
        txt_clave.value = u.get('clave', '') if u.get('clave') else ""
        txt_nombres.value = u['nombres']
        txt_apellidos.value = u['apellidos']
        txt_cedula.value = u.get('cedula', '') if u.get('cedula') else ""
        txt_sangre.value = u.get('tipo_sangre', 'O+')
        dropdown_rol.value = u['rol']
        dropdown_area_tipo.value = u['area_tipo']
        actualizar_visibilidad_areas()
        dropdown_area_valor.value = u['area_valor']
        
        btn_guardar.text = "Actualizar Cambios"
        btn_eliminar.visible = True
        btn_cancelar.visible = True
        mostrar_panel_admin()

    def limpiar_formulario():
        global USUARIO_SELECCIONADO_ID
        USUARIO_SELECCIONADO_ID = None
        txt_p00.value = txt_carnet.value = txt_correo.value = txt_clave.value = ""
        txt_nombres.value = txt_apellidos.value = txt_cedula.value = ""
        txt_p00.disabled = False
        dropdown_rol.value = "tecnico"
        dropdown_area_tipo.value = "numero"
        actualizar_visibilidad_areas()
        btn_guardar.text = "Guardar"
        btn_eliminar.visible = False
        btn_cancelar.visible = False
        mostrar_panel_admin()
    def generar_filas_tabla():
        tabla_usuarios.rows.clear()
        for u in LISTA_USUARIOS_LOCALES:
            cobertura = f"Estadal ({u['area_valor']})" if u['area_tipo'] == "estadal" else f"Área Num. {u['area_valor']}"
            tabla_usuarios.rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(u['id_p00'], weight="bold")),
                    ft.DataCell(ft.Text(f"{u['nombres']} {u['apellidos']}")),
                    ft.DataCell(ft.Text(u['correo'])),
                    ft.DataCell(ft.Text(u['rol'].upper())),
                    ft.DataCell(ft.Text(cobertura))
                ],
                on_select_changed=lambda e, user=u: seleccionar_usuario_para_editar(user)
            ))

    def consultar_usuarios_servidor():
        global LISTA_USUARIOS_LOCALES
        try:
            res = requests.get(f"{API_URL}/usuarios/listar", timeout=5, verify=False)
            if res.status_code == 200 and isinstance(res.json(), list):
                LISTA_USUARIOS_LOCALES = res.json()
                return
        except: pass
        if len(LISTA_USUARIOS_LOCALES) == 0:
            LISTA_USUARIOS_LOCALES = [
                {"id_p00": "P001", "id_carnet": "C-ADMIN-01", "correo": "admin@sistema.com", "nombres": "Administrador", "apellidos": "General", "cedula": "V-0", "tipo_sangre": "O+", "area_tipo": "estadal", "area_valor": "TODAS", "rol": "admin"}
            ]

    def cerrar_sesion_admin(e):
        global SESSION_ADMIN
        SESSION_ADMIN.clear()
        limpiar_formulario()
        mostrar_login_inicial()

    def guardar_usuario(e):
        global LISTA_USUARIOS_LOCALES
        if not txt_p00.value.strip() or not txt_correo.value.strip():
            return

        payload = {
            "id_p00": txt_p00.value.strip(), "id_carnet": txt_carnet.value.strip() if txt_carnet.value.strip() else None,
            "correo": txt_correo.value.strip(), "clave": txt_clave.value.strip() if txt_clave.value.strip() else "123",
            "nombres": txt_nombres.value.strip(), "apellidos": txt_apellidos.value.strip(),
            "cedula": txt_cedula.value.strip(), "tipo_sangre": txt_sangre.value.strip(),
            "area_tipo": dropdown_area_tipo.value, "area_valor": dropdown_area_valor.value, "rol": dropdown_rol.value
        }

        try: requests.post(f"{API_URL}/usuarios/registrar", json=payload, timeout=3, verify=False)
        except: pass

        if USUARIO_SELECCIONADO_ID:
            for i, u in enumerate(LISTA_USUARIOS_LOCALES):
                if u['id_p00'] == USUARIO_SELECCIONADO_ID:
                    LISTA_USUARIOS_LOCALES[i] = payload
                    break
        else:
            LISTA_USUARIOS_LOCALES.append(payload)

        limpiar_formulario()
        page.overlay.append(ft.SnackBar(ft.Text("Usuario sincronizado con éxito."), open=True))

    def ejecutar_eliminacion(e):
        global LISTA_USUARIOS_LOCALES
        if not USUARIO_SELECCIONADO_ID: return
        try: requests.delete(f"{API_URL}/usuarios/eliminar/{USUARIO_SELECCIONADO_ID}", timeout=3, verify=False)
        except: pass
        LISTA_USUARIOS_LOCALES = [u for u in LISTA_USUARIOS_LOCALES if u['id_p00'] != USUARIO_SELECCIONADO_ID]
        limpiar_formulario()

    def autenticar_admin(e):
        if txt_user.value.strip() == "admin@sistema.com" and txt_pass.value.strip() == "admin123":
            SESSION_ADMIN["rol"] = "admin"
            consultar_usuarios_servidor()
            mostrar_panel_admin()

    def mostrar_login_inicial():
        page.views.clear()
        page.views.append(ft.View("/login", [
            ft.AppBar(title=ft.Text("Acceso Administrativo"), bgcolor="purple", color="white"),
            ft.Container(
                alignment=ft.alignment.center, padding=50,
                content=ft.Column([
                    ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS, size=60, color="purple"),
                    ft.Text("Módulo de Configuración Base", size=20, weight="bold"),
                    txt_user, txt_pass, 
                    ft.ElevatedButton("Ingresar", on_click=autenticar_admin, width=220, bgcolor="purple", color="white")
                ], horizontal_alignment="center")
            )
        ]))
        page.update()

    def mostrar_panel_admin():
        page.views.clear()
        generar_filas_tabla()
        
        formulario = ft.Container(
            padding=15, bgcolor=ft.Colors.GREY_100, border_radius=10,
            content=ft.Column([
                ft.Text("Gestión Integral de Personal (Mesa de Control y Campo)", weight="bold", size=16, color=ft.Colors.BLUE_900),
                ft.Row([txt_p00, txt_carnet, txt_correo, txt_clave]),
                ft.Row([txt_nombres, txt_apellidos, txt_cedula, txt_sangre]),
                ft.Row([dropdown_rol, dropdown_area_tipo, dropdown_area_valor]),
                ft.Row([btn_guardar, btn_eliminar, btn_cancelar], spacing=10)
            ])
        )
        page.views.append(ft.View("/admin-panel", [
            ft.AppBar(
                title=ft.Text("Panel del Administrador"), bgcolor="purple", color="white",
                actions=[ft.IconButton(ft.icons.LOGOUT, icon_color="white", tooltip="Cerrar Sesión", on_click=cerrar_sesion_admin)]
            ),
            formulario, ft.Divider(),
            ft.Column([tabla_usuarios], expand=True, scroll=ft.ScrollMode.ALWAYS)
        ]))
        page.update()

    btn_guardar.on_click = guardar_usuario
    btn_eliminar.on_click = ejecutar_eliminacion
    btn_cancelar.on_click = lambda e: limpiar_formulario()

    mostrar_login_inicial()

ft.app(target=main)
