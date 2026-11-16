from __future__ import annotations

from typing import Any

from .EntradaPlanificacion import adaptarDatosPlanificacion
from .HorarioBuilder import HorarioDirector, HorarioResultado
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
        return self.__horarioDirector.construirHorarioAcademico(
            resultado, idHorario, periodo
        )

    def construirHorarioDocente(
        self, horarioGuardado: dict[str, Any], cedulaDocente: str
    ) -> dict[str, Any]:
        # Reconstruye el DTO del JSON y delega el filtrado al Builder docente.
        resultado = ResultadoPlanificacion.desdeDiccionario(horarioGuardado)
        horario = self.__horarioDirector.construirHorarioDocente(
            resultado, cedulaDocente
        )
        return horario.aDiccionario()
