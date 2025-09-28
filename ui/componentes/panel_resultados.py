import tkinter as tk
from tkinter import ttk
from typing import Dict, List
from utils.estilos import EstilosModernos, COLORES, FUENTES, ESPACIADO, UtilsUI


class PanelResultados:
    """
    Panel para mostrar los resultados del balanceamiento y métricas.
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.frame_principal = None
        self.tree_estaciones = None
        self.tree_metricas = None
        self.text_recomendaciones = None
        
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea la interfaz del panel de resultados."""
        # Frame principal con estilo card
        card_frame, shadow_frame = EstilosModernos.crear_frame_card(self.parent, ESPACIADO['normal'])
        self.frame_principal = card_frame
        
        # Título del panel
        titulo = ttk.Label(self.frame_principal, 
                          text="📊 Resultados del Balanceamiento", 
                          style='Subtitulo.TLabel')
        titulo.pack(anchor='w', pady=(0, ESPACIADO['normal']))
        
        # Crear notebook para organizar resultados
        notebook = ttk.Notebook(self.frame_principal)
        notebook.pack(fill='both', expand=True)
        
        # Pestaña de asignaciones
        self._crear_pestana_asignaciones(notebook)
        
        # Pestaña de métricas
        self._crear_pestana_metricas(notebook)
        
        # Pestaña de recomendaciones
        self._crear_pestana_recomendaciones(notebook)
        
        # Empaquetar frame principal
        shadow_frame.pack(fill='both', expand=True, padx=2, pady=2)
        card_frame.pack(fill='both', expand=True)
    
    def _crear_pestana_asignaciones(self, notebook):
        """Crea la pestaña de asignaciones por estación."""
        frame_asignaciones = ttk.Frame(notebook, style='Superficie.TFrame', padding=ESPACIADO['normal'])
        notebook.add(frame_asignaciones, text='🏭 Asignaciones')
        
        # Frame para tabla de estaciones
        frame_tabla = ttk.LabelFrame(frame_asignaciones, text="Asignaciones por Estación", padding=ESPACIADO['normal'])
        frame_tabla.pack(fill='both', expand=True)
        
        # Crear tabla de estaciones
        self._crear_tabla_estaciones(frame_tabla)
    
    def _crear_tabla_estaciones(self, parent):
        """Crea la tabla para mostrar las asignaciones por estación."""
        # Frame para tabla con scrollbar
        frame_tree = ttk.Frame(parent)
        frame_tree.pack(fill='both', expand=True)
        
        # Crear Treeview
        columnas = ('Estacion', 'Tareas', 'Tiempo_Total', 'Utilizacion', 'Tiempo_Ocioso', 'Estado')
        self.tree_estaciones = ttk.Treeview(frame_tree, columns=columnas, show='headings', height=10)
        
        # Configurar columnas
        self.tree_estaciones.heading('Estacion', text='Estación')
        self.tree_estaciones.heading('Tareas', text='Tareas Asignadas')
        self.tree_estaciones.heading('Tiempo_Total', text='Tiempo Total (min)')
        self.tree_estaciones.heading('Utilizacion', text='Utilización (%)')
        self.tree_estaciones.heading('Tiempo_Ocioso', text='Tiempo Ocioso (min)')
        self.tree_estaciones.heading('Estado', text='Estado')
        
        # Ajustar ancho de columnas
        self.tree_estaciones.column('Estacion', width=80, anchor='center')
        self.tree_estaciones.column('Tareas', width=150)
        self.tree_estaciones.column('Tiempo_Total', width=120, anchor='center')
        self.tree_estaciones.column('Utilizacion', width=100, anchor='center')
        self.tree_estaciones.column('Tiempo_Ocioso', width=120, anchor='center')
        self.tree_estaciones.column('Estado', width=100, anchor='center')
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame_tree, orient='vertical', command=self.tree_estaciones.yview)
        scrollbar_h = ttk.Scrollbar(frame_tree, orient='horizontal', command=self.tree_estaciones.xview)
        self.tree_estaciones.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Empaquetar tabla y scrollbars
        self.tree_estaciones.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        # Configurar grid
        frame_tree.grid_rowconfigure(0, weight=1)
        frame_tree.grid_columnconfigure(0, weight=1)
    
    def _crear_pestana_metricas(self, notebook):
        """Crea la pestaña de métricas de rendimiento."""
        frame_metricas = ttk.Frame(notebook, style='Superficie.TFrame', padding=ESPACIADO['normal'])
        notebook.add(frame_metricas, text='📈 Métricas')
        
        # Frame superior para métricas principales
        frame_principales = ttk.LabelFrame(frame_metricas, text="Métricas Principales", padding=ESPACIADO['normal'])
        frame_principales.pack(fill='x', pady=(0, ESPACIADO['normal']))
        
        # Grid para métricas principales (2 columnas)
        self._crear_grid_metricas_principales(frame_principales)
        
        # Frame para métricas detalladas
        frame_detalladas = ttk.LabelFrame(frame_metricas, text="Métricas Detalladas", padding=ESPACIADO['normal'])
        frame_detalladas.pack(fill='both', expand=True)
        
        # Crear tabla de métricas detalladas
        self._crear_tabla_metricas_detalladas(frame_detalladas)
    
    def _crear_grid_metricas_principales(self, parent):
        """Crea el grid de métricas principales."""
        # Labels para métricas principales
        self.labels_metricas = {}
        
        metricas_config = [
            ('Número de Estaciones', 'numero_estaciones'),
            ('Tiempo de Ciclo (min)', 'tiempo_ciclo'),
            ('Eficiencia de Línea (%)', 'eficiencia_linea'),
            ('Utilización Promedio (%)', 'utilizacion_promedio'),
            ('Throughput (unid/min)', 'throughput_real'),
            ('Capacidad Diaria (unid)', 'capacidad_diaria'),
            ('Tiempo Ocioso Total (min)', 'tiempo_ocioso_total'),
            ('Factor de Desbalance (%)', 'desbalance')
        ]
        
        for i, (texto, clave) in enumerate(metricas_config):
            fila = i // 2
            columna = (i % 2) * 2
            
            # Label del nombre
            label_nombre = ttk.Label(parent, text=f"{texto}:", style='Normal.TLabel')
            label_nombre.grid(row=fila, column=columna, sticky='w', padx=(0, 10), pady=2)
            
            # Label del valor
            label_valor = ttk.Label(parent, text="--", style='Normal.TLabel', font=FUENTES['normal'])
            label_valor.grid(row=fila, column=columna+1, sticky='w', padx=(0, 30), pady=2)
            
            self.labels_metricas[clave] = label_valor
    
    def _crear_tabla_metricas_detalladas(self, parent):
        """Crea la tabla de métricas detalladas por estación."""
        # Frame para tabla
        frame_tree = ttk.Frame(parent)
        frame_tree.pack(fill='both', expand=True)
        
        # Crear Treeview para métricas
        columnas = ('Metrica', 'Valor', 'Descripcion')
        self.tree_metricas = ttk.Treeview(frame_tree, columns=columnas, show='headings', height=8)
        
        # Configurar columnas
        self.tree_metricas.heading('Metrica', text='Métrica')
        self.tree_metricas.heading('Valor', text='Valor')
        self.tree_metricas.heading('Descripcion', text='Descripción')
        
        # Ajustar ancho de columnas
        self.tree_metricas.column('Metrica', width=200)
        self.tree_metricas.column('Valor', width=100, anchor='center')
        self.tree_metricas.column('Descripcion', width=300)
        
        # Scrollbar
        scrollbar_metricas = ttk.Scrollbar(frame_tree, orient='vertical', command=self.tree_metricas.yview)
        self.tree_metricas.configure(yscrollcommand=scrollbar_metricas.set)
        
        # Empaquetar
        self.tree_metricas.pack(side='left', fill='both', expand=True)
        scrollbar_metricas.pack(side='right', fill='y')
    
    def _crear_pestana_recomendaciones(self, notebook):
        """Crea la pestaña de recomendaciones."""
        frame_recomendaciones = ttk.Frame(notebook, style='Superficie.TFrame', padding=ESPACIADO['normal'])
        notebook.add(frame_recomendaciones, text='💡 Recomendaciones')
        
        # Frame para indicadores de calidad
        frame_calidad = ttk.LabelFrame(frame_recomendaciones, text="Indicadores de Calidad", padding=ESPACIADO['normal'])
        frame_calidad.pack(fill='x', pady=(0, ESPACIADO['normal']))
        
        # Crear indicadores
        self._crear_indicadores_calidad(frame_calidad)
        
        # Frame para recomendaciones
        frame_rec = ttk.LabelFrame(frame_recomendaciones, text="Recomendaciones de Mejora", padding=ESPACIADO['normal'])
        frame_rec.pack(fill='both', expand=True)
        
        # Crear área de texto para recomendaciones
        self._crear_area_recomendaciones(frame_rec)
    
    def _crear_indicadores_calidad(self, parent):
        """Crea los indicadores de calidad del balanceamiento."""
        self.labels_calidad = {}
        
        # Indicadores en grid
        indicadores = [
            ('Balance Perfecto', 'balance_perfecto'),
            ('Número de Cuellos de Botella', 'numero_cuellos_botella'),
            ('Factor de Suavizado', 'factor_suavizado'),
            ('Índice de Distribución', 'indice_distribucion')
        ]
        
        for i, (texto, clave) in enumerate(indicadores):
            fila = i // 2
            columna = (i % 2) * 2
            
            label_nombre = ttk.Label(parent, text=f"{texto}:", style='Normal.TLabel')
            label_nombre.grid(row=fila, column=columna, sticky='w', padx=(0, 10), pady=5)
            
            label_valor = ttk.Label(parent, text="--", style='Normal.TLabel')
            label_valor.grid(row=fila, column=columna+1, sticky='w', padx=(0, 30), pady=5)
            
            self.labels_calidad[clave] = label_valor
    
    def _crear_area_recomendaciones(self, parent):
        """Crea el área de texto para recomendaciones."""
        # Frame para texto con scrollbar
        frame_texto = ttk.Frame(parent)
        frame_texto.pack(fill='both', expand=True)
        
        # Text widget para recomendaciones
        self.text_recomendaciones = tk.Text(frame_texto, 
                                           height=8,
                                           font=FUENTES['normal'],
                                           bg=COLORES['superficie'],
                                           fg=COLORES['texto_primario'],
                                           wrap=tk.WORD,
                                           state='disabled')
        
        # Scrollbar para texto
        scrollbar_texto = ttk.Scrollbar(frame_texto, orient='vertical', command=self.text_recomendaciones.yview)
        self.text_recomendaciones.configure(yscrollcommand=scrollbar_texto.set)
        
        # Empaquetar
        self.text_recomendaciones.pack(side='left', fill='both', expand=True)
        scrollbar_texto.pack(side='right', fill='y')
    
    def actualizar_resultados(self, estaciones: List, metricas: Dict):
        """Actualiza todos los resultados mostrados."""
        self._actualizar_tabla_estaciones(estaciones, metricas)
        self._actualizar_metricas(metricas)
        self._actualizar_recomendaciones(metricas)
    
    def _actualizar_tabla_estaciones(self, estaciones: List, metricas: Dict):
        """Actualiza la tabla de estaciones."""
        # Limpiar tabla
        for item in self.tree_estaciones.get_children():
            self.tree_estaciones.delete(item)
        
        if not estaciones:
            return
        
        # Agregar datos de estaciones
        for estacion in estaciones:
            # Determinar estado de la estación
            utilizacion = estacion.calcular_utilizacion()
            if utilizacion >= 98:
                estado = "🔴 Cuello Botella"
            elif utilizacion >= 85:
                estado = "🟡 Alta Carga"
            elif utilizacion >= 70:
                estado = "🟢 Óptima"
            else:
                estado = "🔵 Baja Carga"
            
            # Formatear tareas asignadas
            tareas_str = ", ".join(estacion.obtener_ids_tareas())
            if len(tareas_str) > 25:
                tareas_str = tareas_str[:22] + "..."
            
            self.tree_estaciones.insert('', 'end', values=(
                f"Est. {estacion.numero}",
                tareas_str,
                f"{estacion.tiempo_total:.1f}",
                f"{utilizacion:.1f}%",
                f"{estacion.obtener_tiempo_ocioso():.1f}",
                estado
            ))
    
    def _actualizar_metricas(self, metricas: Dict):
        """Actualiza las métricas mostradas."""
        if not metricas:
            return
        
        # Extraer métricas de diferentes categorías
        basicas = metricas.get('metricas_basicas', {})
        eficiencia = metricas.get('metricas_eficiencia', {})
        produccion = metricas.get('metricas_produccion', {})
        
        # Actualizar labels de métricas principales
        actualizaciones = {
            'numero_estaciones': basicas.get('numero_estaciones', 0),
            'tiempo_ciclo': f"{basicas.get('tiempo_ciclo', 0):.2f}",
            'eficiencia_linea': f"{eficiencia.get('eficiencia_linea', 0):.1f}",
            'utilizacion_promedio': f"{eficiencia.get('utilizacion_promedio', 0):.1f}",
            'throughput_real': f"{produccion.get('throughput_real', 0):.3f}",
            'capacidad_diaria': f"{produccion.get('capacidad_diaria', 0):.0f}",
            'tiempo_ocioso_total': f"{eficiencia.get('tiempo_ocioso_total', 0):.1f}",
            'desbalance': f"{eficiencia.get('desbalance', 0):.1f}"
        }
        
        for clave, valor in actualizaciones.items():
            if clave in self.labels_metricas:
                self.labels_metricas[clave].config(text=str(valor))
        
        # Actualizar tabla de métricas detalladas
        self._actualizar_tabla_metricas_detalladas(metricas)
    
    def _actualizar_tabla_metricas_detalladas(self, metricas: Dict):
        """Actualiza la tabla de métricas detalladas."""
        # Limpiar tabla
        for item in self.tree_metricas.get_children():
            self.tree_metricas.delete(item)
        
        # Preparar datos para mostrar
        metricas_detalle = [
            ("Estaciones Mínimas Teóricas", 
             metricas.get('metricas_basicas', {}).get('numero_estaciones_minimo_teorico', 0),
             "Número mínimo de estaciones según teoría"),
            ("Utilización Máxima", 
             f"{metricas.get('metricas_eficiencia', {}).get('utilizacion_maxima', 0):.1f}%",
             "Mayor utilización entre todas las estaciones"),
            ("Utilización Mínima", 
             f"{metricas.get('metricas_eficiencia', {}).get('utilizacion_minima', 0):.1f}%",
             "Menor utilización entre todas las estaciones"),
            ("Tiempo Ocioso Porcentual", 
             f"{metricas.get('metricas_eficiencia', {}).get('tiempo_ocioso_porcentaje', 0):.1f}%",
             "Porcentaje total de tiempo improductivo"),
            ("Throughput Teórico", 
             f"{metricas.get('metricas_produccion', {}).get('throughput_teorico', 0):.3f}",
             "Unidades por minuto (teórico)"),
            ("Utilización de Capacidad", 
             f"{metricas.get('metricas_produccion', {}).get('utilizacion_capacidad', 0):.1f}%",
             "Porcentaje de capacidad utilizada vs demanda")
        ]
        
        # Agregar métricas a la tabla
        for metrica, valor, descripcion in metricas_detalle:
            self.tree_metricas.insert('', 'end', values=(metrica, valor, descripcion))
    
    def _actualizar_recomendaciones(self, metricas: Dict):
        """Actualiza los indicadores de calidad y recomendaciones."""
        calidad = metricas.get('indicadores_calidad', {})
        
        # Actualizar indicadores de calidad
        actualizaciones_calidad = {
            'balance_perfecto': "✅ Sí" if calidad.get('balance_perfecto', False) else "❌ No",
            'numero_cuellos_botella': calidad.get('numero_cuellos_botella', 0),
            'factor_suavizado': f"{calidad.get('factor_suavizado', 0):.1f}",
            'indice_distribucion': f"{calidad.get('indice_distribucion', 0):.1f}%"
        }
        
        for clave, valor in actualizaciones_calidad.items():
            if clave in self.labels_calidad:
                self.labels_calidad[clave].config(text=str(valor))
        
        # Actualizar recomendaciones
        recomendaciones = calidad.get('recomendaciones', [])
        
        self.text_recomendaciones.config(state='normal')
        self.text_recomendaciones.delete(1.0, tk.END)
        
        if recomendaciones:
            texto_recomendaciones = "📋 RECOMENDACIONES DE MEJORA:\n\n"
            for i, rec in enumerate(recomendaciones, 1):
                texto_recomendaciones += f"{i}. {rec}\n\n"
            
            # Agregar interpretación de métricas
            texto_recomendaciones += "📊 INTERPRETACIÓN DE MÉTRICAS:\n\n"
            
            eficiencia_linea = metricas.get('metricas_eficiencia', {}).get('eficiencia_linea', 0)
            if eficiencia_linea >= 90:
                texto_recomendaciones += "• Eficiencia excelente (≥90%): La línea está muy bien balanceada.\n"
            elif eficiencia_linea >= 80:
                texto_recomendaciones += "• Eficiencia buena (80-89%): Hay margen de mejora moderado.\n"
            elif eficiencia_linea >= 70:
                texto_recomendaciones += "• Eficiencia regular (70-79%): Se recomienda rebalancear.\n"
            else:
                texto_recomendaciones += "• Eficiencia baja (<70%): Requiere rediseño del balanceamiento.\n"
            
            utilizacion_promedio = metricas.get('metricas_eficiencia', {}).get('utilizacion_promedio', 0)
            if utilizacion_promedio >= 85:
                texto_recomendaciones += "• Utilización alta: Las estaciones están bien aprovechadas.\n"
            elif utilizacion_promedio >= 70:
                texto_recomendaciones += "• Utilización moderada: Aceptable pero mejorable.\n"
            else:
                texto_recomendaciones += "• Utilización baja: Considere reducir estaciones.\n"
        else:
            texto_recomendaciones = "No hay datos suficientes para generar recomendaciones."
        
        self.text_recomendaciones.insert(1.0, texto_recomendaciones)
        self.text_recomendaciones.config(state='disabled')
    
    def limpiar_resultados(self):
        """Limpia todos los resultados mostrados."""
        # Limpiar tabla de estaciones
        for item in self.tree_estaciones.get_children():
            self.tree_estaciones.delete(item)
        
        # Limpiar tabla de métricas
        for item in self.tree_metricas.get_children():
            self.tree_metricas.delete(item)
        
        # Resetear labels de métricas
        for label in self.labels_metricas.values():
            label.config(text="--")
        
        # Resetear labels de calidad
        for label in self.labels_calidad.values():
            label.config(text="--")
        
        # Limpiar recomendaciones
        self.text_recomendaciones.config(state='normal')
        self.text_recomendaciones.delete(1.0, tk.END)
        self.text_recomendaciones.insert(1.0, "Ejecute el balanceamiento para ver recomendaciones.")
        self.text_recomendaciones.config(state='disabled')