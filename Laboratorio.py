from Asignatura import Asignatura
from EspacioFisico import EspacioFisico


class Laboratorio(EspacioFisico):
    def __init__(
        self,
        codigoAula: str,
        capacidadMaxima: int,
        equiposEspeciales: str,
        tipoLaboratorio: str,
    ) -> None:
        super().__init__(codigoAula, capacidadMaxima)
        self.__equiposEspeciales = equiposEspeciales
        self.__tipoLaboratorio = tipoLaboratorio

    @property
    def equiposEspeciales(self) -> str:
        return self.__equiposEspeciales

    @equiposEspeciales.setter
    def equiposEspeciales(self, valor: str) -> None:
        self.__equiposEspeciales = valor

    @property
    def tipoLaboratorio(self) -> str:
        return self.__tipoLaboratorio

    @tipoLaboratorio.setter
    def tipoLaboratorio(self, valor: str) -> None:
        self.__tipoLaboratorio = valor

    def cumpleRequisitosDeAsignatura(self, asignatura: Asignatura) -> bool:
        if not isinstance(asignatura, Asignatura):
            raise TypeError("Se esperaba un objeto Asignatura.")
        return asignatura.requiereLaboratorio()
