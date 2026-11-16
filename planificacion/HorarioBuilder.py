# Este módulo ensambla objetos Horario a partir de una planificación calculada.
#
# Este módulo implementa el patrón de diseño creacional Builder, en el cual se
# crean distintos tipos de horarios que podrían existir dentro de una institución
# empleando el mismo bloque de código.

from __future__ import annotations

from datetime import time
from typing import Any

from modelos.FranjaHoraria import FranjaHoraria
from modelos.Horario import Horario
from .ResultadoPlanificacion import ResultadoPlanificacion


class HorarioResultado:

    # Producto final que encapsula el objeto Horario junto con los metadatos
    # y detalle de sesiones asignadas generadas durante la construcción.

    def __init__(
        self,
        horario: Horario,
        resultadoPlanificacion: ResultadoPlanificacion,
    ) -> None:
        self.horario = horario
        self.resultadoPlanificacion = resultadoPlanificacion
        self.paralelos = resultadoPlanificacion.paralelos
        self.sesiones = resultadoPlanificacion.sesiones
        self.estadisticas = {
            **resultadoPlanificacion.estadisticas,
            "periodo": horario.periodoAcademico,
            "totalParalelos": len(self.paralelos),
            "totalBloques": len(self.sesiones),
        }
        self.franjasSinConflicto = resultadoPlanificacion.franjasSinConflicto

    def aDiccionario(self) -> dict[str, Any]:
        datos = self.resultadoPlanificacion.aDiccionario()
        datos.update({
            "idHorario": self.horario.idHorario,
            "periodo": self.horario.periodoAcademico,
            "tipoHorario": self.horario.tipoHorario,
        })
        return datos

    def __str__(self) -> str:
        resumen = [
            self.horario.generarMallaHoraria(),
            f"\nTotal paralelos planificados: {len(self.paralelos)}",
            f"Total bloques horarios asignados: {len(self.sesiones)}",
            f"Sin conflictos detectados: {self.franjasSinConflicto}",
        ]
        return "\n".join(resumen)


class HorarioBuilder:
    # Define los pasos comunes para ensamblar un Horario.

    tipoHorario = "Académico Presencial"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> HorarioBuilder:

        # Reinicia el estado del constructor para ensamblar otro horario.

        self._id_horario = "HOR-001"
        self._periodo_academico = "2026-2"
        self._tipo_horario = self.tipoHorario
        self._resultadoPlanificacion: ResultadoPlanificacion | None = None
        return self

    def conIdentificador(
        self,
        id_horario: str | None = None,
        periodo: str | None = None,
        tipo: str | None = None,
    ) -> HorarioBuilder:
        if id_horario is not None:
            self._id_horario = id_horario
        if periodo is not None:
            self._periodo_academico = periodo
        if tipo is not None:
            self._tipo_horario = tipo
        return self

    def conResultadoPlanificacion(
        self,
        resultadoPlanificacion: ResultadoPlanificacion,
    ) -> HorarioBuilder:
        if not isinstance(resultadoPlanificacion, ResultadoPlanificacion):
            raise TypeError("Se requiere un objeto ResultadoPlanificacion.")
        self._resultadoPlanificacion = resultadoPlanificacion
        return self

    def construir(self) -> HorarioResultado:

        # Ensambla el objeto Horario según los datos configurados.
        if self._resultadoPlanificacion is None:
            raise ValueError("Falta el resultado de planificación para construir el horario.")


        # Instanciación y ensamblado del objeto central Horario
        horario = Horario(
            self._id_horario,
            self._periodo_academico,
            self._tipo_horario,
        )
        for sesion in self._resultadoPlanificacion.sesiones:
            franja = FranjaHoraria(
                sesion["dia"],
                time.fromisoformat(sesion["inicio"]),
                time.fromisoformat(sesion["fin"]),
            )
            horario.agregarFranja(franja)

        return HorarioResultado(horario, self._resultadoPlanificacion)


class HorarioAcademicoBuilder(HorarioBuilder):
    # Especializa el tipo de horario sin cambiar los pasos comunes.

    tipoHorario = "Académico"


class HorarioExamenesBuilder(HorarioBuilder):
    # Especializa el tipo de horario para una planificación de exámenes.

    tipoHorario = "Exámenes"


class HorarioDocenteBuilder(HorarioBuilder):
    # Construye el horario docente desde un resultado ya filtrado.

    tipoHorario = "Horario docente"


class HorarioDirector:
    # Ejecuta la misma secuencia para cualquier implementación de HorarioBuilder.

    def construir(
        self,
        builder: HorarioBuilder,
        resultadoPlanificacion: ResultadoPlanificacion,
        idHorario: str | None = None,
        periodo: str | None = None,
    ) -> HorarioResultado:
        # El director depende de la abstracción, no de constructores concretos.
        builder.reset()
        if idHorario is not None or periodo is not None:
            builder.conIdentificador(idHorario, periodo)
        return (
            builder
            .conResultadoPlanificacion(resultadoPlanificacion)
            .construir()
        )
