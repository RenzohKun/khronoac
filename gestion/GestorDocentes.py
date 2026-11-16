from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Mapping

from persistencia import KhronoacPersistenciaDatos


class EstadoGestionDocente(str, Enum):
    # Resultado de una operación del catálogo de docentes.

    GUARDADO = "guardado"
    ELIMINADO = "eliminado"
    DATOS_INCOMPLETOS = "datos_incompletos"
    DISPONIBILIDAD_REQUERIDA = "disponibilidad_requerida"
    CEDULA_DUPLICADA = "cedula_duplicada"
    NO_ENCONTRADO = "no_encontrado"
    DOCENTE_ASIGNADO = "docente_asignado"


class GestorDocentes:
    # Coordina altas, ediciones y bajas del catálogo persistido de docentes.

    def __init__(
        self,
        datos: dict[str, Any],
        persistencia: KhronoacPersistenciaDatos,
        interfaz: Any | None = None,
        invalidar_plan: Callable[[], None] | None = None,
        refrescar_listas: Callable[[], None] | None = None,
    ) -> None:
        self._datos = datos
        self._persistencia = persistencia
        self._interfaz = interfaz
        self._invalidar_plan = invalidar_plan or (lambda: None)
        self._refrescar_listas = refrescar_listas or (lambda: None)
        self._cedula_editando: str | None = None

    def guardarDesdeInterfaz(self) -> None:
        interfaz = self._interfazRequerida()
        formulario = interfaz.leerFormularioDocente()
        resultado = self.guardar(formulario, self._cedula_editando)

        if resultado is EstadoGestionDocente.DATOS_INCOMPLETOS:
            interfaz.mostrarAviso(
                "Datos incompletos",
                "Cédula, nombres y apellidos son obligatorios.",
            )
            return
        if resultado is EstadoGestionDocente.DISPONIBILIDAD_REQUERIDA:
            interfaz.mostrarAviso(
                "Disponibilidad requerida",
                "Selecciona al menos un día disponible.",
            )
            return
        if resultado is EstadoGestionDocente.CEDULA_DUPLICADA:
            interfaz.mostrarAviso(
                "Identificador duplicado",
                "Ya existe otro docente con esa cédula.",
            )
            return
        if resultado is EstadoGestionDocente.NO_ENCONTRADO:
            interfaz.mostrarError(
                "Error",
                "No se encontró el docente que intentas editar.",
            )
            return

        self._invalidar_plan()
        self.limpiarDesdeInterfaz()
        self._refrescar_listas()
        interfaz.mostrarInformacion("Éxito", "Docente guardado correctamente.")

    def seleccionarDesdeInterfaz(self, cedula: str) -> None:
        docente = self.obtener(cedula)
        if docente is None:
            return
        self._cedula_editando = docente["cedula"]
        self._interfazRequerida().cargarDocente(docente)

    def limpiarDesdeInterfaz(self) -> None:
        self._cedula_editando = None
        self._interfazRequerida().limpiarDocente()

    def eliminarDesdeInterfaz(self) -> None:
        interfaz = self._interfazRequerida()
        cedula = interfaz.docenteSeleccionado()
        if cedula is None:
            return

        if self.estaAsignado(cedula):
            interfaz.mostrarAviso(
                "Docente asignado",
                "Reasigna o elimina las asignaturas de este docente antes de eliminarlo.",
            )
            return

        if not interfaz.confirmar(
            "Confirmar", "¿Eliminar el docente seleccionado?"
        ):
            return

        resultado = self.eliminar(cedula)
        if resultado is EstadoGestionDocente.DOCENTE_ASIGNADO:
            interfaz.mostrarAviso(
                "Docente asignado",
                "Reasigna o elimina las asignaturas de este docente antes de eliminarlo.",
            )
            return
        if resultado is not EstadoGestionDocente.ELIMINADO:
            return

        self._invalidar_plan()
        self.limpiarDesdeInterfaz()
        self._refrescar_listas()

    def _interfazRequerida(self) -> Any:
        if self._interfaz is None:
            raise RuntimeError(
                "Esta operación requiere una interfaz de Khronoac conectada."
            )
        return self._interfaz

    def obtener(self, cedula: str) -> dict[str, Any] | None:
        return next(
            (
                docente
                for docente in self._datos["docentes"]
                if docente["cedula"] == cedula
            ),
            None,
        )

    def estaAsignado(self, cedula: str) -> bool:
        return any(
            asignatura["docenteCedula"] == cedula
            for asignatura in self._datos["asignaturas"]
        )

    def guardar(
        self,
        formulario: Mapping[str, Any],
        cedula_anterior: str | None = None,
    ) -> EstadoGestionDocente:
        cedula = formulario["cedula"].strip()
        nombres = formulario["nombres"].strip()
        apellidos = formulario["apellidos"].strip()

        if not all((cedula, nombres, apellidos)):
            return EstadoGestionDocente.DATOS_INCOMPLETOS

        dias = formulario["diasDisponibles"]
        if not dias:
            return EstadoGestionDocente.DISPONIBILIDAD_REQUERIDA

        docentes = self._datos["docentes"]
        indice_anterior = self._indicePorCedula(docentes, cedula_anterior)
        if cedula_anterior is not None and indice_anterior is None:
            return EstadoGestionDocente.NO_ENCONTRADO

        indice_nuevo = self._indicePorCedula(docentes, cedula)
        if indice_nuevo is not None and cedula != cedula_anterior:
            return EstadoGestionDocente.CEDULA_DUPLICADA

        docente = {
            "cedula": cedula,
            "nombres": nombres,
            "apellidos": apellidos,
            "correoElectronico": formulario["correoElectronico"].strip(),
            "tituloAcademico": formulario["tituloAcademico"].strip(),
            "diasDisponibles": list(dias),
        }

        if cedula_anterior is None:
            docentes.append(docente)
        else:
            docentes[indice_anterior] = docente
            if cedula != cedula_anterior:
                for asignatura in self._datos["asignaturas"]:
                    if asignatura["docenteCedula"] == cedula_anterior:
                        asignatura["docenteCedula"] = cedula

        self._guardarCambios()
        return EstadoGestionDocente.GUARDADO

    def eliminar(self, cedula: str) -> EstadoGestionDocente:
        if self.estaAsignado(cedula):
            return EstadoGestionDocente.DOCENTE_ASIGNADO

        indice = self._indicePorCedula(self._datos["docentes"], cedula)
        if indice is None:
            return EstadoGestionDocente.NO_ENCONTRADO

        del self._datos["docentes"][indice]
        self._guardarCambios()
        return EstadoGestionDocente.ELIMINADO

    def _guardarCambios(self) -> None:
        self._datos["ultimoHorario"] = None
        self._persistencia.guardarDatos(self._datos)

    @staticmethod
    def _indicePorCedula(
        docentes: list[dict[str, Any]], cedula: str | None
    ) -> int | None:
        if cedula is None:
            return None
        return next(
            (
                indice
                for indice, docente in enumerate(docentes)
                if docente["cedula"] == cedula
            ),
            None,
        )
