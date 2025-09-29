"""
Componentes modulares de la interfaz de usuario.

Contiene:
- PanelEntradaDatos: Panel para captura de datos de tareas y configuración
- PanelResultados: Panel para mostrar resultados del balanceamiento
- PanelGraficos: Panel para visualización de gráficos y métricas
- PanelVistaPrevia: Panel para vista previa y exportación de reportes PDF
"""

from .panel_entrada import PanelEntradaDatos
from .panel_resultados import PanelResultados
from .panel_graficos import PanelGraficos
from .panel_vista_previa_pdf import PanelVistaPrevia

__all__ = ['PanelEntradaDatos', 'PanelResultados', 'PanelGraficos', 'PanelVistaPrevia']