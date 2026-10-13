from abc import ABC, abstractmethod

class Persona(ABC):

    def __init__(self, cedula: str, nombres: str, apellidos: str, correoElectronico: str,):
        self._cedula: str = cedula
        self._nombres: str = nombres
        self._apellidos: str = apellidos
        self._correoElectronico: str = correoElectronico

    @property
    def cedula(self) -> str:
        return self._cedula

    @property
    def nombres(self) -> str:
        return self._nombres

    @property
    def apellidos(self) -> str:
        return self._apellidos

    @property
    def correo_institucional(self) -> str:
        return self._correoInstitucional

    @abstractmethod
    def obtenerDatos(self) -> str:
        pass
    
    @abstractmethod
    def obtenerCargaAcademica(self) -> str:
        pass