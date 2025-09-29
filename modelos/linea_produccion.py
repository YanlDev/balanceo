from typing import Dict, List
from modelos.tarea import Tarea
from modelos.estacion import Estacion


class LineaProduccion:
    """
    Representa una línea completa de producción.
    
    Atributos:
        tareas (Dict[str, Tarea]): Diccionario de todas las tareas
        estaciones (List[Estacion]): Lista de estaciones de trabajo
        demanda_diaria (int): Unidades requeridas por día
        tiempo_disponible (float): Tiempo disponible por día (minutos)
    """
    
    def __init__(self, demanda_diaria: int, tiempo_disponible: float):
        self.tareas: Dict[str, Tarea] = {}
        self.estaciones: List[Estacion] = []
        self.demanda_diaria = demanda_diaria
        self.tiempo_disponible = tiempo_disponible
        self._tiempo_ciclo = 0.0
    
    def agregar_tarea(self, tarea: Tarea) -> None:
        """Agrega una tarea al sistema."""
        self.tareas[tarea.id] = tarea
        self._actualizar_relaciones_precedencia()
    
    def _actualizar_relaciones_precedencia(self) -> None:
        """Actualiza las relaciones de precedencia entre todas las tareas."""
        # Limpiar sucesores existentes
        for tarea in self.tareas.values():
            tarea._sucesores.clear()

        # CORRECCIÓN: Construir sucesores correctamente
        # Si tarea A tiene precedencia B, entonces A es sucesor de B
        for tarea in self.tareas.values():
            for precedencia_id in tarea.precedencias:
                if precedencia_id in self.tareas:
                    # precedencia_id -> tarea.id (precedencia_id es predecesor de tarea)
                    self.tareas[precedencia_id].agregar_sucesor(tarea.id)
    
    def calcular_tiempo_ciclo(self) -> float:
        """
        Calcula el tiempo de ciclo teórico basado en demanda y tiempo disponible.
        Tiempo_ciclo = Tiempo_disponible / Demanda_diaria
        """
        if self.demanda_diaria <= 0:
            return float('inf')
        
        self._tiempo_ciclo = self.tiempo_disponible / self.demanda_diaria
        return self._tiempo_ciclo
    
    def obtener_tiempo_ciclo(self) -> float:
        """Retorna el tiempo de ciclo actual."""
        if self._tiempo_ciclo == 0:
            return self.calcular_tiempo_ciclo()
        return self._tiempo_ciclo
    
    def obtener_tiempo_total_tareas(self) -> float:
        """Suma total de tiempos de todas las tareas."""
        return sum(tarea.tiempo for tarea in self.tareas.values())
    
    def calcular_numero_minimo_estaciones(self) -> int:
        """
        Calcula el número mínimo teórico de estaciones.
        Min_estaciones = ceil(Suma_tiempos / Tiempo_ciclo)
        """
        import math
        tiempo_total = self.obtener_tiempo_total_tareas()
        tiempo_ciclo = self.obtener_tiempo_ciclo()
        
        if tiempo_ciclo == 0:
            return len(self.tareas)
        
        return math.ceil(tiempo_total / tiempo_ciclo)
    
    def validar_precedencias(self) -> List[str]:
        """
        Valida que todas las precedencias existan.
        Retorna lista de errores encontrados.
        """
        errores = []
        
        for tarea in self.tareas.values():
            for precedencia_id in tarea.precedencias:
                if precedencia_id not in self.tareas:
                    errores.append(f"Tarea {tarea.id}: precedencia '{precedencia_id}' no existe")
        
        return errores
    
    def detectar_ciclos(self) -> bool:
        """
        Detecta si existen ciclos en las precedencias usando DFS.
        Retorna True si hay ciclos.
        """
        def tiene_ciclo(tarea_id: str, visitados: set, pila: set) -> bool:
            if tarea_id in pila:
                return True
            if tarea_id in visitados:
                return False
            
            visitados.add(tarea_id)
            pila.add(tarea_id)
            
            if tarea_id in self.tareas:
                for sucesor_id in self.tareas[tarea_id].obtener_sucesores():
                    if tiene_ciclo(sucesor_id, visitados, pila):
                        return True
            
            pila.remove(tarea_id)
            return False
        
        visitados = set()
        for tarea_id in self.tareas:
            if tarea_id not in visitados:
                if tiene_ciclo(tarea_id, visitados, set()):
                    return True
        
        return False
    
    def obtener_tareas_sin_precedencias(self) -> List[Tarea]:
        """Retorna tareas que no tienen precedencias (pueden iniciar)."""
        return [tarea for tarea in self.tareas.values() if not tarea.precedencias]
    
    def limpiar_estaciones(self) -> None:
        """Limpia todas las estaciones asignadas."""
        self.estaciones.clear()
    
    def __str__(self) -> str:
        return f"Línea({len(self.tareas)} tareas, {len(self.estaciones)} estaciones)"