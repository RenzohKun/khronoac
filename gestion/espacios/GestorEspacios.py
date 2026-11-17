# Coordina la gestión de aulas y laboratorios separando formularios y reglas.
# Valida los datos, crea el espacio con la fábrica, actualiza el catálogo,
# invalida el horario y persiste los cambios antes de refrescar la interfaz.
from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Mapping

from fabrica_espacios import crearEspacio
from persistencia import KhronoacPersistenciaDatos


class _EspacioInvalido(ValueError):
    """Distingue el rechazo de la fábrica de los errores de persistencia."""


class EstadoGestionEspacio(str, Enum):
    GUARDADO = "guardado"
    ELIMINADO = "eliminado"
    CAPACIDAD_INVALIDA = "capacidad_invalida"
    CODIGO_REQUERIDO = "codigo_requerido"
    TIPO_LABORATORIO_REQUERIDO = "tipo_laboratorio_requerido"
    CODIGO_DUPLICADO = "codigo_duplicado"
    NO_ENCONTRADO = "no_encontrado"


class GestorEspacios:
    """Separa las operaciones del catálogo de la coordinación de formularios."""

    def __init__(
        self,
        datos: dict[str, Any],
        persistencia: KhronoacPersistenciaDatos,
        interfaz: Any | None = None,
        invalidarPlan: Callable[[], None] | None = None,
        refrescarListas: Callable[[], None] | None = None,
    ) -> None:
        self._datos = datos
        self._persistencia = persistencia
        self._interfaz = interfaz
        self._invalidarPlan = invalidarPlan or (lambda: None)
        self._refrescarListas = refrescarListas or (lambda: None)
        self._codigoEditando: str | None = None

    def guardarDesdeInterfaz(self) -> None:
        interfaz = self._interfazRequerida()
        formulario = interfaz.leerFormularioEspacio()
        try:
            resultado = self.guardar(formulario, self._codigoEditando)
        except _EspacioInvalido as error:
            interfaz.mostrarAviso("Tipo inválido", str(error))
            return

        if resultado is EstadoGestionEspacio.CAPACIDAD_INVALIDA:
            interfaz.mostrarAviso(
                "Capacidad inválida", "La capacidad debe ser un entero mayor que cero."
            )
            return
        if resultado is EstadoGestionEspacio.CODIGO_REQUERIDO:
            interfaz.mostrarAviso("Dato incompleto", "El código del espacio es obligatorio.")
            return
        if resultado is EstadoGestionEspacio.TIPO_LABORATORIO_REQUERIDO:
            interfaz.mostrarAviso("Dato incompleto", "Indica el tipo de laboratorio.")
            return
        if resultado is EstadoGestionEspacio.CODIGO_DUPLICADO:
            interfaz.mostrarAviso("Código duplicado", "Ya existe otro espacio con ese código.")
            return

        self.limpiarDesdeInterfaz()
        self._refrescarListas()

    def seleccionarDesdeInterfaz(self, codigo: str) -> None:
        espacio = self.obtener(codigo)
        if espacio is None:
            return
        self._codigoEditando = espacio["codigoAula"]
        self._interfazRequerida().cargarEspacio(espacio)

    def limpiarDesdeInterfaz(self) -> None:
        self._codigoEditando = None
        self._interfazRequerida().limpiarEspacio()

    def eliminarDesdeInterfaz(self) -> None:
        interfaz = self._interfazRequerida()
        codigo = interfaz.espacioSeleccionado()
        if codigo is None:
            return
        if not interfaz.confirmar("Confirmar", "¿Eliminar el espacio seleccionado?"):
            return
        if self.eliminar(codigo) is not EstadoGestionEspacio.ELIMINADO:
            return
        self.limpiarDesdeInterfaz()
        self._refrescarListas()

    def _interfazRequerida(self) -> Any:
        if self._interfaz is None:
            raise RuntimeError(
                "Esta operación requiere una interfaz de Khronoac conectada."
            )
        return self._interfaz

    def obtener(self, codigo: str) -> dict[str, Any] | None:
        return next(
            (espacio for espacio in self._datos["espacios"]
             if espacio["codigoAula"] == codigo),
            None,
        )

    def guardar(
        self, datosEspacio: Mapping[str, Any], codigoAnterior: str | None = None
    ) -> EstadoGestionEspacio:
        """Guarda el espacio; propaga ValueError si la fábrica rechaza su tipo."""
        codigo = datosEspacio["codigoAula"].strip()
        try:
            capacidad = int(datosEspacio["capacidadMaxima"])
            if capacidad < 1:
                raise ValueError
        except ValueError:
            return EstadoGestionEspacio.CAPACIDAD_INVALIDA
        if not codigo:
            return EstadoGestionEspacio.CODIGO_REQUERIDO

        tipo = datosEspacio["tipo"]
        if tipo == "Laboratorio" and not datosEspacio["tipoLaboratorio"].strip():
            return EstadoGestionEspacio.TIPO_LABORATORIO_REQUERIDO

        try:
            espacio = crearEspacio({
                **datosEspacio,
                "codigoAula": codigo,
                "capacidadMaxima": capacidad,
                "equiposEspeciales": datosEspacio["equiposEspeciales"].strip(),
                "tipoLaboratorio": datosEspacio["tipoLaboratorio"].strip(),
            })
        except ValueError as error:
            raise _EspacioInvalido(str(error)) from error
        registro = {
            "codigoAula": espacio.codigoAula,
            "capacidadMaxima": espacio.capacidadMaxima,
            "tipo": tipo,
            "tipoLaboratorio": getattr(espacio, "tipoLaboratorio", ""),
            "equiposEspeciales": getattr(espacio, "equiposEspeciales", ""),
        }
        espacios = self._datos["espacios"]
        claveAnterior = codigoAnterior or codigo
        existente = self._indicePorCodigo(espacios, claveAnterior)
        if any(
            item["codigoAula"].casefold() == codigo.casefold()
            and item["codigoAula"] != claveAnterior
            for item in espacios
        ):
            return EstadoGestionEspacio.CODIGO_DUPLICADO

        if existente is None:
            espacios.append(registro)
        else:
            espacios[existente] = registro
        self._guardarCambios()
        return EstadoGestionEspacio.GUARDADO

    def eliminar(self, codigo: str) -> EstadoGestionEspacio:
        if self.obtener(codigo) is None:
            return EstadoGestionEspacio.NO_ENCONTRADO
        self._datos["espacios"] = [
            espacio for espacio in self._datos["espacios"]
            if espacio["codigoAula"] != codigo
        ]
        self._guardarCambios()
        return EstadoGestionEspacio.ELIMINADO

    def _guardarCambios(self) -> None:
        self._datos["ultimoHorario"] = None
        # El controlador tampoco debe conservar el plan si falla la escritura.
        self._invalidarPlan()
        self._persistencia.guardarDatos(self._datos)

    @staticmethod
    def _indicePorCodigo(
        espacios: list[dict[str, Any]], codigo: str
    ) -> int | None:
        return next(
            (indice for indice, espacio in enumerate(espacios)
             if espacio["codigoAula"] == codigo),
            None,
        )
