from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from Estudiante import Estudiante

class Paralelo:

    def __init__(self, nombreParalelo: str, cupoMaximo: int):
        self.nombreParalelo: str = nombreParalelo
        self.cupoMaximo: int = cupoMaximo
        self.estudiantesInscritos: List["Estudiante"] = []

    def agregarEstudiante(self, estudiante: "Estudiante") -> None:
        if len(self.estudiantesInscritos) < self.cupoMaximo:
            if estudiante not in self.estudiantesInscritos:
                self.estudiantesInscritos.append(estudiante)
        else:
            print(f"El paralelo {self.nombreParalelo} está lleno.")

    def calcularDemanda(self) -> int:
        return len(self.estudiantesInscritos)