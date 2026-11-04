from __future__ import annotations

import math
from datetime import time
from typing import Any, List, Dict, Tuple, Optional

from modelos.Asignatura import Asignatura
from modelos.Docente import Docente
from modelos.EspacioFisico import EspacioFisico
from modelos.Estudiante import Estudiante
from modelos.FranjaHoraria import FranjaHoraria
from modelos.Horario import Horario
from modelos.Laboratorio import Laboratorio
from modelos.Paralelo import Paralelo


class HorarioResultado:
    """
    Producto final que encapsula el objeto Horario junto con los metadatos
    y detalle de sesiones asignadas generadas durante la construcción.
    """

    def __init__(
        self,
        horario: Horario,
        paralelos: List[Dict[str, Any]],
        sesiones: List[Dict[str, Any]],
        estadisticas: Dict[str, Any],
    ) -> None:
        self.horario = horario
        self.paralelos = paralelos
        self.sesiones = sesiones
        self.estadisticas = estadisticas

    def __str__(self) -> str:
        resumen = [
            self.horario.generarMallaHoraria(),
            f"\nTotal paralelos planificados: {len(self.paralelos)}",
            f"Total bloques horarios asignados: {len(self.sesiones)}",
            f"Sin conflictos detectados: {not self.horario.validarConflictos()}",
        ]
        return "\n".join(resumen)


class HorarioBuilder:
    """
    Constructor concreto (Builder) para la entidad Horario.
    Permite configurar paso a paso los insumos y restricciones del sistema,
    resolviendo de forma desacoplada la lógica de asignación.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> HorarioBuilder:
        """Reinicia el estado del constructor para una nueva planificación."""
        self._id_horario: str = "HOR-001"
        self._periodo_academico: str = "2026-2"
        self._tipo_horario: str = "Académico Presencial"
        self._dias: Tuple[str, ...] = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")
        self._hora_inicio: int = 7
        self._hora_fin: int = 20
        self._minimo_estudiantes: int = 10

        self._docentes: Dict[str, Docente] = {}
        self._espacios: Dict[str, EspacioFisico] = {}
        self._asignaturas_raw: List[Dict[str, Any]] = []
        return self

    def con_identificador(self, id_horario: str, periodo: str, tipo: str = "Académico") -> HorarioBuilder:
        self._id_horario = id_horario
        self._periodo_academico = periodo
        self._tipo_horario = tipo
        return self

    def con_ventana_horaria(self, dias: Tuple[str, ...], hora_inicio: int, hora_fin: int) -> HorarioBuilder:
        self._dias = dias
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin
        return self

    def con_minimo_estudiantes(self, minimo: int) -> HorarioBuilder:
        if minimo < 1:
            raise ValueError("El mínimo de estudiantes debe ser mayor a 0.")
        self._minimo_estudiantes = minimo
        return self

    def con_docentes(self, docentes: List[Docente]) -> HorarioBuilder:
        for d in docentes:
            self._docentes[d.cedula] = d
        return self

    def con_espacios(self, espacios: List[EspacioFisico]) -> HorarioBuilder:
        for e in espacios:
            self._espacios[e.codigoAula] = e
        return self

    def con_asignaturas(self, asignaturas_data: List[Dict[str, Any]]) -> HorarioBuilder:
        self._asignaturas_raw = asignaturas_data
        return self

    def _preparar_secciones_y_tareas(
        self,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
        secciones: List[Dict[str, Any]] = []
        tareas: List[Dict[str, Any]] = []
        errores: List[str] = []

        for reg in self._asignaturas_raw:
            nombre = reg["nombreAsignatura"]
            horas = reg["horasRequeridas"]
            req_lab = reg.get("requiereLaboratorio", False)
            demanda = int(reg["demandaEstimada"])
            cedula_doc = reg["docenteCedula"]

            asig_obj = Asignatura(nombre, horas, req_lab)
            docente = self._docentes.get(cedula_doc)
            if not docente:
                errores.append(f"{nombre}: el docente con cédula {cedula_doc} no está registrado.")
                continue

            espacios_validos = [
                (cod, esp)
                for cod, esp in self._espacios.items()
                if esp.capacidadMaxima >= self._minimo_estudiantes and esp.esAptoParaAsignatura(asig_obj)
            ]

            if not espacios_validos:
                tipo = "laboratorio" if req_lab else "aula común"
                errores.append(f"{nombre}: no hay {tipo} disponible con capacidad mínima de {self._minimo_estudiantes}.")
                continue

            capacidad_max = max(e.capacidadMaxima for _, e in espacios_validos)
            cant_paralelos = math.ceil(demanda / capacidad_max)
            tamanos = [demanda // cant_paralelos] * cant_paralelos
            for idx in range(demanda % cant_paralelos):
                tamanos[idx] += 1

            if min(tamanos) < self._minimo_estudiantes:
                errores.append(f"{nombre}: demanda {demanda} no permite crear paralelos válidos.")
                continue

            for idx, cant in enumerate(tamanos, start=1):
                nombre_p = f"{nombre} - {idx}"
                paralelo = Paralelo(nombre_p, capacidad_max, asig_obj)
                for est_id in range(1, cant + 1):
                    paralelo.agregarEstudiante(
                        Estudiante(
                            f"EST-{nombre[:3]}-{idx}-{est_id:03d}",
                            f"Estudiante {est_id}",
                            f"Paralelo {idx}",
                            f"alumno{est_id}@uleam.edu.ec",
                        )
                    )

                sec = {
                    "asignatura": nombre,
                    "nombreParalelo": paralelo.nombreParalelo,
                    "numero": idx,
                    "demanda": paralelo.calcularDemanda(),
                    "cupoMaximo": paralelo.cupoMaximo,
                    "docenteCedula": cedula_doc,
                    "horas": asig_obj.obtenerHorasTotales(),
                    "requiereLaboratorio": req_lab,
                }
                secciones.append(sec)

                for num_hora in range(1, asig_obj.obtenerHorasTotales() + 1):
                    candidatos = []
                    for dia in self._dias:
                        for h in range(self._hora_inicio, self._hora_fin):
                            franja = FranjaHoraria(dia, time(h), time(h + 1))
                            if not docente.verificarDisponibilidad(franja):
                                continue
                            for cod, esp in espacios_validos:
                                if esp.capacidadMaxima >= cant:
                                    candidatos.append((dia, h, cod))
                    tareas.append({
                        "seccion": sec,
                        "numeroHora": num_hora,
                        "franjasCandidatas": candidatos,
                    })

        return secciones, tareas, errores

    def _resolver_asignacion(
        self, tareas: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        resultado: List[Dict[str, Any]] = []
        docente_ocupado: set[Tuple[str, str, int]] = set()
        paralelo_ocupado: set[Tuple[str, str, int]] = set()
        nodos = 0
        limite_nodos = 200_000

        def buscar(indice: int) -> bool:
            nonlocal nodos
            nodos += 1
            if nodos > limite_nodos or indice == len(tareas):
                return indice == len(tareas)

            tarea = tareas[indice]
            sec = tarea["seccion"]
            for dia, hora, cod in tarea["franjasCandidatas"]:
                clave_doc = (sec["docenteCedula"], dia, hora)
                clave_par = (sec["nombreParalelo"], dia, hora)
                esp = self._espacios[cod]
                franja = FranjaHoraria(dia, time(hora), time(hora + 1))

                if clave_doc in docente_ocupado or clave_par in paralelo_ocupado:
                    continue
                if not esp.estaDisponible(franja) or not esp.reservarFranja(franja):
                    continue

                docente_ocupado.add(clave_doc)
                paralelo_ocupado.add(clave_par)
                resultado.append({
                    "dia": dia,
                    "inicio": f"{hora:02d}:00",
                    "fin": f"{hora + 1:02d}:00",
                    "asignatura": sec["asignatura"],
                    "paralelo": sec["nombreParalelo"],
                    "numeroParalelo": sec["numero"],
                    "estudiantes": sec["demanda"],
                    "docente": sec["docenteCedula"],
                    "espacio": cod,
                    "franja": franja,
                })

                if buscar(indice + 1):
                    return True

                resultado.pop()
                docente_ocupado.remove(clave_doc)
                paralelo_ocupado.remove(clave_par)
                esp.liberarFranja(franja)

            return False

        tareas.sort(key=lambda t: len(t["franjasCandidatas"]))
        return resultado if buscar(0) else None

    def construir(self) -> HorarioResultado:
        """
        Ensambla y valida el objeto complejo Horario según los pasos configurados.
        """
        if not self._docentes or not self._espacios or not self._asignaturas_raw:
            raise ValueError("Insumos insuficientes para construir el horario.")

        secciones, tareas, errores = self._preparar_secciones_y_tareas()
        if errores:
            raise RuntimeError(f"Restricciones no satisfechas:\n- " + "\n- ".join(errores))

        bloques = self._resolver_asignacion(tareas)
        if bloques is None:
            raise RuntimeError("No se encontró una distribución horaria libre de colisiones.")

        # Instanciación y ensamblado del objeto central Horario
        horario = Horario(self._id_horario, self._periodo_academico, self._tipo_horario)
        for sesion in bloques:
            horario.agregarFranja(sesion["franja"])

        if horario.validarConflictos():
            raise RuntimeError("Violación de integridad: se detectaron solapamientos en el horario.")

        estadisticas = {
            "periodo": self._periodo_academico,
            "totalParalelos": len(secciones),
            "totalBloques": len(bloques),
            "minimoEstudiantes": self._minimo_estudiantes,
        }

        return HorarioResultado(
            horario=horario,
            paralelos=secciones,
            sesiones=[{k: v for k, v in b.items() if k != "franja"} for b in bloques],
            estadisticas=estadisticas,
        )


class HorarioDirector:
    """
    Clase Directora opcional del patrón Builder.
    Define rutinas predeterminadas de construcción a partir de fuentes de datos.
    """

    def __init__(self, builder: HorarioBuilder) -> None:
        self._builder = builder

    def construir_planificacion_estandar(
        self,
        docentes: List[Docente],
        espacios: List[EspacioFisico],
        asignaturas: List[Dict[str, Any]],
        minimo_alumnos: int = 15,
    ) -> HorarioResultado:
        """Coordina los pasos para una construcción académica estándar."""
        return (
            self._builder.reset()
            .con_identificador("HOR-DIR-01", "2026-2", "Carrera Software")
            .con_minimo_estudiantes(minimo_alumnos)
            .con_docentes(docentes)
            .con_espacios(espacios)
            .con_asignaturas(asignaturas)
            .construir()
        )

if __name__ == "__main__":
    print("=" * 70)
    print("Patron Builder — KHRONOAC")
    print("=" * 70)

    doc1 = Docente("1312345678", "Jharol", "Ormaza", "jharol@uleam.edu.ec", "Magíster")
    for d in ("Lunes", "Martes", "Miércoles"):
        doc1.registrarDisponibilidad(FranjaHoraria(d, time(7), time(12)))

    doc2 = Docente("1309876543", "Elena", "Mero", "elena@uleam.edu.ec", "PhD")
    for d in ("Miércoles", "Jueves", "Viernes"):
        doc2.registrarDisponibilidad(FranjaHoraria(d, time(8), time(13)))

    aula = EspacioFisico("AULA-101", 35)
    lab = Laboratorio("LAB-204", 30, "30 PCs Core i7, Switch Cisco", "Redes y Software")

    materias = [
        {
            "nombreAsignatura": "Programación Orientada a Objetos",
            "horasRequeridas": 3,
            "requiereLaboratorio": True,
            "demandaEstimada": 25,
            "docenteCedula": "1312345678",
        },
        {
            "nombreAsignatura": "Bases de Datos",
            "horasRequeridas": 2,
            "requiereLaboratorio": False,
            "demandaEstimada": 28,
            "docenteCedula": "1309876543",
        },
    ]

    print("\n--- 1. Construcción paso a paso mediante HorarioBuilder ---")
    builder = HorarioBuilder()
    resultado = (
        builder.con_identificador("HOR-2026-POO", "Periodo 2026-2")
        .con_minimo_estudiantes(12)
        .con_docentes([doc1, doc2])
        .con_espacios([aula, lab])
        .con_asignaturas(materias)
        .construir()
    )

    print(resultado)

    print("\n--- 2. Construcción orquestada mediante HorarioDirector ---")
    director = HorarioDirector(builder)
    resultado_dir = director.construir_planificacion_estandar(
        docentes=[doc1, doc2],
        espacios=[aula, lab],
        asignaturas=materias,
        minimo_alumnos=10,
    )
    print(f"Horario coordinado por Director exitoso. Malla generada:")
    print(resultado_dir.horario.generarMallaHoraria())
    print("\n[OK] El patrón Builder construyó el horario complejo sin acoplamiento a la UI.")
