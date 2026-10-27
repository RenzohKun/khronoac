"""
Paquete de modelos de dominio para Khronoac.

Este archivo convierte la carpeta 'modelos' en un paquete de Python, permitiendo
centralizar y exportar las clases del sistema para importarlas de forma directa.
"""

from .Persona import Persona
from .Estudiante import Estudiante
from .Docente import Docente
from .AsistenteDocente import AsistenteDocente
from .Asignatura import Asignatura
from .EspacioFisico import EspacioFisico
from .Laboratorio import Laboratorio
from .FranjaHoraria import FranjaHoraria
from .Horario import Horario
from .Paralelo import Paralelo

__all__ = [
    "Persona",
    "Estudiante",
    "Docente",
    "AsistenteDocente",
    "Asignatura",
    "EspacioFisico",
    "Laboratorio",
    "FranjaHoraria",
    "Horario",
    "Paralelo",
]