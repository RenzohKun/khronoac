# Coordina los casos de uso de datos y horarios entre persistencia y planificación.
# Carga el estado compartido, valida solicitudes, genera, consulta e invalida horarios
# y delega su almacenamiento y exportación sin depender de la interfaz gráfica.
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from persistencia import KhronoacPersistenciaDatos
from planificacion import ServicioPlanificacionHorario


class MotivoSolicitudHorarioInvalida(str, Enum):
    SIN_ASIGNATURAS = "sin_asignaturas"
    SIN_RECURSOS = "sin_recursos"
    MINIMO_INVALIDO = "minimo_invalido"


class SolicitudHorarioInvalida(ValueError):
    def __init__(self, motivo: MotivoSolicitudHorarioInvalida) -> None:
        self.motivo = motivo
        super().__init__(motivo.value)


# -------- Facade --------
class ServicioKhronoac:
    def __init__(
        self,
        persistencia: KhronoacPersistenciaDatos,
        servicioPlanificacion: ServicioPlanificacionHorario,
    ) -> None:
        self._persistencia = persistencia
        self._servicioPlanificacion = servicioPlanificacion
        self.datos = persistencia.cargarDatos()

    @property
    def persistencia(self) -> KhronoacPersistenciaDatos:
        return self._persistencia

    def invalidarHorario(self) -> None:
        # El gestor que llama este método persiste después el catálogo y el horario.
        self.datos["ultimoHorario"] = None

    def obtenerHorario(self) -> dict[str, Any] | None:
        return self.datos.get("ultimoHorario")

    def generarHorario(self, minimo: int) -> dict[str, Any]:
        if not self.datos["asignaturas"]:
            raise SolicitudHorarioInvalida(
                MotivoSolicitudHorarioInvalida.SIN_ASIGNATURAS
            )
        if not self.datos["espacios"] or not self.datos["docentes"]:
            raise SolicitudHorarioInvalida(MotivoSolicitudHorarioInvalida.SIN_RECURSOS)
        if minimo < 1:
            raise SolicitudHorarioInvalida(
                MotivoSolicitudHorarioInvalida.MINIMO_INVALIDO
            )

        resultado = self._servicioPlanificacion.generarHorarioAcademico(
            self.datos["asignaturas"],
            self.datos["docentes"],
            self.datos["espacios"],
            minimo,
            "HOR-001",
            "Periodo actual",
        ).aDiccionario()
        datosActualizados = {**self.datos, "ultimoHorario": resultado}
        self._persistencia.guardarDatos(datosActualizados)
        self.datos["ultimoHorario"] = resultado
        return resultado

    def construirHorarioDocente(self, cedulaDocente: str) -> dict[str, Any] | None:
        horario = self.obtenerHorario()
        if not horario:
            return None
        return self._servicioPlanificacion.construirHorarioDocente(
            horario, cedulaDocente
        )

    def exportarHorario(self) -> Path | None:
        horario = self.obtenerHorario()
        if not horario or not horario.get("sesiones"):
            return None
        return self._persistencia.guardarHorarioExportado(horario)


def crearServicioKhronoac(
    directorioDatos: Path,
    dias: tuple[str, ...],
    horaInicio: int,
    horaFin: int,
) -> ServicioKhronoac:
    persistencia = KhronoacPersistenciaDatos(directorioDatos)
    servicioPlanificacion = ServicioPlanificacionHorario(dias, horaInicio, horaFin)
    return ServicioKhronoac(persistencia, servicioPlanificacion)
# ----- Fin del patrón Facade ------------
