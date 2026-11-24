import unittest
from datetime import time

from modelos.Asignatura import Asignatura
from modelos.EspacioFisico import EspacioFisico
from modelos.FranjaHoraria import FranjaHoraria
from modelos.Laboratorio import Laboratorio


class PatronesEstructuralesTests(unittest.TestCase):
    def test_laboratorio_decorates_and_delegates_space_behavior(self) -> None:
        laboratorio = Laboratorio("LAB-01", 30, "PC", "Computación")
        franja = FranjaHoraria("Lunes", time(8), time(9))

        self.assertIsInstance(laboratorio, EspacioFisico)
        self.assertTrue(
            laboratorio.esAptoParaAsignatura(Asignatura("Programación", 3, True))
        )
        self.assertFalse(
            laboratorio.esAptoParaAsignatura(Asignatura("Matemática", 3, False))
        )
        self.assertTrue(laboratorio.reservarFranja(franja))
        self.assertEqual([franja], laboratorio.franjasOcupadas)
        self.assertFalse(laboratorio.estaDisponible(franja))

if __name__ == "__main__":
    unittest.main()
