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

       
        BG          = "#0f1623"   
        CARD        = "#1a2233"   
        CARD_BORDER = "#243047"   
        FG          = "#e8edf5"   
        FG_MUTED    = "#7a8faa"   
        ACCENT      = "#3b82f6"   
        ACCENT_HOV  = "#2563eb"   
        ACCENT2     = "#6366f1"   
        HEADING_FG  = "#c7d8f0"   
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
      
        encabezado = tk.Frame(self.raiz, bg="#0a1120", pady=0)
        encabezado.pack(fill="x")

   
        tk.Frame(encabezado, height=3, bg="#3b82f6").pack(fill="x")

        inner = tk.Frame(encabezado, bg="#0a1120")
        inner.pack(fill="x", padx=28, pady=(14, 14))

        fila_titulo = tk.Frame(inner, bg="#0a1120")
        fila_titulo.pack(fill="x")

        tk.Label(fila_titulo, text="🗓", font=("Segoe UI", 20),
                 bg="#0a1120", fg="#3b82f6").pack(side="left")
        tk.Label(fila_titulo, text=" Khronoac", font=("Segoe UI", 20, "bold"),
                 bg="#0a1120", fg="#e8edf5").pack(side="left")
        tk.Label(fila_titulo, text=" v1.0", font=("Segoe UI", 9, "bold"),
                 bg="#0a1120", fg="#3b82f6").pack(side="left", pady=(6, 0))

        tk.Label(inner,
                 text="Gestión de recursos académicos  ·  Generación automática de horarios sin conflictos",
                 font=("Segoe UI", 9), bg="#0a1120", fg="#4a6080").pack(anchor="w", pady=(3, 0))


        tk.Frame(self.raiz, height=1, bg="#1e3054").pack(fill="x")

   
        area_principal = ttk.Frame(self.raiz)
        area_principal.pack(fill="both", expand=True)


        self._sidebar = tk.Frame(area_principal, bg="#0d1420", width=210)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        tk.Frame(area_principal, width=1, bg="#1e3054").pack(side="left", fill="y")

        self._contenedor = ttk.Frame(area_principal, padding=(24, 16, 24, 16))
        self._contenedor.pack(side="left", fill="both", expand=True)


        self.tab_docentes    = ttk.Frame(self._contenedor, padding=4)
        self.tab_asignaturas = ttk.Frame(self._contenedor, padding=4)
        self.tab_espacios    = ttk.Frame(self._contenedor, padding=4)
        self.tab_horario     = ttk.Frame(self._contenedor, padding=4)

        self._construir_tab_docentes()
        self._construir_tab_asignaturas()
        self._construir_tab_espacios()
        self._construir_tab_horario()

        
        self._btn_sidebar: dict[str, tk.Button] = {}
        self._frame_activo: ttk.Frame | None = None

        tk.Frame(self._sidebar, bg="#0d1420", height=20).pack()
        tk.Label(self._sidebar, text="MENÚ", font=("Segoe UI", 7, "bold"),
                 bg="#0d1420", fg="#2d3f5a").pack(anchor="w", padx=20, pady=(0, 6))

        secciones = [
            ("👤", "Docentes",          self.tab_docentes),
            ("📚", "Asignaturas",        self.tab_asignaturas),
            ("🏫", "Aulas y Labs",       self.tab_espacios),
            ("🗓", "Planificar Horario", self.tab_horario),
        ]

        for icono, etiqueta, frame in secciones:
            contenedor_btn = tk.Frame(self._sidebar, bg="#0d1420")
            contenedor_btn.pack(fill="x", pady=1)

            indicador = tk.Frame(contenedor_btn, width=3, bg="#0d1420")
            indicador.pack(side="left", fill="y")

            cuerpo = tk.Frame(contenedor_btn, bg="#0d1420")
            cuerpo.pack(side="left", fill="x", expand=True)

            lbl_icono = tk.Label(cuerpo, text=icono, font=("Segoe UI", 13),
                                 bg="#0d1420", fg="#4a6080")
            lbl_icono.pack(side="left", padx=(14, 6), pady=10)

            lbl_texto = tk.Label(cuerpo, text=etiqueta, font=("Segoe UI", 10, "bold"),
                                 bg="#0d1420", fg="#4a6080", anchor="w")
            lbl_texto.pack(side="left", fill="x", expand=True)

            clave = etiqueta

            def _activar(f=frame, k=clave, ind=indicador,
                         li=lbl_icono, lt=lbl_texto, cb=cuerpo):
                self._cambiar_seccion(k, f, ind, li, lt, cb)

            for widget in (contenedor_btn, cuerpo, lbl_icono, lbl_texto):
                widget.bind("<Button-1>", lambda _e, fn=_activar: fn())
                widget.config(cursor="hand2")

            self._btn_sidebar[clave] = (indicador, lbl_icono, lbl_texto, cuerpo, frame)

       
        tk.Frame(self._sidebar, bg="#1a2640", height=1).pack(fill="x", padx=16, pady=12)
        tk.Label(self._sidebar, text="Khronoac v1.0", font=("Segoe UI", 7),
                 bg="#0d1420", fg="#2d3f5a").pack(anchor="w", padx=20)

        
        primer_clave = list(self._btn_sidebar)[0]
        primer_datos = self._btn_sidebar[primer_clave]
        self._cambiar_seccion(primer_clave, primer_datos[4],
                              primer_datos[0], primer_datos[1],
                              primer_datos[2], primer_datos[3])

    def _cambiar_seccion(self, clave_activa: str, frame: ttk.Frame,
                         indicador: tk.Frame, lbl_icono: tk.Label,
                         lbl_texto: tk.Label, cuerpo: tk.Frame) -> None:
        """Oculta la sección actual y muestra la seleccionada."""
        if self._frame_activo is not None:
            self._frame_activo.pack_forget()

       
        for clave, (ind, li, lt, cb, _) in self._btn_sidebar.items():
            ind.config(bg="#0d1420")
            li.config(bg="#0d1420", fg="#4a6080")
            lt.config(bg="#0d1420", fg="#4a6080")
            cb.config(bg="#0d1420")
            for w in cb.winfo_children():
                try:
                    w.config(bg="#0d1420")
                except Exception:
                    pass

     
        indicador.config(bg="#3b82f6")
        lbl_icono.config(bg="#162032", fg="#93c5fd")
        lbl_texto.config(bg="#162032", fg="#ffffff")
        cuerpo.config(bg="#162032")

        frame.pack(fill="both", expand=True)
        self._frame_activo = frame

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
    def _seccion_header(parent: tk.Widget, icono: str, titulo: str, subtitulo: str = "") -> None:
        """Dibuja un encabezado de sección con icono, título y línea decorativa."""
        fila = tk.Frame(parent, bg="#0f1623")
        fila.pack(fill="x", pady=(0, 2))
        tk.Label(fila, text=icono, font=("Segoe UI", 16), bg="#0f1623", fg="#3b82f6").pack(side="left")
        bloque_txt = tk.Frame(fila, bg="#0f1623")
        bloque_txt.pack(side="left", padx=(8, 0))
        tk.Label(bloque_txt, text=titulo, font=("Segoe UI", 13, "bold"),
                 bg="#0f1623", fg="#e8edf5").pack(anchor="w")
        if subtitulo:
            tk.Label(bloque_txt, text=subtitulo, font=("Segoe UI", 8),
                     bg="#0f1623", fg="#7a8faa").pack(anchor="w")
        tk.Frame(parent, height=1, bg="#243047").pack(fill="x", pady=(6, 12))

    @staticmethod
    def _campo(parent: tk.Widget, titulo: str, variable: tk.StringVar,
               fila: int, columna: int, ancho: int = 25) -> ttk.Entry:
        """Campo de texto con etiqueta flotante sobre fondo Card."""
        bloque = tk.Frame(parent, bg="#1a2233")
        bloque.grid(row=fila, column=columna, padx=(0, 10), pady=(0, 8), sticky="ew")
        tk.Label(bloque, text=titulo, font=("Segoe UI", 8), bg="#1a2233", fg="#7a8faa").pack(anchor="w", pady=(0, 2))
        entrada = ttk.Entry(bloque, textvariable=variable, width=ancho)
        entrada.pack(fill="x")
        return entrada

    def _dia_toggle(self, parent: tk.Frame, dia: str) -> tk.Button:
        """Botón toggle para seleccionar un día de la semana."""
        var = tk.BooleanVar(value=True)
        self.docente_dias_vars[dia] = var

        ACTIVO   = ("#1e3a5f", "#3b82f6", "#93c5fd")   
        INACTIVO = ("#151e2d", "#243047", "#4a5568")

        btn = tk.Button(
            parent,
            text=dia[:3],
            width=5,
            font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0,
            cursor="hand2",
        )

        def _actualizar():
            estado = var.get()
            bg, _, fg = ACTIVO if estado else INACTIVO
            btn.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)

        def _toggle():
            var.set(not var.get())
            _actualizar()

        btn.config(command=_toggle)
        _actualizar()
        return btn

   

    def _construir_tab_docentes(self) -> None:
        self._seccion_header(
            self.tab_docentes, "👤", "Gestión de Docentes",
            "Registra, edita y elimina los docentes del período académico"
        )

       
        card = tk.Frame(self.tab_docentes, bg="#1a2233", padx=16, pady=14)
        card.pack(fill="x", pady=(0, 10))
        tk.Frame(card, height=2, bg="#3b82f6").pack(fill="x", pady=(0, 12))  

        self.doc_cedula    = tk.StringVar()
        self.doc_nombres   = tk.StringVar()
        self.doc_apellidos = tk.StringVar()
        self.doc_correo    = tk.StringVar()
        self.doc_titulo    = tk.StringVar()

        grid = tk.Frame(card, bg="#1a2233")
        grid.pack(fill="x")
        for col in range(5):
            grid.columnconfigure(col, weight=1)

        self._campo(grid, "Cédula / identificador", self.doc_cedula,    0, 0)
        self._campo(grid, "Nombres",                self.doc_nombres,   0, 1)
        self._campo(grid, "Apellidos",              self.doc_apellidos, 0, 2)
        self._campo(grid, "Correo electrónico",     self.doc_correo,    0, 3)
        self._campo(grid, "Título académico",       self.doc_titulo,    0, 4)

       
        fila_dias = tk.Frame(card, bg="#1a2233")
        fila_dias.pack(fill="x", pady=(4, 0))
        tk.Label(fila_dias, text="Disponibilidad semanal  (07:00 – 20:00)",
                 font=("Segoe UI", 8), bg="#1a2233", fg="#7a8faa").pack(side="left", padx=(0, 14))
        for dia in self.dias:
            self._dia_toggle(fila_dias, dia).pack(side="left", padx=3)

       
        fila_btn = tk.Frame(card, bg="#1a2233")
        fila_btn.pack(fill="x", pady=(12, 0))
        tk.Frame(fila_btn, bg="#1a2233").pack(side="left", expand=True)   
        ttk.Button(fila_btn, text="  ✔  Guardar docente", style="Accent.TButton",
                   command=self.acciones["guardar_docente"]).pack(side="left", padx=(0, 6))
        ttk.Button(fila_btn, text="  ✕  Limpiar",
                   command=self.acciones["limpiar_docente"]).pack(side="left")

      
        fila_tabla = tk.Frame(self.tab_docentes, bg="#0f1623")
        fila_tabla.pack(fill="x", pady=(4, 4))
        tk.Label(fila_tabla, text="Docentes registrados", font=("Segoe UI", 9, "bold"),
                 bg="#0f1623", fg="#c7d8f0").pack(side="left")
        ttk.Button(fila_tabla, text="  🗑  Eliminar seleccionado", style="Danger.TButton",
                   command=self.acciones["eliminar_docente"]).pack(side="right")

        columnas = (
            ("cedula",  "Identificador",   120),
            ("nombre",  "Docente",         220),
            ("correo",  "Correo",          220),
            ("titulo",  "Título",          180),
            ("dias",    "Días disponibles",250),
        )
        self.tree_docentes = self._crear_tree(self.tab_docentes, columnas)
        self.tree_docentes.bind("<<TreeviewSelect>>", self.__evento_seleccion_docente)

    def _construir_tab_asignaturas(self) -> None:
        self._seccion_header(
            self.tab_asignaturas, "📚", "Gestión de Asignaturas",
            "Vincula asignaturas con docentes y configura su demanda"
        )

        card = tk.Frame(self.tab_asignaturas, bg="#1a2233", padx=16, pady=14)
        card.pack(fill="x", pady=(0, 10))
        tk.Frame(card, height=2, bg="#6366f1").pack(fill="x", pady=(0, 12))

        self.asig_nombre      = tk.StringVar()
        self.asig_horas       = tk.StringVar(value="3")
        self.asig_demanda     = tk.StringVar(value="30")
        self.asig_docente     = tk.StringVar()
        self.asig_laboratorio = tk.BooleanVar()

        grid = tk.Frame(card, bg="#1a2233")
        grid.pack(fill="x")
        for col in range(4):
            grid.columnconfigure(col, weight=1)

        self._campo(grid, "Nombre de la asignatura",          self.asig_nombre,  0, 0)
        self._campo(grid, "Horas por semana",                 self.asig_horas,   0, 1)
        self._campo(grid, "Demanda estimada de estudiantes",  self.asig_demanda, 0, 2)

        bloque_doc = tk.Frame(grid, bg="#1a2233")
        bloque_doc.grid(row=0, column=3, padx=(0, 0), pady=(0, 8), sticky="ew")
        tk.Label(bloque_doc, text="Docente responsable", font=("Segoe UI", 8),
                 bg="#1a2233", fg="#7a8faa").pack(anchor="w", pady=(0, 2))
        self.combo_docente = ttk.Combobox(bloque_doc, textvariable=self.asig_docente, state="readonly")
        self.combo_docente.pack(fill="x")

        fila_lab = tk.Frame(card, bg="#1a2233")
        fila_lab.pack(fill="x", pady=(2, 0))

      
        lab_var  = self.asig_laboratorio
        lab_lbl  = tk.Label(fila_lab, text="⬜  Requiere laboratorio", font=("Segoe UI", 9),
                            bg="#1a2233", fg="#7a8faa", cursor="hand2")
        lab_lbl.pack(side="left")

        def _toggle_lab(_=None):
            lab_var.set(not lab_var.get())
            lab_lbl.config(
                text=("☑  Requiere laboratorio" if lab_var.get() else "⬜  Requiere laboratorio"),
                fg=("#3b82f6" if lab_var.get() else "#7a8faa"),
            )
        lab_lbl.bind("<Button-1>", _toggle_lab)

        fila_btn = tk.Frame(card, bg="#1a2233")
        fila_btn.pack(fill="x", pady=(12, 0))
        tk.Frame(fila_btn, bg="#1a2233").pack(side="left", expand=True)
        ttk.Button(fila_btn, text="  ✔  Guardar asignatura", style="Accent.TButton",
                   command=self.acciones["guardar_asignatura"]).pack(side="left", padx=(0, 6))
        ttk.Button(fila_btn, text="  ✕  Limpiar",
                   command=self.acciones["limpiar_asignatura"]).pack(side="left")

        fila_tabla = tk.Frame(self.tab_asignaturas, bg="#0f1623")
        fila_tabla.pack(fill="x", pady=(4, 4))
        tk.Label(fila_tabla, text="Asignaturas registradas", font=("Segoe UI", 9, "bold"),
                 bg="#0f1623", fg="#c7d8f0").pack(side="left")
        ttk.Button(fila_tabla, text="  🗑  Eliminar seleccionado", style="Danger.TButton",
                   command=self.acciones["eliminar_asignatura"]).pack(side="right")

        columnas = (
            ("nombre",  "Asignatura",        220),
            ("horas",   "Horas/semana",       110),
            ("demanda", "Demanda estimada",   140),
            ("docente", "Docente",            220),
            ("lab",     "Laboratorio",        110),
        )
        self.tree_asignaturas = self._crear_tree(self.tab_asignaturas, columnas)
        self.tree_asignaturas.bind("<<TreeviewSelect>>", self.__evento_seleccion_asignatura)

    def _construir_tab_espacios(self) -> None:
        self._seccion_header(
            self.tab_espacios, "🏫", "Aulas y Laboratorios",
            "Administra los espacios físicos disponibles y su capacidad"
        )

        card = tk.Frame(self.tab_espacios, bg="#1a2233", padx=16, pady=14)
        card.pack(fill="x", pady=(0, 10))
        tk.Frame(card, height=2, bg="#10b981").pack(fill="x", pady=(0, 12))

        self.esp_codigo    = tk.StringVar()
        self.esp_capacidad = tk.StringVar(value="30")
        self.esp_tipo      = tk.StringVar(value="Aula")
        self.esp_tipo_lab  = tk.StringVar()
        self.esp_equipos   = tk.StringVar()

        grid = tk.Frame(card, bg="#1a2233")
        grid.pack(fill="x")
        for col in range(4):
            grid.columnconfigure(col, weight=1)

        self._campo(grid, "Código del espacio",  self.esp_codigo,    0, 0)
        self._campo(grid, "Capacidad máxima",    self.esp_capacidad, 0, 1)

        bloque_tipo = tk.Frame(grid, bg="#1a2233")
        bloque_tipo.grid(row=0, column=2, padx=(0, 10), pady=(0, 8), sticky="ew")
        tk.Label(bloque_tipo, text="Tipo", font=("Segoe UI", 8),
                 bg="#1a2233", fg="#7a8faa").pack(anchor="w", pady=(0, 2))
        ttk.Combobox(bloque_tipo, textvariable=self.esp_tipo,
                     values=("Aula", "Laboratorio"), state="readonly").pack(fill="x")

        self._campo(grid, "Tipo de laboratorio", self.esp_tipo_lab, 0, 3)
        self._campo(grid, "Equipos especiales",  self.esp_equipos,  1, 0)

        tk.Label(grid, text="ℹ  Los campos de laboratorio solo aplican cuando el tipo es 'Laboratorio'.",
                 font=("Segoe UI", 8), bg="#1a2233", fg="#4a5568").grid(
                     row=1, column=1, columnspan=2, sticky="w", pady=(4, 0))

        fila_btn = tk.Frame(card, bg="#1a2233")
        fila_btn.pack(fill="x", pady=(12, 0))
        tk.Frame(fila_btn, bg="#1a2233").pack(side="left", expand=True)
        ttk.Button(fila_btn, text="  ✔  Guardar espacio", style="Accent.TButton",
                   command=self.acciones["guardar_espacio"]).pack(side="left", padx=(0, 6))
        ttk.Button(fila_btn, text="  ✕  Limpiar",
                   command=self.acciones["limpiar_espacio"]).pack(side="left")

        fila_tabla = tk.Frame(self.tab_espacios, bg="#0f1623")
        fila_tabla.pack(fill="x", pady=(4, 4))
        tk.Label(fila_tabla, text="Espacios registrados", font=("Segoe UI", 9, "bold"),
                 bg="#0f1623", fg="#c7d8f0").pack(side="left")
        ttk.Button(fila_tabla, text="  🗑  Eliminar seleccionado", style="Danger.TButton",
                   command=self.acciones["eliminar_espacio"]).pack(side="right")

        columnas = (
            ("codigo",   "Código",              150),
            ("tipo",     "Tipo",                140),
            ("capacidad","Capacidad",            110),
            ("detalle",  "Equipamiento / tipo",  360),
        )
        self.tree_espacios = self._crear_tree(self.tab_espacios, columnas)
        self.tree_espacios.bind("<<TreeviewSelect>>", self.__evento_seleccion_espacio)

    def _construir_tab_horario(self) -> None:
        self._seccion_header(
            self.tab_horario, "🗓", "Planificador de Horarios",
            "Genera automáticamente el horario sin conflictos de docente, aula o paralelo"
        )

        
        card = tk.Frame(self.tab_horario, bg="#1a2233", padx=16, pady=14)
        card.pack(fill="x", pady=(0, 10))
        tk.Frame(card, height=2, bg="#f59e0b").pack(fill="x", pady=(0, 12))

        fila_ctrl = tk.Frame(card, bg="#1a2233")
        fila_ctrl.pack(fill="x")

        blq_min = tk.Frame(fila_ctrl, bg="#1a2233")
        blq_min.pack(side="left", padx=(0, 20))
        tk.Label(blq_min, text="Mínimo de estudiantes por paralelo",
                 font=("Segoe UI", 8), bg="#1a2233", fg="#7a8faa").pack(anchor="w")
        self.minimo_var = tk.StringVar(value="10")
        ttk.Spinbox(blq_min, from_=1, to=200, textvariable=self.minimo_var, width=8).pack(anchor="w", pady=(2, 0))

        sep_v = tk.Frame(fila_ctrl, width=1, bg="#243047")
        sep_v.pack(side="left", fill="y", padx=(0, 20))

        ttk.Button(fila_ctrl, text="  ▶  Generar horario", style="Accent.TButton",
                   command=self.acciones["generar_horario"]).pack(side="left", padx=(0, 8))
        ttk.Button(fila_ctrl, text="  ↓  Exportar JSON",
                   command=self.acciones["exportar_horario"]).pack(side="left")

        
        fila_tabla = tk.Frame(self.tab_horario, bg="#0f1623")
        fila_tabla.pack(fill="x", pady=(4, 4))
        tk.Label(fila_tabla, text="Horario generado", font=("Segoe UI", 9, "bold"),
                 bg="#0f1623", fg="#c7d8f0").pack(side="left")

        columnas = (
            ("dia",        "Día",                100),
            ("inicio",     "Inicio",              75),
            ("fin",        "Fin",                 75),
            ("asignatura", "Asignatura",          180),
            ("paralelo",   "Paralelo / grupo",    230),
            ("demanda",    "Estudiantes",          90),
            ("docente",    "Docente",             180),
            ("espacio",    "Aula / laboratorio",  150),
        )
        self.tree_horario = self._crear_tree(self.tab_horario, columnas)

        self.estado_horario = tk.StringVar(value="Registra docentes, asignaturas y espacios para comenzar.")
        tk.Label(self.tab_horario, textvariable=self.estado_horario,
                 font=("Segoe UI", 8), bg="#0f1623", fg="#7a8faa",
                 wraplength=900, justify="left").pack(anchor="w", pady=(8, 0))

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
