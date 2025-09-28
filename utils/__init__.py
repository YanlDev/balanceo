"""
Módulo de utilidades para el sistema de balanceamiento de líneas.

Contiene:
- Validador y ValidacionError: Clases para validación de datos
- EstilosModernos, COLORES, FUENTES, ESPACIADO: Utilidades de estilo UI
"""

from .validacion import Validador, ValidacionError

# Importar estilos solo si es necesario (evitar dependencia de tkinter)
try:
    from .estilos import EstilosModernos, COLORES, FUENTES, ESPACIADO
    __all__ = ['Validador', 'ValidacionError', 'EstilosModernos', 'COLORES', 'FUENTES', 'ESPACIADO']
except ImportError:
    # Si tkinter no está disponible, solo exportar validación
    __all__ = ['Validador', 'ValidacionError']