"""
Módulo de modelos de dominio para el sistema de balanceamiento de líneas.

Contiene las clases principales:
- Tarea: Representa una tarea individual en la línea de producción
- Estacion: Representa una estación de trabajo
- LineaProduccion: Gestiona el conjunto completo de tareas y estaciones
"""

from .tarea import Tarea
from .estacion import Estacion
from .linea_produccion import LineaProduccion

__all__ = ['Tarea', 'Estacion', 'LineaProduccion']