from typing import TYPE_CHECKING
from EspacioFisico import EspacioFisico

if TYPE_CHECKING:
    from Asignatura import Asignatura

class Laboratorio(EspacioFisico):

    def __init__(self, codigoAula: str, capacidadMaxima: int, equiposEspeciales: str,tipoLaboratorio: str,):
        super().__init__(codigoAula, capacidadMaxima)
        self.equiposEspeciales: str = equiposEspeciales
        self.tipoLaboratorio: str = tipoLaboratorio

    def cumpleRequisitosDeAsignatura(self, asignatura: "Asignatura") -> bool:

        if hasattr(asignatura, "requiereLaboratorio"):
            return asignatura.requiereLaboratorio()
        return getattr(asignatura, "requiere_laboratorio", False)