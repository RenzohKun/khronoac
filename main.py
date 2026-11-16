from __future__ import annotations
import tkinter as tk
from pathlib import Path
from typing import Any
from modelos.Asignatura    import Asignatura
from persistencia      import KhronoacPersistenciaDatos
from interfaz          import KhronoacInterfaz
from fabrica_espacios  import crearEspacio
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
        self.docente_editando:   str | None    = None
        self.asignatura_editando: str | None   = None
        self.espacio_editando:   str | None    = None

      
        self.interfaz = KhronoacInterfaz(self, self.crearAccionesInterfaz(), DIAS)
        self.interfaz.construir()
        self.refrescarListas()

    def crearAccionesInterfaz(self) -> dict[str, Any]:
        """Mapa de callbacks que la interfaz puede invocar."""
        return {
            "guardarDocente":      self.guardarDocente,
            "limpiarDocente":      self.limpiarDocente,
            "eliminarDocente":     self.eliminarDocente,
            "seleccionarDocente":  self.seleccionarDocente,
            "guardarAsignatura":   self.guardarAsignatura,
            "limpiarAsignatura":   self.limpiarAsignatura,
            "eliminarAsignatura":  self.eliminarAsignatura,
            "seleccionarAsignatura": self.seleccionarAsignatura,
            "guardarEspacio":      self.guardarEspacio,
            "limpiarEspacio":      self.limpiarEspacio,
            "eliminarEspacio":     self.eliminarEspacio,
            "seleccionarEspacio":  self.seleccionarEspacio,
            "generarHorario":      self.generarHorario,
            "construirHorarioDocente": self.construirHorarioDocente,
            "exportarHorario":     self.exportarHorario,
        }



    def invalidarPlan(self) -> None:
        self.plan_actual = None
        self.datos["ultimoHorario"] = None

    @staticmethod
    def indicePorClave(
        registros: list[dict[str, Any]], clave: str, valor: str
    ) -> int | None:
        return next(
            (i for i, registro in enumerate(registros) if registro.get(clave) == valor),
            None,
        )

    def obtenerDocente(self, cedula: str) -> dict[str, Any] | None:
        return next(
            (persona for persona in self.datos["docentes"] if persona["cedula"] == cedula),
            None,
        )

    def refrescarListas(self) -> None:
        self.interfaz.actualizarListas(
            self.datos["docentes"],
            self.datos["asignaturas"],
            self.datos["espacios"],
        )
        self.mostrarPlanGuardado()

   

    def guardarDocente(self) -> None:
        formulario = self.interfaz.leerFormularioDocente()
        cedula    = formulario["cedula"].strip()
        nombres   = formulario["nombres"].strip()
        apellidos = formulario["apellidos"].strip()

        if not all((cedula, nombres, apellidos)):
            self.interfaz.mostrarAviso(
                "Datos incompletos",
                "Cédula, nombres y apellidos son obligatorios.",
            )
            return

        dias = formulario["diasDisponibles"]
        if not dias:
            self.interfaz.mostrarAviso(
                "Disponibilidad requerida",
                "Selecciona al menos un día disponible.",
            )
            return

        clave_anterior = self.docente_editando
        indice_nuevo   = self.indicePorClave(self.datos["docentes"], "cedula", cedula)

       
        if clave_anterior is None and indice_nuevo is not None:
            self.interfaz.mostrarAviso(
                "Identificador duplicado",
                "Ya existe otro docente con esa cédula.",
            )
            return

        docente = {
            "cedula":            cedula,
            "nombres":           nombres,
            "apellidos":         apellidos,
            "correoElectronico": formulario["correoElectronico"].strip(),
            "tituloAcademico":   formulario["tituloAcademico"].strip(),
            "diasDisponibles":   dias,
        }

        if clave_anterior is None:
            self.datos["docentes"].append(docente)

        else:
            indice_anterior = self.indicePorClave(
                self.datos["docentes"], "cedula", clave_anterior
            )

            if indice_anterior is None:
                self.interfaz.mostrarError(
                    "Error",
                    "No se encontró el docente que intentas editar.",
                )
                return

          
            if indice_nuevo is not None and cedula != clave_anterior:
                self.interfaz.mostrarAviso(
                    "Identificador duplicado",
                    "Esa cédula ya pertenece a otro docente.",
                )
                return

            self.datos["docentes"][indice_anterior] = docente

           
            if cedula != clave_anterior:
                for asignatura in self.datos["asignaturas"]:
                    if asignatura["docenteCedula"] == clave_anterior:
                        asignatura["docenteCedula"] = cedula

        self.invalidarPlan()
        self.persistencia.guardarDatos(self.datos)
        self.limpiarDocente()
        self.refrescarListas()
        self.interfaz.mostrarInformacion("Éxito", "Docente guardado correctamente.")

    def seleccionarDocente(self, cedula: str) -> None:
        docente = self.obtenerDocente(cedula)
        if docente is None:
            return
        self.docente_editando = docente["cedula"]
        self.interfaz.cargarDocente(docente)

    def limpiarDocente(self) -> None:
        self.docente_editando = None
        self.interfaz.limpiarDocente()

    def eliminarDocente(self) -> None:
        cedula = self.interfaz.docenteSeleccionado()
        if cedula is None:
            return

        if any(asig["docenteCedula"] == cedula for asig in self.datos["asignaturas"]):
            self.interfaz.mostrarAviso(
                "Docente asignado",
                "Reasigna o elimina las asignaturas de este docente antes de eliminarlo.",
            )
            return

        if self.interfaz.confirmar("Confirmar", "¿Eliminar el docente seleccionado?"):
            self.datos["docentes"] = [
                d for d in self.datos["docentes"] if d["cedula"] != cedula
            ]
            self.invalidarPlan()
            self.persistencia.guardarDatos(self.datos)
            self.limpiarDocente()
            self.refrescarListas()


    def guardarAsignatura(self) -> None:
        formulario = self.interfaz.leerFormularioAsignatura()
        nombre     = formulario["nombreAsignatura"].strip()

        try:
            horas   = int(formulario["horasRequeridas"])
            demanda = int(formulario["demandaEstimada"])
            if horas < 1 or demanda < 1:
                raise ValueError
        except ValueError:
            self.interfaz.mostrarAviso(
                "Revisa los valores",
                "Las horas semanales y la demanda deben ser enteros mayores que cero.",
            )
            return

        cedula_docente = formulario["docenteCedula"]
        if not nombre or not cedula_docente:
            self.interfaz.mostrarAviso(
                "Datos incompletos",
                "Escribe el nombre y selecciona un docente registrado.",
            )
            return

        asignatura = Asignatura(nombre, horas, formulario["requiereLaboratorio"])
        registro = {
            "nombreAsignatura":   asignatura.nombreAsignatura,
            "horasRequeridas":    asignatura.obtenerHorasTotales(),
            "requiereLaboratorio": asignatura.requiereLaboratorio(),
            "demandaEstimada":    demanda,
            "docenteCedula":      cedula_docente,
        }

        clave_anterior = self.asignatura_editando or nombre
        existente = self.indicePorClave(
            self.datos["asignaturas"], "nombreAsignatura", clave_anterior
        )
        duplicada = next(
            (
                a for a in self.datos["asignaturas"]
                if a["nombreAsignatura"].casefold() == nombre.casefold()
                and a["nombreAsignatura"] != clave_anterior
            ),
            None,
        )
        if duplicada is not None:
            self.interfaz.mostrarAviso(
                "Asignatura duplicada", "Ya existe otra asignatura con ese nombre."
            )
            return

        if existente is None:
            self.datos["asignaturas"].append(registro)
        else:
            self.datos["asignaturas"][existente] = registro

        self.invalidarPlan()
        self.persistencia.guardarDatos(self.datos)
        self.limpiarAsignatura()
        self.refrescarListas()

    def seleccionarAsignatura(self, nombre: str) -> None:
        asignatura = next(
            (item for item in self.datos["asignaturas"]
             if item["nombreAsignatura"] == nombre),
            None,
        )
        if asignatura is None:
            return
        self.asignatura_editando = asignatura["nombreAsignatura"]
        docente = self.obtenerDocente(asignatura["docenteCedula"])
        self.interfaz.cargarAsignatura(asignatura, docente)

    def limpiarAsignatura(self) -> None:
        self.asignatura_editando = None
        self.interfaz.limpiarAsignatura()

    def eliminarAsignatura(self) -> None:
        nombre = self.interfaz.asignaturaSeleccionada()
        if nombre is not None and self.interfaz.confirmar(
            "Confirmar", "¿Eliminar la asignatura seleccionada?"
        ):
            self.datos["asignaturas"] = [
                a for a in self.datos["asignaturas"]
                if a["nombreAsignatura"] != nombre
            ]
            self.invalidarPlan()
            self.persistencia.guardarDatos(self.datos)
            self.limpiarAsignatura()
            self.refrescarListas()


    def guardarEspacio(self) -> None:
        formulario = self.interfaz.leerFormularioEspacio()
        codigo     = formulario["codigoAula"].strip()

        try:
            capacidad = int(formulario["capacidadMaxima"])
            if capacidad < 1:
                raise ValueError
        except ValueError:
            self.interfaz.mostrarAviso(
                "Capacidad inválida",
                "La capacidad debe ser un entero mayor que cero.",
            )
            return

        if not codigo:
            self.interfaz.mostrarAviso(
                "Dato incompleto", "El código del espacio es obligatorio."
            )
            return

        tipo = formulario["tipo"]
        if tipo == "Laboratorio" and not formulario["tipoLaboratorio"].strip():
            self.interfaz.mostrarAviso("Dato incompleto", "Indica el tipo de laboratorio.")
            return

        datos_espacio = {
            **formulario,
            "codigoAula":        codigo,
            "capacidadMaxima":   capacidad,
            "equiposEspeciales": formulario["equiposEspeciales"].strip(),
            "tipoLaboratorio":   formulario["tipoLaboratorio"].strip(),
        }

        try:
            espacio_objeto = crearEspacio(datos_espacio)
        except ValueError as error:
            self.interfaz.mostrarAviso("Tipo inválido", str(error))
            return

        detalle_lab = {
            "tipoLaboratorio":   getattr(espacio_objeto, "tipoLaboratorio", ""),
            "equiposEspeciales": getattr(espacio_objeto, "equiposEspeciales", ""),
        }
        registro = {
            "codigoAula":      espacio_objeto.codigoAula,
            "capacidadMaxima": espacio_objeto.capacidadMaxima,
            "tipo":            tipo,
            **detalle_lab,
        }

        clave_anterior = self.espacio_editando or codigo
        existente  = self.indicePorClave(self.datos["espacios"], "codigoAula", clave_anterior)
        duplicado  = next(
            (
                e for e in self.datos["espacios"]
                if e["codigoAula"].casefold() == codigo.casefold()
                and e["codigoAula"] != clave_anterior
            ),
            None,
        )
        if duplicado is not None:
            self.interfaz.mostrarAviso(
                "Código duplicado", "Ya existe otro espacio con ese código."
            )
            return

        if existente is None:
            self.datos["espacios"].append(registro)
        else:
            self.datos["espacios"][existente] = registro

        self.invalidarPlan()
        self.persistencia.guardarDatos(self.datos)
        self.limpiarEspacio()
        self.refrescarListas()

    def seleccionarEspacio(self, codigo: str) -> None:
        espacio = next(
            (item for item in self.datos["espacios"] if item["codigoAula"] == codigo),
            None,
        )
        if espacio is None:
            return
        self.espacio_editando = espacio["codigoAula"]
        self.interfaz.cargarEspacio(espacio)

    def limpiarEspacio(self) -> None:
        self.espacio_editando = None
        self.interfaz.limpiarEspacio()

    def eliminarEspacio(self) -> None:
        codigo = self.interfaz.espacioSeleccionado()
        if codigo is not None and self.interfaz.confirmar(
            "Confirmar", "¿Eliminar el espacio seleccionado?"
        ):
            self.datos["espacios"] = [
                e for e in self.datos["espacios"] if e["codigoAula"] != codigo
            ]
            self.invalidarPlan()
            self.persistencia.guardarDatos(self.datos)
            self.limpiarEspacio()
            self.refrescarListas()



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
