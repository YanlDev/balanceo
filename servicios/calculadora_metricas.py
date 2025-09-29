from typing import Dict, List
import math
from modelos.linea_produccion import LineaProduccion
from modelos.estacion import Estacion


class CalculadoraMetricas:
    """
    Calcula métricas de rendimiento para líneas de producción balanceadas.
    """
    
    def __init__(self, linea_produccion: LineaProduccion):
        self.linea_produccion = linea_produccion
    
    def calcular_todas_las_metricas(self) -> Dict[str, any]:
        """
        Calcula todas las métricas disponibles para la línea de producción.
        """
        estaciones = self.linea_produccion.estaciones
        
        if not estaciones:
            return self._metricas_vacias()
        
        return {
            'metricas_basicas': self._calcular_metricas_basicas(),
            'metricas_eficiencia': self._calcular_metricas_eficiencia(),
            'metricas_produccion': self._calcular_metricas_produccion(),
            'metricas_por_estacion': self._calcular_metricas_por_estacion(),
            'indicadores_calidad': self._calcular_indicadores_calidad()
        }
    
    def _calcular_metricas_basicas(self) -> Dict[str, float]:
        """Calcula métricas básicas del sistema."""
        estaciones = self.linea_produccion.estaciones
        tiempo_ciclo = self.linea_produccion.obtener_tiempo_ciclo()
        
        return {
            'numero_estaciones': len(estaciones),
            'numero_estaciones_minimo_teorico': self.linea_produccion.calcular_numero_minimo_estaciones(),
            'tiempo_ciclo': tiempo_ciclo,
            'tiempo_total_tareas': self.linea_produccion.obtener_tiempo_total_tareas(),
            'demanda_diaria': self.linea_produccion.demanda_diaria,
            'tiempo_disponible': self.linea_produccion.tiempo_disponible
        }
    
    def _calcular_metricas_eficiencia(self) -> Dict[str, float]:
        """Calcula métricas relacionadas con la eficiencia."""
        estaciones = self.linea_produccion.estaciones
        tiempo_ciclo = self.linea_produccion.obtener_tiempo_ciclo()
        tiempo_total_tareas = self.linea_produccion.obtener_tiempo_total_tareas()
        
        if not estaciones or tiempo_ciclo == 0:
            return {
                'eficiencia_linea': 0.0,
                'utilizacion_promedio': 0.0,
                'desbalance': 100.0,
                'tiempo_ocioso_total': 0.0,
                'tiempo_ocioso_porcentaje': 100.0,
                'indice_suavidad': 0.0
            }
        
        # Eficiencia de la línea
        tiempo_productivo_total = len(estaciones) * tiempo_ciclo
        eficiencia_linea = (tiempo_total_tareas / tiempo_productivo_total) * 100
        
        # Utilización por estación
        utilizaciones = [est.calcular_utilizacion() for est in estaciones]
        utilizacion_promedio = sum(utilizaciones) / len(utilizaciones)
        
        # Desbalance (diferencia entre máxima y mínima utilización)
        utilizacion_max = max(utilizaciones)
        utilizacion_min = min(utilizaciones)
        desbalance = utilizacion_max - utilizacion_min
        
        # Tiempo ocioso
        tiempo_ocioso_total = sum(est.obtener_tiempo_ocioso() for est in estaciones)
        tiempo_ocioso_porcentaje = (tiempo_ocioso_total / tiempo_productivo_total) * 100
        
        # CORRECCIÓN: Índice de suavidad (Smoothness Index)
        # Formula correcta: SI = sqrt(sum((Ti - Tc)^2) / n)
        # Donde Ti es el tiempo de la estación i, Tc es el tiempo de ciclo
        suma_cuadrados = sum((est.tiempo_total - tiempo_ciclo) ** 2 for est in estaciones)
        indice_suavidad = math.sqrt(suma_cuadrados / len(estaciones))
        
        return {
            'eficiencia_linea': eficiencia_linea,
            'utilizacion_promedio': utilizacion_promedio,
            'utilizacion_maxima': utilizacion_max,
            'utilizacion_minima': utilizacion_min,
            'desbalance': desbalance,
            'tiempo_ocioso_total': tiempo_ocioso_total,
            'tiempo_ocioso_porcentaje': tiempo_ocioso_porcentaje,
            'indice_suavidad': indice_suavidad
        }
    
    def _calcular_metricas_produccion(self) -> Dict[str, float]:
        """Calcula métricas relacionadas con la producción."""
        tiempo_ciclo = self.linea_produccion.obtener_tiempo_ciclo()
        tiempo_disponible = self.linea_produccion.tiempo_disponible
        demanda_diaria = self.linea_produccion.demanda_diaria
        
        if tiempo_ciclo == 0:
            return {
                'throughput_teorico': 0.0,
                'throughput_real': 0.0,
                'capacidad_diaria': 0.0,
                'capacidad_maxima_diaria': 0.0,
                'utilizacion_capacidad': 0.0,
                'tiempo_por_unidad': 0.0
            }
        
        # Throughput (unidades por minuto)
        throughput_teorico = 1 / tiempo_ciclo
        
        # En la realidad, el throughput está limitado por la estación más lenta
        estaciones = self.linea_produccion.estaciones
        if estaciones:
            tiempo_estacion_mas_lenta = max(est.tiempo_total for est in estaciones)
            throughput_real = 1 / tiempo_estacion_mas_lenta if tiempo_estacion_mas_lenta > 0 else 0
        else:
            throughput_real = throughput_teorico
        
        # Capacidad diaria real
        capacidad_diaria = throughput_real * tiempo_disponible
        
        # Capacidad máxima teórica
        capacidad_maxima_diaria = throughput_teorico * tiempo_disponible
        
        # Utilización de capacidad
        utilizacion_capacidad = (demanda_diaria / capacidad_diaria * 100) if capacidad_diaria > 0 else 0
        
        return {
            'throughput_teorico': throughput_teorico,
            'throughput_real': throughput_real,
            'capacidad_diaria': capacidad_diaria,
            'capacidad_maxima_diaria': capacidad_maxima_diaria,
            'utilizacion_capacidad': min(utilizacion_capacidad, 100.0),
            'tiempo_por_unidad': 1 / throughput_real if throughput_real > 0 else float('inf')
        }
    
    def _calcular_metricas_por_estacion(self) -> List[Dict[str, any]]:
        """Calcula métricas detalladas por estación."""
        estaciones = self.linea_produccion.estaciones
        
        metricas_estaciones = []
        for estacion in estaciones:
            metricas = {
                'numero': estacion.numero,
                'numero_tareas': len(estacion.tareas_asignadas),
                'tiempo_total': estacion.tiempo_total,
                'tiempo_ciclo_max': estacion.tiempo_ciclo_max,
                'utilizacion': estacion.calcular_utilizacion(),
                'tiempo_ocioso': estacion.obtener_tiempo_ocioso(),
                'tareas_asignadas': [
                    {
                        'id': tarea.id,
                        'descripcion': tarea.descripcion,
                        'tiempo': tarea.tiempo,
                        'peso_posicional': tarea.peso_posicional
                    }
                    for tarea in estacion.tareas_asignadas
                ],
                'es_cuello_botella': False  # Se calculará después
            }
            metricas_estaciones.append(metricas)
        
        # Identificar cuellos de botella (estaciones con mayor tiempo total)
        if metricas_estaciones:
            tiempo_max = max(m['tiempo_total'] for m in metricas_estaciones)
            for metrica in metricas_estaciones:
                metrica['es_cuello_botella'] = metrica['tiempo_total'] == tiempo_max
        
        return metricas_estaciones
    
    def _calcular_indicadores_calidad(self) -> Dict[str, any]:
        """Calcula indicadores de calidad del balanceamiento."""
        estaciones = self.linea_produccion.estaciones
        
        if not estaciones:
            return {
                'balance_perfecto': False,
                'numero_cuellos_botella': 0,
                'factor_suavizado': 0.0,
                'indice_distribucion': 0.0,
                'recomendaciones': []
            }
        
        utilizaciones = [est.calcular_utilizacion() for est in estaciones]
        tiempo_ciclo = self.linea_produccion.obtener_tiempo_ciclo()
        
        # Balance perfecto (todas las estaciones con utilización > 95%)
        balance_perfecto = all(u >= 95.0 for u in utilizaciones)
        
        # Número de cuellos de botella (estaciones con utilización > 98%)
        numero_cuellos_botella = sum(1 for u in utilizaciones if u >= 98.0)
        
        # Factor de suavizado (menor varianza = mejor distribución)
        if len(utilizaciones) > 1:
            utilizacion_promedio = sum(utilizaciones) / len(utilizaciones)
            varianza = sum((u - utilizacion_promedio) ** 2 for u in utilizaciones) / len(utilizaciones)
            factor_suavizado = max(0, 100 - varianza)  # Mayor valor = mejor distribución
        else:
            factor_suavizado = 100.0
        
        # Índice de distribución (qué tan bien distribuidas están las cargas)
        utilizacion_max = max(utilizaciones)
        utilizacion_min = min(utilizaciones)
        if utilizacion_max > 0:
            indice_distribucion = (utilizacion_min / utilizacion_max) * 100
        else:
            indice_distribucion = 100.0
        
        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(utilizaciones, tiempo_ciclo)
        
        return {
            'balance_perfecto': balance_perfecto,
            'numero_cuellos_botella': numero_cuellos_botella,
            'factor_suavizado': factor_suavizado,
            'indice_distribucion': indice_distribucion,
            'recomendaciones': recomendaciones
        }
    
    def _generar_recomendaciones(self, utilizaciones: List[float], tiempo_ciclo: float) -> List[str]:
        """Genera recomendaciones para mejorar el balanceamiento."""
        recomendaciones = []
        
        if not utilizaciones:
            return recomendaciones
        
        utilizacion_promedio = sum(utilizaciones) / len(utilizaciones)
        utilizacion_max = max(utilizaciones)
        utilizacion_min = min(utilizaciones)
        
        # Recomendaciones basadas en utilización
        if utilizacion_max > 95:
            recomendaciones.append("Considere reducir el tiempo de ciclo o redistribuir tareas para evitar cuellos de botella")
        
        if utilizacion_min < 70:
            recomendaciones.append("Algunas estaciones tienen baja utilización. Considere consolidar tareas")
        
        if (utilizacion_max - utilizacion_min) > 20:
            recomendaciones.append("Existe un desbalance significativo. Revise la distribución de tareas")
        
        if utilizacion_promedio < 80:
            recomendaciones.append("La eficiencia general es baja. Considere reducir el número de estaciones")
        
        # Recomendaciones basadas en número de estaciones
        num_estaciones = len(utilizaciones)
        min_teorico = self.linea_produccion.calcular_numero_minimo_estaciones()
        
        if num_estaciones > min_teorico + 2:
            recomendaciones.append(f"Número de estaciones ({num_estaciones}) es alto comparado con el mínimo teórico ({min_teorico})")
        
        if not recomendaciones:
            recomendaciones.append("El balanceamiento actual es satisfactorio")
        
        return recomendaciones
    
    def _metricas_vacias(self) -> Dict[str, any]:
        """Retorna estructura de métricas vacía cuando no hay estaciones."""
        return {
            'metricas_basicas': {
                'numero_estaciones': 0,
                'numero_estaciones_minimo_teorico': 0,
                'tiempo_ciclo': 0.0,
                'tiempo_total_tareas': 0.0,
                'demanda_diaria': self.linea_produccion.demanda_diaria,
                'tiempo_disponible': self.linea_produccion.tiempo_disponible
            },
            'metricas_eficiencia': {
                'eficiencia_linea': 0.0,
                'utilizacion_promedio': 0.0,
                'desbalance': 0.0,
                'tiempo_ocioso_total': 0.0,
                'tiempo_ocioso_porcentaje': 0.0,
                'indice_suavidad': 0.0
            },
            'metricas_produccion': {
                'throughput_teorico': 0.0,
                'throughput_real': 0.0,
                'capacidad_diaria': 0.0,
                'capacidad_maxima_diaria': 0.0,
                'utilizacion_capacidad': 0.0,
                'tiempo_por_unidad': 0.0
            },
            'metricas_por_estacion': [],
            'indicadores_calidad': {
                'balance_perfecto': False,
                'numero_cuellos_botella': 0,
                'factor_suavizado': 0.0,
                'indice_distribucion': 0.0,
                'recomendaciones': ["No hay estaciones definidas"]
            }
        }
    
    def calcular_eficiencia(self) -> float:
        """Calcula la eficiencia de la línea (método de conveniencia)."""
        metricas = self._calcular_metricas_eficiencia()
        return metricas.get('eficiencia_linea', 0.0)
    
    def calcular_throughput(self) -> float:
        """Calcula el throughput real (método de conveniencia)."""
        metricas = self._calcular_metricas_produccion()
        return metricas.get('throughput_real', 0.0)
    
    def obtener_utilizacion_por_estacion(self) -> List[float]:
        """Retorna lista de utilizaciones por estación (método de conveniencia)."""
        if not self.linea_produccion.estaciones:
            return []
        return [est.calcular_utilizacion() for est in self.linea_produccion.estaciones]