from __future__ import annotations
import tkinter as tk
from pathlib import Path
from typing import Any
from gestion import GestorAsignaturas, GestorDocentes, GestorEspacios
from persistencia      import KhronoacPersistenciaDatos
from interfaz          import KhronoacInterfaz
from planificacion import (
    DatosPlanificacionInvalidos,
    ServicioPlanificacionHorario,
    SinPlanificacionDisponible,
)


DIAS       = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")
HORA_INICIO = 7
HORA_FIN    = 20


class KhronoacApp(tk.Tk):
    """Controlador principal de Khronoac.

    Orquesta la interfaz gráfica, la capa de persistencia y la lógica
    de planificación de horarios académicos.
    """

   

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
        self.servicioPlanificacion = ServicioPlanificacionHorario(
            DIAS, HORA_INICIO, HORA_FIN
        )
        self.datos                             = self.persistencia.cargarDatos()
        self.plan_actual: dict[str, Any] | None = self.datos["ultimoHorario"]

        self.interfaz = KhronoacInterfaz(self, {}, DIAS)
        self.gestorDocentes = GestorDocentes(
            self.datos,
            self.persistencia,
            self.interfaz,
            self.invalidarPlan,
            self.refrescarListas,
        )
        self.gestorAsignaturas = GestorAsignaturas(
            self.datos,
            self.persistencia,
            obtenerDocente=self.gestorDocentes.obtener,
            interfaz=self.interfaz,
            invalidarPlan=self.invalidarPlan,
            refrescarListas=self.refrescarListas,
        )
        self.gestorEspacios = GestorEspacios(
            self.datos,
            self.persistencia,
            interfaz=self.interfaz,
            invalidarPlan=self.invalidarPlan,
            refrescarListas=self.refrescarListas,
        )
        self.interfaz.acciones.update(self.crearAccionesInterfaz())
        self.interfaz.construir()
        self.refrescarListas()

    def crearAccionesInterfaz(self) -> dict[str, Any]:
        """Mapa de callbacks que la interfaz puede invocar."""
        return {
            "guardarDocente":      self.gestorDocentes.guardarDesdeInterfaz,
            "limpiarDocente":      self.gestorDocentes.limpiarDesdeInterfaz,
            "eliminarDocente":     self.gestorDocentes.eliminarDesdeInterfaz,
            "seleccionarDocente":  self.gestorDocentes.seleccionarDesdeInterfaz,
            "guardarAsignatura":   self.gestorAsignaturas.guardarDesdeInterfaz,
            "limpiarAsignatura":   self.gestorAsignaturas.limpiarDesdeInterfaz,
            "eliminarAsignatura":  self.gestorAsignaturas.eliminarDesdeInterfaz,
            "seleccionarAsignatura": self.gestorAsignaturas.seleccionarDesdeInterfaz,
            "guardarEspacio":      self.gestorEspacios.guardarDesdeInterfaz,
            "limpiarEspacio":      self.gestorEspacios.limpiarDesdeInterfaz,
            "eliminarEspacio":     self.gestorEspacios.eliminarDesdeInterfaz,
            "seleccionarEspacio":  self.gestorEspacios.seleccionarDesdeInterfaz,
            "generarHorario":      self.generarHorario,
            "construirHorarioDocente": self.construirHorarioDocente,
            "exportarHorario":     self.exportarHorario,
        }



    def invalidarPlan(self) -> None:
        self.plan_actual = None
        self.datos["ultimoHorario"] = None

    def refrescarListas(self) -> None:
        self.interfaz.actualizarListas(
            self.datos["docentes"],
            self.datos["asignaturas"],
            self.datos["espacios"],
        )
        self.mostrarPlanGuardado()

    # Coordina la solicitud de la interfaz y guarda el horario resultante.
    def generarHorario(self) -> None:
        if not self.datos["asignaturas"]:
            self.interfaz.mostrarAviso(
                "Faltan asignaturas",
                "Registra al menos una asignatura antes de generar el horario.",
            )
            return

        if not self.datos["espacios"] or not self.datos["docentes"]:
            self.interfaz.mostrarAviso(
                "Faltan recursos",
                "Registra al menos un docente y un espacio físico.",
            )
            return

        try:
            minimo = int(self.interfaz.leerMinimoParalelo())
            if minimo < 1:
                raise ValueError
        except ValueError:
            self.interfaz.mostrarAviso(
                "Mínimo inválido",
                "El mínimo por paralelo debe ser un entero mayor que cero.",
            )
            return

        try:
            horarioResultado = self.servicioPlanificacion.generarHorarioAcademico(
                self.datos["asignaturas"],
                self.datos["docentes"],
                self.datos["espacios"],
                minimo,
                "HOR-001",
                "Periodo actual",
            )
        except DatosPlanificacionInvalidos as error:
            mensaje_detalle = "\n".join(
                f"• {problema}" for problema in str(error).splitlines()
            )
            self.interfaz.mostrarError(
                "No se puede generar el horario",
                f"Corrige los siguientes inconvenientes:\n\n{mensaje_detalle}",
            )
            self.interfaz.mostrarEstadoHorario(
                "No se generó el horario: hay recursos o paralelos que no cumplen las restricciones."
            )
            return
        except SinPlanificacionDisponible as error:
            self.interfaz.mostrarError(
                "No se encontró una planificación",
                str(error),
            )
            self.interfaz.mostrarEstadoHorario(
                "No se encontró una planificación que satisfaga todas las restricciones."
            )
            return

        plan = horarioResultado.aDiccionario()
        self.plan_actual = plan
        self.datos["ultimoHorario"] = self.plan_actual
        self.persistencia.guardarDatos(self.datos)
        self.mostrarPlanGuardado()
        self.interfaz.mostrarEstadoHorario(
            f"Horario generado: {len(plan['paralelos'])} paralelos, {len(plan['sesiones'])}"
            " bloques de clase. Demanda distribuida entre"
            f" {minimo} y la capacidad de cada aula."
        )


    def mostrarPlanGuardado(self) -> None:
        self.plan_actual = self.datos.get("ultimoHorario")
        self.interfaz.mostrarHorario(self.plan_actual, self.datos["docentes"])

    # Delega la vista docente al servicio sin reconstruir el DTO en el controlador.
    def construirHorarioDocente(self, cedulaDocente: str) -> dict[str, Any] | None:
        if not self.plan_actual:
            return None
        return self.servicioPlanificacion.construirHorarioDocente(
            self.plan_actual, cedulaDocente
        )

    def exportarHorario(self) -> None:
        if not self.plan_actual or not self.plan_actual.get("sesiones"):
            self.interfaz.mostrarInformacion(
                "Sin horario", "Genera un horario antes de exportarlo."
            )
            return
        archivo = self.persistencia.guardarHorarioExportado(self.plan_actual)
        self.interfaz.mostrarInformacion(
            "Horario exportado", f"Se guardó el horario en:\n{archivo}"
        )

if __name__ == "__main__":
    KhronoacApp().mainloop()
