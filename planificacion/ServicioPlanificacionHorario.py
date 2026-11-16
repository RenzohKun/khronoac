from __future__ import annotations

from typing import Any, Callable

from .EntradaPlanificacion import adaptarDatosPlanificacion
from .HorarioBuilder import (
    HorarioAcademicoBuilder,
    HorarioBuilder,
    HorarioDirector,
    HorarioDocenteBuilder,
    HorarioExamenesBuilder,
    HorarioResultado,
)
from .PlanificadorHorario import PlanificadorHorario
from .ResultadoPlanificacion import ResultadoPlanificacion


class ServicioPlanificacionHorario:

    # Conecta el adaptador de entrada, PlanificadorHorario y HorarioDirector.
    def __init__(
        self,
        dias: tuple[str, ...],
        horaInicio: int,
        horaFin: int,
        limiteNodos: int = 250_000,
    ) -> None:
        self.__dias = dias
        self.__horaInicio = horaInicio
        self.__horaFin = horaFin
        self.__planificador = PlanificadorHorario(
            dias, horaInicio, horaFin, limiteNodos
        )
        self.__horarioDirector = HorarioDirector()
        self.__constructoresBuilder: dict[str, Callable[[], HorarioBuilder]] = {
            "academico": HorarioAcademicoBuilder,
            "examenes": HorarioExamenesBuilder,
            "docente": HorarioDocenteBuilder,
        }

    def registrarBuilder(
        self, tipoHorario: str, constructor: Callable[[], HorarioBuilder]
    ) -> None:
        # Registra una variante nueva sin modificar el director ni el servicio.
        if not tipoHorario:
            raise ValueError("El tipo de horario es obligatorio.")
        if not callable(constructor):
            raise TypeError("El constructor registrado debe ser invocable sin argumentos.")
        self.__constructoresBuilder[tipoHorario] = constructor

    def construirHorario(
        self,
        tipoHorario: str,
        resultadoPlanificacion: ResultadoPlanificacion,
        idHorario: str | None = None,
        periodo: str | None = None,
    ) -> HorarioResultado:
        # Resuelve el Builder registrado y delega la construcción al director.
        constructor = self.__constructoresBuilder.get(tipoHorario)
        if constructor is None:
            raise ValueError(f"No hay un Builder registrado para '{tipoHorario}'.")
        builder = constructor()
        if not isinstance(builder, HorarioBuilder):
            raise TypeError("El constructor registrado debe producir un HorarioBuilder.")
        return self.__horarioDirector.construir(
            builder, resultadoPlanificacion, idHorario, periodo
        )

    def generarHorarioAcademico(
        self,
        registrosAsignaturas: list[dict[str, Any]],
        registrosDocentes: list[dict[str, Any]],
        registrosEspacios: list[dict[str, Any]],
        minimo: int,
        idHorario: str = "HOR-ACA-01",
        periodo: str = "Periodo actual",
    ) -> HorarioResultado:
        # Adapta registros, calcula el horario y lo construye con el Builder.
        datos = adaptarDatosPlanificacion(
            registrosAsignaturas,
            registrosDocentes,
            registrosEspacios,
            self.__horaInicio,
            self.__horaFin,
        )
        resultado = self.__planificador.generarHorario(datos, minimo)
        return self.construirHorario(
            "academico", resultado, idHorario, periodo
        )

    def construirHorarioDocente(
        self, horarioGuardado: dict[str, Any], cedulaDocente: str
    ) -> dict[str, Any]:
        # Reconstruye el DTO, filtra sus datos y usa el Builder docente registrado.
        resultado = ResultadoPlanificacion.desdeDiccionario(
            horarioGuardado
        ).paraDocente(cedulaDocente)
        horario = self.construirHorario(
            "docente", resultado, "HOR-DOC-01", "Periodo actual"
        )
        return horario.aDiccionario()
