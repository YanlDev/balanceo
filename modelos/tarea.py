from typing import List, Set
from utils.validacion import ValidacionError


class Tarea:
    """
    Representa una tarea en la línea de producción.
    
    Atributos:
        id (str): Identificador único de la tarea
        descripcion (str): Descripción de la tarea
        tiempo (float): Tiempo en minutos para completar la tarea
        precedencias (Set[str]): IDs de tareas que deben completarse antes
        peso_posicional (float): Peso calculado por el algoritmo RPW
    """
    
    def __init__(self, id: str, descripcion: str, tiempo: float, precedencias: List[str] = None):
        self.id = id
        self.descripcion = descripcion
        self.tiempo = tiempo
        self.precedencias = set(precedencias) if precedencias else set()
        self.peso_posicional = 0.0
        self._sucesores = set()  # Se calculará dinámicamente
        
        self._validar_datos()
    
    def _validar_datos(self) -> None:
        """Valida los datos de entrada de la tarea."""
        if not self.id or not isinstance(self.id, str):
            raise ValidacionError("El ID de la tarea debe ser una cadena no vacía")
        
        if not self.descripcion or not isinstance(self.descripcion, str):
            raise ValidacionError("La descripción debe ser una cadena no vacía")
        
        if not isinstance(self.tiempo, (int, float)) or self.tiempo <= 0:
            raise ValidacionError("El tiempo debe ser un número positivo")
    
    def agregar_predecesor(self, tarea_id: str) -> None:
        """Agrega una tarea predecesora."""
        self.precedencias.add(tarea_id)
    
    def agregar_sucesor(self, tarea_id: str) -> None:
        """Agrega una tarea sucesora."""
        self._sucesores.add(tarea_id)
    
    def obtener_sucesores(self) -> Set[str]:
        """Retorna el conjunto de sucesores de la tarea."""
        return self._sucesores.copy()
    
    def calcular_peso_posicional(self, todas_tareas: dict) -> float:
        """
        Calcula el peso posicional de la tarea.
        Peso = tiempo_tarea + suma_tiempos_sucesores
        """
        if self.peso_posicional > 0:
            return self.peso_posicional
        
        peso = self.tiempo
        for sucesor_id in self._sucesores:
            if sucesor_id in todas_tareas:
                peso += todas_tareas[sucesor_id].calcular_peso_posicional(todas_tareas)
        
        self.peso_posicional = peso
        return peso
    
    def __str__(self) -> str:
        return f"Tarea({self.id}: {self.tiempo}min, peso={self.peso_posicional:.1f})"
    
    def __repr__(self) -> str:
        return self.__str__()