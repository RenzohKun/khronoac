from __future__ import annotations

import json
import math
import tkinter as tk
from datetime import time
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any

from modelos.Asignatura import Asignatura
from modelos.Docente import Docente
from modelos.EspacioFisico import EspacioFisico
from modelos.Estudiante import Estudiante
from modelos.FranjaHoraria import FranjaHoraria
from modelos.Horario import Horario
from modelos.Laboratorio import Laboratorio
from modelos.Paralelo import Paralelo


DIAS = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")
HORA_INICIO = 7
HORA_FIN = 20

# Carpeta dedicada para almacenar los archivos JSON modulares
CARPETA_DATOS = Path(__file__).with_name("khronoac_datos")


def leer_datos() -> dict[str, Any]:
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    
    return {
        "docentes": _leer_seccion("docentes", []),
        "asignaturas": _leer_seccion("asignaturas", []),
        "espacios": _leer_seccion("espacios", []),
        "ultimoHorario": _leer_seccion("horario", None),
    }


def _leer_seccion(nombre: str, por_defecto: Any) -> Any:
    archivo = CARPETA_DATOS / f"{nombre}.json"
    if not archivo.exists():
        return por_defecto
    try:
        with archivo.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return por_defecto


def _guardar_seccion(nombre: str, contenido: Any) -> None:
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    archivo = CARPETA_DATOS / f"{nombre}.json"
    temporal = CARPETA_DATOS / f"{nombre}.tmp"
    with temporal.open("w", encoding="utf-8") as f:
        json.dump(contenido, f, ensure_ascii=False, indent=2)
    temporal.replace(archivo)


class KhronoacApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Khronoac — Planificador de Horarios Académicos")
        self.geometry("1200x780")
        self.minsize(960, 640)
        self.configure(bg="#0f1623")
        try:
            self.iconbitmap(str(Path(__file__).with_name("khronoac_icon.ico")))
        except Exception:
            pass

        self.datos = leer_datos()
        self.docente_por_etiqueta: dict[str, str] = {}
        self.docente_dias_vars: dict[str, tk.BooleanVar] = {}
        self.plan_actual: dict[str, Any] | None = self.datos["ultimoHorario"]
        self.docente_editando: str | None = None
        self.asignatura_editando: str | None = None
        self.espacio_editando: str | None = None

        self._configurar_estilos()
        self._construir_interfaz()
        self._refrescar_listas()
        self._mostrar_plan_guardado()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        # ── Colores base ──────────────────────────────────────────────────
        BG          = "#0f1623"   # fondo principal oscuro
        CARD        = "#1a2233"   # fondo de tarjetas/paneles
        CARD_BORDER = "#243047"   # borde sutil de tarjetas
        FG          = "#e8edf5"   # texto principal
        FG_MUTED    = "#7a8faa"   # texto secundario
        ACCENT      = "#3b82f6"   # azul brillante primario
        ACCENT_HOV  = "#2563eb"   # hover del acento
        ACCENT2     = "#6366f1"   # índigo para variaciones
        HEADING_FG  = "#c7d8f0"   # encabezados de columna
        ROW_ODD     = "#1a2233"
        ROW_EVEN    = "#151e2d"
        SEL_BG      = "#1e3a5f"
        SEL_FG      = "#ffffff"

        estilo.configure("TFrame",           background=BG)
        estilo.configure("Card.TFrame",       background=CARD,    relief="flat",  borderwidth=1)
        estilo.configure("TLabel",            background=BG,      foreground=FG,  font=("Segoe UI", 10))
        estilo.configure("Title.TLabel",      background=BG,      foreground=FG,  font=("Segoe UI", 22, "bold"))
        estilo.configure("Subtitle.TLabel",   background=BG,      foreground=FG_MUTED, font=("Segoe UI", 9))
        estilo.configure("Card.TLabel",       background=CARD,    foreground=FG,  font=("Segoe UI", 9))
        estilo.configure("CardHead.TLabel",   background=CARD,    foreground=HEADING_FG, font=("Segoe UI", 9, "bold"))

        estilo.configure("TButton",
                         padding=(13, 8),
                         font=("Segoe UI", 9, "bold"),
                         background=CARD_BORDER,
                         foreground=FG,
                         relief="flat",
                         borderwidth=0)
        estilo.map("TButton",
                   background=[("active", "#2e3f5a")],
                   foreground=[("active", "#ffffff")])

        estilo.configure("Accent.TButton",
                         background=ACCENT,
                         foreground="#ffffff",
                         padding=(14, 8),
                         font=("Segoe UI", 9, "bold"),
                         relief="flat",
                         borderwidth=0)
        estilo.map("Accent.TButton",
                   background=[("active", ACCENT_HOV)],
                   foreground=[("active", "#ffffff")])

        estilo.configure("Danger.TButton",
                         background="#7f1d1d",
                         foreground="#fca5a5",
                         padding=(12, 7),
                         font=("Segoe UI", 9, "bold"),
                         relief="flat",
                         borderwidth=0)
        estilo.map("Danger.TButton",
                   background=[("active", "#991b1b")],
                   foreground=[("active", "#ffffff")])

        estilo.configure("Treeview",
                         background=ROW_ODD,
                         foreground=FG,
                         fieldbackground=ROW_ODD,
                         rowheight=30,
                         font=("Segoe UI", 9),
                         borderwidth=0,
                         relief="flat")
        estilo.configure("Treeview.Heading",
                         background=CARD_BORDER,
                         foreground=HEADING_FG,
                         font=("Segoe UI", 9, "bold"),
                         relief="flat",
                         padding=(6, 6))
        estilo.map("Treeview",
                   background=[("selected", SEL_BG)],
                   foreground=[("selected", SEL_FG)])
        estilo.map("Treeview.Heading",
                   background=[("active", ACCENT2)])

        estilo.configure("TNotebook",
                         background=BG,
                         borderwidth=0,
                         tabmargins=(0, 0, 0, 0))
        estilo.configure("TNotebook.Tab",
                         background=CARD,
                         foreground=FG_MUTED,
                         padding=(18, 10),
                         font=("Segoe UI", 9, "bold"),
                         borderwidth=0)
        estilo.map("TNotebook.Tab",
                   background=[("selected", BG),       ("active", "#1e2d45")],
                   foreground=[("selected", ACCENT),   ("active", FG)])

        estilo.configure("TScrollbar",
                         background=CARD_BORDER,
                         troughcolor=BG,
                         borderwidth=0,
                         arrowsize=12)
        estilo.map("TScrollbar",
                   background=[("active", ACCENT2)])

        estilo.configure("TEntry",
                         fieldbackground="#0d1520",
                         foreground=FG,
                         insertcolor=ACCENT,
                         borderwidth=1,
                         relief="flat",
                         padding=(6, 5))
        estilo.configure("TCombobox",
                         fieldbackground="#0d1520",
                         foreground=FG,
                         background=CARD_BORDER,
                         borderwidth=1,
                         relief="flat",
                         padding=(6, 5))
        estilo.map("TCombobox",
                   fieldbackground=[("readonly", "#0d1520")],
                   foreground=[("readonly", FG)])

        estilo.configure("TSpinbox",
                         fieldbackground="#0d1520",
                         foreground=FG,
                         background=CARD_BORDER,
                         borderwidth=1,
                         relief="flat",
                         padding=(4, 4))

        estilo.configure("TCheckbutton",
                         background=CARD,
                         foreground=FG,
                         font=("Segoe UI", 9))
        estilo.map("TCheckbutton",
                   background=[("active", CARD)],
                   foreground=[("active", "#ffffff")])

    def _construir_interfaz(self) -> None:
        encabezado = ttk.Frame(self, padding=(28, 20, 28, 14))
        encabezado.pack(fill="x")

        fila_titulo = ttk.Frame(encabezado)
        fila_titulo.pack(fill="x")
        ttk.Label(fila_titulo, text="🗓  Khronoac", style="Title.TLabel").pack(side="left")
        ttk.Label(
            fila_titulo,
            text="v1.0",
            foreground="#3b82f6",
            background="#0f1623",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(10, 0), pady=(8, 0))

        ttk.Label(
            encabezado,
            text="Gestión de recursos académicos · Generación automática de horarios sin conflictos",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        sep = tk.Frame(self, height=1, bg="#1e3054")
        sep.pack(fill="x", padx=0, pady=(2, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(10, 14))

        self.tab_docentes = ttk.Frame(self.notebook, padding=16)
        self.tab_asignaturas = ttk.Frame(self.notebook, padding=16)
        self.tab_espacios = ttk.Frame(self.notebook, padding=16)
        self.tab_horario = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(self.tab_docentes,   text="  👤  Docentes  ")
        self.notebook.add(self.tab_asignaturas, text="  📚  Asignaturas  ")
        self.notebook.add(self.tab_espacios,   text="  🏫  Aulas y Laboratorios  ")
        self.notebook.add(self.tab_horario,    text="  🗓  Planificar Horario  ")

        self._construir_tab_docentes()
        self._construir_tab_asignaturas()
        self._construir_tab_espacios()
        self._construir_tab_horario()

    @staticmethod
    def _crear_tree(parent: ttk.Frame, columnas: tuple[tuple[str, str, int], ...]) -> ttk.Treeview:
        contenedor = ttk.Frame(parent, style="Card.TFrame")
        contenedor.pack(fill="both", expand=True)
        nombres = tuple(columna[0] for columna in columnas)
        tree = ttk.Treeview(contenedor, columns=nombres, show="headings", selectmode="browse")
        for clave, titulo, ancho in columnas:
            tree.heading(clave, text=titulo)
            tree.column(clave, width=ancho, minwidth=70, anchor="w")
        scroll_y = ttk.Scrollbar(contenedor, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(contenedor, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)
        return tree

    @staticmethod
    def _campo(parent: ttk.Frame, titulo: str, variable: tk.StringVar, fila: int, columna: int,
               ancho: int = 25) -> ttk.Entry:
        bloque = ttk.Frame(parent, style="Card.TFrame")
        bloque.grid(row=fila, column=columna, padx=(0, 12), pady=5, sticky="ew")
        ttk.Label(bloque, text=titulo, style="Card.TLabel").pack(anchor="w", pady=(0, 3))
        entrada = ttk.Entry(bloque, textvariable=variable, width=ancho)
        entrada.pack(fill="x")
        return entrada

    def _construir_tab_docentes(self) -> None:
        formulario = ttk.Frame(self.tab_docentes, style="Card.TFrame", padding=12)
        formulario.pack(fill="x", pady=(0, 12))
        self.doc_cedula = tk.StringVar()
        self.doc_nombres = tk.StringVar()
        self.doc_apellidos = tk.StringVar()
        self.doc_correo = tk.StringVar()
        self.doc_titulo = tk.StringVar()
        for col in range(5):
            formulario.columnconfigure(col, weight=1)
        self._campo(formulario, "Cédula / identificador", self.doc_cedula, 0, 0)
        self._campo(formulario, "Nombres", self.doc_nombres, 0, 1)
        self._campo(formulario, "Apellidos", self.doc_apellidos, 0, 2)
        self._campo(formulario, "Correo electrónico", self.doc_correo, 0, 3)
        self._campo(formulario, "Título académico", self.doc_titulo, 0, 4)

        dias = ttk.Frame(formulario, style="Card.TFrame")
        dias.grid(row=1, column=0, columnspan=5, sticky="w", pady=(8, 3))
        ttk.Label(dias, text="Disponibilidad semanal  (07:00 – 20:00):", style="Card.TLabel").pack(side="left", padx=(0, 14))
        for dia in DIAS:
            variable = tk.BooleanVar(value=True)
            self.docente_dias_vars[dia] = variable
            ttk.Checkbutton(dias, text=dia, variable=variable).pack(side="left", padx=4)

        acciones = ttk.Frame(formulario, style="Card.TFrame")
        acciones.grid(row=2, column=0, columnspan=5, sticky="e", pady=(8, 0))
        ttk.Button(acciones, text="  ✔  Guardar docente", style="Accent.TButton", command=self._guardar_docente).pack(side="left", padx=5)
        ttk.Button(acciones, text="  ✕  Limpiar", command=self._limpiar_docente).pack(side="left", padx=5)

        columnas = (("cedula", "Identificador", 120), ("nombre", "Docente", 220),
                    ("correo", "Correo", 220), ("titulo", "Título", 180), ("dias", "Días disponibles", 250))
        self.tree_docentes = self._crear_tree(self.tab_docentes, columnas)
        self.tree_docentes.bind("<<TreeviewSelect>>", self._seleccionar_docente)
        ttk.Button(self.tab_docentes, text="  🗑  Eliminar seleccionado", style="Danger.TButton", command=self._eliminar_docente).pack(anchor="e", pady=(10, 2))

    def _construir_tab_asignaturas(self) -> None:
        formulario = ttk.Frame(self.tab_asignaturas, style="Card.TFrame", padding=12)
        formulario.pack(fill="x", pady=(0, 12))
        self.asig_nombre = tk.StringVar()
        self.asig_horas = tk.StringVar(value="3")
        self.asig_demanda = tk.StringVar(value="30")
        self.asig_docente = tk.StringVar()
        self.asig_laboratorio = tk.BooleanVar()
        for col in range(4):
            formulario.columnconfigure(col, weight=1)
        self._campo(formulario, "Nombre de la asignatura", self.asig_nombre, 0, 0)
        self._campo(formulario, "Horas por semana", self.asig_horas, 0, 1)
        self._campo(formulario, "Demanda estimada de estudiantes", self.asig_demanda, 0, 2)
        bloque = ttk.Frame(formulario, style="Card.TFrame")
        bloque.grid(row=0, column=3, padx=(0, 10), pady=5, sticky="ew")
        ttk.Label(bloque, text="Docente responsable", style="Card.TLabel").pack(anchor="w", pady=(0, 3))
        self.combo_docente = ttk.Combobox(bloque, textvariable=self.asig_docente, state="readonly")
        self.combo_docente.pack(fill="x")
        ttk.Checkbutton(formulario, text="Requiere laboratorio", variable=self.asig_laboratorio).grid(row=1, column=0, sticky="w", pady=7)
        acciones = ttk.Frame(formulario, style="Card.TFrame")
        acciones.grid(row=1, column=1, columnspan=3, sticky="e", pady=5)
        ttk.Button(acciones, text="  ✔  Guardar asignatura", style="Accent.TButton", command=self._guardar_asignatura).pack(side="left", padx=5)
        ttk.Button(acciones, text="  ✕  Limpiar", command=self._limpiar_asignatura).pack(side="left", padx=5)

        columnas = (("nombre", "Asignatura", 220), ("horas", "Horas/semana", 110),
                    ("demanda", "Demanda estimada", 140), ("docente", "Docente", 220), ("lab", "Laboratorio", 110))
        self.tree_asignaturas = self._crear_tree(self.tab_asignaturas, columnas)
        self.tree_asignaturas.bind("<<TreeviewSelect>>", self._seleccionar_asignatura)
        ttk.Button(self.tab_asignaturas, text="  🗑  Eliminar seleccionado", style="Danger.TButton", command=self._eliminar_asignatura).pack(anchor="e", pady=(10, 2))

    def _construir_tab_espacios(self) -> None:
        formulario = ttk.Frame(self.tab_espacios, style="Card.TFrame", padding=12)
        formulario.pack(fill="x", pady=(0, 12))
        self.esp_codigo = tk.StringVar()
        self.esp_capacidad = tk.StringVar(value="30")
        self.esp_tipo = tk.StringVar(value="Aula")
        self.esp_tipo_lab = tk.StringVar()
        self.esp_equipos = tk.StringVar()
        for col in range(4):
            formulario.columnconfigure(col, weight=1)
        self._campo(formulario, "Código del espacio", self.esp_codigo, 0, 0)
        self._campo(formulario, "Capacidad máxima", self.esp_capacidad, 0, 1)
        bloque_tipo = ttk.Frame(formulario, style="Card.TFrame")
        bloque_tipo.grid(row=0, column=2, padx=(0, 12), pady=5, sticky="ew")
        ttk.Label(bloque_tipo, text="Tipo", style="Card.TLabel").pack(anchor="w", pady=(0, 3))
        tipo = ttk.Combobox(bloque_tipo, textvariable=self.esp_tipo, values=("Aula", "Laboratorio"), state="readonly")
        tipo.pack(fill="x")
        self._campo(formulario, "Tipo de laboratorio", self.esp_tipo_lab, 0, 3)
        self._campo(formulario, "Equipos especiales", self.esp_equipos, 1, 0)
        ttk.Label(formulario, text="Los datos de laboratorio solo se usan cuando el tipo es Laboratorio.", style="Card.TLabel").grid(row=1, column=1, columnspan=2, sticky="w")
        acciones = ttk.Frame(formulario, style="Card.TFrame")
        acciones.grid(row=1, column=3, sticky="e", pady=5)
        ttk.Button(acciones, text="  ✔  Guardar espacio", style="Accent.TButton", command=self._guardar_espacio).pack(side="left", padx=5)
        ttk.Button(acciones, text="  ✕  Limpiar", command=self._limpiar_espacio).pack(side="left", padx=5)

        columnas = (("codigo", "Código", 150), ("tipo", "Tipo", 140),
                    ("capacidad", "Capacidad", 110), ("detalle", "Equipamiento / tipo", 360))
        self.tree_espacios = self._crear_tree(self.tab_espacios, columnas)
        self.tree_espacios.bind("<<TreeviewSelect>>", self._seleccionar_espacio)
        ttk.Button(self.tab_espacios, text="  🗑  Eliminar seleccionado", style="Danger.TButton", command=self._eliminar_espacio).pack(anchor="e", pady=(10, 2))

    def _construir_tab_horario(self) -> None:
        controles = ttk.Frame(self.tab_horario, style="Card.TFrame", padding=12)
        controles.pack(fill="x", pady=(0, 12))
        ttk.Label(controles, text="Mínimo de estudiantes por paralelo:", style="Card.TLabel").pack(side="left")
        self.minimo_var = tk.StringVar(value="10")
        ttk.Spinbox(controles, from_=1, to=200, textvariable=self.minimo_var, width=7).pack(side="left", padx=10)
        ttk.Button(controles, text="  ▶  Generar horario", style="Accent.TButton", command=self._generar_horario).pack(side="left", padx=8)
        ttk.Button(controles, text="  ↓  Exportar JSON", command=self._exportar_horario).pack(side="left", padx=6)
        ttk.Label(
            self.tab_horario,
            text="Cada hora se planifica como un bloque de 60 min · Lunes a Viernes · 07:00 – 20:00 · Sin conflictos de docente, aula o paralelo.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(6, 10))
        columnas = (("dia", "Día", 100), ("inicio", "Inicio", 75), ("fin", "Fin", 75),
                    ("asignatura", "Asignatura", 180), ("paralelo", "Paralelo", 90),
                    ("demanda", "Estudiantes", 90), ("docente", "Docente", 180), ("espacio", "Aula / laboratorio", 150))
        self.tree_horario = self._crear_tree(self.tab_horario, columnas)
        self.estado_horario = tk.StringVar(value="Registra docentes, asignaturas y espacios para comenzar.")
        ttk.Label(self.tab_horario, textvariable=self.estado_horario, style="Subtitle.TLabel", wraplength=1000).pack(anchor="w", pady=(10, 0))

    def _guardar_archivo(self) -> None:
        _guardar_seccion("docentes", self.datos["docentes"])
        _guardar_seccion("asignaturas", self.datos["asignaturas"])
        _guardar_seccion("espacios", self.datos["espacios"])
        _guardar_seccion("horario", self.datos["ultimoHorario"])  # Guarda en horario.json

    def _invalidar_plan(self) -> None:
        self.plan_actual = None
        self.datos["ultimoHorario"] = None

    @staticmethod
    def _indice_por_clave(registros: list[dict[str, Any]], clave: str, valor: str) -> int | None:
        return next((i for i, registro in enumerate(registros) if registro.get(clave) == valor), None)

    def _docente_etiqueta(self, docente: dict[str, Any]) -> str:
        return f"{docente['cedula']} — {docente['nombres']} {docente['apellidos']}"

    def _obtener_docente(self, cedula: str) -> dict[str, Any] | None:
        return next((persona for persona in self.datos["docentes"] if persona["cedula"] == cedula), None)

    def _refrescar_listas(self) -> None:
        for tree in (self.tree_docentes, self.tree_asignaturas, self.tree_espacios, self.tree_horario):
            tree.delete(*tree.get_children())

        for docente in self.datos["docentes"]:
            self.tree_docentes.insert("", "end", iid=docente["cedula"], values=(
                docente["cedula"], f"{docente['nombres']} {docente['apellidos']}", docente["correoElectronico"],
                docente["tituloAcademico"], ", ".join(docente["diasDisponibles"]),
            ))
        self.docente_por_etiqueta = {
            self._docente_etiqueta(docente): docente["cedula"] for docente in self.datos["docentes"]
        }
        valores_docentes = list(self.docente_por_etiqueta)
        self.combo_docente.configure(values=valores_docentes)
        if self.asig_docente.get() not in valores_docentes:
            self.asig_docente.set(valores_docentes[0] if valores_docentes else "")

        for asignatura in self.datos["asignaturas"]:
            docente = self._obtener_docente(asignatura["docenteCedula"])
            nombre_docente = self._docente_etiqueta(docente) if docente else "Sin docente"
            self.tree_asignaturas.insert("", "end", iid=asignatura["nombreAsignatura"], values=(
                asignatura["nombreAsignatura"], asignatura["horasRequeridas"], asignatura["demandaEstimada"],
                nombre_docente, "Sí" if asignatura["requiereLaboratorio"] else "No",
            ))
        for espacio in self.datos["espacios"]:
            detalle = (
                f"{espacio.get('tipoLaboratorio', '')} | {espacio.get('equiposEspeciales', '')}"
                if espacio["tipo"] == "Laboratorio" else "Aula general"
            )
            self.tree_espacios.insert("", "end", iid=espacio["codigoAula"], values=(
                espacio["codigoAula"], espacio["tipo"], espacio["capacidadMaxima"], detalle,
            ))
        self._mostrar_plan_guardado()

    def _guardar_docente(self) -> None:
        cedula = self.doc_cedula.get().strip()
        nombres = self.doc_nombres.get().strip()
        apellidos = self.doc_apellidos.get().strip()

        if not all((cedula, nombres, apellidos)):
            messagebox.showwarning(
                "Datos incompletos",
                "Cédula, nombres y apellidos son obligatorios."
            )
            return

        dias = [
            dia for dia, variable in self.docente_dias_vars.items()
            if variable.get()
        ]

        if not dias:
            messagebox.showwarning(
                "Disponibilidad requerida",
                "Selecciona al menos un día disponible."
            )
            return

        clave_anterior = self.docente_editando

        indice_nuevo = self._indice_por_clave(
            self.datos["docentes"], "cedula", cedula
        )

        # Si es un docente nuevo, comprobar que no exista su cédula.
        if clave_anterior is None and indice_nuevo is not None:
            messagebox.showwarning(
                "Identificador duplicado",
                "Ya existe otro docente con esa cédula."
            )
            return

        docente = {
            "cedula": cedula,
            "nombres": nombres,
            "apellidos": apellidos,
            "correoElectronico": self.doc_correo.get().strip(),
            "tituloAcademico": self.doc_titulo.get().strip(),
            "diasDisponibles": dias,
        }

        if clave_anterior is None:
            
            self.datos["docentes"].append(docente)

        else:
            
            indice_anterior = self._indice_por_clave(
                self.datos["docentes"], "cedula", clave_anterior
            )

            if indice_anterior is None:
                messagebox.showerror(
                    "Error",
                    "No se encontró el docente que intentas editar."
                )
                return

            # Evitar usar la cédula de otro docente.
            if indice_nuevo is not None and cedula != clave_anterior:
                messagebox.showwarning(
                    "Identificador duplicado",
                    "Esa cédula ya pertenece a otro docente."
                )
                return

            self.datos["docentes"][indice_anterior] = docente

            # Actualizar las asignaturas si cambió la cédula.
            if cedula != clave_anterior:
                for asignatura in self.datos["asignaturas"]:
                    if asignatura["docenteCedula"] == clave_anterior:
                        asignatura["docenteCedula"] = cedula

        self._invalidar_plan()
        self._guardar_archivo()

        # Limpiar el formulario y salir del modo edición.
        self._limpiar_docente()
        self._refrescar_listas()

        messagebox.showinfo(
            "Éxito",
            "Docente guardado correctamente."
        )

    def _seleccionar_docente(self, _evento: tk.Event) -> None:
        seleccion = self.tree_docentes.selection()
        if not seleccion:
            return
        docente = self._obtener_docente(seleccion[0])
        if docente is None:
            return
        self.docente_editando = docente["cedula"]
        self.doc_cedula.set(docente["cedula"])
        self.doc_nombres.set(docente["nombres"])
        self.doc_apellidos.set(docente["apellidos"])
        self.doc_correo.set(docente["correoElectronico"])
        self.doc_titulo.set(docente["tituloAcademico"])
        for dia, variable in self.docente_dias_vars.items():
            variable.set(dia in docente["diasDisponibles"])

    def _limpiar_docente(self) -> None:
        self.docente_editando = None
        for variable in (self.doc_cedula, self.doc_nombres, self.doc_apellidos, self.doc_correo, self.doc_titulo):
            variable.set("")
        for variable in self.docente_dias_vars.values():
            variable.set(True)
        self.tree_docentes.selection_remove(self.tree_docentes.selection())

    def _eliminar_docente(self) -> None:
        seleccion = self.tree_docentes.selection()
        if not seleccion:
            return
        cedula = seleccion[0]
        if any(asig["docenteCedula"] == cedula for asig in self.datos["asignaturas"]):
            messagebox.showwarning("Docente asignado", "Reasigna o elimina las asignaturas de este docente antes de eliminarlo.")
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar el docente seleccionado?"):
            self.datos["docentes"] = [d for d in self.datos["docentes"] if d["cedula"] != cedula]
            self._invalidar_plan()
            self._guardar_archivo()
            self._limpiar_docente()
            self._refrescar_listas()

    def _guardar_asignatura(self) -> None:
        nombre = self.asig_nombre.get().strip()
        try:
            horas, demanda = int(self.asig_horas.get()), int(self.asig_demanda.get())
            if horas < 1 or demanda < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Revisa los valores", "Las horas semanales y la demanda deben ser enteros mayores que cero.")
            return
        etiqueta_docente = self.asig_docente.get()
        cedula_docente = self.docente_por_etiqueta.get(etiqueta_docente)
        if not nombre or not cedula_docente:
            messagebox.showwarning("Datos incompletos", "Escribe el nombre y selecciona un docente registrado.")
            return
        asignatura = Asignatura(nombre, horas, self.asig_laboratorio.get())
        registro = {
            "nombreAsignatura": asignatura.nombreAsignatura,
            "horasRequeridas": asignatura.obtenerHorasTotales(),
            "requiereLaboratorio": asignatura.requiereLaboratorio(),
            "demandaEstimada": demanda, "docenteCedula": cedula_docente,
        }
        clave_anterior = self.asignatura_editando or nombre
        existente = self._indice_por_clave(self.datos["asignaturas"], "nombreAsignatura", clave_anterior)
        duplicada = next((a for a in self.datos["asignaturas"]
                          if a["nombreAsignatura"].casefold() == nombre.casefold()
                          and a["nombreAsignatura"] != clave_anterior), None)
        if duplicada is not None:
            messagebox.showwarning("Asignatura duplicada", "Ya existe otra asignatura con ese nombre.")
            return
        if existente is None:
            self.datos["asignaturas"].append(registro)
        else:
            self.datos["asignaturas"][existente] = registro
        self._invalidar_plan()
        self._guardar_archivo()
        self._limpiar_asignatura()
        self._refrescar_listas()

    def _seleccionar_asignatura(self, _evento: tk.Event) -> None:
        seleccion = self.tree_asignaturas.selection()
        if not seleccion:
            return
        asignatura = next((a for a in self.datos["asignaturas"] if a["nombreAsignatura"] == seleccion[0]), None)
        if asignatura is None:
            return
        self.asignatura_editando = asignatura["nombreAsignatura"]
        self.asig_nombre.set(asignatura["nombreAsignatura"])
        self.asig_horas.set(str(asignatura["horasRequeridas"]))
        self.asig_demanda.set(str(asignatura["demandaEstimada"]))
        self.asig_laboratorio.set(asignatura["requiereLaboratorio"])
        docente = self._obtener_docente(asignatura["docenteCedula"])
        self.asig_docente.set(self._docente_etiqueta(docente) if docente else "")

    def _limpiar_asignatura(self) -> None:
        self.asignatura_editando = None
        self.asig_nombre.set("")
        self.asig_horas.set("3")
        self.asig_demanda.set("30")
        self.asig_laboratorio.set(False)
        docentes = list(self.docente_por_etiqueta)
        self.asig_docente.set(docentes[0] if docentes else "")
        self.tree_asignaturas.selection_remove(self.tree_asignaturas.selection())

    def _eliminar_asignatura(self) -> None:
        seleccion = self.tree_asignaturas.selection()
        if seleccion and messagebox.askyesno("Confirmar", "¿Eliminar la asignatura seleccionada?"):
            nombre = seleccion[0]
            self.datos["asignaturas"] = [a for a in self.datos["asignaturas"] if a["nombreAsignatura"] != nombre]
            self._invalidar_plan()
            self._guardar_archivo()
            self._limpiar_asignatura()
            self._refrescar_listas()

    def _guardar_espacio(self) -> None:
        codigo = self.esp_codigo.get().strip()
        try:
            capacidad = int(self.esp_capacidad.get())
            if capacidad < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Capacidad inválida", "La capacidad debe ser un entero mayor que cero.")
            return
        if not codigo:
            messagebox.showwarning("Dato incompleto", "El código del espacio es obligatorio.")
            return
        tipo = self.esp_tipo.get()
        if tipo == "Laboratorio" and not self.esp_tipo_lab.get().strip():
            messagebox.showwarning("Dato incompleto", "Indica el tipo de laboratorio.")
            return
        if tipo == "Laboratorio":
            espacio_objeto = Laboratorio(codigo, capacidad, self.esp_equipos.get().strip(), self.esp_tipo_lab.get().strip())
            detalle_lab = {"tipoLaboratorio": espacio_objeto.tipoLaboratorio,
                           "equiposEspeciales": espacio_objeto.equiposEspeciales}
        else:
            espacio_objeto = EspacioFisico(codigo, capacidad)
            detalle_lab = {"tipoLaboratorio": "", "equiposEspeciales": ""}
        registro = {"codigoAula": espacio_objeto.codigoAula,
                    "capacidadMaxima": espacio_objeto.capacidadMaxima, "tipo": tipo, **detalle_lab}
        clave_anterior = self.espacio_editando or codigo
        existente = self._indice_por_clave(self.datos["espacios"], "codigoAula", clave_anterior)
        duplicado = next((e for e in self.datos["espacios"]
                          if e["codigoAula"].casefold() == codigo.casefold()
                          and e["codigoAula"] != clave_anterior), None)
        if duplicado is not None:
            messagebox.showwarning("Código duplicado", "Ya existe otro espacio con ese código.")
            return
        if existente is None:
            self.datos["espacios"].append(registro)
        else:
            self.datos["espacios"][existente] = registro
        self._invalidar_plan()
        self._guardar_archivo()
        self._limpiar_espacio()
        self._refrescar_listas()

    def _seleccionar_espacio(self, _evento: tk.Event) -> None:
        seleccion = self.tree_espacios.selection()
        if not seleccion:
            return
        espacio = next((e for e in self.datos["espacios"] if e["codigoAula"] == seleccion[0]), None)
        if espacio is None:
            return
        self.espacio_editando = espacio["codigoAula"]
        self.esp_codigo.set(espacio["codigoAula"])
        self.esp_capacidad.set(str(espacio["capacidadMaxima"]))
        self.esp_tipo.set(espacio["tipo"])
        self.esp_tipo_lab.set(espacio.get("tipoLaboratorio", ""))
        self.esp_equipos.set(espacio.get("equiposEspeciales", ""))

    def _limpiar_espacio(self) -> None:
        self.espacio_editando = None
        self.esp_codigo.set("")
        self.esp_capacidad.set("30")
        self.esp_tipo.set("Aula")
        self.esp_tipo_lab.set("")
        self.esp_equipos.set("")
        self.tree_espacios.selection_remove(self.tree_espacios.selection())

    def _eliminar_espacio(self) -> None:
        seleccion = self.tree_espacios.selection()
        if seleccion and messagebox.askyesno("Confirmar", "¿Eliminar el espacio seleccionado?"):
            codigo = seleccion[0]
            self.datos["espacios"] = [e for e in self.datos["espacios"] if e["codigoAula"] != codigo]
            self._invalidar_plan()
            self._guardar_archivo()
            self._limpiar_espacio()
            self._refrescar_listas()

    def _crear_docente(self, registro: dict[str, Any]) -> Docente:
        docente = Docente(
            registro["cedula"], registro["nombres"], registro["apellidos"],
            registro["correoElectronico"], registro["tituloAcademico"],
        )
        for dia in registro["diasDisponibles"]:
            docente.registrarDisponibilidad(FranjaHoraria(dia, time(HORA_INICIO), time(HORA_FIN)))
        return docente

    def _crear_espacio(self, registro: dict[str, Any]) -> EspacioFisico:
        if registro["tipo"] == "Laboratorio":
            return Laboratorio(registro["codigoAula"], registro["capacidadMaxima"],
                               registro.get("equiposEspeciales", ""), registro.get("tipoLaboratorio", ""))
        return EspacioFisico(registro["codigoAula"], registro["capacidadMaxima"])

    def _generar_horario(self) -> None:
        if not self.datos["asignaturas"]:
            messagebox.showwarning("Faltan asignaturas", "Registra al menos una asignatura antes de generar el horario.")
            return
        if not self.datos["espacios"] or not self.datos["docentes"]:
            messagebox.showwarning("Faltan recursos", "Registra al menos un docente y un espacio físico.")
            return
        try:
            minimo = int(self.minimo_var.get())
            if minimo < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Mínimo inválido", "El mínimo por paralelo debe ser un entero mayor que cero.")
            return

        self._invalidar_plan()
        self._guardar_archivo()
        self._mostrar_plan_guardado()

        docentes = {d["cedula"]: self._crear_docente(d) for d in self.datos["docentes"]}
        espacios = {e["codigoAula"]: self._crear_espacio(e) for e in self.datos["espacios"]}
        secciones: list[dict[str, Any]] = []
        tareas: list[dict[str, Any]] = []
        problemas: list[str] = []

        for registro in self.datos["asignaturas"]:
            asignatura = Asignatura(registro["nombreAsignatura"], registro["horasRequeridas"], registro["requiereLaboratorio"])
            docente = docentes.get(registro["docenteCedula"])
            if docente is None:
                problemas.append(f"{asignatura.nombreAsignatura}: el docente registrado ya no existe.")
                continue

            espacios_validos = []
            for clave, espacio in espacios.items():
                if espacio.capacidadMaxima < minimo:
                    continue
                if asignatura.requiereLaboratorio():
                    if isinstance(espacio, Laboratorio) and espacio.cumpleRequisitosDeAsignatura(asignatura):
                        espacios_validos.append((clave, espacio))
                else:
                    espacios_validos.append((clave, espacio))

            if not espacios_validos:
                tipo = "laboratorio" if asignatura.requiereLaboratorio() else "aula"
                problemas.append(f"{asignatura.nombreAsignatura}: no hay {tipo} con capacidad de al menos {minimo}.")
                continue

            demanda = int(registro["demandaEstimada"])
            capacidad_maxima = max(espacio.capacidadMaxima for _, espacio in espacios_validos)
            cantidad_paralelos = math.ceil(demanda / capacidad_maxima)
            tamanos = [demanda // cantidad_paralelos] * cantidad_paralelos
            for indice in range(demanda % cantidad_paralelos):
                tamanos[indice] += 1
            if min(tamanos) < minimo:
                problemas.append(
                    f"{asignatura.nombreAsignatura}: con demanda {demanda}, capacidad {capacidad_maxima} "
                    f"y mínimo {minimo}, no se pueden formar paralelos válidos."
                )
                continue

            if not any(docente.verificarDisponibilidad(FranjaHoraria(dia, time(HORA_INICIO), time(HORA_INICIO + 1))) for dia in DIAS):
                problemas.append(f"{asignatura.nombreAsignatura}: su docente no tiene disponibilidad en días laborables.")
                continue

            for indice, cantidad in enumerate(tamanos, start=1):
                nombre_p = f"{asignatura.nombreAsignatura} - {indice}"
                
                paralelo_obj = Paralelo(nombre_p, capacidad_maxima, asignatura)
                for est_id in range(1, cantidad + 1):
                    alumno_temporal = Estudiante(
                        f"EST-{asignatura.nombreAsignatura[:3]}-{indice}-{est_id:03d}",
                        f"Estudiante {est_id}",
                        f"Paralelo {indice}",
                        f"estudiante{est_id}@uleam.edu.ec"
                    )
                    paralelo_obj.agregarEstudiante(alumno_temporal)

                seccion = {
                    "asignatura": asignatura.nombreAsignatura,
                    "nombreParalelo": paralelo_obj.nombreParalelo,
                    "numero": indice,
                    "demanda": paralelo_obj.calcularDemanda(),
                    "cupoMaximo": paralelo_obj.cupoMaximo,
                    "docenteCedula": registro["docenteCedula"],
                    "horas": asignatura.obtenerHorasTotales(),
                    "requiereLaboratorio": asignatura.requiereLaboratorio(),
                }
                secciones.append(seccion)

                for numero_hora in range(1, asignatura.obtenerHorasTotales() + 1):
                    candidatos = []
                    for dia in DIAS:
                        for hora in range(HORA_INICIO, HORA_FIN):
                            franja = FranjaHoraria(dia, time(hora), time(hora + 1))
                            if not docente.verificarDisponibilidad(franja):
                                continue
                            for codigo, espacio in espacios_validos:
                                if espacio.capacidadMaxima >= cantidad:
                                    candidatos.append((dia, hora, codigo))
                    tareas.append({
                        "seccion": seccion, "numeroHora": numero_hora,
                        "franjasCandidatas": candidatos,
                    })

        if problemas:
            messagebox.showerror("No se puede generar el horario", "Corrige estos datos y vuelve a intentarlo:\n\n• " + "\n• ".join(problemas))
            self.estado_horario.set("No se generó el horario: hay recursos o paralelos que no cumplen las restricciones.")
            return

        tareas.sort(key=lambda tarea: len(tarea["franjasCandidatas"]))
        resultado = self._asignar_bloques(tareas, espacios)
        if resultado is None:
            messagebox.showerror(
                "No se encontró una planificación",
                "No se pudieron ubicar todas las horas sin cruces. Revisa disponibilidades, número de aulas y horas requeridas.",
            )
            self.estado_horario.set("No se encontró una planificación que satisfaga todas las restricciones.")
            return

        horario = Horario("HOR-001", "Periodo actual", "Académico")
        for sesion in resultado:
            horario.agregarFranja(sesion["franja"])
        resultado.sort(key=lambda sesion: (DIAS.index(sesion["dia"]), sesion["inicio"], sesion["asignatura"], sesion["numeroParalelo"]))
        self.plan_actual = {
            "paralelos": secciones,
            "sesiones": [
                {k: v for k, v in sesion.items() if k != "franja"}
                for sesion in resultado
            ],
            "minimoEstudiantes": minimo,
            "bloqueMinutos": 60,
            "franjasSinConflicto": not self._tiene_conflicto(resultado),
        }
        self.datos["ultimoHorario"] = self.plan_actual
        self._guardar_archivo()
        self._mostrar_plan_guardado()
        self.estado_horario.set(
            f"Horario generado: {len(secciones)} paralelos, {len(resultado)} bloques de clase. "
            f"Demanda distribuida entre {minimo} y la capacidad de cada aula."
        )

    def _asignar_bloques(self, tareas: list[dict[str, Any]],
                         espacios: dict[str, EspacioFisico]) -> list[dict[str, Any]] | None:
        resultado: list[dict[str, Any]] = []
        docente_ocupado: set[tuple[str, str, int]] = set()
        paralelo_ocupado: set[tuple[str, str, int]] = set()
        nodos = 0
        limite_nodos = 250_000

        def buscar(indice: int) -> bool:
            nonlocal nodos
            nodos += 1
            if nodos > limite_nodos:
                return False
            if indice == len(tareas):
                return True
            tarea = tareas[indice]
            seccion = tarea["seccion"]
            for dia, hora, codigo in tarea["franjasCandidatas"]:
                clave_docente = (seccion["docenteCedula"], dia, hora)
                clave_paralelo = (seccion["nombreParalelo"], dia, hora)
                espacio = espacios[codigo]
                franja = FranjaHoraria(dia, time(hora), time(hora + 1))
                if clave_docente in docente_ocupado or clave_paralelo in paralelo_ocupado:
                    continue
                if not espacio.estaDisponible(franja):
                    continue
                if not espacio.reservarFranja(franja):
                    continue
                docente_ocupado.add(clave_docente)
                paralelo_ocupado.add(clave_paralelo)
                resultado.append({
                    "dia": dia,
                    "inicio": f"{hora:02d}:00",
                    "fin": f"{hora + 1:02d}:00",
                    "asignatura": seccion["asignatura"],
                    "paralelo": seccion["nombreParalelo"],
                    "numeroParalelo": seccion["numero"],
                    "estudiantes": seccion["demanda"],
                    "docente": seccion["docenteCedula"],
                    "espacio": codigo,
                    "franja": franja,
                })
                if buscar(indice + 1):
                    return True
                resultado.pop()
                docente_ocupado.remove(clave_docente)
                paralelo_ocupado.remove(clave_paralelo)
                espacio.liberarFranja(franja)
            return False

        return resultado if buscar(0) else None

    @staticmethod
    def _tiene_conflicto(sesiones: list[dict[str, Any]]) -> bool:
        ocupaciones: set[tuple[str, str, str]] = set()
        for sesion in sesiones:
            for recurso in ("docente", "espacio", "paralelo"):
                clave = (recurso, sesion[recurso] if recurso != "paralelo" else sesion["paralelo"], sesion["dia"] + sesion["inicio"])
                if clave in ocupaciones:
                    return True
                ocupaciones.add(clave)
        return False

    def _mostrar_plan_guardado(self) -> None:
        if not hasattr(self, "tree_horario"):
            return
        self.tree_horario.delete(*self.tree_horario.get_children())
        plan = self.datos.get("ultimoHorario")
        if not plan:
            return
        self.plan_actual = plan
        for sesion in plan.get("sesiones", []):
            docente = self._obtener_docente(sesion["docente"])
            nombre_docente = f"{docente['nombres']} {docente['apellidos']}" if docente else sesion["docente"]
            self.tree_horario.insert("", "end", values=(
                sesion["dia"], sesion["inicio"], sesion["fin"], sesion["asignatura"],
                sesion["paralelo"], sesion["estudiantes"], nombre_docente, sesion["espacio"],
            ))
        if plan.get("sesiones"):
            self.estado_horario.set(
                f"Horario guardado: {len(plan.get('paralelos', []))} paralelos, "
                f"{len(plan['sesiones'])} bloques; mínimo configurado: {plan.get('minimoEstudiantes', '—')} estudiantes."
            )

    def _exportar_horario(self) -> None:
        if not self.plan_actual or not self.plan_actual.get("sesiones"):
            messagebox.showinfo("Sin horario", "Genera un horario antes de exportarlo.")
            return
        archivo = CARPETA_DATOS / "horario_exportado.json"
        with archivo.open("w", encoding="utf-8") as salida:
            json.dump(self.plan_actual, salida, ensure_ascii=False, indent=2)
        messagebox.showinfo("Horario exportado", f"Se guardó el horario en:\n{archivo}")


if __name__ == "__main__":
    KhronoacApp().mainloop()