import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import List, Dict
from utils.estilos import EstilosModernos, COLORES, ESPACIADO


class PanelGraficos:
    """
    Panel para mostrar gráficos y visualizaciones del balanceamiento.
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.frame_principal = None
        self.canvas_utilizacion = None
        self.canvas_comparacion = None
        
        # Configurar estilo de matplotlib
        self._configurar_matplotlib()
        
        self._crear_interfaz()
    
    def _configurar_matplotlib(self):
        """Configura el estilo de matplotlib para que coincida con la aplicación."""
        plt.style.use('default')
        plt.rcParams.update({
            'font.size': 9,
            'font.family': 'sans-serif',
            'axes.labelsize': 10,
            'axes.titlesize': 12,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.facecolor': COLORES['superficie'],
            'axes.facecolor': COLORES['superficie'],
            'axes.edgecolor': COLORES['borde'],
            'axes.linewidth': 0.8,
            'grid.alpha': 0.3
        })
    
    def _crear_interfaz(self):
        """Crea la interfaz del panel de gráficos."""
        # Frame principal con estilo card
        card_frame, shadow_frame = EstilosModernos.crear_frame_card(self.parent, ESPACIADO['normal'])
        self.frame_principal = card_frame
        
        # Título del panel
        titulo = ttk.Label(self.frame_principal, 
                          text="📊 Visualizaciones", 
                          style='Subtitulo.TLabel')
        titulo.pack(anchor='w', pady=(0, ESPACIADO['normal']))
        
        # Crear notebook para organizar gráficos
        notebook = ttk.Notebook(self.frame_principal)
        notebook.pack(fill='both', expand=True)
        
        # Pestaña de utilización por estación
        self._crear_pestana_utilizacion(notebook)
        
        # Pestaña de comparación y análisis
        self._crear_pestana_comparacion(notebook)
        
        # Empaquetar frame principal
        shadow_frame.pack(fill='both', expand=True, padx=2, pady=2)
        card_frame.pack(fill='both', expand=True)
    
    def _crear_pestana_utilizacion(self, notebook):
        """Crea la pestaña de gráfico de utilización."""
        frame_utilizacion = ttk.Frame(notebook, style='Superficie.TFrame', padding=ESPACIADO['pequeno'])
        notebook.add(frame_utilizacion, text='📊 Utilización por Estación')
        
        # Crear figura para gráfico de utilización
        self.fig_utilizacion = Figure(figsize=(10, 6), dpi=100, facecolor=COLORES['superficie'])
        self.ax_utilizacion = self.fig_utilizacion.add_subplot(111)
        
        # Canvas para matplotlib
        self.canvas_utilizacion = FigureCanvasTkAgg(self.fig_utilizacion, frame_utilizacion)
        self.canvas_utilizacion.get_tk_widget().pack(fill='both', expand=True)
        
        # Inicializar gráfico vacío
        self._inicializar_grafico_utilizacion()
    
    def _crear_pestana_comparacion(self, notebook):
        """Crea la pestaña de gráficos de comparación."""
        frame_comparacion = ttk.Frame(notebook, style='Superficie.TFrame', padding=ESPACIADO['pequeno'])
        notebook.add(frame_comparacion, text='📈 Análisis Comparativo')
        
        # Crear figura para gráficos de comparación
        self.fig_comparacion = Figure(figsize=(12, 8), dpi=100, facecolor=COLORES['superficie'])
        
        # Canvas para matplotlib
        self.canvas_comparacion = FigureCanvasTkAgg(self.fig_comparacion, frame_comparacion)
        self.canvas_comparacion.get_tk_widget().pack(fill='both', expand=True)
        
        # Inicializar gráficos vacíos
        self._inicializar_graficos_comparacion()
    
    def _inicializar_grafico_utilizacion(self):
        """Inicializa el gráfico de utilización vacío."""
        self.ax_utilizacion.clear()
        self.ax_utilizacion.set_title('Utilización por Estación', fontsize=14, fontweight='bold')
        self.ax_utilizacion.set_xlabel('Estación')
        self.ax_utilizacion.set_ylabel('Utilización (%)')
        self.ax_utilizacion.set_ylim(0, 100)
        self.ax_utilizacion.grid(True, alpha=0.3)
        
        # Líneas de referencia
        self.ax_utilizacion.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='Capacidad Máxima')
        self.ax_utilizacion.axhline(y=85, color='orange', linestyle='--', alpha=0.7, label='Utilización Alta')
        self.ax_utilizacion.axhline(y=70, color='green', linestyle='--', alpha=0.7, label='Utilización Óptima')
        
        self.ax_utilizacion.legend()
        self.ax_utilizacion.text(0.5, 0.5, 'Ejecute el balanceamiento para ver resultados', 
                                transform=self.ax_utilizacion.transAxes, 
                                ha='center', va='center', fontsize=12, alpha=0.6)
        
        self.fig_utilizacion.tight_layout()
        self.canvas_utilizacion.draw()
    
    def _inicializar_graficos_comparacion(self):
        """Inicializa los gráficos de comparación vacíos."""
        self.fig_comparacion.clear()
        
        # Crear subplots
        gs = self.fig_comparacion.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Gráfico de barras de tiempo por estación
        self.ax_tiempos = self.fig_comparacion.add_subplot(gs[0, 0])
        self.ax_tiempos.set_title('Tiempo Total por Estación', fontweight='bold')
        self.ax_tiempos.set_xlabel('Estación')
        self.ax_tiempos.set_ylabel('Tiempo (min)')
        
        # Gráfico de pastel de distribución de carga
        self.ax_pastel = self.fig_comparacion.add_subplot(gs[0, 1])
        self.ax_pastel.set_title('Distribución de Carga de Trabajo', fontweight='bold')
        
        # Gráfico de línea de eficiencia
        self.ax_eficiencia = self.fig_comparacion.add_subplot(gs[1, 0])
        self.ax_eficiencia.set_title('Métricas de Eficiencia', fontweight='bold')
        self.ax_eficiencia.set_ylabel('Valor (%)')
        
        # Gráfico de barras horizontales de tareas por estación
        self.ax_tareas = self.fig_comparacion.add_subplot(gs[1, 1])
        self.ax_tareas.set_title('Número de Tareas por Estación', fontweight='bold')
        self.ax_tareas.set_xlabel('Número de Tareas')
        
        # Texto informativo
        for ax in [self.ax_tiempos, self.ax_pastel, self.ax_eficiencia, self.ax_tareas]:
            ax.text(0.5, 0.5, 'Sin datos', transform=ax.transAxes, 
                   ha='center', va='center', alpha=0.6)
        
        self.fig_comparacion.tight_layout()
        self.canvas_comparacion.draw()
    
    def actualizar_graficos(self, estaciones: List, metricas: Dict):
        """Actualiza todos los gráficos con nuevos datos."""
        if not estaciones:
            self._inicializar_grafico_utilizacion()
            self._inicializar_graficos_comparacion()
            return
        
        self._actualizar_grafico_utilizacion(estaciones)
        self._actualizar_graficos_comparacion(estaciones, metricas)
    
    def _actualizar_grafico_utilizacion(self, estaciones: List):
        """Actualiza el gráfico de utilización por estación."""
        self.ax_utilizacion.clear()
        
        # Preparar datos
        numeros_estacion = [f"Est. {est.numero}" for est in estaciones]
        utilizaciones = [est.calcular_utilizacion() for est in estaciones]
        
        # Crear colores basados en utilización
        colores = []
        for util in utilizaciones:
            if util >= 98:
                colores.append('#DC3545')  # Rojo - Cuello de botella
            elif util >= 85:
                colores.append('#FFC107')  # Amarillo - Alta carga
            elif util >= 70:
                colores.append('#28A745')  # Verde - Óptima
            else:
                colores.append('#17A2B8')  # Azul - Baja carga
        
        # Crear gráfico de barras
        barras = self.ax_utilizacion.bar(numeros_estacion, utilizaciones, color=colores, alpha=0.8, edgecolor='white', linewidth=1)
        
        # Configurar gráfico
        self.ax_utilizacion.set_title('Utilización por Estación', fontsize=14, fontweight='bold')
        self.ax_utilizacion.set_xlabel('Estación', fontsize=12)
        self.ax_utilizacion.set_ylabel('Utilización (%)', fontsize=12)
        self.ax_utilizacion.set_ylim(0, max(105, max(utilizaciones) * 1.1))
        self.ax_utilizacion.grid(True, alpha=0.3)
        
        # Líneas de referencia
        self.ax_utilizacion.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='Capacidad Máxima (100%)')
        self.ax_utilizacion.axhline(y=85, color='orange', linestyle='--', alpha=0.7, label='Utilización Alta (85%)')
        self.ax_utilizacion.axhline(y=70, color='green', linestyle='--', alpha=0.7, label='Utilización Óptima (70%)')
        
        # Agregar valores sobre las barras
        for i, (barra, util) in enumerate(zip(barras, utilizaciones)):
            altura = barra.get_height()
            self.ax_utilizacion.text(barra.get_x() + barra.get_width()/2., altura + 1,
                                   f'{util:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Agregar información de tareas en cada barra
        for i, (barra, est) in enumerate(zip(barras, estaciones)):
            tareas_texto = ', '.join(est.obtener_ids_tareas())
            if len(tareas_texto) > 15:
                tareas_texto = tareas_texto[:12] + '...'
            
            # Texto dentro de la barra si hay espacio
            if barra.get_height() > 20:
                self.ax_utilizacion.text(barra.get_x() + barra.get_width()/2., barra.get_height()/2,
                                       tareas_texto, ha='center', va='center', 
                                       fontsize=8, color='white', fontweight='bold')
        
        self.ax_utilizacion.legend(loc='upper right')
        
        # Rotar etiquetas del eje x si hay muchas estaciones
        if len(estaciones) > 8:
            self.ax_utilizacion.tick_params(axis='x', rotation=45)
        
        self.fig_utilizacion.tight_layout()
        self.canvas_utilizacion.draw()
    
    def _actualizar_graficos_comparacion(self, estaciones: List, metricas: Dict):
        """Actualiza los gráficos de comparación."""
        self.fig_comparacion.clear()
        
        # Crear subplots con mejor distribución
        gs = self.fig_comparacion.add_gridspec(2, 2, hspace=0.4, wspace=0.3)
        
        # 1. Gráfico de barras de tiempo por estación
        self._crear_grafico_tiempos(gs[0, 0], estaciones)
        
        # 2. Gráfico de pastel de distribución de carga
        self._crear_grafico_pastel(gs[0, 1], estaciones)
        
        # 3. Gráfico de métricas de eficiencia
        self._crear_grafico_metricas(gs[1, 0], metricas)
        
        # 4. Gráfico de tareas por estación
        self._crear_grafico_tareas(gs[1, 1], estaciones)
        
        self.fig_comparacion.tight_layout()
        self.canvas_comparacion.draw()
    
    def _crear_grafico_tiempos(self, subplot_spec, estaciones: List):
        """Crea el gráfico de tiempo total por estación."""
        ax = self.fig_comparacion.add_subplot(subplot_spec)
        
        # Preparar datos
        numeros_estacion = [f"E{est.numero}" for est in estaciones]
        tiempos_totales = [est.tiempo_total for est in estaciones]
        tiempo_ciclo = estaciones[0].tiempo_ciclo_max if estaciones else 0
        
        # Crear gráfico de barras
        barras = ax.bar(numeros_estacion, tiempos_totales, color=COLORES['primario'], alpha=0.7)
        
        # Línea de referencia del tiempo de ciclo
        if tiempo_ciclo > 0:
            ax.axhline(y=tiempo_ciclo, color='red', linestyle='--', alpha=0.7, 
                      label=f'Tiempo de Ciclo ({tiempo_ciclo:.1f} min)')
        
        # Configurar gráfico
        ax.set_title('Tiempo Total por Estación', fontweight='bold', fontsize=11)
        ax.set_xlabel('Estación')
        ax.set_ylabel('Tiempo (min)')
        ax.grid(True, alpha=0.3)
        
        # Agregar valores sobre las barras
        for barra, tiempo in zip(barras, tiempos_totales):
            ax.text(barra.get_x() + barra.get_width()/2., barra.get_height() + 0.5,
                   f'{tiempo:.1f}', ha='center', va='bottom', fontsize=9)
        
        if tiempo_ciclo > 0:
            ax.legend(fontsize=8)
    
    def _crear_grafico_pastel(self, subplot_spec, estaciones: List):
        """Crea el gráfico de pastel de distribución de carga."""
        ax = self.fig_comparacion.add_subplot(subplot_spec)
        
        # Preparar datos
        labels = [f"Est. {est.numero}" for est in estaciones]
        tiempos = [est.tiempo_total for est in estaciones]
        
        # Colores personalizados
        colores_pastel = plt.cm.Set3(range(len(estaciones)))
        
        # Crear gráfico de pastel
        wedges, textos, autotextos = ax.pie(tiempos, labels=labels, autopct='%1.1f%%',
                                           colors=colores_pastel, startangle=90)
        
        ax.set_title('Distribución de Carga de Trabajo', fontweight='bold', fontsize=11)
        
        # Mejorar texto
        for autotext in autotextos:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)
    
    def _crear_grafico_metricas(self, subplot_spec, metricas: Dict):
        """Crea el gráfico de métricas de eficiencia."""
        ax = self.fig_comparacion.add_subplot(subplot_spec)
        
        # Extraer métricas
        eficiencia_data = metricas.get('metricas_eficiencia', {})
        produccion_data = metricas.get('metricas_produccion', {})
        
        # Preparar datos
        categorias = ['Eficiencia\nLínea', 'Utilización\nPromedio', 'Utilización\nCapacidad']
        valores = [
            eficiencia_data.get('eficiencia_linea', 0),
            eficiencia_data.get('utilizacion_promedio', 0),
            produccion_data.get('utilizacion_capacidad', 0)
        ]
        
        # Colores basados en el valor
        colores_metricas = []
        for valor in valores:
            if valor >= 90:
                colores_metricas.append('#28A745')  # Verde excelente
            elif valor >= 80:
                colores_metricas.append('#FFC107')  # Amarillo bueno
            elif valor >= 70:
                colores_metricas.append('#FD7E14')  # Naranja regular
            else:
                colores_metricas.append('#DC3545')  # Rojo malo
        
        # Crear gráfico de barras
        barras = ax.bar(categorias, valores, color=colores_metricas, alpha=0.8)
        
        # Configurar gráfico
        ax.set_title('Métricas de Eficiencia', fontweight='bold', fontsize=11)
        ax.set_ylabel('Porcentaje (%)')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        
        # Agregar valores sobre las barras
        for barra, valor in zip(barras, valores):
            ax.text(barra.get_x() + barra.get_width()/2., barra.get_height() + 2,
                   f'{valor:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Líneas de referencia
        ax.axhline(y=90, color='green', linestyle='--', alpha=0.5, label='Excelente (90%)')
        ax.axhline(y=80, color='orange', linestyle='--', alpha=0.5, label='Bueno (80%)')
        ax.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Aceptable (70%)')
        
        ax.legend(fontsize=7, loc='upper right')
    
    def _crear_grafico_tareas(self, subplot_spec, estaciones: List):
        """Crea el gráfico de número de tareas por estación."""
        ax = self.fig_comparacion.add_subplot(subplot_spec)
        
        # Preparar datos
        numeros_estacion = [f"Est. {est.numero}" for est in estaciones]
        num_tareas = [len(est.tareas_asignadas) for est in estaciones]
        
        # Crear gráfico de barras horizontales
        barras = ax.barh(numeros_estacion, num_tareas, color=COLORES['secundario'], alpha=0.7)
        
        # Configurar gráfico
        ax.set_title('Número de Tareas por Estación', fontweight='bold', fontsize=11)
        ax.set_xlabel('Número de Tareas')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Agregar valores al final de las barras
        for barra, num in zip(barras, num_tareas):
            ax.text(barra.get_width() + 0.1, barra.get_y() + barra.get_height()/2.,
                   str(num), ha='left', va='center', fontsize=9, fontweight='bold')
        
        # Ajustar límites
        if num_tareas:
            ax.set_xlim(0, max(num_tareas) * 1.2)
    
    def limpiar_graficos(self):
        """Limpia todos los gráficos."""
        self._inicializar_grafico_utilizacion()
        self._inicializar_graficos_comparacion()
    
    def exportar_graficos(self, ruta_archivo: str):
        """Exporta los gráficos a un archivo."""
        try:
            # Crear figura combinada para exportar
            fig_export = plt.figure(figsize=(16, 12))
            
            # Copiar gráfico de utilización
            ax1 = fig_export.add_subplot(2, 2, (1, 2))
            # Aquí se copiarían los datos del gráfico de utilización
            
            # Copiar gráficos de comparación
            # Esto requeriría guardar los datos para poder recrear los gráficos
            
            fig_export.suptitle('Análisis de Balanceamiento de Línea - Algoritmo RPW', fontsize=16, fontweight='bold')
            fig_export.tight_layout()
            fig_export.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
            plt.close(fig_export)
            
            return True
        except Exception as e:
            print(f"Error al exportar gráficos: {e}")
            return False