from __future__ import annotations

import math
import tkinter as tk
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
            self.iconbitmap(str(Path(__file__).with_name("khronoac_icon.ico")))
        except Exception:
            pass

        self.persistencia = KhronoacPersistenciaDatos(
            Path(__file__).with_name("khronoac_datos")
        )
        self.datos = self.persistencia.cargar_datos()
        self.plan_actual: dict[str, Any] | None = self.datos["ultimoHorario"]
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
        return next((persona for persona in self.datos["docentes"] if persona["cedula"] == cedula), None)

    def _refrescar_listas(self) -> None:
        self.interfaz.actualizar_listas(
            self.datos["docentes"], self.datos["asignaturas"], self.datos["espacios"]
        )
        self._mostrar_plan_guardado()

    def _guardar_docente(self) -> None:
        formulario = self.interfaz.leer_formulario_docente()
        cedula = formulario["cedula"].strip()
        nombres = formulario["nombres"].strip()
        apellidos = formulario["apellidos"].strip()

        if not all((cedula, nombres, apellidos)):
            self.interfaz.mostrar_aviso(
                "Datos incompletos",
                "Cédula, nombres y apellidos son obligatorios."
            )
            return

        dias = formulario["diasDisponibles"]

        if not dias:
            self.interfaz.mostrar_aviso(
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
            self.interfaz.mostrar_aviso(
                "Identificador duplicado",
                "Ya existe otro docente con esa cédula."
            )
            return

        docente = {
            "cedula": cedula,
            "nombres": nombres,
            "apellidos": apellidos,
            "correoElectronico": formulario["correoElectronico"].strip(),
            "tituloAcademico": formulario["tituloAcademico"].strip(),
            "diasDisponibles": dias,
        }

        if clave_anterior is None:
            
            self.datos["docentes"].append(docente)

        else:
            
            indice_anterior = self._indice_por_clave(
                self.datos["docentes"], "cedula", clave_anterior
            )

            if indice_anterior is None:
                self.interfaz.mostrar_error(
                    "Error",
                    "No se encontró el docente que intentas editar."
                )
                return

            # Evitar usar la cédula de otro docente.
            if indice_nuevo is not None and cedula != clave_anterior:
                self.interfaz.mostrar_aviso(
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
        self.persistencia.guardar_datos(self.datos)

        # Limpiar el formulario y salir del modo edición.
        self._limpiar_docente()
        self._refrescar_listas()

        self.interfaz.mostrar_informacion(
            "Éxito",
            "Docente guardado correctamente."
        )

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
        if any(asig["docenteCedula"] == cedula for asig in self.datos["asignaturas"]):
            self.interfaz.mostrar_aviso(
                "Docente asignado",
                "Reasigna o elimina las asignaturas de este docente antes de eliminarlo.",
            )
            return
        if self.interfaz.confirmar("Confirmar", "¿Eliminar el docente seleccionado?"):
            self.datos["docentes"] = [
                docente for docente in self.datos["docentes"]
                if docente["cedula"] != cedula
            ]
            self._invalidar_plan()
            self.persistencia.guardar_datos(self.datos)
            self._limpiar_docente()
            self._refrescar_listas()

    def _guardar_asignatura(self) -> None:
        formulario = self.interfaz.leer_formulario_asignatura()
        nombre = formulario["nombreAsignatura"].strip()
        try:
            horas, demanda = int(formulario["horasRequeridas"]), int(formulario["demandaEstimada"])
            if horas < 1 or demanda < 1:
                raise ValueError
        except ValueError:
            self.interfaz.mostrar_aviso("Revisa los valores", "Las horas semanales y la demanda deben ser enteros mayores que cero.")
            return
        cedula_docente = formulario["docenteCedula"]
        if not nombre or not cedula_docente:
            self.interfaz.mostrar_aviso("Datos incompletos", "Escribe el nombre y selecciona un docente registrado.")
            return
        asignatura = Asignatura(nombre, horas, formulario["requiereLaboratorio"])
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
        asignatura = next(
            (item for item in self.datos["asignaturas"]
             if item["nombreAsignatura"] == nombre),
            None,
        )
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
        if nombre is not None and self.interfaz.confirmar(
            "Confirmar", "¿Eliminar la asignatura seleccionada?"
        ):
            self.datos["asignaturas"] = [
                asignatura for asignatura in self.datos["asignaturas"]
                if asignatura["nombreAsignatura"] != nombre
            ]
            self._invalidar_plan()
            self.persistencia.guardar_datos(self.datos)
            self._limpiar_asignatura()
            self._refrescar_listas()

    def _guardar_espacio(self) -> None:
        formulario = self.interfaz.leer_formulario_espacio()
        codigo = formulario["codigoAula"].strip()
        try:
            capacidad = int(formulario["capacidadMaxima"])
            if capacidad < 1:
                raise ValueError
        except ValueError:
            self.interfaz.mostrar_aviso("Capacidad inválida", "La capacidad debe ser un entero mayor que cero.")
            return
        if not codigo:
            self.interfaz.mostrar_aviso("Dato incompleto", "El código del espacio es obligatorio.")
            return
        tipo = formulario["tipo"]
        if tipo == "Laboratorio" and not formulario["tipoLaboratorio"].strip():
            self.interfaz.mostrar_aviso("Dato incompleto", "Indica el tipo de laboratorio.")
            return
        if tipo == "Laboratorio":
            espacio_objeto = Laboratorio(codigo, capacidad, formulario["equiposEspeciales"].strip(), formulario["tipoLaboratorio"].strip())
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
        espacio = next(
            (item for item in self.datos["espacios"] if item["codigoAula"] == codigo),
            None,
        )
        if espacio is None:
            return
        self.espacio_editando = espacio["codigoAula"]
        self.interfaz.cargar_espacio(espacio)

    def _limpiar_espacio(self) -> None:
        self.espacio_editando = None
        self.interfaz.limpiar_espacio()

    def _eliminar_espacio(self) -> None:
        codigo = self.interfaz.espacio_seleccionado()
        if codigo is not None and self.interfaz.confirmar(
            "Confirmar", "¿Eliminar el espacio seleccionado?"
        ):
            self.datos["espacios"] = [
                espacio for espacio in self.datos["espacios"]
                if espacio["codigoAula"] != codigo
            ]
            self._invalidar_plan()
            self.persistencia.guardar_datos(self.datos)
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
            self.interfaz.mostrar_aviso("Faltan asignaturas", "Registra al menos una asignatura antes de generar el horario.")
            return
        if not self.datos["espacios"] or not self.datos["docentes"]:
            self.interfaz.mostrar_aviso("Faltan recursos", "Registra al menos un docente y un espacio físico.")
            return
        try:
            minimo = int(self.interfaz.leer_minimo_paralelo())
            if minimo < 1:
                raise ValueError
        except ValueError:
            self.interfaz.mostrar_aviso("Mínimo inválido", "El mínimo por paralelo debe ser un entero mayor que cero.")
            return

        self._invalidar_plan()
        self.persistencia.guardar_datos(self.datos)
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

                if espacio.esAptoParaAsignatura(asignatura):
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
            self.interfaz.mostrar_error("No se puede generar el horario", "Corrige estos datos y vuelve a intentarlo:\n\n• " + "\n• ".join(problemas))
            self.interfaz.mostrar_estado_horario("No se generó el horario: hay recursos o paralelos que no cumplen las restricciones.")
            return

        tareas.sort(key=lambda tarea: len(tarea["franjasCandidatas"]))
        resultado = self._asignar_bloques(tareas, espacios)
        if resultado is None:
            self.interfaz.mostrar_error(
                "No se encontró una planificación",
                "No se pudieron ubicar todas las horas sin cruces. Revisa disponibilidades, número de aulas y horas requeridas.",
            )
            self.interfaz.mostrar_estado_horario("No se encontró una planificación que satisfaga todas las restricciones.")
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
        self.persistencia.guardar_datos(self.datos)
        self._mostrar_plan_guardado()
        self.interfaz.mostrar_estado_horario(
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
        self.plan_actual = self.datos.get("ultimoHorario")
        self.interfaz.mostrar_horario(self.plan_actual, self.datos["docentes"])

    def _exportar_horario(self) -> None:
        if not self.plan_actual or not self.plan_actual.get("sesiones"):
            self.interfaz.mostrar_informacion("Sin horario", "Genera un horario antes de exportarlo.")
            return
        archivo = self.persistencia.guardar_horario_exportado(self.plan_actual)
        self.interfaz.mostrar_informacion("Horario exportado", f"Se guardó el horario en:\n{archivo}")


if __name__ == "__main__":
    KhronoacApp().mainloop()
