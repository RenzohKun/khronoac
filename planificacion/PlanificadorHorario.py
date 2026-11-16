# Este módulo calcula paralelos y asigna franjas, docentes y espacios sin conflictos.

from __future__ import annotations

import math
from datetime import time
from typing import Any

from modelos.EspacioFisico import EspacioFisico
from modelos.FranjaHoraria import FranjaHoraria
from .EntradaPlanificacion import DatosPlanificacion
from .ErroresPlanificacion import DatosPlanificacionInvalidos, SinPlanificacionDisponible
from .ResultadoPlanificacion import ResultadoPlanificacion

class PlanificadorHorario:
    # Calcula paralelos y asigna sus franjas usando datos ya normalizados.

    def __init__(
        self,
        dias: tuple[str, ...],
        hora_inicio: int,
        hora_fin: int,
        limite_nodos: int = 250_000,
    ) -> None:
        self.__dias = dias
        self.__hora_inicio = hora_inicio
        self.__hora_fin = hora_fin
        self.__limite_nodos = limite_nodos

    def generarHorario(
        self,
        datos: DatosPlanificacion,
        minimo: int,
    ) -> ResultadoPlanificacion:
        # Recibe la entrada normalizada y devuelve el resultado del algoritmo.
        docentes = datos.docentes
        espacios = datos.espacios

        secciones: list[dict[str, Any]] = []
        tareas: list[dict[str, Any]] = []
        problemas: list[str] = []
        prototipo_bloque = FranjaHoraria("Lunes", time(0), time(1))

        for entrada in datos.asignaturas:
            asignatura = entrada.asignatura
            docente = docentes.get(entrada.docenteCedula)
            if docente is None:
                problemas.append(
                    f"{asignatura.nombreAsignatura}: el docente registrado ya no existe."
                )
                continue

            espacios_validos = [
                (codigo, espacio)
                for codigo, espacio in espacios.items()
                if espacio.capacidadMaxima >= minimo
                and espacio.esAptoParaAsignatura(asignatura)
            ]
            if not espacios_validos:
                tipo = "laboratorio" if asignatura.requiereLaboratorio() else "aula"
                problemas.append(
                    f"{asignatura.nombreAsignatura}: no hay {tipo} con capacidad"
                    f" de al menos {minimo}."
                )
                continue

            demanda = entrada.demandaEstimada
            capacidad_maxima = max(
                espacio.capacidadMaxima for _, espacio in espacios_validos
            )
            cantidad_paralelos = math.ceil(demanda / capacidad_maxima)
            tamanos = [demanda // cantidad_paralelos] * cantidad_paralelos
            for indice in range(demanda % cantidad_paralelos):
                tamanos[indice] += 1

            if min(tamanos) < minimo:
                problemas.append(
                    f"{asignatura.nombreAsignatura}: con demanda {demanda},"
                    f" capacidad {capacidad_maxima} y mínimo {minimo}, no se"
                    " pueden formar paralelos válidos."
                )
                continue

            for indice, cantidad in enumerate(tamanos, start=1):
                nombre_paralelo = f"{asignatura.nombreAsignatura} {indice}"
                seccion = {
                    "asignatura": asignatura.nombreAsignatura,
                    "nombreParalelo": nombre_paralelo,
                    "numero": indice,
                    "demanda": cantidad,
                    "cupoMaximo": capacidad_maxima,
                    "docenteCedula": entrada.docenteCedula,
                    "horas": asignatura.obtenerHorasTotales(),
                    "requiereLaboratorio": asignatura.requiereLaboratorio(),
                }
                secciones.append(seccion)

                for numero_hora in range(1, asignatura.obtenerHorasTotales() + 1):
                    candidatos = []
                    for dia in self.__dias:
                        for hora in range(self.__hora_inicio, self.__hora_fin):
                            franja = prototipo_bloque.clonar(
                                nuevoDia=dia,
                                nuevaHoraInicio=time(hora),
                                nuevaHoraFin=time(hora + 1),
                            )
                            if not docente.verificarDisponibilidad(franja):
                                continue
                            for codigo, espacio in espacios_validos:
                                if espacio.capacidadMaxima >= cantidad:
                                    candidatos.append((dia, hora, codigo))

                    if not candidatos:
                        problemas.append(
                            f"{nombre_paralelo}, bloque {numero_hora}: el docente"
                            " no tiene disponibilidad en las horas laborables."
                        )
                    tareas.append({
                        "seccion": seccion,
                        "numeroHora": numero_hora,
                        "franjasCandidatas": candidatos,
                    })

        if problemas:
            raise DatosPlanificacionInvalidos("\n".join(problemas))

        resultado = self.asignarBloques(tareas, espacios)
        if resultado is None:
            raise SinPlanificacionDisponible(
                "No se pudieron ubicar todas las horas sin cruces. Revisa"
                " disponibilidades, número de aulas y horas requeridas."
            )

        resultado.sort(
            key=lambda sesion: (
                self.__dias.index(sesion["dia"]),
                sesion["inicio"],
                sesion["asignatura"],
                sesion["numeroParalelo"],
            )
        )
        return ResultadoPlanificacion(
            paralelos=secciones,
            sesiones=[
                {clave: valor for clave, valor in sesion.items() if clave != "franja"}
                for sesion in resultado
            ],
            estadisticas={"minimoEstudiantes": minimo, "bloqueMinutos": 60},
            franjasSinConflicto=not self.tieneConflicto(resultado),
        )

    def asignarBloques(
        self,
        tareas: list[dict[str, Any]],
        espacios: dict[str, EspacioFisico],
    ) -> list[dict[str, Any]] | None:
        # Busca una asignación de franjas sin cruces entre recursos.
        resultado: list[dict[str, Any]] = []
        docentes_ocupados: set[tuple[str, str, int]] = set()
        paralelos_ocupados: set[tuple[str, str, int]] = set()
        sesiones_por_dia = dict.fromkeys(self.__dias, 0)
        nodos = 0
        prototipo = FranjaHoraria("Lunes", time(0), time(1))

        def buscar(indice: int) -> bool:
            nonlocal nodos
            nodos += 1
            if nodos > self.__limite_nodos:
                return False
            if indice == len(tareas):
                return True

            tarea = tareas[indice]
            seccion = tarea["seccion"]
            candidatos = sorted(
                tarea["franjasCandidatas"],
                key=lambda candidato: (
                    sesiones_por_dia[candidato[0]],
                    self.__dias.index(candidato[0]),
                    candidato[1],
                    candidato[2],
                ),
            )
            for dia, hora, codigo in candidatos:
                clave_docente = (seccion["docenteCedula"], dia, hora)
                clave_paralelo = (seccion["nombreParalelo"], dia, hora)
                espacio = espacios[codigo]
                if clave_docente in docentes_ocupados or clave_paralelo in paralelos_ocupados:
                    continue

                franja = prototipo.clonar(
                    nuevoDia=dia,
                    nuevaHoraInicio=time(hora),
                    nuevaHoraFin=time(hora + 1),
                )
                if not espacio.estaDisponible(franja) or not espacio.reservarFranja(franja):
                    continue

                docentes_ocupados.add(clave_docente)
                paralelos_ocupados.add(clave_paralelo)
                sesiones_por_dia[dia] += 1
                resultado.append({
                    "dia": dia,
                    "inicio": f"{hora:02d}:00",
                    "fin": f"{hora + 1:02d}:00",
                    "asignatura": seccion["asignatura"],
                    "paralelo": seccion["nombreParalelo"],
                    "numeroParalelo": seccion["numero"],
                    "estudiantes": seccion["demanda"],
                    "docente": seccion["docenteCedula"],
                    "espacio": codigo,
                    "franja": franja,
                })

                if buscar(indice + 1):
                    return True

                resultado.pop()
                sesiones_por_dia[dia] -= 1
                docentes_ocupados.remove(clave_docente)
                paralelos_ocupados.remove(clave_paralelo)
                espacio.liberarFranja(franja)
            return False

        tareas.sort(key=lambda tarea: len(tarea["franjasCandidatas"]))
        return resultado if buscar(0) else None

    def tieneConflicto(self, sesiones: list[dict[str, Any]]) -> bool:

        # Verifica que una sesión no repita recurso, día y hora.
        ocupaciones: set[tuple[str, str, str]] = set()
        for sesion in sesiones:
            for recurso in ("docente", "espacio", "paralelo"):
                valor = sesion[recurso] if recurso != "paralelo" else sesion["paralelo"]
                clave = (recurso, valor, sesion["dia"] + sesion["inicio"])
                if clave in ocupaciones:
                    return True
                ocupaciones.add(clave)
        return False
