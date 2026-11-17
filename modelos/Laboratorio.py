from modelos.Asignatura import Asignatura
from modelos.EspacioFisico import EspacioDecorador, EspacioFisico


# -------- Decorator: laboratorio concreto --------
class Laboratorio(EspacioDecorador):
    def __init__(
        self,
        codigoAula: str,
        capacidadMaxima: int,
        equiposEspeciales: str,
        tipoLaboratorio: str,
    ) -> None:
        super().__init__(EspacioFisico(codigoAula, capacidadMaxima))
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

    def esAptoParaAsignatura(self, asignatura: Asignatura) -> bool:
        """Sobrescribe el contrato del padre (LSP): Apto únicamente si la asignatura requiere laboratorio."""
        if not isinstance(asignatura, Asignatura):
            raise TypeError("Se esperaba un objeto Asignatura.")
        return asignatura.requiereLaboratorio()
# ----- Fin del patrón Decorator ------------