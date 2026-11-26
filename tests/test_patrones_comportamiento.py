import unittest
from typing import Any

from planificacion.EstrategiaPlanificacion import (
    EstrategiaBalanceada,
    EstrategiaCompacta,
    EstrategiaMatutina,
)
from planificacion.ObservadorHorario import ObservadorHorario
from planificacion.ServicioPlanificacionHorario import ServicioPlanificacionHorario


class ObservadorPrueba(ObservadorHorario):
    def __init__(self) -> None:
        self.eventosRecibidos: list[tuple[str, dict[str, Any]]] = []

    def actualizar(self, evento: str, detalle: dict[str, Any]) -> None:
        self.eventosRecibidos.append((evento, detalle))


class TestPatronesComportamiento(unittest.TestCase):
    def setUp(self) -> None:
        self.dias = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")
        self.docentes = [
            {
                "cedula": "1312345678",
                "nombres": "Ana",
                "apellidos": "García",
                "correoElectronico": "ana@uleam.edu.ec",
                "tituloAcademico": "Ing. en Software",
                "diasDisponibles": list(self.dias),
            }
        ]
        self.espacios = [
            {
                "codigoAula": "Aula-01",
                "capacidadMaxima": 35,
                "tipo": "Aula",
                "tipoLaboratorio": "",
                "equiposEspeciales": "",
            }
        ]
        self.asignaturas = [
            {
                "nombreAsignatura": "Ingeniería de Software",
                "horasRequeridas": 3,
                "requiereLaboratorio": False,
                "demandaEstimada": 25,
                "docenteCedula": "1312345678",
            }
        ]

    def testEstrategiasOrdenamientoCandidatos(self) -> None:
        candidatos = [
            ("Martes", 9, "Aula-01"),
            ("Lunes", 10, "Aula-01"),
            ("Miércoles", 7, "Aula-01"),
        ]
        sesionesPorDia = {"Lunes": 2, "Martes": 1, "Miércoles": 0}

        balanceada = EstrategiaBalanceada().ordenarCandidatos(
            candidatos, sesionesPorDia, self.dias
        )
        self.assertEqual(balanceada[0][0], "Miércoles")

        matutina = EstrategiaMatutina().ordenarCandidatos(
            candidatos, sesionesPorDia, self.dias
        )
        self.assertEqual(matutina[0][1], 7)

        compacta = EstrategiaCompacta().ordenarCandidatos(
            candidatos, sesionesPorDia, self.dias
        )
        self.assertEqual(compacta[0][0], "Lunes")

    def testServicioPlanificacionStrategyYObserver(self) -> None:
        servicio = ServicioPlanificacionHorario(self.dias, 7, 20)
        observador = ObservadorPrueba()
        servicio.suscribirObservador(observador)

        servicio.cambiarEstrategia(EstrategiaCompacta())
        resultado = servicio.generarHorarioAcademico(
            self.asignaturas,
            self.docentes,
            self.espacios,
            minimo=10,
            idHorario="HOR-TEST-01",
            periodo="2026-2",
        )

        self.assertTrue(resultado.franjasSinConflicto)
        self.assertEqual(len(resultado.sesiones), 3)
        self.assertTrue(all(s["dia"] == "Lunes" for s in resultado.sesiones))

        eventos = [ev for ev, _ in observador.eventosRecibidos]
        self.assertEqual(eventos, ["estrategiaActualizada", "horarioGenerado"])
        self.assertEqual(len(servicio.historialEventos), 2)

    def testConstruirHorarioPorAula(self) -> None:
        servicio = ServicioPlanificacionHorario(self.dias, 7, 20)
        resultado = servicio.generarHorarioAcademico(
            self.asignaturas,
            self.docentes,
            self.espacios,
            minimo=10,
            idHorario="HOR-TEST-02",
            periodo="2026-2",
        )

        horarioAula = servicio.construirHorarioAula(
            resultado.aDiccionario(), "Aula-01"
        )
        self.assertEqual(horarioAula["tipoHorario"], "Horario por aula")
        self.assertEqual(len(horarioAula["sesiones"]), 3)
        self.assertTrue(
            all(s["espacio"] == "Aula-01" for s in horarioAula["sesiones"])
        )

        horarioVacio = servicio.construirHorarioAula(
            resultado.aDiccionario(), "Aula-99"
        )
        self.assertEqual(len(horarioVacio["sesiones"]), 0)


if __name__ == "__main__":
    unittest.main()