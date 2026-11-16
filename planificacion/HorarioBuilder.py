# Este módulo ensambla objetos Horario a partir de una planificación calculada.

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
    # Constructor concreto (Builder) para la entidad Horario.
    # Recibe una planificación calculada y construye su representación final.

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> HorarioBuilder:
        # Reinicia el estado del constructor para ensamblar otro horario.
        self._id_horario = "HOR-001"
        self._periodo_academico = "2026-2"
        self._tipo_horario = "Académico Presencial"
        self._resultadoPlanificacion: ResultadoPlanificacion | None = None
        return self

    def conIdentificador(
        self,
        id_horario: str,
        periodo: str,
        tipo: str | None = None,
    ) -> HorarioBuilder:
        self._id_horario = id_horario
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
    def reset(self) -> HorarioAcademicoBuilder:
        super().reset()
        self._tipo_horario = "Académico"
        return self


class HorarioExamenesBuilder(HorarioBuilder):
    def reset(self) -> HorarioExamenesBuilder:
        super().reset()
        self._tipo_horario = "Exámenes"
        return self


class HorarioDocenteBuilder(HorarioBuilder):
    def reset(self) -> HorarioDocenteBuilder:
        super().reset()
        self._tipo_horario = "Horario docente"
        self._cedulaDocente: str | None = None
        return self

    def conDocente(self, cedulaDocente: str) -> HorarioDocenteBuilder:
        self._cedulaDocente = cedulaDocente
        return self

    def construir(self) -> HorarioResultado:
        if self._resultadoPlanificacion is None:
            raise ValueError("Falta el resultado de planificación para construir el horario.")
        if not self._cedulaDocente:
            raise ValueError("Debe indicarse el docente para construir su horario.")

        sesiones = [
            sesion
            for sesion in self._resultadoPlanificacion.sesiones
            if sesion.get("docente") == self._cedulaDocente
        ]
        paralelos = [
            paralelo
            for paralelo in self._resultadoPlanificacion.paralelos
            if paralelo.get("docenteCedula") == self._cedulaDocente
        ]
        self._resultadoPlanificacion = ResultadoPlanificacion(
            paralelos=paralelos,
            sesiones=sesiones,
            estadisticas=dict(self._resultadoPlanificacion.estadisticas),
            franjasSinConflicto=self._resultadoPlanificacion.franjasSinConflicto,
        )
        return super().construir()


class HorarioDirector:
    # Clase Directora del patrón Builder.
    # Define una receta predeterminada a partir del resultado de planificación.

    def __init__(self, builder: HorarioBuilder | None = None) -> None:
        self._builder = builder or HorarioBuilder()

    def construirPlanificacionEstandar(
        self,
        resultadoPlanificacion: ResultadoPlanificacion,
    ) -> HorarioResultado:
        # Coordina los pasos para una construcción académica estándar.
        self._builder.reset()
        self._builder.conIdentificador(
            "HOR-DIR-01",
            "2026-2",
            "Carrera Software",
        )
        return (
            self._builder
            .conResultadoPlanificacion(resultadoPlanificacion)
            .construir()
        )

    def construirHorarioAcademico(
        self,
        resultadoPlanificacion: ResultadoPlanificacion,
        idHorario: str = "HOR-ACA-01",
        periodo: str = "Periodo actual",
    ) -> HorarioResultado:
        builder = HorarioAcademicoBuilder()
        return (
            builder
            .conIdentificador(idHorario, periodo, "Académico")
            .conResultadoPlanificacion(resultadoPlanificacion)
            .construir()
        )

    def construirHorarioExamenes(
        self,
        resultadoPlanificacion: ResultadoPlanificacion,
        idHorario: str = "HOR-EXA-01",
        periodo: str = "Periodo actual",
    ) -> HorarioResultado:
        builder = HorarioExamenesBuilder()
        return (
            builder
            .conIdentificador(idHorario, periodo, "Exámenes")
            .conResultadoPlanificacion(resultadoPlanificacion)
            .construir()
        )

    def construirHorarioDocente(
        self,
        resultadoPlanificacion: ResultadoPlanificacion,
        cedulaDocente: str,
        idHorario: str = "HOR-DOC-01",
        periodo: str = "Periodo actual",
    ) -> HorarioResultado:
        builder = HorarioDocenteBuilder()
        return (
            builder
            .conIdentificador(idHorario, periodo, "Horario docente")
            .conResultadoPlanificacion(resultadoPlanificacion)
            .conDocente(cedulaDocente)
            .construir()
        )


if __name__ == "__main__":
    resultadoPlanificacion = ResultadoPlanificacion(
        paralelos=[
            {
                "asignatura": "Programación Orientada a Objetos",
                "nombreParalelo": "Programación Orientada a Objetos 1",
                "numero": 1,
                "demanda": 25,
                "cupoMaximo": 35,
                "docenteCedula": "1312345678",
                "horas": 1,
                "requiereLaboratorio": True,
            }
        ],
        sesiones=[
            {
                "dia": "Lunes",
                "inicio": "07:00",
                "fin": "08:00",
                "asignatura": "Programación Orientada a Objetos",
                "paralelo": "Programación Orientada a Objetos 1",
                "numeroParalelo": 1,
                "estudiantes": 25,
                "docente": "1312345678",
                "espacio": "LAB-204",
            }
        ],
        estadisticas={"minimoEstudiantes": 12, "bloqueMinutos": 60},
        franjasSinConflicto=True,
    )
    resultado = (
        HorarioBuilder()
        .conIdentificador("HOR-2026-POO", "Periodo 2026-2")
        .conResultadoPlanificacion(resultadoPlanificacion)
        .construir()
    )
    print(resultado)
