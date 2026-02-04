import customtkinter as ctk
from db_manager import DBManager
from datetime import datetime, timedelta # Importar timedelta
from tkcalendar import Calendar # Importar Calendar
from fpdf import FPDF # Importar FPDF para generar PDFs
import sys
import os

# Clase CustomMessageBox para reemplazar ctk.CTkMessagebox
class CustomMessageBox(ctk.CTkToplevel):
    def __init__(self, master, title, message, icon="info", option_1="Ok", option_2=None):
        super().__init__(master)
        self.title(title)
        self.geometry("300x150")
        self.transient(master)
        self.grab_set()

        self.result = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Frame para el contenido
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Mensaje
        self.message_label = ctk.CTkLabel(content_frame, text=message, wraplength=280)
        self.message_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Frame para los botones
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        self.option_1_button = ctk.CTkButton(button_frame, text=option_1, command=lambda: self._on_button_click(option_1))
        self.option_1_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        if option_2:
            self.option_2_button = ctk.CTkButton(button_frame, text=option_2, command=lambda: self._on_button_click(option_2))
            self.option_2_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing) # Manejar cierre de ventana

    def _on_button_click(self, result):
        self.result = result
        self.destroy()

    def _on_closing(self):
        self.result = None # Si se cierra sin seleccionar opción
        self.destroy()

    def get(self):
        self.master.wait_window(self)
        return self.result

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Happy Body Gym - Control de Asistencia")
        self.geometry("1000x700")
        self.db = DBManager()
        db_connected = self.db.connect()
        if not db_connected:
            CustomMessageBox(self, title="Error de Base de Datos", message="No se pudo conectar a la base de datos.\n\nPor favor, verifique que el archivo Database.accdb existe, que el controlador ODBC de Access está instalado y que la arquitectura (32/64 bits) coincide con su Python.\n\nLa aplicación se cerrará.", icon="cancel").get()
            self.destroy()
            return

        # Configurar el grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Crear el marco de navegación
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Happy Body Gym",
                                                   compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Inicio",
                                         fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.members_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Miembros",
                                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                            anchor="w", command=self.members_button_event)
        self.members_button.grid(row=2, column=0, sticky="ew")

        self.attendance_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Asistencia",
                                               fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                               anchor="w", command=self.attendance_button_event)
        self.attendance_button.grid(row=3, column=0, sticky="ew")

        self.payments_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Pagos",
                                             fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                             anchor="w", command=self.payments_button_event)
        self.payments_button.grid(row=4, column=0, sticky="ew")

        self.observations_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Observaciones",
                                                 fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                 anchor="w", command=self.observations_button_event)
        self.observations_button.grid(row=5, column=0, sticky="ew")

        self.export_pdf_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Exportar a PDF",
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                anchor="w", command=self.pdf_export_button_event)
        self.export_pdf_button.grid(row=6, column=0, sticky="ew")

        self.appearance_mode_label = ctk.CTkLabel(self.navigation_frame, text="Modo de Apariencia:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                             command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=10, sticky="ew")

        # Crear los marcos de las páginas
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.members_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.attendance_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.payments_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.observations_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.pdf_export_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # --- Contenido del Home Frame ---
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_welcome_label = ctk.CTkLabel(self.home_frame, text="Bienvenido a Happy Body Gym", font=ctk.CTkFont(size=24, weight="bold"))
        self.home_welcome_label.grid(row=0, column=0, padx=20, pady=20)
        self.home_info_label = ctk.CTkLabel(self.home_frame, text="Seleccione una opción del menú lateral para comenzar.", font=ctk.CTkFont(size=14))
        self.home_info_label.grid(row=1, column=0, padx=20, pady=10)

        # --- Contenido del Members Frame ---
        self.members_frame.grid_columnconfigure(0, weight=1) # Una sola columna principal
        self.members_frame.grid_rowconfigure(1, weight=0) # Fila para el formulario (no se expande)
        self.members_frame.grid_rowconfigure(2, weight=1) # Fila para la lista (se expande)

        self.members_title_label = ctk.CTkLabel(self.members_frame, text="Gestión de Miembros", font=ctk.CTkFont(size=20, weight="bold"))
        self.members_title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w") # Ocupa una sola columna

        # Formulario para añadir miembro (dentro de un marco desplazable)
        self.add_member_scroll_frame = ctk.CTkScrollableFrame(self.members_frame, label_text="Añadir Nuevo Miembro y Pago Inicial")
        self.add_member_scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew") # Primera fila, primera columna
        self.add_member_scroll_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.add_member_scroll_frame, text="Nombre:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.member_name_entry = ctk.CTkEntry(self.add_member_scroll_frame, placeholder_text="Nombre")
        self.member_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_member_scroll_frame, text="Apellido:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.member_lastname_entry = ctk.CTkEntry(self.add_member_scroll_frame, placeholder_text="Apellido")
        self.member_lastname_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_member_scroll_frame, text="Cédula:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.member_cedula_entry = ctk.CTkEntry(self.add_member_scroll_frame, placeholder_text="Cédula")
        self.member_cedula_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_member_scroll_frame, text="Teléfono:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.member_phone_entry = ctk.CTkEntry(self.add_member_scroll_frame, placeholder_text="Teléfono")
        self.member_phone_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_member_scroll_frame, text="Fecha Nacimiento (YYYY-MM-DD):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.member_dob_entry = ctk.CTkEntry(self.add_member_scroll_frame, placeholder_text="Seleccionar fecha", state="readonly")
        self.member_dob_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.member_dob_button = ctk.CTkButton(self.add_member_scroll_frame, text="Seleccionar Fecha", command=self.open_calendar_member_dob)
        self.member_dob_button.grid(row=4, column=2, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_member_scroll_frame, text="--- Primer Pago (Opcional) ---", font=ctk.CTkFont(weight="bold")).grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.add_member_scroll_frame, text="Tipo de Membresía:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.payment_type_optionemenu = ctk.CTkOptionMenu(self.add_member_scroll_frame, values=["Ninguno", "Mensual", "Quincenal"])
        self.payment_type_optionemenu.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_member_scroll_frame, text="Monto:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
        self.payment_amount_entry = ctk.CTkEntry(self.add_member_scroll_frame, placeholder_text="Monto del pago")
        self.payment_amount_entry.grid(row=8, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_member_scroll_frame, text="Tipo de Moneda:").grid(row=9, column=0, padx=10, pady=5, sticky="w")
        self.currency_type_optionemenu = ctk.CTkOptionMenu(self.add_member_scroll_frame, values=["$", "Bs", "Monto Digital"])
        self.currency_type_optionemenu.grid(row=9, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_member_scroll_frame, text="Fecha de Pago:").grid(row=10, column=0, padx=10, pady=5, sticky="w")
        self.payment_date_entry = ctk.CTkEntry(self.add_member_scroll_frame, placeholder_text="Seleccionar fecha", state="readonly")
        self.payment_date_entry.grid(row=10, column=1, padx=10, pady=5, sticky="ew")
        self.payment_date_button = ctk.CTkButton(self.add_member_scroll_frame, text="Seleccionar Fecha", command=self.open_calendar_payment_date)
        self.payment_date_button.grid(row=10, column=2, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_member_scroll_frame, text="Referencia:").grid(row=11, column=0, padx=10, pady=5, sticky="w")
        self.payment_reference_entry = ctk.CTkEntry(self.add_member_scroll_frame, placeholder_text="Número de referencia (opcional)")
        self.payment_reference_entry.grid(row=11, column=1, padx=10, pady=5, sticky="ew")

        self.add_member_button = ctk.CTkButton(self.add_member_scroll_frame, text="Añadir Miembro y Registrar Pago", command=self.add_member_event)
        self.add_member_button.grid(row=12, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.member_labels = [] # Para almacenar las etiquetas de los miembros

        # Área para mostrar miembros
        self.members_list_frame = ctk.CTkScrollableFrame(self.members_frame, label_text="Lista de Miembros")
        self.members_list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew") # Segunda fila, primera columna
        # Configurar las columnas para que se expandan uniformemente
        self.members_list_frame.grid_columnconfigure(0, weight=1) # ID
        self.members_list_frame.grid_columnconfigure(1, weight=1) # Nombre
        self.members_list_frame.grid_columnconfigure(2, weight=1) # Apellido
        self.members_list_frame.grid_columnconfigure(3, weight=1) # Cédula
        self.members_list_frame.grid_columnconfigure(4, weight=1) # Teléfono

        # Marco para eliminar miembro
        self.delete_member_frame = ctk.CTkFrame(self.members_frame, fg_color="transparent")
        self.delete_member_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.delete_member_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.delete_member_frame, text="Cédula del Miembro a Eliminar:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.delete_member_cedula_entry = ctk.CTkEntry(self.delete_member_frame, placeholder_text="Cédula del miembro a eliminar")
        self.delete_member_cedula_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.delete_member_button = ctk.CTkButton(self.delete_member_frame, text="Eliminar Miembro", command=self.delete_member_event)
        self.delete_member_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # --- Contenido del Attendance Frame ---
        self.attendance_frame.grid_columnconfigure(0, weight=1)
        self.attendance_frame.grid_rowconfigure(3, weight=1) # Fila para la lista de asistencia

        self.attendance_title_label = ctk.CTkLabel(self.attendance_frame, text="Registro de Asistencia", font=ctk.CTkFont(size=20, weight="bold"))
        self.attendance_title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Marco para búsqueda de miembro
        self.attendance_search_frame = ctk.CTkFrame(self.attendance_frame, fg_color="transparent")
        self.attendance_search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.attendance_search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.attendance_search_frame, text="Cédula del Miembro:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.attendance_cedula_entry = ctk.CTkEntry(self.attendance_search_frame, placeholder_text="Cédula del miembro")
        self.attendance_cedula_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.attendance_search_button = ctk.CTkButton(self.attendance_search_frame, text="Buscar Miembro", command=self.search_member_for_attendance)
        self.attendance_search_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Marco para mostrar el miembro encontrado y registrar asistencia
        self.attendance_member_info_frame = ctk.CTkFrame(self.attendance_frame, fg_color="transparent")
        self.attendance_member_info_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.attendance_member_info_frame.grid_columnconfigure(0, weight=1)
        self.attendance_member_info_frame.grid_columnconfigure(1, weight=1)

        self.attendance_member_name_label = ctk.CTkLabel(self.attendance_member_info_frame, text="Miembro: N/A", font=ctk.CTkFont(weight="bold"))
        self.attendance_member_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.attendance_member_status_label = ctk.CTkLabel(self.attendance_member_info_frame, text="Estado de Pago: N/A", font=ctk.CTkFont(weight="bold"))
        self.attendance_member_status_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.register_attendance_button = ctk.CTkButton(self.attendance_member_info_frame, text="Registrar Asistencia", command=self.register_attendance_event, state="disabled")
        self.register_attendance_button.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.current_member_id_for_attendance = None # Para almacenar el ID del miembro seleccionado

        # Área para mostrar la asistencia del día
        self.attendance_list_frame = ctk.CTkScrollableFrame(self.attendance_frame, label_text="Asistencia del Día")
        self.attendance_list_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.attendance_list_frame.grid_columnconfigure(0, weight=1) # Nombre
        self.attendance_list_frame.grid_columnconfigure(1, weight=1) # Apellido
        self.attendance_list_frame.grid_columnconfigure(2, weight=1) # Cédula
        self.attendance_list_frame.grid_columnconfigure(3, weight=1) # Hora

        self.attendance_labels = [] # Para almacenar las etiquetas de asistencia

        # --- Contenido del Payments Frame ---
        self.payments_frame.grid_columnconfigure(0, weight=1)
        self.payments_frame.grid_rowconfigure(3, weight=1) # Fila para la lista de pagos

        self.payments_title_label = ctk.CTkLabel(self.payments_frame, text="Gestión de Pagos", font=ctk.CTkFont(size=20, weight="bold"))
        self.payments_title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Marco para búsqueda de miembro en Pagos
        self.payments_search_frame = ctk.CTkFrame(self.payments_frame, fg_color="transparent")
        self.payments_search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.payments_search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.payments_search_frame, text="Cédula del Miembro:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.payments_cedula_entry = ctk.CTkEntry(self.payments_search_frame, placeholder_text="Cédula del miembro")
        self.payments_cedula_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.payments_search_button = ctk.CTkButton(self.payments_search_frame, text="Buscar Miembro", command=self.search_member_for_payment)
        self.payments_search_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Marco para mostrar el miembro encontrado y registrar pago
        self.payments_member_info_frame = ctk.CTkFrame(self.payments_frame, fg_color="transparent")
        self.payments_member_info_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.payments_member_info_frame.grid_columnconfigure(0, weight=1)
        self.payments_member_info_frame.grid_columnconfigure(1, weight=1)

        self.payments_member_name_label = ctk.CTkLabel(self.payments_member_info_frame, text="Miembro: N/A", font=ctk.CTkFont(weight="bold"))
        self.payments_member_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.payments_member_status_label = ctk.CTkLabel(self.payments_member_info_frame, text="Estado de Pago: N/A", font=ctk.CTkFont(weight="bold"))
        self.payments_member_status_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.payments_expiry_date_label = ctk.CTkLabel(self.payments_member_info_frame, text="Fecha de Vencimiento: N/A", font=ctk.CTkFont(weight="bold"))
        self.payments_expiry_date_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Formulario para añadir pago (dentro de un marco)
        self.add_payment_frame = ctk.CTkFrame(self.payments_member_info_frame)
        self.add_payment_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        self.add_payment_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.add_payment_frame, text="Tipo de Membresía:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.new_payment_type_optionemenu = ctk.CTkOptionMenu(self.add_payment_frame, values=["Mensual", "Quincenal"])
        self.new_payment_type_optionemenu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_payment_frame, text="Monto:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.new_payment_amount_entry = ctk.CTkEntry(self.add_payment_frame, placeholder_text="Monto del pago")
        self.new_payment_amount_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_payment_frame, text="Tipo de Moneda:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.new_currency_type_optionemenu = ctk.CTkOptionMenu(self.add_payment_frame, values=["$", "Bs", "Monto Digital"])
        self.new_currency_type_optionemenu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_payment_frame, text="Fecha de Pago:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.new_payment_date_entry = ctk.CTkEntry(self.add_payment_frame, placeholder_text="Seleccionar fecha", state="readonly")
        self.new_payment_date_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.new_payment_date_button = ctk.CTkButton(self.add_payment_frame, text="Seleccionar Fecha", command=self.open_calendar_new_payment_date)
        self.new_payment_date_button.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_payment_frame, text="Referencia:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.new_payment_reference_entry = ctk.CTkEntry(self.add_payment_frame, placeholder_text="Número de referencia (opcional)")
        self.new_payment_reference_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        self.register_new_payment_button = ctk.CTkButton(self.add_payment_frame, text="Registrar Pago", command=self.register_new_payment_event, state="disabled")
        self.register_new_payment_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.current_member_id_for_payment = None # Para almacenar el ID del miembro seleccionado para pago

        # Área para mostrar el historial de pagos del miembro seleccionado
        self.payments_list_frame = ctk.CTkScrollableFrame(self.payments_frame, label_text="Historial de Pagos")
        self.payments_list_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.payments_list_frame.grid_columnconfigure(0, weight=1) # Fecha
        self.payments_list_frame.grid_columnconfigure(1, weight=1) # Monto
        self.payments_list_frame.grid_columnconfigure(2, weight=1) # Tipo
        self.payments_list_frame.grid_columnconfigure(3, weight=1) # Descripción

        self.payment_labels = [] # Para almacenar las etiquetas de pagos

        # --- Contenido del Observations Frame ---
        self.observations_frame.grid_columnconfigure(0, weight=1)
        self.observations_frame.grid_rowconfigure(3, weight=1) # Fila para la lista de observaciones

        self.observations_title_label = ctk.CTkLabel(self.observations_frame, text="Gestión de Observaciones", font=ctk.CTkFont(size=20, weight="bold"))
        self.observations_title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Marco para búsqueda de miembro en Observaciones
        self.observations_search_frame = ctk.CTkFrame(self.observations_frame, fg_color="transparent")
        self.observations_search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.observations_search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.observations_search_frame, text="Cédula del Miembro:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.observations_cedula_entry = ctk.CTkEntry(self.observations_search_frame, placeholder_text="Cédula del miembro")
        self.observations_cedula_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.observations_search_button = ctk.CTkButton(self.observations_search_frame, text="Buscar Miembro", command=self.search_member_for_observation)
        self.observations_search_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Marco para mostrar el miembro encontrado y añadir observación
        self.observations_member_info_frame = ctk.CTkFrame(self.observations_frame, fg_color="transparent")
        self.observations_member_info_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.observations_member_info_frame.grid_columnconfigure(0, weight=1)

        self.observations_member_name_label = ctk.CTkLabel(self.observations_member_info_frame, text="Miembro: N/A", font=ctk.CTkFont(weight="bold"))
        self.observations_member_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.observations_member_info_frame, text="Nueva Observación:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.new_observation_textbox = ctk.CTkTextbox(self.observations_member_info_frame, height=100)
        self.new_observation_textbox.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.add_observation_button = ctk.CTkButton(self.observations_member_info_frame, text="Añadir Observación", command=self.add_observation_event, state="disabled")
        self.add_observation_button.grid(row=3, column=0, padx=5, pady=10, sticky="ew")

        self.current_member_id_for_observation = None # Para almacenar el ID del miembro seleccionado para observación

        # Área para mostrar el historial de observaciones del miembro seleccionado
        self.observations_list_frame = ctk.CTkScrollableFrame(self.observations_frame, label_text="Historial de Observaciones")
        self.observations_list_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.observations_list_frame.grid_columnconfigure(0, weight=1) # Observación
        self.observations_list_frame.grid_columnconfigure(1, weight=1) # Fecha (si aplica)

        self.observation_labels = [] # Para almacenar las etiquetas de observaciones

        # Seleccionar el marco inicial
        self.select_frame_by_name("home")
        self.load_members() # Cargar miembros al inicio
        self.print_member_table_columns() # Añadir esta línea para depuración
        self.check_and_notify_expired_payments() # Verificar y notificar pagos vencidos al inicio

    def delete_member_event(self):
        """Elimina un miembro de la base de datos."""
        cedula = self.delete_member_cedula_entry.get()
        if not cedula:
            CustomMessageBox(self, title="Error", message="Por favor, ingrese la cédula del miembro a eliminar.", icon="warning")
            return

        member = self.db.get_member_by_cedula(cedula)
        if not member:
            CustomMessageBox(self, title="Error", message=f"No se encontró miembro con cédula: {cedula}", icon="warning")
            return

        member_id = member.get("ID")
        confirm = CustomMessageBox(self, title="Confirmar Eliminación", 
                                    message=f"¿Está seguro de que desea eliminar a {member.get('Nombre')} {member.get('Apellido')} (Cédula: {cedula}) y todos sus registros asociados?",
                                    icon="question", option_1="Cancelar", option_2="Eliminar")
        
        if confirm.get() == "Eliminar":
            if self.db.delete_member(member_id):
                CustomMessageBox(self, title="Éxito", message=f"Miembro {member.get('Nombre')} {member.get('Apellido')} eliminado exitosamente.", icon="info")
                self.delete_member_cedula_entry.delete(0, ctk.END)
                self.load_members() # Recargar la lista de miembros
            else:
                CustomMessageBox(self, title="Error", message="Error al eliminar el miembro.", icon="cancel")
        else:
            print("Eliminación cancelada.")

    def check_and_notify_expired_payments(self):
        """Verifica los pagos vencidos y muestra una notificación."""
        members = self.db.get_members()
        expired_members = []

        for member in members:
            member_id = member.get("ID-Miembro")
            name = member.get("Nombre")
            lastname = member.get("Apellido")
            
            status, expiry_date = self.check_member_payment_status(member_id)
            
            if "Vencido" in status and expiry_date: # Ensure expiry_date is not None
                expired_members.append(f"{name} {lastname} (Cédula: {member.get('Cedula')}) - Vencido desde: {expiry_date.strftime('%Y-%m-%d')}")
            elif "Vencido" in status and not expiry_date:
                expired_members.append(f"{name} {lastname} (Cédula: {member.get('Cedula')}) - Vencido (fecha no disponible)")
        
        if expired_members:
            message = "Los siguientes miembros tienen pagos vencidos:\n\n" + "\n".join(expired_members)
            CustomMessageBox(self, title="Pagos Vencidos", message=message, icon="warning")
        else:
            print("No hay pagos vencidos.") # Para depuración, se puede quitar en producción

    def load_members(self):
        """Carga y muestra la lista de miembros en el frame de miembros."""
        # Limpiar etiquetas existentes
        for label in self.member_labels:
            label.destroy()
        self.member_labels.clear()

        members = self.db.get_members()

        if members:
            # Crear encabezados de tabla
            headers = ["ID", "Nombre", "Apellido", "Cédula", "Teléfono"]
            for col_idx, header_text in enumerate(headers):
                header_label = ctk.CTkLabel(self.members_list_frame, text=header_text, font=ctk.CTkFont(weight="bold"))
                header_label.grid(row=0, column=col_idx, padx=5, pady=2, sticky="w")
                self.member_labels.append(header_label)

            # Llenar la tabla con datos de miembros
            for row_idx, member in enumerate(members):
                member_id = member.get("ID-Miembro", "")
                name = member.get("Nombre", "")
                lastname = member.get("Apellido", "")
                cedula = member.get("Cedula", "")
                phone = member.get("Telefono", "")

                ctk.CTkLabel(self.members_list_frame, text=member_id).grid(row=row_idx + 1, column=0, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.members_list_frame, text=name).grid(row=row_idx + 1, column=1, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.members_list_frame, text=lastname).grid(row=row_idx + 1, column=2, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.members_list_frame, text=cedula).grid(row=row_idx + 1, column=3, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.members_list_frame, text=phone).grid(row=row_idx + 1, column=4, padx=2, pady=2, sticky="w")

                # Almacenar las etiquetas para poder limpiarlas después
                self.member_labels.extend([
                    self.members_list_frame.grid_slaves(row=row_idx + 1, column=0)[0],
                    self.members_list_frame.grid_slaves(row=row_idx + 1, column=1)[0],
                    self.members_list_frame.grid_slaves(row=row_idx + 1, column=2)[0],
                    self.members_list_frame.grid_slaves(row_idx + 1, column=3)[0],
                    self.members_list_frame.grid_slaves(row_idx + 1, column=4)[0]
                ])
        else:
            no_members_label = ctk.CTkLabel(self.members_list_frame, text="No hay miembros registrados.")
            no_members_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.member_labels.append(no_members_label)

    def open_calendar_member_dob(self):
        def set_date():
            selected_date = cal.get_date()
            self.member_dob_entry.configure(state="normal")
            self.member_dob_entry.delete(0, ctk.END)
            self.member_dob_entry.insert(0, selected_date)
            self.member_dob_entry.configure(state="readonly")
            top.destroy()

        top = ctk.CTkToplevel(self)
        top.title("Seleccionar Fecha de Nacimiento")
        top.geometry("300x300")
        top.transient(self) # Hace que la ventana sea transitoria de la principal
        top.grab_set() # Captura todos los eventos de entrada para esta ventana

        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=20)

        ctk.CTkButton(top, text="Seleccionar", command=set_date).pack(pady=10)
        self.wait_window(top) # Espera hasta que la ventana top sea destruida

    def open_calendar_payment_date(self):
        def set_date():
            selected_date = cal.get_date()
            self.payment_date_entry.configure(state="normal")
            self.payment_date_entry.delete(0, ctk.END)
            self.payment_date_entry.insert(0, selected_date)
            self.payment_date_entry.configure(state="readonly")
            top.destroy()

        top = ctk.CTkToplevel(self)
        top.title("Seleccionar Fecha de Pago")
        top.geometry("300x300")
        top.transient(self) # Hace que la ventana sea transitoria de la principal
        top.grab_set() # Captura todos los eventos de entrada para esta ventana

        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=20)

        ctk.CTkButton(top, text="Seleccionar", command=set_date).pack(pady=10)
        self.wait_window(top) # Espera hasta que la ventana top sea destruida

    def open_calendar_new_payment_date(self):
        def set_date():
            selected_date = cal.get_date()
            self.new_payment_date_entry.configure(state="normal")
            self.new_payment_date_entry.delete(0, ctk.END)
            self.new_payment_date_entry.insert(0, selected_date)
            self.new_payment_date_entry.configure(state="readonly")
            top.destroy()

        top = ctk.CTkToplevel(self)
        top.title("Seleccionar Fecha de Pago")
        top.geometry("300x300")
        top.transient(self) # Hace que la ventana sea transitoria de la principal
        top.grab_set() # Captura todos los eventos de entrada para esta ventana

        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=20)

        ctk.CTkButton(top, text="Seleccionar", command=set_date).pack(pady=10)
        self.wait_window(top) # Espera hasta que la ventana top sea destruida

    def print_member_table_columns(self):
        columns = self.db.get_table_columns("Miembros")
        print(f"Columnas de la tabla Miembros: {columns}")

    def select_frame_by_name(self, name):
        # Establecer el color del botón para el marco seleccionado
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.members_button.configure(fg_color=("gray75", "gray25") if name == "members" else "transparent")
        self.attendance_button.configure(fg_color=("gray75", "gray25") if name == "attendance" else "transparent")
        self.payments_button.configure(fg_color=("gray75", "gray25") if name == "payments" else "transparent")
        self.observations_button.configure(fg_color=("gray75", "gray25") if name == "observations" else "transparent")
        self.export_pdf_button.configure(fg_color=("gray75", "gray25") if name == "pdf_export" else "transparent")

        # Mostrar el marco seleccionado
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "members":
            self.members_frame.grid(row=0, column=1, sticky="nsew")
            self.load_members() # Recargar miembros cada vez que se visita
        else:
            self.members_frame.grid_forget()
        if name == "attendance":
            self.attendance_frame.grid(row=0, column=1, sticky="nsew")
            self.load_daily_attendance() # Cargar la asistencia del día al entrar
        else:
            self.attendance_frame.grid_forget()
        if name == "payments":
            self.payments_frame.grid(row=0, column=1, sticky="nsew")
            self.load_payments_history(None) # Cargar historial de pagos vacío al entrar
        else:
            self.payments_frame.grid_forget()
        if name == "observations":
            self.observations_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.observations_frame.grid_forget()
        if name == "pdf_export":
            self.pdf_export_frame.grid(row=0, column=1, sticky="nsew")
            self.setup_pdf_export_frame() # Setup the PDF export frame when it's selected
        else:
            self.pdf_export_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def members_button_event(self):
        self.select_frame_by_name("members")

    def attendance_button_event(self):
        self.select_frame_by_name("attendance")
        self.load_daily_attendance() # Cargar la asistencia del día al entrar

    def payments_button_event(self):
        self.select_frame_by_name("payments")
        self.load_payments_history(None) # Cargar historial de pagos vacío al entrar

    def observations_button_event(self):
        self.select_frame_by_name("observations")

    def pdf_export_button_event(self):
        self.select_frame_by_name("pdf_export")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def add_member_event(self):
        name = self.member_name_entry.get()
        lastname = self.member_lastname_entry.get()
        cedula = self.member_cedula_entry.get()
        phone = self.member_phone_entry.get()
        dob_str = self.member_dob_entry.get() # Fecha de nacimiento del miembro

        if not name or not lastname or not cedula or not phone:
            CustomMessageBox(self, title="Error de Entrada", message="Nombre, Apellido, Cédula y Teléfono son obligatorios.", icon="warning").get()
            return

        try:
            # Añadir miembro a la tabla Miembros
            new_member_id = self.db.add_member(name, lastname, cedula, phone)
            if new_member_id:
                CustomMessageBox(self, title="Éxito", message=f"Miembro {name} {lastname} ({cedula}) añadido exitosamente.", icon="info").get()
                
                # Registrar la fecha de nacimiento en Observaciones
                if dob_str:
                    try:
                        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                        if not self.db.add_observation(new_member_id, "Fecha de nacimiento del miembro", dob):
                            CustomMessageBox(self, title="Error", message="Error al registrar la fecha de nacimiento en Observaciones.", icon="cancel").get()
                    except ValueError:
                        CustomMessageBox(self, title="Error de Formato", message="Formato de fecha de nacimiento incorrecto. Use YYYY-MM-DD.", icon="warning").get()
                
                # Procesar el pago inicial si se proporcionó
                payment_type = self.payment_type_optionemenu.get()
                payment_amount_str = self.payment_amount_entry.get()
                currency_type = self.currency_type_optionemenu.get()
                payment_date_str = self.payment_date_entry.get()
                payment_reference = self.payment_reference_entry.get()

                if payment_type != "Ninguno" and payment_amount_str:
                    try:
                        payment_amount = float(payment_amount_str)
                        payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d").date() if payment_date_str else datetime.now().date()
                        
                        if self.db.add_payment(new_member_id, payment_amount, payment_date, payment_type, currency_type, payment_reference):
                            CustomMessageBox(self, title="Éxito", message=f"Pago inicial de {payment_amount} {currency_type} registrado para el miembro {name} {lastname}.", icon="info").get()
                            
                            # Registrar en Pago-Mensual o Pago-Quincenal si aplica (para control de validez)
                            if payment_type == "Mensual":
                                fecha_inicio = payment_date
                                if fecha_inicio.month == 12:
                                    fecha_fin = fecha_inicio.replace(year=fecha_inicio.year + 1, month=1, day=1) - timedelta(days=1)
                                else:
                                    fecha_fin = fecha_inicio.replace(month=fecha_inicio.month + 1, day=1) - timedelta(days=1)
                                
                                if not self.db.add_monthly_payment(new_member_id, fecha_inicio, fecha_fin):
                                    CustomMessageBox(self, title="Error", message="Error al registrar membresía mensual para control de validez.", icon="cancel").get()
                            elif payment_type == "Quincenal":
                                fecha_inicio = payment_date
                                fecha_fin = fecha_inicio + timedelta(days=14)

                                if not self.db.add_fortnightly_payment(new_member_id, fecha_inicio, fecha_fin):
                                    CustomMessageBox(self, title="Error", message="Error al registrar membresía quincenal para control de validez.", icon="cancel").get()

                            # Limpiar campos del formulario de añadir miembro y pago inicial
                            self.member_name_entry.delete(0, ctk.END)
                            self.member_lastname_entry.delete(0, ctk.END)
                            self.member_cedula_entry.delete(0, ctk.END)
                            self.member_phone_entry.delete(0, ctk.END)
                            self.member_dob_entry.configure(state="normal")
                            self.member_dob_entry.delete(0, ctk.END)
                            self.member_dob_entry.configure(state="readonly")
                            self.payment_type_optionemenu.set("Ninguno")
                            self.payment_amount_entry.delete(0, ctk.END)
                            self.currency_type_optionemenu.set("$")
                            self.payment_date_entry.configure(state="normal")
                            self.payment_date_entry.delete(0, ctk.END)
                            self.payment_date_entry.configure(state="readonly")
                            self.payment_reference_entry.delete(0, ctk.END)

                            # Actualizar estado de pago y historial
                            payment_status, expiry_date = self.check_member_payment_status(new_member_id)
                            self.payments_member_status_label.configure(text=f"Estado de Pago: {payment_status}")
                            self.load_payments_history(new_member_id)
                            self.load_members() # Recargar la lista de miembros
                        else:
                            CustomMessageBox(self, title="Error", message="Error al registrar el nuevo pago.", icon="cancel").get()
                    except ValueError:
                        CustomMessageBox(self, title="Error de Formato", message="Monto o Fecha de Pago incorrectos. Asegúrese de que el monto sea un número y la fecha esté en formato YYYY-MM-DD.", icon="warning").get()
                    except Exception as e:
                        CustomMessageBox(self, title="Error Inesperado", message=f"Ocurrió un error inesperado al procesar el pago: {e}", icon="cancel").get()
                else:
                    CustomMessageBox(self, title="Información", message="No se proporcionó información de pago inicial o tipo de membresía. Miembro añadido sin pago inicial.", icon="info").get()
                self.load_members() # Recargar la lista de miembros incluso si no hay pago inicial
            else:
                CustomMessageBox(self, title="Error", message="Error al añadir miembro. La cédula podría ya existir o hay un problema con la base de datos.", icon="cancel").get()
        except Exception as e:
            CustomMessageBox(self, title="Error Crítico", message=f"Ocurrió un error crítico al intentar añadir el miembro: {e}", icon="cancel").get()

    def load_payments_history(self, member_id):
        """Carga y muestra el historial de pagos de un miembro."""
        # Limpiar etiquetas existentes
        for label in self.payment_labels:
            label.destroy()
        self.payment_labels.clear()

        if member_id is None:
            no_payments_label = ctk.CTkLabel(self.payments_list_frame, text="Seleccione un miembro para ver su historial de pagos.")
            no_payments_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.payment_labels.append(no_payments_label)
            return

        payments = self.db.get_payments_by_member(member_id)

        if payments:
            # Crear encabezados de tabla
            # Ajustar encabezados para reflejar las columnas disponibles
            headers = ["Fecha", "Monto ($)", "Monto (Bs)", "Monto (Digital)", "Referencia"]
            for col_idx, header_text in enumerate(headers):
                header_label = ctk.CTkLabel(self.payments_list_frame, text=header_text, font=ctk.CTkFont(weight="bold"))
                header_label.grid(row=0, column=col_idx, padx=5, pady=2, sticky="w")
                self.payment_labels.append(header_label)

            # Llenar la tabla con datos de pagos
            for row_idx, payment in enumerate(payments):
                # Usar los nombres de columna exactos de la base de datos
                fecha = payment.get("Fecha-Pago", "").strftime("%Y-%m-%d") if isinstance(payment.get("Fecha-Pago"), datetime) else ""
                monto_usd = payment.get("Efectivo-$", "")
                monto_bs = payment.get("Efectivo-Bs", "")
                monto_digital_bs = payment.get("Monto-Digital-Bs", "")
                referencia = payment.get("Referencia", "")

                ctk.CTkLabel(self.payments_list_frame, text=fecha).grid(row=row_idx + 1, column=0, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.payments_list_frame, text=monto_usd).grid(row=row_idx + 1, column=1, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.payments_list_frame, text=monto_bs).grid(row=row_idx + 1, column=2, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.payments_list_frame, text=monto_digital_bs).grid(row=row_idx + 1, column=3, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.payments_list_frame, text=referencia).grid(row=row_idx + 1, column=4, padx=2, pady=2, sticky="w")

                # Almacenar las etiquetas para poder limpiarlas después
                self.payment_labels.extend([
                    self.payments_list_frame.grid_slaves(row=row_idx + 1, column=0)[0],
                    self.payments_list_frame.grid_slaves(row=row_idx + 1, column=1)[0],
                    self.payments_list_frame.grid_slaves(row=row_idx + 1, column=2)[0],
                    self.payments_list_frame.grid_slaves(row_idx + 1, column=3)[0],
                    self.payments_list_frame.grid_slaves(row_idx + 1, column=4)[0]
                ])
        else:
            no_payments_label = ctk.CTkLabel(self.payments_list_frame, text="No hay historial de pagos para este miembro.")
            no_payments_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.payment_labels.append(no_payments_label)

    def load_observations_history(self, member_id):
        """Carga y muestra el historial de observaciones de un miembro."""
        # Limpiar etiquetas existentes
        for label in self.observation_labels:
            label.destroy()
        self.observation_labels.clear()

        if member_id is None:
            no_observations_label = ctk.CTkLabel(self.observations_list_frame, text="Seleccione un miembro para ver su historial de observaciones.")
            no_observations_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.observation_labels.append(no_observations_label)
            return

        observations = self.db.get_observations(member_id)

        if observations:
            # Crear encabezados de tabla
            headers = ["Observación", "Fecha"]
            for col_idx, header_text in enumerate(headers):
                header_label = ctk.CTkLabel(self.observations_list_frame, text=header_text, font=ctk.CTkFont(weight="bold"))
                header_label.grid(row=0, column=col_idx, padx=5, pady=2, sticky="w")
                self.observation_labels.append(header_label)

            # Llenar la tabla con datos de observaciones
            for row_idx, obs in enumerate(observations):
                # Asumiendo que 'Observacion' y 'Fecha' son las claves en el diccionario de la observación
                observation_text = obs.get("Observacion", "")
                observation_date = obs.get("Fecha", "").strftime("%Y-%m-%d") if isinstance(obs.get("Fecha"), datetime) else ""

                # Calculate wraplength dynamically, ensuring it's a positive value
                # Use a default sensible value if winfo_width is not yet available or too small
                frame_width = self.observations_list_frame.winfo_width()
                wraplength_val = max(1, int(frame_width * 0.7)) # Ensure wraplength is at least 1
                ctk.CTkLabel(self.observations_list_frame, text=observation_text, wraplength=wraplength_val).grid(row=row_idx + 1, column=0, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.observations_list_frame, text=observation_date).grid(row=row_idx + 1, column=1, padx=2, pady=2, sticky="w")

                # Almacenar las etiquetas para poder limpiarlas después
                self.observation_labels.extend([
                    self.observations_list_frame.grid_slaves(row=row_idx + 1, column=0)[0],
                    self.observations_list_frame.grid_slaves(row=row_idx + 1, column=1)[0]
                ])
        else:
            no_observations_label = ctk.CTkLabel(self.observations_list_frame, text="No hay historial de observaciones para este miembro.")
            no_observations_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.observation_labels.append(no_observations_label)

    def search_member_for_attendance(self):
        """Busca un miembro por cédula para el registro de asistencia."""
        cedula = self.attendance_cedula_entry.get()
        if not cedula:
            print("Por favor, ingrese una cédula para buscar.")
            self.attendance_member_name_label.configure(text="Miembro: N/A")
            self.attendance_member_status_label.configure(text="Estado de Pago: N/A")
            self.register_attendance_button.configure(state="disabled")
            self.current_member_id_for_attendance = None
            return

        member = self.db.get_member_by_cedula(cedula)
        if member:
            member_id = member.get("ID")  # Usar el alias correcto 'ID' que retorna get_member_by_cedula
            name = member.get("Nombre")
            lastname = member.get("Apellido")
            self.attendance_member_name_label.configure(text=f"Miembro: {name} {lastname}")

            # Verificar estado de pago
            payment_status, expiry_date = self.check_member_payment_status(member_id)
            self.attendance_member_status_label.configure(text=f"Estado de Pago: {payment_status}")

            self.current_member_id_for_attendance = member_id
            # Habilitar el botón de asistencia si el pago está al día
            if payment_status == "Al día":
                self.register_attendance_button.configure(state="normal")
            else:
                self.register_attendance_button.configure(state="disabled")
        else:
            print(f"No se encontró miembro con cédula: {cedula}")
            self.attendance_member_name_label.configure(text="Miembro: No encontrado")
            self.attendance_member_status_label.configure(text="Estado de Pago: N/A")
            self.register_attendance_button.configure(state="disabled")
            self.current_member_id_for_attendance = None

    def register_attendance_event(self):
        """Registra la asistencia del miembro seleccionado."""
        print(f"Intentando registrar asistencia para el miembro con ID: {self.current_member_id_for_attendance}")

        # Validar que haya un miembro seleccionado
        if not self.current_member_id_for_attendance:
            CustomMessageBox(self, title="Error", message="No hay miembro seleccionado para registrar asistencia.", icon="warning").get()
            return

        try:
            # Validar que el ID es un número válido
            try:
                member_id_int = int(self.current_member_id_for_attendance)
            except Exception as e:
                CustomMessageBox(self, title="Error", message=f"ID de miembro inválido: {self.current_member_id_for_attendance}", icon="warning").get()
                print(f"ID de miembro inválido: {self.current_member_id_for_attendance}, error: {e}")
                return

            # Intentar registrar asistencia
            result = self.db.record_attendance(member_id_int)
            print(f"Resultado de record_attendance: {result}")
            if result:
                CustomMessageBox(self, title="Éxito", message="Asistencia registrada correctamente.", icon="info").get()
                self.load_daily_attendance()  # Recargar la lista de asistencia del día
                # Limpiar el formulario y deshabilitar el botón
                self.attendance_cedula_entry.delete(0, ctk.END)
                self.attendance_member_name_label.configure(text="Miembro: N/A")
                self.attendance_member_status_label.configure(text="Estado de Pago: N/A")
                self.register_attendance_button.configure(state="disabled")
                self.current_member_id_for_attendance = None
            else:
                CustomMessageBox(self, title="Error", message="No se pudo registrar la asistencia. Verifique la conexión con la base de datos o si ya fue registrada hoy.", icon="cancel").get()
        except Exception as e:
            CustomMessageBox(self, title="Error", message=f"Error inesperado al registrar asistencia: {e}", icon="cancel").get()

    def load_daily_attendance(self):
        """Carga y muestra la asistencia del día actual."""
        # Limpiar etiquetas existentes
        for label in self.attendance_labels:
            label.destroy()
        self.attendance_labels.clear()

        today = datetime.now().date()
        attendance_list = self.db.get_attendance_by_date(today)

        if attendance_list:
            # Crear encabezados de tabla
            headers = ["Nombre", "Apellido", "Cédula", "Hora"]
            for col_idx, header_text in enumerate(headers):
                header_label = ctk.CTkLabel(self.attendance_list_frame, text=header_text, font=ctk.CTkFont(weight="bold"))
                header_label.grid(row=0, column=col_idx, padx=5, pady=2, sticky="w")
                self.attendance_labels.append(header_label)

            # Llenar la tabla con datos de asistencia
            for row_idx, attendance in enumerate(attendance_list):
                # Asumiendo que 'Nombre', 'Apellido', 'Cedula', 'Hora' son las claves en el diccionario de asistencia
                name = attendance.get("Nombre", "")
                lastname = attendance.get("Apellido", "")
                cedula = attendance.get("Cedula", "")
                # Formatear la hora si es un objeto datetime
                attendance_time = attendance.get("Hora", "").strftime("%H:%M:%S") if isinstance(attendance.get("Hora"), datetime) else ""
                ctk.CTkLabel(self.attendance_list_frame, text=name).grid(row=row_idx + 1, column=0, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.attendance_list_frame, text=lastname).grid(row=row_idx + 1, column=1, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.attendance_list_frame, text=cedula).grid(row=row_idx + 1, column=2, padx=2, pady=2, sticky="w")
                ctk.CTkLabel(self.attendance_list_frame, text=attendance_time).grid(row=row_idx + 1, column=3, padx=2, pady=2, sticky="w")

                # Almacenar las etiquetas para poder limpiarlas después
                self.attendance_labels.extend([
                    self.attendance_list_frame.grid_slaves(row=row_idx + 1, column=0)[0],
                    self.attendance_list_frame.grid_slaves(row=row_idx + 1, column=1)[0],
                    self.attendance_list_frame.grid_slaves(row=row_idx + 1, column=2)[0],
                    self.attendance_list_frame.grid_slaves(row_idx + 1, column=3)[0]
                ])
        else:
            no_attendance_label = ctk.CTkLabel(self.attendance_list_frame, text="No hay asistencia registrada para hoy.")
            no_attendance_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.attendance_labels.append(no_attendance_label)

    def check_member_payment_status(self, member_id):
        """Verifica el estado de pago de un miembro."""
        # Obtener el último pago del miembro
        last_payment = self.db.get_latest_payment(member_id)

        if not last_payment:
            return "Sin pagos registrados", None

        payment_date = last_payment.get("Fecha-Pago")
        payment_type = last_payment.get("Tipo-Membresia")

        if not payment_date or not payment_type:
            return "Estado desconocido", None

        today = datetime.now().date()
        expiry_date = None

        if payment_type == "Mensual":
            # Calcular la fecha de vencimiento para membresía mensual
            # Sumar un mes a la fecha de pago
            if payment_date.month == 12:
                expiry_date = payment_date.replace(year=payment_date.year + 1, month=1)
            else:
                expiry_date = payment_date.replace(month=payment_date.month + 1)
            # Restar un día para obtener el último día de validez
            expiry_date = expiry_date - timedelta(days=1)

            # Ensure expiry_date is a date object for comparison
            if isinstance(expiry_date, datetime):
                expiry_date = expiry_date.date()

            if today <= expiry_date:
                return "Al día", expiry_date
            else:
                return f"Vencido desde {expiry_date.strftime('%Y-%m-%d')}", expiry_date

        elif payment_type == "Quincenal":
            # Calcular la fecha de vencimiento para membresía quincenal
            expiry_date = payment_date + timedelta(days=14)

            if today <= expiry_date:
                return "Al día", expiry_date
            else:
                return f"Vencido desde {expiry_date.strftime('%Y-%m-%d')}", expiry_date

        else:
            return "Tipo de membresía desconocido", None

    def search_member_for_payment(self):
        """Busca un miembro por cédula para la gestión de pagos."""
        cedula = self.payments_cedula_entry.get()
        if not cedula:
            print("Por favor, ingrese una cédula para buscar.")
            self.payments_member_name_label.configure(text="Miembro: N/A")
            self.payments_member_status_label.configure(text="Estado de Pago: N/A")
            self.payments_expiry_date_label.configure(text="Fecha de Vencimiento: N/A")
            self.register_new_payment_button.configure(state="disabled")
            self.current_member_id_for_payment = None
            self.load_payments_history(None) # Limpiar historial de pagos
            return

        member = self.db.get_member_by_cedula(cedula)

        if member:
            member_id = member.get("ID")
            name = member.get("Nombre")
            lastname = member.get("Apellido")
            self.payments_member_name_label.configure(text=f"Miembro: {name} {lastname}")

            # Verificar estado de pago y obtener fecha de vencimiento
            payment_status, expiry_date = self.check_member_payment_status(member_id)
            self.payments_member_status_label.configure(text=f"Estado de Pago: {payment_status}")
            if expiry_date:
                self.payments_expiry_date_label.configure(text=f"Fecha de Vencimiento: {expiry_date.strftime('%Y-%m-%d')}")
            else:
                self.payments_expiry_date_label.configure(text="Fecha de Vencimiento: N/A")

            self.current_member_id_for_payment = member_id
            self.register_new_payment_button.configure(state="normal")
            self.load_payments_history(member_id) # Cargar historial de pagos del miembro
        else:
            print(f"No se encontró miembro con cédula: {cedula}")
            self.payments_member_name_label.configure(text="Miembro: No encontrado")
            self.payments_member_status_label.configure(text="Estado de Pago: N/A")
            self.payments_expiry_date_label.configure(text="Fecha de Vencimiento: N/A")
            self.register_new_payment_button.configure(state="disabled")
            self.current_member_id_for_payment = None
            self.load_payments_history(None) # Limpiar historial de pagos

    def register_new_payment_event(self):
        """Registra un nuevo pago para el miembro seleccionado."""
        if not self.current_member_id_for_payment:
            print("Error: No hay miembro seleccionado para registrar el pago.")
            return

        payment_type = self.new_payment_type_optionemenu.get()
        payment_amount_str = self.new_payment_amount_entry.get()
        currency_type = self.new_currency_type_optionemenu.get()
        payment_date_str = self.new_payment_date_entry.get()
        payment_reference = self.new_payment_reference_entry.get()

        if not payment_type or not payment_amount_str or not currency_type or not payment_date_str:
            print("Error: Tipo de membresía, Monto, Tipo de Moneda y Fecha de Pago son obligatorios.")
            return

        try:
            payment_amount = float(payment_amount_str)
            payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d").date()

            if self.db.add_payment(self.current_member_id_for_payment, payment_amount, payment_date, payment_type, currency_type, payment_reference):
                print(f"Nuevo pago de {payment_amount} {currency_type} registrado para el miembro ID: {self.current_member_id_for_payment}.")
                
                # Registrar en Pago-Mensual o Pago-Quincenal si aplica (para control de validez)
                if payment_type == "Mensual":
                    fecha_inicio = payment_date
                    if fecha_inicio.month == 12:
                        fecha_fin = fecha_inicio.replace(year=fecha_inicio.year + 1, month=1, day=1) - timedelta(days=1)
                    else:
                        fecha_fin = fecha_inicio.replace(month=fecha_inicio.month + 1, day=1) - timedelta(days=1)
                    
                    if self.db.add_monthly_payment(self.current_member_id_for_payment, fecha_inicio, fecha_fin):
                        print("Membresía mensual registrada para control de validez.")
                    else:
                        print("Error al registrar membresía mensual para control de validez.")
                elif payment_type == "Quincenal":
                    fecha_inicio = payment_date
                    fecha_fin = fecha_inicio + timedelta(days=14)

                    if self.db.add_fortnightly_payment(self.current_member_id_for_payment, fecha_inicio, fecha_fin):
                        print("Membresía quincenal registrada para control de validez.")
                    else:
                        print("Error al registrar membresía quincenal para control de validez.")

                # Limpiar campos del formulario de nuevo pago
                self.new_payment_amount_entry.delete(0, ctk.END)
                self.new_payment_date_entry.configure(state="normal")
                self.new_payment_date_entry.delete(0, ctk.END)
                self.new_payment_date_entry.configure(state="readonly")
                self.new_payment_reference_entry.delete(0, ctk.END)
                self.new_payment_type_optionemenu.set("Mensual")
                self.new_currency_type_optionemenu.set("$")

                # Actualizar estado de pago y historial
                payment_status, expiry_date = self.check_member_payment_status(self.current_member_id_for_payment)
                self.payments_member_status_label.configure(text=f"Estado de Pago: {payment_status}")
                if expiry_date:
                    self.payments_expiry_date_label.configure(text=f"Fecha de Vencimiento: {expiry_date.strftime('%Y-%m-%d')}")
                else:
                    self.payments_expiry_date_label.configure(text="Fecha de Vencimiento: N/A")
                self.load_payments_history(self.current_member_id_for_payment)
            else:
                print("Error al registrar el nuevo pago.")
        except ValueError:
            print("Error: Monto o Fecha de Pago incorrectos. Asegúrese de que el monto sea un número y la fecha esté en formato YYYY-MM-%D.")
        except Exception as e:
            print(f"Error inesperado al procesar nuevo pago: {e}")

    def search_member_for_observation(self):
        """Busca un miembro por cédula para la gestión de observaciones."""
        cedula = self.observations_cedula_entry.get()
        if not cedula:
            print("Por favor, ingrese una cédula para buscar.")
            self.observations_member_name_label.configure(text="Miembro: N/A")
            self.add_observation_button.configure(state="disabled")
            self.current_member_id_for_observation = None
            self.load_observations_history(None) # Limpiar historial de observaciones
            return

        member = self.db.get_member_by_cedula(cedula)

        if member:
            member_id = member.get("ID")
            name = member.get("Nombre")
            lastname = member.get("Apellido")
            self.observations_member_name_label.configure(text=f"Miembro: {name} {lastname}")
            self.current_member_id_for_observation = member_id
            self.add_observation_button.configure(state="normal")
            self.load_observations_history(member_id) # Cargar historial de observaciones del miembro
        else:
            print(f"No se encontró miembro con cédula: {cedula}")
            self.observations_member_name_label.configure(text="Miembro: No encontrado")
            self.add_observation_button.configure(state="disabled")
            self.current_member_id_for_observation = None
            self.load_observations_history(None) # Limpiar historial de observaciones

    def add_observation_event(self):
        """Añade una nueva observación para el miembro seleccionado."""
        if not self.current_member_id_for_observation:
            print("Error: No hay miembro seleccionado para añadir la observación.")
            return

        observation_text = self.new_observation_textbox.get("1.0", ctk.END).strip() # Obtener todo el texto y limpiar espacios
        if not observation_text:
            print("Error: La observación no puede estar vacía.")
            return

        if self.db.add_observation(self.current_member_id_for_observation, observation_text):
            print(f"Observación añadida para el miembro ID: {self.current_member_id_for_observation}")
            self.new_observation_textbox.delete("1.0", ctk.END) # Limpiar el textbox
            self.load_observations_history(self.current_member_id_for_observation) # Recargar historial de observaciones
        else:
            print("Error al añadir la observación.")

    def setup_pdf_export_frame(self):
        """Configura el contenido del marco de exportación a PDF."""
        # Limpiar el frame antes de añadir nuevos widgets
        for widget in self.pdf_export_frame.winfo_children():
            widget.destroy()

        self.pdf_export_frame.grid_columnconfigure(0, weight=1)
        self.pdf_export_frame.grid_rowconfigure(3, weight=1) # Fila para el área de mensajes

        self.pdf_export_title_label = ctk.CTkLabel(self.pdf_export_frame, text="Exportar Datos a PDF", font=ctk.CTkFont(size=20, weight="bold"))
        self.pdf_export_title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.pdf_export_options_frame = ctk.CTkFrame(self.pdf_export_frame, fg_color="transparent")
        self.pdf_export_options_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.pdf_export_options_frame.grid_columnconfigure(0, weight=1)
        self.pdf_export_options_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.pdf_export_options_frame, text="Seleccione la tabla a exportar:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.pdf_table_selection_optionemenu = ctk.CTkOptionMenu(self.pdf_export_options_frame, values=["Miembros", "Asistencia", "Pagos", "Observaciones"])
        self.pdf_table_selection_optionemenu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.pdf_table_selection_optionemenu.set("Miembros") # Valor por defecto

        # Botón para exportar PDF (colocado en el frame de exportación, no en la barra lateral)
        self.export_pdf_button = ctk.CTkButton(self.pdf_export_options_frame, text="Generar PDF", command=self.generate_pdf_report)
        self.export_pdf_button.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.pdf_export_status_label = ctk.CTkLabel(self.pdf_export_frame, text="", text_color="green")
        self.pdf_export_status_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")

    def generate_pdf_report(self):
        """Genera un informe PDF de la tabla seleccionada."""
        selected_table = self.pdf_table_selection_optionemenu.get()
        data = []
        headers = []
        title = ""

        if selected_table == "Miembros":
            data = self.db.get_members()
            headers = ["ID", "Nombre", "Apellido", "Cédula", "Teléfono"]
            title = "Reporte de Miembros"
        elif selected_table == "Asistencia":
            # Para asistencia, podríamos querer un rango de fechas o solo el día actual
            # Por simplicidad, exportaremos la asistencia del día actual
            today = datetime.now().date()
            data = self.db.get_attendance_by_date(today)
            headers = ["Nombre", "Apellido", "Cédula", "Hora"]
            title = f"Reporte de Asistencia del {today.strftime('%Y-%m-%d')}"
        elif selected_table == "Pagos":
            # Para pagos, exportar todos los pagos o de un rango de fechas
            # Por simplicidad, exportaremos todos los pagos
            data = self.db.get_all_payments() # Necesitarás un método en DBManager para esto
            headers = ["Miembro", "Fecha", "Monto ($)", "Monto (Bs)", "Monto (Digital)", "Referencia", "Tipo Membresía"]
            title = "Reporte de Pagos"
        elif selected_table == "Observaciones":
            data = self.db.get_all_observations() # Necesitarás un método en DBManager para esto
            headers = ["Miembro", "Observación", "Fecha"]
            title = "Reporte de Observaciones"
        else:
            CustomMessageBox(self, title="Error", message="Tabla no reconocida para exportar.", icon="warning").get()
            return

        if not data:
            CustomMessageBox(self, title="Información", message=f"No hay datos para exportar en la tabla '{selected_table}'.", icon="info").get()
            return

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Título del PDF
            pdf.cell(200, 10, title, ln=True, align="C")
            pdf.ln(10)

            # Encabezados de la tabla
            col_widths = [pdf.w / (len(headers) + 1)] * len(headers) # Distribución equitativa
            
            # Ajustar anchos de columna para campos específicos si es necesario
            if selected_table == "Miembros":
                col_widths = [20, 40, 40, 30, 30] # ID, Nombre, Apellido, Cédula, Teléfono
            elif selected_table == "Asistencia":
                col_widths = [45, 45, 40, 30] # Nombre, Apellido, Cédula, Hora
            elif selected_table == "Pagos":
                col_widths = [35, 25, 25, 25, 25, 25, 25] # Miembro, Fecha, Monto ($), Monto (Bs), Monto (Digital), Referencia, Tipo Membresía
            elif selected_table == "Observaciones":
                col_widths = [40, 100, 30] # Miembro, Observación, Fecha

            for i, header in enumerate(headers):
                pdf.set_font("Arial", style="B", size=10)
                pdf.cell(col_widths[i], 10, header, border=1, align="C")
            pdf.ln()

            # Datos de la tabla
            pdf.set_font("Arial", size=9)
            for row in data:
                if selected_table == "Miembros":
                    pdf.cell(col_widths[0], 10, str(row.get("ID-Miembro", "")), border=1)
                    pdf.cell(col_widths[1], 10, row.get("Nombre", ""), border=1)
                    pdf.cell(col_widths[2], 10, row.get("Apellido", ""), border=1)
                    pdf.cell(col_widths[3], 10, row.get("Cedula", ""), border=1)
                    pdf.cell(col_widths[4], 10, row.get("Telefono", ""), border=1)
                elif selected_table == "Asistencia":
                    member_info = self.db.get_member_by_id(row.get("ID-Miembro"))
                    member_name = f"{member_info.get('Nombre', '')} {member_info.get('Apellido', '')}" if member_info else "N/A"
                    member_cedula = member_info.get('Cedula', '') if member_info else "N/A"
                    
                    pdf.cell(col_widths[0], 10, member_name, border=1)
                    pdf.cell(col_widths[1], 10, member_cedula, border=1)
                    pdf.cell(col_widths[2], 10, row.get("Fecha", "").strftime("%Y-%m-%d") if isinstance(row.get("Fecha"), datetime) else "", border=1)
                    pdf.cell(col_widths[3], 10, row.get("Hora", "").strftime("%H:%M:%S") if isinstance(row.get("Hora"), datetime) else "", border=1)
                elif selected_table == "Pagos":
                    member_info = self.db.get_member_by_id(row.get("ID-Miembro"))
                    member_name = f"{member_info.get('Nombre', '')} {member_info.get('Apellido', '')}" if member_info else "N/A"
                    
                    fecha = row.get("Fecha-Pago", "").strftime("%Y-%m-%d") if isinstance(row.get("Fecha-Pago"), datetime) else ""
                    monto_usd = str(row.get("Efectivo-$", ""))
                    monto_bs = str(row.get("Efectivo-Bs", ""))
                    monto_digital_bs = str(row.get("Monto-Digital-Bs", ""))
                    referencia = row.get("Referencia", "")
                    tipo_membresia = row.get("Tipo-Membresia", "")

                    pdf.cell(col_widths[0], 10, member_name, border=1)
                    pdf.cell(col_widths[1], 10, fecha, border=1)
                    pdf.cell(col_widths[2], 10, monto_usd, border=1)
                    pdf.cell(col_widths[3], 10, monto_bs, border=1)
                    pdf.cell(col_widths[4], 10, monto_digital_bs, border=1)
                    pdf.cell(col_widths[5], 10, referencia, border=1)
                    pdf.cell(col_widths[6], 10, tipo_membresia, border=1)
                elif selected_table == "Observaciones":
                    member_info = self.db.get_member_by_id(row.get("ID-Miembro"))
                    member_name = f"{member_info.get('Nombre', '')} {member_info.get('Apellido', '')}" if member_info else "N/A"
                    observation_text = row.get("Observacion", "")
                    observation_date = row.get("Fecha", "").strftime("%Y-%m-%d") if isinstance(row.get("Fecha"), datetime) else ""
                    pdf.cell(col_widths[0], 10, member_name, border=1)
                    # MultiCell para observaciones largas
                    y_before = pdf.get_y()
                    x_before = pdf.get_x()
                    pdf.multi_cell(col_widths[1], 10, observation_text, border=1)
                    y_after = pdf.get_y()
                    cell_height = y_after - y_before
                    # Si la observación es corta, mantener la altura mínima de celda
                    if cell_height == 0:
                        cell_height = 10
                    # Mover X a la posición de la siguiente columna y Y al inicio de la fila
                    pdf.set_xy(x_before + col_widths[0] + col_widths[1], y_before)
                    pdf.cell(col_widths[2], cell_height, observation_date, border=1)
                    # Mover Y a la siguiente fila
                    pdf.set_y(y_before + cell_height)
                pdf.ln()

            file_name = f"Reporte_{selected_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            import os
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            file_path = os.path.join(desktop_path, file_name)
            pdf.output(file_path)
            CustomMessageBox(self, title="Éxito", message=f"Reporte PDF generado exitosamente: {file_path}", icon="info").get()
            self.pdf_export_status_label.configure(text=f"PDF generado: {file_path}", text_color="green")
        except Exception as e:
            CustomMessageBox(self, title="Error al Generar PDF", message=f"Ocurrió un error al generar el PDF: {e}", icon="cancel").get()
            self.pdf_export_status_label.configure(text=f"Error: {e}", text_color="red")

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__ == "__main__":
    app = App()
    app.mainloop()
    app.db.disconnect() # Asegurarse de cerrar la conexión al salir
