from typing import List

class Asignatura:
    def __init__(self, nombreAsignatura: str, horasRequeridas: int, requiereLaboratorio: bool):
        self._nombreAsignatura = nombreAsignatura
        self._horasRequeridas = horasRequeridas
        self._requiereLaboratorio = requiereLaboratorio

    @property
    def nombreAsignatura(self) -> str:
        return self._nombreAsignatura

    @property
    def horasRequeridas(self) -> int:
        return self._horasRequeridas

    def obtenerHorasTotales(self) -> int:
        return self._horasRequeridas

    def requiereLaboratorio(self) -> bool:
        return self._requiereLaboratorio

    def __str__(self) -> str:
        return f"{self._nombreAsignatura} | Horas: {self._horasRequeridas} | Lab: {self._requiereLaboratorio}"