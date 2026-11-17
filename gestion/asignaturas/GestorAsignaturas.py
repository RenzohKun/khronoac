# Gestiona el catálogo de asignaturas y coordina sus formularios por separado.
# Valida los datos, actualiza los registros, invalida el horario y persiste los cambios.
from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Mapping

from modelos.Asignatura import Asignatura
from persistencia import KhronoacPersistenciaDatos


class EstadoGestionAsignatura(str, Enum):
    GUARDADO = "guardado"
    ELIMINADO = "eliminado"
    VALORES_INVALIDOS = "valores_invalidos"
    DATOS_INCOMPLETOS = "datos_incompletos"
    NOMBRE_DUPLICADO = "nombre_duplicado"
    NO_ENCONTRADO = "no_encontrado"


class GestorAsignaturas:
    """Separa las operaciones del catálogo de la coordinación de formularios."""

    def __init__(
        self,
        datos: dict[str, Any],
        persistencia: KhronoacPersistenciaDatos,
        obtenerDocente: Callable[[str], dict[str, Any] | None],
        interfaz: Any | None = None,
        invalidarPlan: Callable[[], None] | None = None,
        refrescarListas: Callable[[], None] | None = None,
    ) -> None:
        self._datos = datos
        self._persistencia = persistencia
        self._obtenerDocente = obtenerDocente
        self._interfaz = interfaz
        self._invalidarPlan = invalidarPlan or (lambda: None)
        self._refrescarListas = refrescarListas or (lambda: None)
        self._nombreEditando: str | None = None

    def guardarDesdeInterfaz(self) -> None:
        interfaz = self._interfazRequerida()
        formulario = interfaz.leerFormularioAsignatura()
        resultado = self.guardar(formulario, self._nombreEditando)

        if resultado is EstadoGestionAsignatura.VALORES_INVALIDOS:
            interfaz.mostrarAviso(
                "Revisa los valores",
                "Las horas semanales y la demanda deben ser enteros mayores que cero.",
            )
            return
        if resultado is EstadoGestionAsignatura.DATOS_INCOMPLETOS:
            interfaz.mostrarAviso(
                "Datos incompletos",
                "Escribe el nombre y selecciona un docente registrado.",
            )
            return
        if resultado is EstadoGestionAsignatura.NOMBRE_DUPLICADO:
            interfaz.mostrarAviso(
                "Asignatura duplicada", "Ya existe otra asignatura con ese nombre."
            )
            return

        self.limpiarDesdeInterfaz()
        self._refrescarListas()

    def seleccionarDesdeInterfaz(self, nombre: str) -> None:
        asignatura = self.obtener(nombre)
        if asignatura is None:
            return
        self._nombreEditando = asignatura["nombreAsignatura"]
        docente = self._obtenerDocente(asignatura["docenteCedula"])
        self._interfazRequerida().cargarAsignatura(asignatura, docente)

    def limpiarDesdeInterfaz(self) -> None:
        self._nombreEditando = None
        self._interfazRequerida().limpiarAsignatura()

    def eliminarDesdeInterfaz(self) -> None:
        interfaz = self._interfazRequerida()
        nombre = interfaz.asignaturaSeleccionada()
        if nombre is None:
            return
        if not interfaz.confirmar(
            "Confirmar", "¿Eliminar la asignatura seleccionada?"
        ):
            return

        resultado = self.eliminar(nombre)
        if resultado is not EstadoGestionAsignatura.ELIMINADO:
            return

        self.limpiarDesdeInterfaz()
        self._refrescarListas()

    def _interfazRequerida(self) -> Any:
        if self._interfaz is None:
            raise RuntimeError(
                "Esta operación requiere una interfaz de Khronoac conectada."
            )
        return self._interfaz

    def obtener(self, nombre: str) -> dict[str, Any] | None:
        return next(
            (
                asignatura
                for asignatura in self._datos["asignaturas"]
                if asignatura["nombreAsignatura"] == nombre
            ),
            None,
        )

    def guardar(
        self,
        datosAsignatura: Mapping[str, Any],
        nombreAnterior: str | None = None,
    ) -> EstadoGestionAsignatura:
        nombre = datosAsignatura["nombreAsignatura"].strip()

        try:
            horas = int(datosAsignatura["horasRequeridas"])
            demanda = int(datosAsignatura["demandaEstimada"])
            if horas < 1 or demanda < 1:
                raise ValueError
        except ValueError:
            return EstadoGestionAsignatura.VALORES_INVALIDOS

        cedulaDocente = datosAsignatura["docenteCedula"]
        if not nombre or not cedulaDocente:
            return EstadoGestionAsignatura.DATOS_INCOMPLETOS

        asignatura = Asignatura(nombre, horas, datosAsignatura["requiereLaboratorio"])
        registro = {
            "nombreAsignatura": asignatura.nombreAsignatura,
            "horasRequeridas": asignatura.obtenerHorasTotales(),
            "requiereLaboratorio": asignatura.requiereLaboratorio(),
            "demandaEstimada": demanda,
            "docenteCedula": cedulaDocente,
        }

        asignaturas = self._datos["asignaturas"]
        claveAnterior = nombreAnterior or nombre
        existente = self._indicePorNombre(asignaturas, claveAnterior)
        duplicada = any(
            item["nombreAsignatura"].casefold() == nombre.casefold()
            and item["nombreAsignatura"] != claveAnterior
            for item in asignaturas
        )
        if duplicada:
            return EstadoGestionAsignatura.NOMBRE_DUPLICADO

        if existente is None:
            asignaturas.append(registro)
        else:
            asignaturas[existente] = registro

        self._guardarCambios()
        return EstadoGestionAsignatura.GUARDADO

    def eliminar(self, nombre: str) -> EstadoGestionAsignatura:
        if self.obtener(nombre) is None:
            return EstadoGestionAsignatura.NO_ENCONTRADO

        self._datos["asignaturas"] = [
            asignatura for asignatura in self._datos["asignaturas"]
            if asignatura["nombreAsignatura"] != nombre
        ]
        self._guardarCambios()
        return EstadoGestionAsignatura.ELIMINADO

    def _guardarCambios(self) -> None:
        self._datos["ultimoHorario"] = None
        # El controlador tampoco debe conservar el plan si falla la escritura.
        self._invalidarPlan()
        self._persistencia.guardarDatos(self._datos)

    @staticmethod
    def _indicePorNombre(
        asignaturas: list[dict[str, Any]], nombre: str
    ) -> int | None:
        return next(
            (
                indice
                for indice, asignatura in enumerate(asignaturas)
                if asignatura["nombreAsignatura"] == nombre
            ),
            None,
        )
