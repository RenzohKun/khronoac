from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable


class KhronoacInterfaz:
    def __init__(
        self,
        raiz: tk.Misc,
        acciones: dict[str, Callable[..., Any]],
        dias: tuple[str, ...],
    ) -> None:
        self.raiz = raiz
        self.acciones = acciones
        self.dias = dias
        self.docente_por_etiqueta: dict[str, str] = {}
        self.docente_dias_vars: dict[str, tk.BooleanVar] = {}

    def construir(self) -> None:
        self._configurar_estilos()
        self._construir_interfaz()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self.raiz)
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
        encabezado = ttk.Frame(self.raiz, padding=(28, 20, 28, 14))
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

        sep = tk.Frame(self.raiz, height=1, bg="#1e3054")
        sep.pack(fill="x", padx=0, pady=(2, 0))

        self.notebook = ttk.Notebook(self.raiz)
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
        for dia in self.dias:
            variable = tk.BooleanVar(value=True)
            self.docente_dias_vars[dia] = variable
            ttk.Checkbutton(dias, text=dia, variable=variable).pack(side="left", padx=4)

        acciones = ttk.Frame(formulario, style="Card.TFrame")
        acciones.grid(row=2, column=0, columnspan=5, sticky="e", pady=(8, 0))
        ttk.Button(acciones, text="  ✔  Guardar docente", style="Accent.TButton", command=self.acciones["guardar_docente"]).pack(side="left", padx=5)
        ttk.Button(acciones, text="  ✕  Limpiar", command=self.acciones["limpiar_docente"]).pack(side="left", padx=5)

        columnas = (("cedula", "Identificador", 120), ("nombre", "Docente", 220),
                    ("correo", "Correo", 220), ("titulo", "Título", 180), ("dias", "Días disponibles", 250))
        self.tree_docentes = self._crear_tree(self.tab_docentes, columnas)
        self.tree_docentes.bind("<<TreeviewSelect>>", self.__evento_seleccion_docente)
        ttk.Button(self.tab_docentes, text="  🗑  Eliminar seleccionado", style="Danger.TButton", command=self.acciones["eliminar_docente"]).pack(anchor="e", pady=(10, 2))

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
        ttk.Button(acciones, text="  ✔  Guardar asignatura", style="Accent.TButton", command=self.acciones["guardar_asignatura"]).pack(side="left", padx=5)
        ttk.Button(acciones, text="  ✕  Limpiar", command=self.acciones["limpiar_asignatura"]).pack(side="left", padx=5)

        columnas = (("nombre", "Asignatura", 220), ("horas", "Horas/semana", 110),
                    ("demanda", "Demanda estimada", 140), ("docente", "Docente", 220), ("lab", "Laboratorio", 110))
        self.tree_asignaturas = self._crear_tree(self.tab_asignaturas, columnas)
        self.tree_asignaturas.bind("<<TreeviewSelect>>", self.__evento_seleccion_asignatura)
        ttk.Button(self.tab_asignaturas, text="  🗑  Eliminar seleccionado", style="Danger.TButton", command=self.acciones["eliminar_asignatura"]).pack(anchor="e", pady=(10, 2))

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
        ttk.Button(acciones, text="  ✔  Guardar espacio", style="Accent.TButton", command=self.acciones["guardar_espacio"]).pack(side="left", padx=5)
        ttk.Button(acciones, text="  ✕  Limpiar", command=self.acciones["limpiar_espacio"]).pack(side="left", padx=5)

        columnas = (("codigo", "Código", 150), ("tipo", "Tipo", 140),
                    ("capacidad", "Capacidad", 110), ("detalle", "Equipamiento / tipo", 360))
        self.tree_espacios = self._crear_tree(self.tab_espacios, columnas)
        self.tree_espacios.bind("<<TreeviewSelect>>", self.__evento_seleccion_espacio)
        ttk.Button(self.tab_espacios, text="  🗑  Eliminar seleccionado", style="Danger.TButton", command=self.acciones["eliminar_espacio"]).pack(anchor="e", pady=(10, 2))

    def _construir_tab_horario(self) -> None:
        controles = ttk.Frame(self.tab_horario, style="Card.TFrame", padding=12)
        controles.pack(fill="x", pady=(0, 12))
        ttk.Label(controles, text="Mínimo de estudiantes por paralelo:", style="Card.TLabel").pack(side="left")
        self.minimo_var = tk.StringVar(value="10")
        ttk.Spinbox(controles, from_=1, to=200, textvariable=self.minimo_var, width=7).pack(side="left", padx=10)
        ttk.Button(controles, text="  ▶  Generar horario", style="Accent.TButton", command=self.acciones["generar_horario"]).pack(side="left", padx=8)
        ttk.Button(controles, text="  ↓  Exportar JSON", command=self.acciones["exportar_horario"]).pack(side="left", padx=6)
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

    def leer_formulario_docente(self) -> dict[str, Any]:
        return {
            "cedula": self.doc_cedula.get(),
            "nombres": self.doc_nombres.get(),
            "apellidos": self.doc_apellidos.get(),
            "correoElectronico": self.doc_correo.get(),
            "tituloAcademico": self.doc_titulo.get(),
            "diasDisponibles": [
                dia for dia, variable in self.docente_dias_vars.items() if variable.get()
            ],
        }

    def leer_formulario_asignatura(self) -> dict[str, Any]:
        return {
            "nombreAsignatura": self.asig_nombre.get(),
            "horasRequeridas": self.asig_horas.get(),
            "demandaEstimada": self.asig_demanda.get(),
            "docenteCedula": self.docente_por_etiqueta.get(self.asig_docente.get()),
            "requiereLaboratorio": self.asig_laboratorio.get(),
        }

    def leer_formulario_espacio(self) -> dict[str, Any]:
        return {
            "codigoAula": self.esp_codigo.get(),
            "capacidadMaxima": self.esp_capacidad.get(),
            "tipo": self.esp_tipo.get(),
            "tipoLaboratorio": self.esp_tipo_lab.get(),
            "equiposEspeciales": self.esp_equipos.get(),
        }

    def leer_minimo_paralelo(self) -> str:
        return self.minimo_var.get()

    def docente_seleccionado(self) -> str | None:
        return self.__id_seleccionado(self.tree_docentes)

    def asignatura_seleccionada(self) -> str | None:
        return self.__id_seleccionado(self.tree_asignaturas)

    def espacio_seleccionado(self) -> str | None:
        return self.__id_seleccionado(self.tree_espacios)

    @staticmethod
    def __id_seleccionado(tabla: ttk.Treeview) -> str | None:
        seleccion = tabla.selection()
        return seleccion[0] if seleccion else None

    def cargar_docente(self, docente: dict[str, Any]) -> None:
        self.doc_cedula.set(docente["cedula"])
        self.doc_nombres.set(docente["nombres"])
        self.doc_apellidos.set(docente["apellidos"])
        self.doc_correo.set(docente["correoElectronico"])
        self.doc_titulo.set(docente["tituloAcademico"])
        for dia, variable in self.docente_dias_vars.items():
            variable.set(dia in docente["diasDisponibles"])

    def cargar_asignatura(
        self, asignatura: dict[str, Any], docente: dict[str, Any] | None
    ) -> None:
        self.asig_nombre.set(asignatura["nombreAsignatura"])
        self.asig_horas.set(str(asignatura["horasRequeridas"]))
        self.asig_demanda.set(str(asignatura["demandaEstimada"]))
        self.asig_laboratorio.set(asignatura["requiereLaboratorio"])
        self.asig_docente.set(self.__etiqueta_docente(docente) if docente else "")

    def cargar_espacio(self, espacio: dict[str, Any]) -> None:
        self.esp_codigo.set(espacio["codigoAula"])
        self.esp_capacidad.set(str(espacio["capacidadMaxima"]))
        self.esp_tipo.set(espacio["tipo"])
        self.esp_tipo_lab.set(espacio.get("tipoLaboratorio", ""))
        self.esp_equipos.set(espacio.get("equiposEspeciales", ""))

    def limpiar_docente(self) -> None:
        for variable in (
            self.doc_cedula, self.doc_nombres, self.doc_apellidos,
            self.doc_correo, self.doc_titulo,
        ):
            variable.set("")
        for variable in self.docente_dias_vars.values():
            variable.set(True)
        self.tree_docentes.selection_remove(self.tree_docentes.selection())

    def limpiar_asignatura(self) -> None:
        self.asig_nombre.set("")
        self.asig_horas.set("3")
        self.asig_demanda.set("30")
        self.asig_laboratorio.set(False)
        docentes = list(self.docente_por_etiqueta)
        self.asig_docente.set(docentes[0] if docentes else "")
        self.tree_asignaturas.selection_remove(self.tree_asignaturas.selection())

    def limpiar_espacio(self) -> None:
        self.esp_codigo.set("")
        self.esp_capacidad.set("30")
        self.esp_tipo.set("Aula")
        self.esp_tipo_lab.set("")
        self.esp_equipos.set("")
        self.tree_espacios.selection_remove(self.tree_espacios.selection())

    def actualizar_listas(
        self,
        docentes: list[dict[str, Any]],
        asignaturas: list[dict[str, Any]],
        espacios: list[dict[str, Any]],
    ) -> None:
        for tabla in (self.tree_docentes, self.tree_asignaturas, self.tree_espacios):
            tabla.delete(*tabla.get_children())

        for docente in docentes:
            self.tree_docentes.insert(
                "", "end", iid=docente["cedula"], values=(
                    docente["cedula"],
                    f"{docente['nombres']} {docente['apellidos']}",
                    docente["correoElectronico"],
                    docente["tituloAcademico"],
                    ", ".join(docente["diasDisponibles"]),
                )
            )

        self.docente_por_etiqueta = {
            self.__etiqueta_docente(docente): docente["cedula"] for docente in docentes
        }
        valores_docentes = list(self.docente_por_etiqueta)
        self.combo_docente.configure(values=valores_docentes)
        if self.asig_docente.get() not in valores_docentes:
            self.asig_docente.set(valores_docentes[0] if valores_docentes else "")

        docentes_por_cedula = {docente["cedula"]: docente for docente in docentes}
        for asignatura in asignaturas:
            docente = docentes_por_cedula.get(asignatura["docenteCedula"])
            nombre_docente = self.__etiqueta_docente(docente) if docente else "Sin docente"
            self.tree_asignaturas.insert(
                "", "end", iid=asignatura["nombreAsignatura"], values=(
                    asignatura["nombreAsignatura"],
                    asignatura["horasRequeridas"],
                    asignatura["demandaEstimada"],
                    nombre_docente,
                    "Sí" if asignatura["requiereLaboratorio"] else "No",
                )
            )

        for espacio in espacios:
            detalle = (
                f"{espacio.get('tipoLaboratorio', '')} | {espacio.get('equiposEspeciales', '')}"
                if espacio["tipo"] == "Laboratorio" else "Aula general"
            )
            self.tree_espacios.insert(
                "", "end", iid=espacio["codigoAula"], values=(
                    espacio["codigoAula"], espacio["tipo"],
                    espacio["capacidadMaxima"], detalle,
                )
            )

    def mostrar_horario(
        self,
        plan: dict[str, Any] | None,
        docentes: list[dict[str, Any]],
    ) -> None:
        self.tree_horario.delete(*self.tree_horario.get_children())
        if not plan:
            return
        docentes_por_cedula = {docente["cedula"]: docente for docente in docentes}
        for sesion in plan.get("sesiones", []):
            docente = docentes_por_cedula.get(sesion["docente"])
            nombre_docente = (
                f"{docente['nombres']} {docente['apellidos']}"
                if docente else sesion["docente"]
            )
            self.tree_horario.insert(
                "", "end", values=(
                    sesion["dia"], sesion["inicio"], sesion["fin"],
                    sesion["asignatura"], sesion["paralelo"],
                    sesion["estudiantes"], nombre_docente, sesion["espacio"],
                )
            )
        if plan.get("sesiones"):
            self.mostrar_estado_horario(
                f"Horario guardado: {len(plan.get('paralelos', []))} paralelos, "
                f"{len(plan['sesiones'])} bloques; mínimo configurado: "
                f"{plan.get('minimoEstudiantes', '—')} estudiantes."
            )

    def mostrar_estado_horario(self, texto: str) -> None:
        self.estado_horario.set(texto)

    @staticmethod
    def mostrar_aviso(titulo: str, texto: str) -> None:
        messagebox.showwarning(titulo, texto)

    @staticmethod
    def mostrar_error(titulo: str, texto: str) -> None:
        messagebox.showerror(titulo, texto)

    @staticmethod
    def mostrar_informacion(titulo: str, texto: str) -> None:
        messagebox.showinfo(titulo, texto)

    @staticmethod
    def confirmar(titulo: str, texto: str) -> bool:
        return messagebox.askyesno(titulo, texto)

    @staticmethod
    def __etiqueta_docente(docente: dict[str, Any] | None) -> str:
        if docente is None:
            return ""
        return f"{docente['cedula']} — {docente['nombres']} {docente['apellidos']}"

    def __evento_seleccion_docente(self, _evento: tk.Event) -> None:
        seleccionado = self.docente_seleccionado()
        if seleccionado is not None:
            self.acciones["seleccionar_docente"](seleccionado)

    def __evento_seleccion_asignatura(self, _evento: tk.Event) -> None:
        seleccionado = self.asignatura_seleccionada()
        if seleccionado is not None:
            self.acciones["seleccionar_asignatura"](seleccionado)

    def __evento_seleccion_espacio(self, _evento: tk.Event) -> None:
        seleccionado = self.espacio_seleccionado()
        if seleccionado is not None:
            self.acciones["seleccionar_espacio"](seleccionado)
