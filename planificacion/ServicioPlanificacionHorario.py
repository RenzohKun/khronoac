from __future__ import annotations

from typing import Any

from .EntradaPlanificacion import adaptarDatosPlanificacion
from .EstrategiaPlanificacion import EstrategiaPlanificacion
from .HorarioBuilder import HorarioDirector, HorarioResultado
from .ObservadorHorario import (
    HistorialEventosHorario,
    ObservadorHorario,
    SujetoPlanificacion,
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
        estrategia: EstrategiaPlanificacion | None = None,
    ) -> None:
        self.__dias = dias
        self.__horaInicio = horaInicio
        self.__horaFin = horaFin
        self.__planificador = PlanificadorHorario(
            dias, horaInicio, horaFin, limiteNodos, estrategia
        )
        self.__horarioDirector = HorarioDirector()
        self.__sujetoEventos = SujetoPlanificacion()
        self.__historial = HistorialEventosHorario()
        self.__sujetoEventos.suscribir(self.__historial)

    @property
    def historialEventos(self) -> list[dict[str, Any]]:
        return self.__historial.registros

    def suscribirObservador(self, observador: ObservadorHorario) -> None:
        self.__sujetoEventos.suscribir(observador)

    def desuscribirObservador(self, observador: ObservadorHorario) -> None:
        self.__sujetoEventos.desuscribir(observador)

    def cambiarEstrategia(self, estrategia: EstrategiaPlanificacion) -> None:
        self.__planificador.establecerEstrategia(estrategia)
        self.__sujetoEventos.notificar(
            "estrategiaActualizada",
            {"estrategia": type(estrategia).__name__},
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
        horario = self.__horarioDirector.construirHorarioAcademico(
            resultado, idHorario, periodo
        )
        self.__sujetoEventos.notificar(
            "horarioGenerado",
            {
                "idHorario": idHorario,
                "periodo": periodo,
                "totalParalelos": len(horario.paralelos),
                "totalBloques": len(horario.sesiones),
                "estrategia": type(self.__planificador.estrategia).__name__,
            },
        )
        return horario

    def construirHorarioDocente(
        self, horarioGuardado: dict[str, Any], cedulaDocente: str
    ) -> dict[str, Any]:
        # Reconstruye el DTO del JSON y delega el filtrado al Builder docente.
        resultado = ResultadoPlanificacion.desdeDiccionario(horarioGuardado)
        horario = self.__horarioDirector.construirHorarioDocente(
            resultado, cedulaDocente
        )
        return horario.aDiccionario()