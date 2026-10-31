class Asignatura:
    def __init__(
        self, nombreAsignatura: str, horasRequeridas: int, requiereLaboratorio: bool
    ) -> None:
        self.__nombreAsignatura = nombreAsignatura
        self.__horasRequeridas = horasRequeridas
        self.__requiereLaboratorio = bool(requiereLaboratorio)

    @property
    def nombreAsignatura(self) -> str:
        return self.__nombreAsignatura

    @nombreAsignatura.setter
    def nombreAsignatura(self, valor: str) -> None:
        self.__nombreAsignatura = valor

    @property
    def horasRequeridas(self) -> int:
        return self.__horasRequeridas

    @horasRequeridas.setter
    def horasRequeridas(self, valor: int) -> None:
        if valor < 0:
            raise ValueError("Las horas requeridas no pueden ser negativas.")
        self.__horasRequeridas = valor

    def obtenerHorasTotales(self) -> int:
        return self.__horasRequeridas

    def requiereLaboratorio(self) -> bool:
        return self.__requiereLaboratorio

    def establecerRequiereLaboratorio(self, valor: bool) -> None:
        self.__requiereLaboratorio = bool(valor)

    def __str__(self) -> str:
        return (
            f"{self.__nombreAsignatura} | Horas: {self.__horasRequeridas} "
            f"| Lab: {self.__requiereLaboratorio}"
        )
