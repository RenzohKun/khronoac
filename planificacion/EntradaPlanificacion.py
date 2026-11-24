# Este archivo es el adaptador de entrada del flujo de planificación de horarios.
# Recibe registros en el formato externo de formularios o JSON y los transforma a
# una estructura que el planificador entiende.
#
# Cumple una función parecida al patrón de diseño estructural Adapter, pero no es
# en precisión un Adapter clásico basado en objetos, sino que es un módulo con
# funciones de conversión.

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Any

from fabrica_espacios import crearEspacio
from modelos.Asignatura import Asignatura
from modelos.Docente import Docente
from modelos.EspacioFisico import EspacioFisico
from modelos.FranjaHoraria import FranjaHoraria
from .ErroresPlanificacion import DatosPlanificacionInvalidos


# -------- Adapter --------
@dataclass(frozen=True)
class AsignaturaPlanificacion:

    # Datos de asignatura que el algoritmo necesita para planificar.

    asignatura: Asignatura
    docenteCedula: str
    demandaEstimada: int


@dataclass(frozen=True)
class DatosPlanificacion:

    # Entrada normalizada que separa el algoritmo del formato de formularios y JSON.

    asignaturas: list[AsignaturaPlanificacion]
    docentes: dict[str, Docente]
    espacios: dict[str, EspacioFisico]


def adaptarDatosPlanificacion(
    registrosAsignaturas: list[dict[str, Any]],
    registrosDocentes: list[dict[str, Any]],
    registrosEspacios: list[dict[str, Any]],
    horaInicio: int,
    horaFin: int,
) -> DatosPlanificacion:

    # Convierte registros externos a entidades y datos usados por planificación.

    try:
        docentes = {
            registro["cedula"]: crearDocente(registro, horaInicio, horaFin)
            for registro in registrosDocentes
        }
        espacios = {
            registro["codigoAula"]: crearEspacio(registro)
            for registro in registrosEspacios
        }
        asignaturas = [
            AsignaturaPlanificacion(
                asignatura=Asignatura(
                    registro["nombreAsignatura"],
                    registro["horasRequeridas"],
                    registro["requiereLaboratorio"],
                ),
                docenteCedula=registro["docenteCedula"],
                demandaEstimada=int(registro["demandaEstimada"]),
            )
            for registro in registrosAsignaturas
        ]
    except (KeyError, TypeError, ValueError) as error:
        raise DatosPlanificacionInvalidos(
            f"Los datos de planificación no son válidos: {error}"
        ) from error
    return DatosPlanificacion(asignaturas, docentes, espacios)


def crearDocente(
    registro: dict[str, Any], horaInicio: int, horaFin: int
) -> Docente:

    # Crea el docente de dominio y sus franjas disponibles.

    docente = Docente(
        registro["cedula"],
        registro["nombres"],
        registro["apellidos"],
        registro["correoElectronico"],
        registro["tituloAcademico"],
    )
    for dia in registro["diasDisponibles"]:
        docente.registrarDisponibilidad(
            FranjaHoraria(dia, time(horaInicio), time(horaFin))
        )
    return docente
# ----- Fin del patrón Adapter ------------