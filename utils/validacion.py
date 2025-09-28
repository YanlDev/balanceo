import re
from typing import List, Any, Union


class ValidacionError(Exception):
    """Excepción personalizada para errores de validación."""
    pass


class Validador:
    """
    Clase utilitaria para validaciones comunes en el sistema.
    """
    
    @staticmethod
    def validar_id_tarea(id_tarea: str) -> bool:
        """
        Valida que el ID de tarea sea válido.
        Reglas: No vacío, solo letras, números y guiones, máximo 10 caracteres.
        """
        if not id_tarea or not isinstance(id_tarea, str):
            return False
        
        # Patrón: letras, números, guiones, hasta 10 caracteres
        patron = r'^[A-Za-z0-9\-_]{1,10}$'
        return bool(re.match(patron, id_tarea.strip()))
    
    @staticmethod
    def validar_tiempo_positivo(tiempo: Union[int, float]) -> bool:
        """Valida que el tiempo sea un número positivo."""
        try:
            tiempo_float = float(tiempo)
            return tiempo_float > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validar_descripcion(descripcion: str) -> bool:
        """
        Valida que la descripción sea válida.
        Reglas: No vacía, máximo 100 caracteres.
        """
        if not descripcion or not isinstance(descripcion, str):
            return False
        
        descripcion = descripcion.strip()
        return 1 <= len(descripcion) <= 100
    
    @staticmethod
    def validar_precedencias(precedencias: List[str], tareas_existentes: List[str] = None) -> List[str]:
        """
        Valida lista de precedencias.
        Retorna lista de errores encontrados.
        """
        errores = []
        
        if not isinstance(precedencias, list):
            errores.append("Las precedencias deben ser una lista")
            return errores
        
        for precedencia in precedencias:
            if not Validador.validar_id_tarea(precedencia):
                errores.append(f"ID de precedencia inválido: '{precedencia}'")
        
        # Validar que las precedencias existan (si se proporciona lista de tareas)
        if tareas_existentes is not None:
            for precedencia in precedencias:
                if precedencia not in tareas_existentes:
                    errores.append(f"Precedencia '{precedencia}' no existe")
        
        # Validar duplicados
        if len(precedencias) != len(set(precedencias)):
            errores.append("Hay precedencias duplicadas")
        
        return errores
    
    @staticmethod
    def validar_demanda_diaria(demanda: Union[int, float]) -> bool:
        """Valida que la demanda diaria sea válida."""
        try:
            demanda_int = int(demanda)
            return demanda_int > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validar_tiempo_disponible(tiempo: Union[int, float]) -> bool:
        """Valida que el tiempo disponible sea válido (en minutos)."""
        try:
            tiempo_float = float(tiempo)
            return 60 <= tiempo_float <= 1440  # Entre 1 hora y 24 horas
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def limpiar_texto(texto: str) -> str:
        """Limpia y normaliza texto de entrada."""
        if not isinstance(texto, str):
            return ""
        
        # Remover espacios extra y normalizar
        texto = texto.strip()
        texto = re.sub(r'\s+', ' ', texto)  # Múltiples espacios -> uno solo
        return texto
    
    @staticmethod
    def validar_datos_completos_tarea(id_tarea: str, descripcion: str, 
                                    tiempo: Any, precedencias: List[str] = None) -> List[str]:
        """
        Valida todos los datos de una tarea completa.
        Retorna lista de errores encontrados.
        """
        errores = []
        
        # Validar ID
        if not Validador.validar_id_tarea(id_tarea):
            errores.append("ID de tarea inválido (solo letras, números, guiones, máx 10 caracteres)")
        
        # Validar descripción
        if not Validador.validar_descripcion(descripcion):
            errores.append("Descripción inválida (1-100 caracteres)")
        
        # Validar tiempo
        if not Validador.validar_tiempo_positivo(tiempo):
            errores.append("Tiempo debe ser un número positivo")
        
        # Validar precedencias
        if precedencias is not None:
            errores_prec = Validador.validar_precedencias(precedencias)
            errores.extend(errores_prec)
        
        return errores
    
    @staticmethod
    def validar_datos_linea_produccion(demanda_diaria: Any, tiempo_disponible: Any) -> List[str]:
        """
        Valida datos de configuración de línea de producción.
        Retorna lista de errores encontrados.
        """
        errores = []
        
        if not Validador.validar_demanda_diaria(demanda_diaria):
            errores.append("Demanda diaria debe ser un número entero positivo")
        
        if not Validador.validar_tiempo_disponible(tiempo_disponible):
            errores.append("Tiempo disponible debe estar entre 60 y 1440 minutos")
        
        return errores