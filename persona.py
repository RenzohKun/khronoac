from abc import ABC, abstractmethod

class Persona(ABC):

    def __init__(self, cedula: str, nombres: str, apellidos: str, correo_institucional: str,):
        self._cedula: str = cedula
        self._nombres: str = nombres
        self._apellidos: str = apellidos
        self._correo_institucional: str = correo_institucional

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
        return self._correo_institucional

    @abstractmethod
    def obtener_datos(self) -> str:
        pass
    
    @abstractmethod
    def obtener_carga_academica(self) -> str:
        pass