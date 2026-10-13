from typing import List

from Asignatura import Asignatura
from Estudiante import Estudiante


class Paralelo:
    def __init__(
        self,
        nombreParalelo: str,
        cupoMaximo: int,
        asignatura: Asignatura | None = None,
    ) -> None:
        if cupoMaximo < 0:
            raise ValueError("El cupo máximo no puede ser negativo.")
        self.__nombreParalelo = nombreParalelo
        self.__cupoMaximo = cupoMaximo
        self.__estudiantesInscritos: List[Estudiante] = []
        self.__asignatura = asignatura

    @property
    def nombreParalelo(self) -> str:
        return self.__nombreParalelo

    @nombreParalelo.setter
    def nombreParalelo(self, valor: str) -> None:
        self.__nombreParalelo = valor

    @property
    def cupoMaximo(self) -> int:
        return self.__cupoMaximo

    @cupoMaximo.setter
    def cupoMaximo(self, valor: int) -> None:
        if valor < len(self.__estudiantesInscritos):
            raise ValueError("El cupo no puede ser menor a los estudiantes inscritos.")
        self.__cupoMaximo = valor

    @property
    def estudiantesInscritos(self) -> List[Estudiante]:
        return self.__estudiantesInscritos.copy()

    @property
    def asignatura(self) -> Asignatura | None:
        return self.__asignatura

    @asignatura.setter
    def asignatura(self, valor: Asignatura | None) -> None:
        if valor is not None and not isinstance(valor, Asignatura):
            raise TypeError("La asignatura debe ser un objeto Asignatura.")
        self.__asignatura = valor

    def agregarEstudiante(self, estudiante: Estudiante) -> None:
        if not isinstance(estudiante, Estudiante):
            raise TypeError("Solo se pueden agregar objetos Estudiante.")
        if estudiante in self.__estudiantesInscritos:
            return
        if len(self.__estudiantesInscritos) >= self.__cupoMaximo:
            raise ValueError(f"El paralelo {self.__nombreParalelo} está lleno.")
        self.__estudiantesInscritos.append(estudiante)

    def calcularDemanda(self) -> int:
        return len(self.__estudiantesInscritos)
