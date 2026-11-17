# Punto de entrada y controlador gráfico de Khronoac. Configura la ventana Tk,
# crea el servicio de aplicación y los gestores de docentes, asignaturas y espacios,
# conecta sus operaciones con los callbacks de la interfaz y presenta formularios,
# tablas, avisos y horarios. Delega carga y persistencia al servicio de aplicación,
# y delega validación, cálculo, consulta y exportación de horarios a sus servicios;
# aquí solo coordina las solicitudes gráficas y traduce sus resultados a mensajes.
from __future__ import annotations
import tkinter as tk
from pathlib import Path
from typing import Any
from aplicacion import (
    MotivoSolicitudHorarioInvalida,
    SolicitudHorarioInvalida,
    crearServicioKhronoac,
)
from gestion import GestorAsignaturas, GestorDocentes, GestorEspacios
from interfaz          import KhronoacInterfaz
from planificacion import DatosPlanificacionInvalidos, SinPlanificacionDisponible


DIAS       = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")
HORA_INICIO = 7
HORA_FIN    = 20


class KhronoacApp(tk.Tk):
    # Controlador principal que organiza la ventana y enlaza vistas y gestores.

   

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

       
        self.servicioAplicacion = crearServicioKhronoac(
            Path(__file__).with_name("khronoac_datos"), DIAS, HORA_INICIO, HORA_FIN
        )
        self.datos = self.servicioAplicacion.datos

        self.interfaz = KhronoacInterfaz(self, {}, DIAS)
        self.gestorDocentes = GestorDocentes(
            self.datos,
            self.servicioAplicacion.persistencia,
            self.interfaz,
            self.servicioAplicacion.invalidarHorario,
            self.refrescarListas,
        )
        self.gestorAsignaturas = GestorAsignaturas(
            self.datos,
            self.servicioAplicacion.persistencia,
            obtenerDocente=self.gestorDocentes.obtener,
            interfaz=self.interfaz,
            invalidarPlan=self.servicioAplicacion.invalidarHorario,
            refrescarListas=self.refrescarListas,
        )
        self.gestorEspacios = GestorEspacios(
            self.datos,
            self.servicioAplicacion.persistencia,
            interfaz=self.interfaz,
            invalidarPlan=self.servicioAplicacion.invalidarHorario,
            refrescarListas=self.refrescarListas,
        )
        self.interfaz.acciones.update(self.crearAccionesInterfaz())
        self.interfaz.construir()
        self.refrescarListas()

    def crearAccionesInterfaz(self) -> dict[str, Any]:
        # Mapa de callbacks que la interfaz puede invocar.
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



    def refrescarListas(self) -> None:
        self.interfaz.actualizarListas(
            self.datos["docentes"],
            self.datos["asignaturas"],
            self.datos["espacios"],
        )
        self.mostrarPlanGuardado()

    # Coordina la solicitud gráfica con los servicios de planificación y datos.
    def generarHorario(self) -> None:
        try:
            minimo = int(self.interfaz.leerMinimoParalelo())
        except ValueError:
            self.interfaz.mostrarAviso(
                "Mínimo inválido",
                "El mínimo por paralelo debe ser un entero mayor que cero.",
            )
            return

        try:
            plan = self.servicioAplicacion.generarHorario(minimo)
        except SolicitudHorarioInvalida as error:
            mensajes = {
                MotivoSolicitudHorarioInvalida.SIN_ASIGNATURAS: (
                    "Faltan asignaturas",
                    "Registra al menos una asignatura antes de generar el horario.",
                ),
                MotivoSolicitudHorarioInvalida.SIN_RECURSOS: (
                    "Faltan recursos",
                    "Registra al menos un docente y un espacio físico.",
                ),
                MotivoSolicitudHorarioInvalida.MINIMO_INVALIDO: (
                    "Mínimo inválido",
                    "El mínimo por paralelo debe ser un entero mayor que cero.",
                ),
            }
            self.interfaz.mostrarAviso(*mensajes[error.motivo])
            return
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
            self.interfaz.mostrarError("No se encontró una planificación", str(error))
            self.interfaz.mostrarEstadoHorario(
                "No se encontró una planificación que satisfaga todas las restricciones."
            )
            return
        except OSError as error:
            self.interfaz.mostrarError(
                "No se pudo guardar el horario", f"No se guardó la planificación: {error}"
            )
            return

        self.mostrarPlanGuardado()
        self.interfaz.mostrarEstadoHorario(
            f"Horario generado: {len(plan['paralelos'])} paralelos, {len(plan['sesiones'])}"
            " bloques de clase. Demanda distribuida entre"
            f" {minimo} y la capacidad de cada aula."
        )


    def mostrarPlanGuardado(self) -> None:
        self.interfaz.mostrarHorario(
            self.servicioAplicacion.obtenerHorario(), self.datos["docentes"]
        )

    # Delega la vista docente al servicio de aplicación.
    def construirHorarioDocente(self, cedulaDocente: str) -> dict[str, Any] | None:
        return self.servicioAplicacion.construirHorarioDocente(cedulaDocente)

    def exportarHorario(self) -> None:
        try:
            archivo = self.servicioAplicacion.exportarHorario()
        except OSError as error:
            self.interfaz.mostrarError(
                "No se pudo exportar el horario", f"No se guardó el archivo: {error}"
            )
            return
        if archivo is None:
            self.interfaz.mostrarInformacion(
                "Sin horario", "Genera un horario antes de exportarlo."
            )
            return
        self.interfaz.mostrarInformacion(
            "Horario exportado", f"Se guardó el horario en:\n{archivo}"
        )

if __name__ == "__main__":
    KhronoacApp().mainloop()
