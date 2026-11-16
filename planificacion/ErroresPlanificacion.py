# Este archivo se encarga de definir dos errores que permiten distinguir entre
# datos o condiciones inválidas y falta de una planificación disponible.
#
# Estas clases son excepciones propias de la planificación, sirven para que
# la aplicación distinga dos tipos de problema.

# Los datos o las condiciones no permiten planificar.
class DatosPlanificacionInvalidos(ValueError):
    # Indica que los datos no permiten crear una planificación válida.
    pass


# Los datos pareces válidos, pero el planificador no logra ubicar todas las
# clases sin cruces.
class SinPlanificacionDisponible(RuntimeError):
    # Indica que no se encontró una asignación que respete las restricciones.
    pass

# Se escriben como una clase que hereda de otra excepción porque en Python una
# excepción personalizada se define así.