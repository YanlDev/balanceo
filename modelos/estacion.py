from typing import List
from modelos.tarea import Tarea


class Estacion:
    """
    Representa una estación de trabajo en la línea de producción.
    
    Atributos:
        numero (int): Número identificador de la estación
        tareas_asignadas (List[Tarea]): Lista de tareas asignadas
        tiempo_total (float): Tiempo total de todas las tareas asignadas
        tiempo_ciclo_max (float): Tiempo de ciclo máximo permitido
    """
    
    def __init__(self, numero: int, tiempo_ciclo_max: float):
        self.numero = numero
        self.tareas_asignadas: List[Tarea] = []
        self.tiempo_total = 0.0
        self.tiempo_ciclo_max = tiempo_ciclo_max
    
    def puede_agregar_tarea(self, tarea: Tarea) -> bool:
        """
        Verifica si una tarea puede ser agregada a la estación.
        Considera restricciones de tiempo de ciclo.
        """
        return (self.tiempo_total + tarea.tiempo) <= self.tiempo_ciclo_max
    
    def agregar_tarea(self, tarea: Tarea) -> bool:
        """
        Agrega una tarea a la estación si es posible.
        Retorna True si se agregó exitosamente.
        """
        if self.puede_agregar_tarea(tarea):
            self.tareas_asignadas.append(tarea)
            self.tiempo_total += tarea.tiempo
            return True
        return False
    
    def remover_tarea(self, tarea_id: str) -> bool:
        """Remueve una tarea de la estación."""
        for i, tarea in enumerate(self.tareas_asignadas):
            if tarea.id == tarea_id:
                self.tiempo_total -= tarea.tiempo
                self.tareas_asignadas.pop(i)
                return True
        return False
    
    def calcular_utilizacion(self) -> float:
        """Calcula el porcentaje de utilización de la estación."""
        if self.tiempo_ciclo_max == 0:
            return 0.0
        return (self.tiempo_total / self.tiempo_ciclo_max) * 100
    
    def obtener_tiempo_ocioso(self) -> float:
        """Calcula el tiempo ocioso de la estación."""
        return max(0, self.tiempo_ciclo_max - self.tiempo_total)
    
    def obtener_ids_tareas(self) -> List[str]:
        """Retorna lista de IDs de tareas asignadas."""
        return [tarea.id for tarea in self.tareas_asignadas]
    
    def __str__(self) -> str:
        tareas_ids = ", ".join(self.obtener_ids_tareas())
        return f"Estación {self.numero}: [{tareas_ids}] ({self.tiempo_total:.1f}min)"
    
    def __repr__(self) -> str:
        return self.__str__()