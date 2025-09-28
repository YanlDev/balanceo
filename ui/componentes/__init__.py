"""
Componentes modulares de la interfaz de usuario.

Contiene:
- PanelEntradaDatos: Panel para captura de datos de tareas y configuración
- PanelResultados: Panel para mostrar resultados del balanceamiento
- PanelGraficos: Panel para visualización de gráficos y métricas
"""

from .panel_entrada import PanelEntradaDatos
from .panel_resultados import PanelResultados
from .panel_graficos import PanelGraficos

__all__ = ['PanelEntradaDatos', 'PanelResultados', 'PanelGraficos']