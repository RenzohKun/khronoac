from __future__ import annotations

import math
import tkinter as tk
import webbrowser
from datetime import time
from pathlib import Path
from typing import Any

from modelos.Asignatura import Asignatura
from modelos.Docente import Docente
from modelos.EspacioFisico import EspacioFisico
from modelos.Estudiante import Estudiante
from modelos.FranjaHoraria import FranjaHoraria
from modelos.Horario import Horario
from modelos.Laboratorio import Laboratorio
from modelos.Paralelo import Paralelo
from persistencia import KhronoacPersistenciaDatos
from interfaz import KhronoacInterfaz


DIAS = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")
HORA_INICIO = 7
HORA_FIN = 20


class KhronoacApp(tk.Tk):
    """Controlador principal de la aplicación Khronoac.

    Gestiona el ciclo de vida de la GUI, la persistencia en disco y
    orquesta el algoritmo de planificación horaria con los modelos POO.
    """

    def _crear_acciones_interfaz(self) -> dict[str, Any]:
        return {
            "guardar_docente": self._guardar_docente,
            "limpiar_docente": self._limpiar_docente,
            "eliminar_docente": self._eliminar_docente,
            "seleccionar_docente": self._seleccionar_docente,
            "guardar_asignatura": self._guardar_asignatura,
            "limpiar_asignatura": self._limpiar_asignatura,
            "eliminar_asignatura": self._eliminar_asignatura,
            "seleccionar_asignatura": self._seleccionar_asignatura,
            "guardar_espacio": self._guardar_espacio,
            "limpiar_espacio": self._limpiar_espacio,
            "eliminar_espacio": self._eliminar_espacio,
            "seleccionar_espacio": self._seleccionar_espacio,
            "generar_horario": self._generar_horario,
            "exportar_horario": self._exportar_horario,
        }

    def __init__(self) -> None:
        super().__init__()
        self.title("Khronoac — Planificador de Horarios Académicos")
        self.geometry("1200x780")
        self.minsize(960, 640)
        self.configure(bg="#0f1623")
        try:
            ruta_icono = Path(__file__).with_name("khronoac_icon.ico")
            if ruta_icono.exists():
                self.iconbitmap(str(ruta_icono))
        except Exception:
            pass

        self.persistencia = KhronoacPersistenciaDatos(
            Path(__file__).with_name("khronoac_datos")
        )
        self.datos: dict[str, Any] = self.persistencia.cargar_datos()
        self.plan_actual: dict[str, Any] | None = self.datos.get("ultimoHorario")
        self.docente_editando: str | None = None
        self.asignatura_editando: str | None = None
        self.espacio_editando: str | None = None

        self.interfaz = KhronoacInterfaz(self, self._crear_acciones_interfaz(), DIAS)
        self.interfaz.construir()
        self._refrescar_listas()

    def _invalidar_plan(self) -> None:
        self.plan_actual = None
        self.datos["ultimoHorario"] = None

    @staticmethod
    def _indice_por_clave(registros: list[dict[str, Any]], clave: str, valor: str) -> int | None:
        return next((i for i, registro in enumerate(registros) if registro.get(clave) == valor), None)

    def _obtener_docente(self, cedula: str) -> dict[str, Any] | None:
        return next((persona for persona in self.datos["docentes"] if persona.get("cedula") == cedula), None)

    def _refrescar_listas(self) -> None:
        self.interfaz.actualizar_listas(
            self.datos["docentes"], self.datos["asignaturas"], self.datos["espacios"]
        )
        self._mostrar_plan_guardado()

    def _guardar_docente(self) -> None:
        formulario = self.interfaz.leer_formulario_docente()
        cedula = str(formulario["cedula"]).strip()
        nombres = str(formulario["nombres"]).strip()
        apellidos = str(formulario["apellidos"]).strip()

        if not all((cedula, nombres, apellidos)):
            self.interfaz.mostrar_aviso("Datos incompletos", "Cédula, nombres y apellidos son obligatorios.")
            return

        dias = formulario.get("diasDisponibles", [])
        if not dias:
            self.interfaz.mostrar_aviso("Disponibilidad requerida", "Selecciona al menos un día disponible.")
            return

        clave_anterior = self.docente_editando
        indice_nuevo = self._indice_por_clave(self.datos["docentes"], "cedula", cedula)

        if clave_anterior is None and indice_nuevo is not None:
            self.interfaz.mostrar_aviso("Identificador duplicado", "Ya existe otro docente con esa cédula.")
            return

        docente = {
            "cedula": cedula,
            "nombres": nombres,
            "apellidos": apellidos,
            "correoElectronico": str(formulario.get("correoElectronico", "")).strip(),
            "tituloAcademico": str(formulario.get("tituloAcademico", "")).strip(),
            "diasDisponibles": dias,
        }

        if clave_anterior is None:
            self.datos["docentes"].append(docente)
        else:
            indice_anterior = self._indice_por_clave(self.datos["docentes"], "cedula", clave_anterior)
            if indice_anterior is None:
                self.interfaz.mostrar_error("Error", "No se encontró el docente que intentas editar.")
                return

            if indice_nuevo is not None and cedula != clave_anterior:
                self.interfaz.mostrar_aviso("Identificador duplicado", "Esa cédula ya pertenece a otro docente.")
                return

            self.datos["docentes"][indice_anterior] = docente

            if cedula != clave_anterior:
                for asignatura in self.datos["asignaturas"]:
                    if asignatura.get("docenteCedula") == clave_anterior:
                        asignatura["docenteCedula"] = cedula

        self._invalidar_plan()
        self.persistencia.guardar_datos(self.datos)
        self._limpiar_docente()
        self._refrescar_listas()
        self.interfaz.mostrar_informacion("Éxito", "Docente guardado correctamente.")

    def _seleccionar_docente(self, cedula: str) -> None:
        docente = self._obtener_docente(cedula)
        if docente is None:
            return
        self.docente_editando = docente["cedula"]
        self.interfaz.cargar_docente(docente)

    def _limpiar_docente(self) -> None:
        self.docente_editando = None
        self.interfaz.limpiar_docente()

    def _eliminar_docente(self) -> None:
        cedula = self.interfaz.docente_seleccionado()
        if cedula is None:
            return
        if any(asig.get("docenteCedula") == cedula for asig in self.datos["asignaturas"]):
            self.interfaz.mostrar_aviso("Docente asignado", "Reasigna o elimina las asignaturas de este docente antes de eliminarlo.")
            return
        if self.interfaz.confirmar("Confirmar", "¿Eliminar el docente seleccionado?"):
            self.datos["docentes"] = [d for d in self.datos["docentes"] if d.get("cedula") != cedula]
            self._invalidar_plan()
            self.persistencia.guardar_datos(self.datos)
            self._limpiar_docente()
            self._refrescar_listas()

    def _guardar_asignatura(self) -> None:
        formulario = self.interfaz.leer_formulario_asignatura()
        nombre = str(formulario["nombreAsignatura"]).strip()
        try:
            horas = int(formulario["horasRequeridas"])
            demanda = int(formulario["demandaEstimada"])
            if horas < 1 or demanda < 1:
                raise ValueError
        except (ValueError, KeyError):
            self.interfaz.mostrar_aviso("Revisa los valores", "Las horas semanales y la demanda deben ser enteros mayores que cero.")
            return

        cedula_docente = str(formulario.get("docenteCedula", "")).strip()
        if not nombre or not cedula_docente:
            self.interfaz.mostrar_aviso("Datos incompletos", "Escribe el nombre y selecciona un docente registrado.")
            return

        asignatura = Asignatura(nombre, horas, bool(formulario.get("requiereLaboratorio", False)))
        registro = {
            "nombreAsignatura": asignatura.nombreAsignatura,
            "horasRequeridas": asignatura.obtenerHorasTotales(),
            "requiereLaboratorio": asignatura.requiereLaboratorio(),
            "demandaEstimada": demanda,
            "docenteCedula": cedula_docente,
        }
        clave_anterior = self.asignatura_editando or nombre
        existente = self._indice_por_clave(self.datos["asignaturas"], "nombreAsignatura", clave_anterior)
        duplicada = next((a for a in self.datos["asignaturas"]
                          if a.get("nombreAsignatura", "").casefold() == nombre.casefold()
                          and a.get("nombreAsignatura") != clave_anterior), None)
        if duplicada is not None:
            self.interfaz.mostrar_aviso("Asignatura duplicada", "Ya existe otra asignatura con ese nombre.")
            return

        if existente is None:
            self.datos["asignaturas"].append(registro)
        else:
            self.datos["asignaturas"][existente] = registro

        self._invalidar_plan()
        self.persistencia.guardar_datos(self.datos)
        self._limpiar_asignatura()
        self._refrescar_listas()

    def _seleccionar_asignatura(self, nombre: str) -> None:
        asignatura = next((item for item in self.datos["asignaturas"] if item.get("nombreAsignatura") == nombre), None)
        if asignatura is None:
            return
        self.asignatura_editando = asignatura["nombreAsignatura"]
        docente = self._obtener_docente(asignatura["docenteCedula"])
        self.interfaz.cargar_asignatura(asignatura, docente)

    def _limpiar_asignatura(self) -> None:
        self.asignatura_editando = None
        self.interfaz.limpiar_asignatura()

    def _eliminar_asignatura(self) -> None:
        nombre = self.interfaz.asignatura_seleccionada()
        if nombre is not None and self.interfaz.confirmar("Confirmar", "¿Eliminar la asignatura seleccionada?"):
            self.datos["asignaturas"] = [a for a in self.datos["asignaturas"] if a.get("nombreAsignatura") != nombre]
            self._invalidar_plan()
            self.persistencia.guardar_datos(self.datos)
            self._limpiar_asignatura()
            self._refrescar_listas()

    def _guardar_espacio(self) -> None:
        formulario = self.interfaz.leer_formulario_espacio()
        codigo = str(formulario["codigoAula"]).strip()
        try:
            capacidad = int(formulario["capacidadMaxima"])
            if capacidad < 1:
                raise ValueError
        except (ValueError, KeyError):
            self.interfaz.mostrar_aviso("Capacidad inválida", "La capacidad debe ser un entero mayor que cero.")
            return

        if not codigo:
            self.interfaz.mostrar_aviso("Dato incompleto", "El código del espacio es obligatorio.")
            return

        tipo = str(formulario.get("tipo", "Aula"))
        tipo_lab = str(formulario.get("tipoLaboratorio", "")).strip()
        equipos = str(formulario.get("equiposEspeciales", "")).strip()

        if tipo == "Laboratorio" and not tipo_lab:
            self.interfaz.mostrar_aviso("Dato incompleto", "Indica el tipo de laboratorio.")
            return

        if tipo == "Laboratorio":
            espacio_objeto = Laboratorio(codigo, capacidad, equipos, tipo_lab)
            detalle_lab = {"tipoLaboratorio": espacio_objeto.tipoLaboratorio, "equiposEspeciales": espacio_objeto.equiposEspeciales}
        else:
            espacio_objeto = EspacioFisico(codigo, capacidad)
            detalle_lab = {"tipoLaboratorio": "", "equiposEspeciales": ""}

        registro = {"codigoAula": espacio_objeto.codigoAula, "capacidadMaxima": espacio_objeto.capacidadMaxima, "tipo": tipo, **detalle_lab}
        clave_anterior = self.espacio_editando or codigo
        existente = self._indice_por_clave(self.datos["espacios"], "codigoAula", clave_anterior)
        duplicado = next((e for e in self.datos["espacios"]
                          if e.get("codigoAula", "").casefold() == codigo.casefold()
                          and e.get("codigoAula") != clave_anterior), None)
        if duplicado is not None:
            self.interfaz.mostrar_aviso("Código duplicado", "Ya existe otro espacio con ese código.")
            return

        if existente is None:
            self.datos["espacios"].append(registro)
        else:
            self.datos["espacios"][existente] = registro

        self._invalidar_plan()
        self.persistencia.guardar_datos(self.datos)
        self._limpiar_espacio()
        self._refrescar_listas()

    def _seleccionar_espacio(self, codigo: str) -> None:
        espacio = next((item for item in self.datos["espacios"] if item.get("codigoAula") == codigo), None)
        if espacio is None:
            return
        self.espacio_editando = espacio["codigoAula"]
        self.interfaz.cargar_espacio(espacio)

    def _limpiar_espacio(self) -> None:
        self.espacio_editando = None
        self.interfaz.limpiar_espacio()

    def _eliminar_espacio(self) -> None:
        codigo = self.interfaz.espacio_seleccionado()
        if codigo is not None and self.interfaz.confirmar("Confirmar", "¿Eliminar el espacio seleccionado?"):
            self.datos["espacios"] = [e for e in self.datos["espacios"] if e.get("codigoAula") != codigo]
            self._invalidar_plan()
            self.persistencia.guardar_datos(self.datos)
            self._limpiar_espacio()
            self._refrescar_listas()

    def _crear_docente(self, registro: dict[str, Any]) -> Docente:
        docente = Docente(
            registro["cedula"], registro["nombres"], registro["apellidos"],
            registro["correoElectronico"], registro["tituloAcademico"],
        )
        for dia in registro.get("diasDisponibles", []):
            docente.registrarDisponibilidad(FranjaHoraria(dia, time(HORA_INICIO), time(HORA_FIN)))
        return docente

    def _crear_espacio(self, registro: dict[str, Any]) -> EspacioFisico:
        if registro.get("tipo") == "Laboratorio":
            return Laboratorio(
                registro["codigoAula"],
                registro["capacidadMaxima"],
                registro.get("equiposEspeciales", ""),
                registro.get("tipoLaboratorio", "")
            )
        return EspacioFisico(registro["codigoAula"], registro["capacidadMaxima"])

    def _generar_horario(self, silencioso: bool = False) -> bool:
        if not self.datos["asignaturas"]:
            if not silencioso:
                self.interfaz.mostrar_aviso("Faltan asignaturas", "Registra al menos una asignatura antes de generar el horario.")
            return False
        if not self.datos["espacios"] or not self.datos["docentes"]:
            if not silencioso:
                self.interfaz.mostrar_aviso("Faltan recursos", "Registra al menos un docente y un espacio físico.")
            return False

        try:
            minimo = int(self.interfaz.leer_minimo_paralelo())
            if minimo < 1:
                raise ValueError
        except Exception:
            minimo = 20

        self._invalidar_plan()
        self.persistencia.guardar_datos(self.datos)
        if not silencioso:
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
                problemas.append(f"{asignatura.nombreAsignatura}: el docente registrado no existe.")
                continue

            espacios_validos = [
                (c, e) for c, e in espacios.items()
                if e.capacidadMaxima >= minimo and e.esAptoParaAsignatura(asignatura)
            ]

            if not espacios_validos:
                tipo = "laboratorio" if asignatura.requiereLaboratorio() else "aula"
                problemas.append(f"{asignatura.nombreAsignatura}: no cuenta con {tipo} apto con capacidad >= {minimo}.")
                continue

            demanda = int(registro["demandaEstimada"])
            capacidad_maxima = max(e.capacidadMaxima for _, e in espacios_validos)
            cantidad_paralelos = math.ceil(demanda / capacidad_maxima)
            tamanos = [demanda // cantidad_paralelos] * cantidad_paralelos
            for idx in range(demanda % cantidad_paralelos):
                tamanos[idx] += 1

            if min(tamanos) < minimo:
                problemas.append(f"{asignatura.nombreAsignatura}: la demanda calculada no cumple con el cupo mínimo.")
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
                        "seccion": seccion,
                        "numeroHora": numero_hora,
                        "franjasCandidatas": candidatos,
                    })

        if problemas:
            if not silencioso:
                self.interfaz.mostrar_error("Error de Generación", "\n• " + "\n• ".join(problemas))
            return False

        tareas.sort(key=lambda t: len(t["franjasCandidatas"]))
        resultado = self._asignar_bloques(tareas, espacios)
        if resultado is None:
            if not silencioso:
                self.interfaz.mostrar_error("Sin Solución", "No fue posible ubicar todas las horas sin cruces horarias.")
            return False

        horario = Horario("HOR-001", "2026-1", "Presencial")
        mapa_docentes = {d["cedula"]: f"{d['nombres']} {d['apellidos']}" for d in self.datos.get("docentes", [])}

        for sesion in resultado:
            franja = sesion["franja"]
            setattr(franja, "asignatura", sesion["asignatura"])
            setattr(franja, "docente", mapa_docentes.get(sesion["docente"], sesion["docente"]))
            setattr(franja, "aula", sesion["espacio"])
            setattr(franja, "paralelo", sesion["paralelo"])
            horario.agregarFranja(franja)

        resultado.sort(key=lambda s: (DIAS.index(s["dia"]), s["inicio"], s["asignatura"], s["numeroParalelo"]))
        self.plan_actual = {
            "paralelos": secciones,
            "sesiones": [{k: v for k, v in s.items() if k != "franja"} for s in resultado],
            "minimoEstudiantes": minimo,
            "bloqueMinutos": 60,
            "franjasSinConflicto": not horario.validarConflictos(),
        }
        self.datos["ultimoHorario"] = self.plan_actual
        self.persistencia.guardar_datos(self.datos)

        print("\n" + horario.generarMallaHoraria() + "\n")

        nombre_materia = str(secciones[0]["asignatura"]) if secciones else "GENERAL"
        nombre_limpio = nombre_materia.replace(" ", "_").replace("/", "_")
        ruta_html = Path(__file__).with_name(f"Horario_{nombre_limpio}.html")
        horario.exportarHTML(str(ruta_html), f"Curso: {nombre_materia.upper()}")[cite: 1]

        if not silencioso:
            self._mostrar_plan_guardado()
            self.interfaz.mostrar_estado_horario(
                f"Horario generado: {len(secciones)} paralelos, {len(resultado)} bloques. "
                f"Exportado listo en HTML y JSON."
            )
        return True

    def _asignar_bloques(self, tareas: list[dict[str, Any]], espacios: dict[str, EspacioFisico]) -> list[dict[str, Any]] | None:
        resultado: list[dict[str, Any]] = []
        docente_ocupado: set[tuple[str, str, int]] = set()
        paralelo_ocupado: set[tuple[str, str, int]] = set()
        nodos = 0
        limite_nodos = 250_000

        def buscar(indice: int) -> bool:
            nonlocal nodos
            nodos += 1
            if nodos > limite_nodos or indice == len(tareas):
                return indice == len(tareas)
            tarea = tareas[indice]
            seccion = tarea["seccion"]
            for dia, hora, codigo in tarea["franjasCandidatas"]:
                clave_docente = (seccion["docenteCedula"], dia, hora)
                clave_paralelo = (seccion["nombreParalelo"], dia, hora)
                espacio = espacios[codigo]
                franja = FranjaHoraria(dia, time(hora), time(hora + 1))

                if clave_docente in docente_ocupado or clave_paralelo in paralelo_ocupado:
                    continue
                if not espacio.estaDisponible(franja) or not espacio.reservarFranja(franja):
                    continue

                docente_ocupado.add(clave_docente)
                paralelo_ocupado.add(clave_paralelo)
                resultado.append({
                    "dia": dia, "inicio": f"{hora:02d}:00", "fin": f"{hora + 1:02d}:00",
                    "asignatura": seccion["asignatura"], "paralelo": seccion["nombreParalelo"],
                    "numeroParalelo": seccion["numero"], "estudiantes": seccion["demanda"],
                    "docente": seccion["docenteCedula"], "espacio": codigo, "franja": franja,
                })
                if buscar(indice + 1):
                    return True
                resultado.pop()
                docente_ocupado.remove(clave_docente)
                paralelo_ocupado.remove(clave_paralelo)
                espacio.liberarFranja(franja)
            return False

        return resultado if buscar(0) else None

    def _mostrar_plan_guardado(self) -> None:
        self.plan_actual = self.datos.get("ultimoHorario")
        self.interfaz.mostrar_horario(self.plan_actual, self.datos["docentes"])

    def _exportar_horario(self) -> None:
        if not self.plan_actual or not self.plan_actual.get("sesiones"):
            self.interfaz.mostrar_informacion("Sin horario", "Genera un horario antes de exportarlo.")
            return

        archivo_json = self.persistencia.guardar_horario_exportado(self.plan_actual)

        horario = Horario("HOR-ULEAM", "2026-1", "Presencial")
        mapa_docentes = {d["cedula"]: f"{d['nombres']} {d['apellidos']}" for d in self.datos.get("docentes", [])}

        for sesion in self.plan_actual["sesiones"]:
            h_ini_val = int(sesion["inicio"].split(":")[0])
            h_fin_val = int(sesion["fin"].split(":")[0])
            franja = FranjaHoraria(sesion["dia"], time(h_ini_val), time(h_fin_val))

            setattr(franja, "asignatura", sesion["asignatura"])
            setattr(franja, "docente", mapa_docentes.get(sesion["docente"], sesion["docente"]))
            setattr(franja, "aula", sesion["espacio"])
            setattr(franja, "paralelo", sesion.get("paralelo", ""))

            horario.agregarFranja(franja)

        nombre_materia = str(self.plan_actual["sesiones"][0]["asignatura"]) if self.plan_actual["sesiones"] else "GENERAL"
        nombre_limpio = nombre_materia.replace(" ", "_").replace("/", "_")
        ruta_html = Path(__file__).with_name(f"Horario_{nombre_limpio}.html")

        horario.exportarHTML(str(ruta_html), f"Curso: {nombre_materia.upper()}")[cite: 1]

        contenido_html = ruta_html.read_text(encoding="utf-8")
        if "<script>window.onload" not in contenido_html:
            contenido_html = contenido_html.replace(
                "</body>",
                "<script>window.onload = function() { window.print(); };</script></body>"
            )
            ruta_html.write_text(contenido_html, encoding="utf-8")

        webbrowser.open(ruta_html.resolve().as_uri())

        self.interfaz.mostrar_informacion(
            "Horario exportado",
            f"Se abrió la malla visual en tu navegador para imprimir a PDF.\n\n• HTML: {ruta_html.name}\n• JSON: {Path(archivo_json).name}"
        )


if __name__ == "__main__":
    KhronoacApp().mainloop()