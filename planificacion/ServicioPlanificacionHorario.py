# Servicio de aplicación interna para la planificación de horarios.
# Orquesta la adaptación de datos, la ejecución de estrategias de planificación,
# la construcción de resultados mediante el patrón Builder y la notificación de
# eventos mediante el patrón Observer.

from __future__ import annotations

from typing import Any

from .EntradaPlanificacion import adaptarDatosPlanificacion
from .EstrategiaPlanificacion import EstrategiaPlanificacion
from .HorarioBuilder import (
    HorarioAcademicoBuilder,
    HorarioAulaBuilder,
    HorarioDirector,
    HorarioDocenteBuilder,
    HorarioResultado,
)
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
        horario = self.__horarioDirector.construir(
            HorarioAcademicoBuilder(), resultado, idHorario, periodo
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
        # Filtra las sesiones y paralelos del docente antes de construir su vista.
        resultado = ResultadoPlanificacion.desdeDiccionario(horarioGuardado)
        resultadoDocente = ResultadoPlanificacion(
            paralelos=[
                p for p in resultado.paralelos if p.get("docenteCedula") == cedulaDocente
            ],
            sesiones=[
                s for s in resultado.sesiones if s.get("docente") == cedulaDocente
            ],
            estadisticas=dict(resultado.estadisticas),
            franjasSinConflicto=resultado.franjasSinConflicto,
        )
        horario = self.__horarioDirector.construir(
            HorarioDocenteBuilder(), resultadoDocente, "HOR-DOC-01", "Periodo actual"
        )
        return horario.aDiccionario()

    def construirHorarioAula(
        self, horarioGuardado: dict[str, Any], codigoAula: str
    ) -> dict[str, Any]:
        # Filtra las sesiones y paralelos asignados a un aula o laboratorio específico.
        resultado = ResultadoPlanificacion.desdeDiccionario(horarioGuardado)
        sesionesAula = [
            s for s in resultado.sesiones if s.get("espacio") == codigoAula
        ]
        paralelosIds = {s.get("paralelo") for s in sesionesAula}
        paralelosAula = [
            p for p in resultado.paralelos if p.get("idParalelo") in paralelosIds
        ]
        resultadoAula = ResultadoPlanificacion(
            paralelos=paralelosAula,
            sesiones=sesionesAula,
            estadisticas={
                **resultado.estadisticas,
                "codigoAula": codigoAula,
                "totalParalelos": len(paralelosAula),
                "totalBloques": len(sesionesAula),
            },
            franjasSinConflicto=resultado.franjasSinConflicto,
        )
        horario = self.__horarioDirector.construir(
            HorarioAulaBuilder(),
            resultadoAula,
            f"HOR-AULA-{codigoAula}",
            str(horarioGuardado.get("periodo", "Periodo actual")),
        )
        return horario.aDiccionario()