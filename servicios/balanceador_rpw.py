from typing import List, Dict, Tuple
from modelos.tarea import Tarea
from modelos.estacion import Estacion
from modelos.linea_produccion import LineaProduccion
from utils.validacion import ValidacionError


class BalanceadorRPW:
    """
    Implementa el algoritmo Ranked Positional Weight (RPW) para balancear líneas de producción.
    
    El algoritmo RPW sigue estos pasos:
    1. Calcular pesos posicionales para todas las tareas
    2. Ordenar tareas por peso posicional (descendente)
    3. Asignar tareas secuencialmente a estaciones respetando precedencias
    4. Crear nueva estación si la tarea no cabe en ninguna existente
    """
    
    def __init__(self, linea_produccion: LineaProduccion):
        self.linea_produccion = linea_produccion
        self.tareas_ordenadas: List[Tarea] = []
        self.asignaciones: Dict[str, int] = {}  # tarea_id -> numero_estacion
    
    def balancear(self) -> Tuple[List[Estacion], Dict[str, any]]:
        """
        Ejecuta el algoritmo RPW completo y retorna estaciones balanceadas.
        
        Returns:
            Tuple[List[Estacion], Dict]: Estaciones balanceadas y estadísticas
        """
        # Paso 1: Validaciones iniciales
        self._validar_entrada()
        
        # Paso 2: Calcular pesos posicionales
        self._calcular_pesos_posicionales()
        
        # Paso 3: Ordenar tareas por peso posicional
        self._ordenar_tareas_por_peso()
        
        # Paso 4: Asignar tareas a estaciones
        estaciones = self._asignar_tareas_a_estaciones()
        
        # Paso 5: Generar estadísticas
        estadisticas = self._generar_estadisticas(estaciones)
        
        # Actualizar línea de producción
        self.linea_produccion.estaciones = estaciones
        
        return estaciones, estadisticas
    
    def _validar_entrada(self) -> None:
        """Valida que la entrada sea correcta para el algoritmo."""
        if not self.linea_produccion.tareas:
            raise ValidacionError("No hay tareas definidas en la línea de producción")
        
        # Validar precedencias
        errores_precedencias = self.linea_produccion.validar_precedencias()
        if errores_precedencias:
            raise ValidacionError(f"Errores en precedencias: {'; '.join(errores_precedencias)}")
        
        # Detectar ciclos
        if self.linea_produccion.detectar_ciclos():
            raise ValidacionError("Se detectaron ciclos en las precedencias")
        
        # Validar tiempo de ciclo
        tiempo_ciclo = self.linea_produccion.calcular_tiempo_ciclo()
        if tiempo_ciclo <= 0:
            raise ValidacionError("Tiempo de ciclo inválido")
    
    def _calcular_pesos_posicionales(self) -> None:
        """
        Calcula el peso posicional para todas las tareas.
        Peso posicional = tiempo_tarea + suma_tiempos_todos_sucesores
        """
        # Resetear pesos existentes y flags de cálculo
        for tarea in self.linea_produccion.tareas.values():
            tarea.peso_posicional = 0.0
            tarea._peso_calculado = False
        
        # Calcular pesos usando recursión con memoización
        for tarea in self.linea_produccion.tareas.values():
            tarea.calcular_peso_posicional(self.linea_produccion.tareas)
    
    def _ordenar_tareas_por_peso(self) -> None:
        """
        Ordena las tareas por peso posicional en orden descendente.
        En caso de empate, ordena por menor número de precedencias.
        """
        self.tareas_ordenadas = sorted(
            self.linea_produccion.tareas.values(),
            key=lambda t: (-t.peso_posicional, len(t.precedencias), t.id)
        )
    
    def _asignar_tareas_a_estaciones(self) -> List[Estacion]:
        """
        Asigna tareas a estaciones siguiendo el algoritmo RPW.
        
        CORRECCIÓN PRINCIPAL: Iterar hasta asignar todas las tareas
        """
        estaciones = []
        tiempo_ciclo = self.linea_produccion.obtener_tiempo_ciclo()
        tareas_asignadas = set()
        tareas_pendientes = list(self.tareas_ordenadas)
        
        # Continuar hasta que todas las tareas estén asignadas
        while len(tareas_asignadas) < len(self.linea_produccion.tareas):
            tarea_asignada_en_iteracion = False
            
            # Intentar asignar cada tarea pendiente
            for tarea in list(tareas_pendientes):
                # Verificar si todas las precedencias han sido asignadas
                if not self._precedencias_satisfechas(tarea, tareas_asignadas):
                    continue
                
                # Buscar estación existente donde quepa la tarea
                estacion_asignada = None
                for estacion in estaciones:
                    if estacion.puede_agregar_tarea(tarea):
                        estacion_asignada = estacion
                        break
                
                # Si no cabe en ninguna estación, crear una nueva
                if estacion_asignada is None:
                    numero_estacion = len(estaciones) + 1
                    estacion_asignada = Estacion(numero_estacion, tiempo_ciclo)
                    estaciones.append(estacion_asignada)
                
                # Asignar tarea a la estación
                if estacion_asignada.agregar_tarea(tarea):
                    tareas_asignadas.add(tarea.id)
                    self.asignaciones[tarea.id] = estacion_asignada.numero
                    tareas_pendientes.remove(tarea)
                    tarea_asignada_en_iteracion = True
                    break  # Pasar a la siguiente iteración del while
            
            # Si en una iteración completa no se asignó ninguna tarea, hay un problema
            if not tarea_asignada_en_iteracion:
                tareas_no_asignadas = [t.id for t in tareas_pendientes]
                raise ValidacionError(
                    f"No se pudieron asignar las siguientes tareas: {', '.join(tareas_no_asignadas)}. "
                    "Verifique las precedencias y el tiempo de ciclo."
                )
        
        return estaciones
    
    def _precedencias_satisfechas(self, tarea: Tarea, tareas_asignadas: set) -> bool:
        """
        Verifica si todas las precedencias de una tarea han sido satisfechas.
        """
        return tarea.precedencias.issubset(tareas_asignadas)
    
    def _generar_estadisticas(self, estaciones: List[Estacion]) -> Dict[str, any]:
        """Genera estadísticas del balanceamiento."""
        if not estaciones:
            return {}
        
        tiempo_ciclo = self.linea_produccion.obtener_tiempo_ciclo()
        tiempo_total_tareas = self.linea_produccion.obtener_tiempo_total_tareas()
        
        # Calcular métricas por estación
        utilizaciones = [estacion.calcular_utilizacion() for estacion in estaciones]
        tiempos_ociosos = [estacion.obtener_tiempo_ocioso() for estacion in estaciones]
        
        estadisticas = {
            'numero_estaciones': len(estaciones),
            'tiempo_ciclo': tiempo_ciclo,
            'utilizacion_promedio': sum(utilizaciones) / len(utilizaciones),
            'utilizacion_minima': min(utilizaciones),
            'utilizacion_maxima': max(utilizaciones),
            'tiempo_ocioso_total': sum(tiempos_ociosos),
            'eficiencia_linea': (tiempo_total_tareas / (len(estaciones) * tiempo_ciclo)) * 100,
            'estaciones_detalle': [
                {
                    'numero': est.numero,
                    'tareas': est.obtener_ids_tareas(),
                    'tiempo_total': est.tiempo_total,
                    'utilizacion': est.calcular_utilizacion(),
                    'tiempo_ocioso': est.obtener_tiempo_ocioso()
                }
                for est in estaciones
            ]
        }
        
        return estadisticas
    
    def obtener_tareas_ordenadas(self) -> List[Tarea]:
        """Retorna la lista de tareas ordenadas por peso posicional."""
        return self.tareas_ordenadas.copy()
    
    def obtener_asignaciones(self) -> Dict[str, int]:
        """Retorna el mapeo de tareas a estaciones."""
        return self.asignaciones.copy()