import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import Dict, List

# Importar modelos
from modelos.tarea import Tarea
from modelos.linea_produccion import LineaProduccion

# Importar servicios
from servicios.balanceador_rpw import BalanceadorRPW
from servicios.calculadora_metricas import CalculadoraMetricas

# Importar componentes UI
from ui.componentes.panel_entrada import PanelEntradaDatos
from ui.componentes.panel_resultados import PanelResultados
from ui.componentes.panel_graficos import PanelGraficos

# Importar utilidades
from utils.estilos import EstilosModernos, COLORES, FUENTES, ESPACIADO, UtilsUI
from utils.validacion import ValidacionError


class VentanaPrincipal:
    """
    Ventana principal de la aplicación de balanceamiento de líneas RPW.
    Coordina todos los componentes y maneja la lógica principal.
    """
    
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.linea_produccion = None
            self.balanceador = None
            self.calculadora_metricas = None

            # Componentes UI - inicializar como None
            self.panel_entrada = None
            self.panel_resultados = None
            self.panel_graficos = None

            # Variables de estado - inicializar
            self.datos_balanceados = False
            self.progreso_var = None
            self.label_estado = None

            # Variables para análisis comparativo
            self.tree_eficiencia = None
            self.text_temporal = None
            self.kpi_vars = {}

            self._configurar_ventana()
            self._crear_interfaz()
            self._configurar_eventos()

        except Exception as e:
            # Manejo seguro de errores durante inicialización
            if hasattr(self, 'root'):
                try:
                    messagebox.showerror("Error de Inicialización",
                                       f"Error al inicializar la aplicación:\n\n{str(e)}")
                except:
                    pass
            raise e
    
    def _configurar_ventana(self):
        """Configura la ventana principal."""
        # Configurar propiedades básicas
        self.root.title("Calculadora de Balanceo de Líneas - Algoritmo RPW")
        self.root.state('zoomed')  # Maximizar en Windows
        
        # Intentar maximizar en otros OS
        try:
            self.root.attributes('-zoomed', True)  # Linux
        except:
            try:
                self.root.attributes('-fullscreen', False)  # macOS
                UtilsUI.centrar_ventana(self.root, 1400, 900)
            except:
                UtilsUI.centrar_ventana(self.root, 1400, 900)
        
        # Configurar ícono (si existe)
        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass  # Continuar sin ícono si no existe
        
        # Configurar colores de fondo
        self.root.configure(bg=COLORES['fondo'])
        
        # Configurar tema moderno
        EstilosModernos.configurar_tema_principal()
        
        # Configurar protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_cerrar_aplicacion)
    
    def _crear_interfaz(self):
        """Crea la interfaz principal."""
        # Frame principal
        main_frame = ttk.Frame(self.root, style='Fondo.TFrame', padding=ESPACIADO['normal'])
        main_frame.pack(fill='both', expand=True)
        
        # Crear barra de título personalizada
        self._crear_barra_titulo(main_frame)
        
        # Crear barra de herramientas
        self._crear_barra_herramientas(main_frame)
        
        # Crear área principal con paneles
        self._crear_area_principal(main_frame)
        
        # Crear barra de estado
        self._crear_barra_estado(main_frame)
    
    def _crear_barra_titulo(self, parent):
        """Crea la barra de título con información de la aplicación."""
        frame_titulo = ttk.Frame(parent, style='Superficie.TFrame', padding=ESPACIADO['normal'])
        frame_titulo.pack(fill='x', pady=(0, ESPACIADO['normal']))
        
        # Título principal
        titulo_principal = ttk.Label(frame_titulo, 
                                   text="🏭 Calculadora de Balanceo de Líneas de Producción", 
                                   style='Titulo.TLabel')
        titulo_principal.pack(side='left')
        
        # Información del algoritmo
        info_algoritmo = ttk.Label(frame_titulo, 
                                 text="Algoritmo: Ranked Positional Weight (RPW)", 
                                 style='Secundario.TLabel')
        info_algoritmo.pack(side='right')
        
        # Separador
        separador = EstilosModernos.crear_separador_horizontal(frame_titulo)
        separador.pack(fill='x', pady=(ESPACIADO['pequeno'], 0))
    
    def _crear_barra_herramientas(self, parent):
        """Crea la barra de herramientas con botones principales."""
        frame_herramientas = ttk.Frame(parent, style='Superficie.TFrame', padding=ESPACIADO['normal'])
        frame_herramientas.pack(fill='x', pady=(0, ESPACIADO['normal']))
        
        # Grupo de botones principales
        frame_principales = ttk.Frame(frame_herramientas)
        frame_principales.pack(side='left')
        
        # Botón de balancear (principal)
        self.btn_balancear = ttk.Button(frame_principales, 
                                       text="⚖️ Ejecutar Balanceamiento",
                                       style='Primario.TButton',
                                       command=self._ejecutar_balanceamiento)
        self.btn_balancear.pack(side='left', padx=(0, 10))
        
        # Botón de limpiar
        self.btn_limpiar = ttk.Button(frame_principales,
                                     text="🧹 Limpiar Resultados",
                                     style='Secundario.TButton',
                                     command=self._limpiar_resultados)
        self.btn_limpiar.pack(side='left', padx=(0, 10))
        
        # Grupo de botones de archivo
        frame_archivo = ttk.Frame(frame_herramientas)
        frame_archivo.pack(side='right')
        
        # Botón de exportar
        self.btn_exportar = ttk.Button(frame_archivo,
                                      text="💾 Exportar Resultados",
                                      style='Acento.TButton',
                                      command=self._exportar_resultados)
        self.btn_exportar.pack(side='left', padx=(10, 0))
        
        # Botón de ayuda
        self.btn_ayuda = ttk.Button(frame_archivo,
                                   text="❓ Ayuda",
                                   style='Acento.TButton',
                                   command=self._mostrar_ayuda)
        self.btn_ayuda.pack(side='left', padx=(10, 0))
        
        # Separador
        separador = EstilosModernos.crear_separador_horizontal(frame_herramientas)
        separador.pack(fill='x', pady=(ESPACIADO['pequeno'], 0))
    
    def _crear_area_principal(self, parent):
        """Crea el área principal con los paneles organizados en pestañas."""
        # Crear notebook principal para las pestañas
        self.notebook_principal = ttk.Notebook(parent)
        self.notebook_principal.pack(fill='both', expand=True, padx=ESPACIADO['normal'])

        # Pestaña 1: Configuración y Entrada de Datos
        self._crear_pestana_configuracion()

        # Pestaña 2: Resultados y Análisis Comparativo
        self._crear_pestana_resultados()

        # Pestaña 3: Métricas y Visualizaciones
        self._crear_pestana_metricas()
    
    def _crear_pestana_configuracion(self):
        """Crea la pestaña de configuración y entrada de datos."""
        frame_config = ttk.Frame(self.notebook_principal, style='Fondo.TFrame')
        self.notebook_principal.add(frame_config, text="📋 Configuración de Datos")

        # Panel de entrada de datos ocupa toda la pestaña
        self.panel_entrada = PanelEntradaDatos(frame_config, callback_datos_actualizados=self._on_datos_actualizados)

    def _crear_pestana_resultados(self):
        """Crea la pestaña de resultados con análisis comparativo."""
        frame_resultados = ttk.Frame(self.notebook_principal, style='Fondo.TFrame')
        self.notebook_principal.add(frame_resultados, text="📊 Resultados y Análisis")

        # Dividir en dos secciones verticales
        # Sección superior: Resultados del balanceamiento
        frame_superior = ttk.LabelFrame(frame_resultados, text="Resultados del Balanceamiento",
                                       style='Card.TLabelframe', padding=ESPACIADO['normal'])
        frame_superior.pack(fill='both', expand=True, padx=ESPACIADO['normal'],
                           pady=(ESPACIADO['normal'], ESPACIADO['pequeno']))

        # Sección inferior: Análisis comparativo
        frame_inferior = ttk.LabelFrame(frame_resultados, text="Análisis Comparativo",
                                       style='Card.TLabelframe', padding=ESPACIADO['normal'])
        frame_inferior.pack(fill='both', expand=True, padx=ESPACIADO['normal'],
                           pady=(ESPACIADO['pequeno'], ESPACIADO['normal']))

        # Crear panel de resultados en la sección superior
        self.panel_resultados = PanelResultados(frame_superior)

        # Crear panel de análisis comparativo en la sección inferior
        self._crear_panel_analisis_comparativo(frame_inferior)

    def _crear_pestana_metricas(self):
        """Crea la pestaña de métricas con visualizaciones."""
        frame_metricas = ttk.Frame(self.notebook_principal, style='Fondo.TFrame')
        self.notebook_principal.add(frame_metricas, text="📈 Métricas Visuales")

        # Panel de gráficos y métricas visuales ocupa toda la pestaña
        self.panel_graficos = PanelGraficos(frame_metricas)

    def _crear_panel_analisis_comparativo(self, parent):
        """Crea el panel de análisis comparativo."""
        # Crear notebook interno para diferentes tipos de análisis
        notebook_analisis = ttk.Notebook(parent)
        notebook_analisis.pack(fill='both', expand=True)

        # Sub-pestaña: Eficiencia por estación
        frame_eficiencia = ttk.Frame(notebook_analisis)
        notebook_analisis.add(frame_eficiencia, text="Eficiencia por Estación")

        # Sub-pestaña: Comparación temporal
        frame_temporal = ttk.Frame(notebook_analisis)
        notebook_analisis.add(frame_temporal, text="Análisis Temporal")

        # Sub-pestaña: Indicadores clave
        frame_kpi = ttk.Frame(notebook_analisis)
        notebook_analisis.add(frame_kpi, text="Indicadores Clave (KPI)")

        # Inicializar contenido de análisis comparativo
        self._inicializar_analisis_eficiencia(frame_eficiencia)
        self._inicializar_analisis_temporal(frame_temporal)
        self._inicializar_indicadores_kpi(frame_kpi)

    def _inicializar_analisis_eficiencia(self, parent):
        """Inicializa el análisis de eficiencia por estación."""
        # Crear tabla de eficiencia por estación
        columns = ('Estación', 'Tareas', 'Tiempo Total', 'Utilización %', 'Tiempo Ocioso', 'Estado')
        self.tree_eficiencia = ttk.Treeview(parent, columns=columns, show='headings', height=8)

        # Configurar encabezados
        self.tree_eficiencia.heading('Estación', text='Estación')
        self.tree_eficiencia.heading('Tareas', text='Tareas Asignadas')
        self.tree_eficiencia.heading('Tiempo Total', text='Tiempo Total (min)')
        self.tree_eficiencia.heading('Utilización %', text='Utilización %')
        self.tree_eficiencia.heading('Tiempo Ocioso', text='Tiempo Ocioso (min)')
        self.tree_eficiencia.heading('Estado', text='Estado')

        # Configurar anchos de columnas
        self.tree_eficiencia.column('Estación', width=80)
        self.tree_eficiencia.column('Tareas', width=150)
        self.tree_eficiencia.column('Tiempo Total', width=120)
        self.tree_eficiencia.column('Utilización %', width=100)
        self.tree_eficiencia.column('Tiempo Ocioso', width=120)
        self.tree_eficiencia.column('Estado', width=100)

        # Scrollbar para la tabla
        scrollbar_ef = ttk.Scrollbar(parent, orient='vertical', command=self.tree_eficiencia.yview)
        self.tree_eficiencia.configure(yscrollcommand=scrollbar_ef.set)

        # Pack de componentes
        self.tree_eficiencia.pack(side='left', fill='both', expand=True)
        scrollbar_ef.pack(side='right', fill='y')

    def _inicializar_analisis_temporal(self, parent):
        """Inicializa el análisis temporal."""
        # Label informativo
        info_label = ttk.Label(parent, text="📊 Análisis de tendencias temporales y evolución de métricas",
                              style='Subtitulo.TLabel')
        info_label.pack(pady=ESPACIADO['normal'])

        # Frame para métricas temporales
        frame_metricas = ttk.Frame(parent)
        frame_metricas.pack(fill='both', expand=True, padx=ESPACIADO['normal'])

        # Crear text widget para mostrar análisis temporal
        self.text_temporal = tk.Text(frame_metricas, height=10, wrap='word',
                                   font=FUENTES['normal'], state='disabled')
        scrollbar_temp = ttk.Scrollbar(frame_metricas, orient='vertical', command=self.text_temporal.yview)
        self.text_temporal.configure(yscrollcommand=scrollbar_temp.set)

        self.text_temporal.pack(side='left', fill='both', expand=True)
        scrollbar_temp.pack(side='right', fill='y')

    def _inicializar_indicadores_kpi(self, parent):
        """Inicializa los indicadores clave de rendimiento."""
        # Frame principal para KPIs
        frame_kpis = ttk.Frame(parent)
        frame_kpis.pack(fill='both', expand=True, padx=ESPACIADO['normal'], pady=ESPACIADO['normal'])

        # Crear grid de KPIs (2x3)
        self.kpi_vars = {}
        kpis = [
            ('eficiencia_linea', 'Eficiencia de Línea', '%'),
            ('balance_suavidad', 'Balance de Suavidad', ''),
            ('tiempo_ocioso_total', 'Tiempo Ocioso Total', 'min'),
            ('estaciones_optimas', 'Desviación vs Óptimo', 'estaciones'),
            ('capacidad_produccion', 'Capacidad de Producción', 'und/día'),
            ('indice_productividad', 'Índice de Productividad', '')
        ]

        for i, (key, nombre, unidad) in enumerate(kpis):
            row = i // 2
            col = i % 2

            # Frame para cada KPI
            kpi_frame = ttk.LabelFrame(frame_kpis, text=nombre, padding=ESPACIADO['normal'])
            kpi_frame.grid(row=row, column=col, padx=ESPACIADO['normal'], pady=ESPACIADO['normal'],
                          sticky='ew')

            # Variable para el valor
            var = tk.StringVar(value="--")
            self.kpi_vars[key] = var

            # Label para el valor
            valor_label = ttk.Label(kpi_frame, textvariable=var, style='Titulo.TLabel')
            valor_label.pack()

            # Label para la unidad
            if unidad:
                unidad_label = ttk.Label(kpi_frame, text=unidad, style='Secundario.TLabel')
                unidad_label.pack()

        # Configurar peso de las columnas
        frame_kpis.grid_columnconfigure(0, weight=1)
        frame_kpis.grid_columnconfigure(1, weight=1)

    def _actualizar_analisis_comparativo(self, estaciones, metricas):
        """Actualiza los datos del análisis comparativo."""
        # Actualizar análisis de eficiencia por estación
        self._actualizar_eficiencia_estaciones(estaciones)

        # Actualizar análisis temporal
        self._actualizar_analisis_temporal(metricas)

        # Actualizar KPIs
        self._actualizar_kpis(metricas)

    def _actualizar_eficiencia_estaciones(self, estaciones):
        """Actualiza la tabla de eficiencia por estación."""
        # Limpiar tabla existente
        for item in self.tree_eficiencia.get_children():
            self.tree_eficiencia.delete(item)

        # Agregar datos de cada estación
        for estacion in estaciones:
            utilizacion = estacion.calcular_utilizacion()
            tiempo_ocioso = estacion.obtener_tiempo_ocioso()
            tareas_texto = ", ".join(estacion.obtener_ids_tareas())

            # Determinar estado basado en utilización
            if utilizacion >= 90:
                estado = "🔴 Sobrecargada"
            elif utilizacion >= 75:
                estado = "🟡 Alta"
            elif utilizacion >= 50:
                estado = "🟢 Óptima"
            else:
                estado = "🔵 Baja"

            # Insertar fila
            self.tree_eficiencia.insert('', 'end', values=(
                f"Estación {estacion.numero}",
                tareas_texto,
                f"{estacion.tiempo_total:.2f}",
                f"{utilizacion:.1f}%",
                f"{tiempo_ocioso:.2f}",
                estado
            ))

    def _actualizar_analisis_temporal(self, metricas):
        """Actualiza el análisis temporal."""
        # Generar texto de análisis temporal
        eficiencia = metricas.get('metricas_eficiencia', {})
        basicas = metricas.get('metricas_basicas', {})

        texto_analisis = f"""
📊 ANÁLISIS TEMPORAL Y TENDENCIAS

⏱️  Tiempo de Ciclo: {basicas.get('tiempo_ciclo', 0):.2f} minutos
🎯 Demanda Objetivo: {basicas.get('demanda_diaria', 0)} unidades/día
📈 Eficiencia Alcanzada: {eficiencia.get('eficiencia_linea', 0):.1f}%

🔍 EVALUACIÓN DE RENDIMIENTO:
• Número de estaciones utilizadas: {basicas.get('numero_estaciones', 0)}
• Estaciones mínimas teóricas: {basicas.get('numero_estaciones_minimo_teorico', 0)}
• Diferencia: +{basicas.get('numero_estaciones', 0) - basicas.get('numero_estaciones_minimo_teorico', 0)} estaciones

⚖️  BALANCE Y EQUILIBRIO:
• Índice de suavidad: {eficiencia.get('indice_suavidad', 0):.2f}
• Tiempo ocioso total: {eficiencia.get('tiempo_ocioso_total', 0):.2f} minutos
• Utilización promedio: {eficiencia.get('utilizacion_promedio', 0):.1f}%

📋 RECOMENDACIONES:
"""

        # Agregar recomendaciones basadas en métricas
        if eficiencia.get('eficiencia_linea', 0) < 70:
            texto_analisis += "• ⚠️  Eficiencia baja - Considerar redistribución de tareas\n"
        if eficiencia.get('indice_suavidad', 0) > 2.0:
            texto_analisis += "• ⚠️  Desbalance alto - Revisar asignaciones por tiempo\n"
        if basicas.get('numero_estaciones', 0) > basicas.get('numero_estaciones_minimo_teorico', 0) + 2:
            texto_analisis += "• ⚠️  Exceso de estaciones - Optimización posible\n"

        if eficiencia.get('eficiencia_linea', 0) >= 85:
            texto_analisis += "• ✅ Excelente eficiencia alcanzada\n"
        if eficiencia.get('indice_suavidad', 0) <= 1.0:
            texto_analisis += "• ✅ Buen balance entre estaciones\n"

        # Actualizar widget de texto
        self.text_temporal.configure(state='normal')
        self.text_temporal.delete('1.0', tk.END)
        self.text_temporal.insert('1.0', texto_analisis)
        self.text_temporal.configure(state='disabled')

    def _actualizar_kpis(self, metricas):
        """Actualiza los indicadores clave de rendimiento."""
        eficiencia = metricas.get('metricas_eficiencia', {})
        basicas = metricas.get('metricas_basicas', {})
        produccion = metricas.get('metricas_produccion', {})

        # Actualizar valores de KPIs
        self.kpi_vars['eficiencia_linea'].set(f"{eficiencia.get('eficiencia_linea', 0):.1f}")
        self.kpi_vars['balance_suavidad'].set(f"{eficiencia.get('indice_suavidad', 0):.2f}")
        self.kpi_vars['tiempo_ocioso_total'].set(f"{eficiencia.get('tiempo_ocioso_total', 0):.1f}")

        # Calcular desviación vs óptimo
        actual = basicas.get('numero_estaciones', 0)
        optimo = basicas.get('numero_estaciones_minimo_teorico', 0)
        desviacion = actual - optimo
        self.kpi_vars['estaciones_optimas'].set(f"+{desviacion}" if desviacion > 0 else f"{desviacion}")

        # Capacidad de producción
        capacidad = produccion.get('capacidad_maxima_diaria', basicas.get('demanda_diaria', 0))
        self.kpi_vars['capacidad_produccion'].set(f"{capacidad:.0f}")

        # Índice de productividad (eficiencia normalizada)
        productividad = eficiencia.get('eficiencia_linea', 0) / 100
        self.kpi_vars['indice_productividad'].set(f"{productividad:.2f}")

    def _limpiar_analisis_comparativo(self):
        """Limpia los datos del análisis comparativo."""
        # Limpiar tabla de eficiencia
        if hasattr(self, 'tree_eficiencia'):
            for item in self.tree_eficiencia.get_children():
                self.tree_eficiencia.delete(item)

        # Limpiar análisis temporal
        if hasattr(self, 'text_temporal'):
            self.text_temporal.configure(state='normal')
            self.text_temporal.delete('1.0', tk.END)
            self.text_temporal.insert('1.0', "No hay datos de análisis disponibles.\n\nEjecute el balanceamiento para ver el análisis.")
            self.text_temporal.configure(state='disabled')

        # Resetear KPIs
        if hasattr(self, 'kpi_vars'):
            for var in self.kpi_vars.values():
                var.set("--")
    
    def _crear_barra_estado(self, parent):
        """Crea la barra de estado."""
        frame_estado = ttk.Frame(parent, style='Superficie.TFrame', padding=ESPACIADO['pequeno'])
        frame_estado.pack(fill='x', side='bottom')
        
        # Separador
        separador = EstilosModernos.crear_separador_horizontal(frame_estado)
        separador.pack(fill='x', pady=(0, ESPACIADO['pequeno']))
        
        # Label de estado
        self.label_estado = ttk.Label(frame_estado, 
                                     text="Listo - Configure los datos y ejecute el balanceamiento",
                                     style='Secundario.TLabel')
        self.label_estado.pack(side='left')
        
        # Barra de progreso
        self.progreso_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame_estado, 
                                           variable=self.progreso_var,
                                           maximum=100,
                                           length=200)
        self.progress_bar.pack(side='right', padx=(10, 0))
        
        # Label de progreso
        self.label_progreso = ttk.Label(frame_estado, text="", style='Secundario.TLabel')
        self.label_progreso.pack(side='right', padx=(10, 0))
    
    def _configurar_eventos(self):
        """Configura los eventos y atajos de teclado."""
        # Atajos de teclado
        self.root.bind('<Control-r>', lambda e: self._ejecutar_balanceamiento())
        self.root.bind('<Control-l>', lambda e: self._limpiar_resultados())
        self.root.bind('<Control-s>', lambda e: self._exportar_resultados())
        self.root.bind('<F1>', lambda e: self._mostrar_ayuda())
        self.root.bind('<Escape>', lambda e: self._on_cerrar_aplicacion())
        
        # Configurar tooltips
        EstilosModernos.crear_tooltip(self.btn_balancear, "Ctrl+R: Ejecutar balanceamiento con algoritmo RPW")
        EstilosModernos.crear_tooltip(self.btn_limpiar, "Ctrl+L: Limpiar todos los resultados")
        EstilosModernos.crear_tooltip(self.btn_exportar, "Ctrl+S: Exportar resultados a archivo")
        EstilosModernos.crear_tooltip(self.btn_ayuda, "F1: Mostrar ayuda y documentación")
    
    def _on_datos_actualizados(self):
        """Callback cuando se actualizan los datos de entrada."""
        self.datos_balanceados = False
        self._actualizar_estado("Datos actualizados - Ejecute el balanceamiento para ver resultados")
    
    def _ejecutar_balanceamiento(self):
        """Ejecuta el algoritmo de balanceamiento RPW."""
        try:
            # Validar datos de entrada
            if not self._validar_datos_entrada():
                return
            
            # Actualizar estado
            self._actualizar_estado("Iniciando balanceamiento...")
            self.progreso_var.set(10)
            self.root.update()
            
            # Crear línea de producción
            self._crear_linea_produccion()
            self.progreso_var.set(30)
            self.root.update()
            
            # Ejecutar balanceamiento en hilo separado para no bloquear UI
            threading.Thread(target=self._ejecutar_balanceamiento_async, daemon=True).start()
            
        except Exception as e:
            self._manejar_error("Error al iniciar balanceamiento", str(e))
    
    def _ejecutar_balanceamiento_async(self):
        """Ejecuta el balanceamiento de forma asíncrona."""
        try:
            # Crear balanceador
            self.balanceador = BalanceadorRPW(self.linea_produccion)
            
            # Actualizar progreso
            self.root.after(0, lambda: self.progreso_var.set(50))
            self.root.after(0, lambda: self._actualizar_estado("Calculando pesos posicionales..."))
            
            # Ejecutar balanceamiento
            estaciones, estadisticas = self.balanceador.balancear()
            
            # Actualizar progreso
            self.root.after(0, lambda: self.progreso_var.set(70))
            self.root.after(0, lambda: self._actualizar_estado("Calculando métricas..."))
            
            # Calcular métricas completas
            self.calculadora_metricas = CalculadoraMetricas(self.linea_produccion)
            metricas_completas = self.calculadora_metricas.calcular_todas_las_metricas()
            
            # Actualizar progreso
            self.root.after(0, lambda: self.progreso_var.set(90))
            self.root.after(0, lambda: self._actualizar_estado("Actualizando interfaz..."))
            
            # Actualizar UI en el hilo principal
            self.root.after(0, lambda: self._finalizar_balanceamiento(estaciones, metricas_completas))
            
        except Exception as e:
            self.root.after(0, lambda: self._manejar_error("Error durante balanceamiento", str(e)))
    
    def _finalizar_balanceamiento(self, estaciones, metricas):
        """Finaliza el balanceamiento y actualiza la UI."""
        try:
            # Actualizar paneles principales
            if hasattr(self, 'panel_resultados') and self.panel_resultados:
                self.panel_resultados.actualizar_resultados(estaciones, metricas)

            if hasattr(self, 'panel_graficos') and self.panel_graficos:
                self.panel_graficos.actualizar_graficos(estaciones, metricas)

            # Actualizar análisis comparativo en la pestaña de resultados
            self._actualizar_analisis_comparativo(estaciones, metricas)

            # Marcar como balanceado
            self.datos_balanceados = True

            # Actualizar estado final
            num_estaciones = len(estaciones)
            eficiencia = metricas.get('metricas_eficiencia', {}).get('eficiencia_linea', 0)

            mensaje_final = f"✅ Balanceamiento completado: {num_estaciones} estaciones, {eficiencia:.1f}% eficiencia"
            self._actualizar_estado(mensaje_final)

            # Completar barra de progreso
            self.progreso_var.set(100)

            # Cambiar automáticamente a la pestaña de resultados
            if hasattr(self, 'notebook_principal'):
                self.notebook_principal.select(1)  # Índice 1 = pestaña de resultados

            # Limpiar progreso después de un momento
            self.root.after(3000, lambda: self.progreso_var.set(0))

            # Mostrar resumen
            self._mostrar_resumen_balanceamiento(estaciones, metricas)
            
        except Exception as e:
            self._manejar_error("Error al finalizar balanceamiento", str(e))
    
    def _validar_datos_entrada(self) -> bool:
        """Valida que los datos de entrada sean correctos."""
        try:
            # Obtener datos
            datos_tareas = self.panel_entrada.obtener_datos_tareas()
            config_linea = self.panel_entrada.obtener_configuracion_linea()
            
            # Validaciones básicas
            if not datos_tareas:
                messagebox.showerror("Error de Validación", "Debe definir al menos una tarea")
                return False
            
            if config_linea['demanda_diaria'] <= 0:
                messagebox.showerror("Error de Validación", "La demanda diaria debe ser mayor a 0")
                return False
            
            if config_linea['tiempo_disponible'] <= 0:
                messagebox.showerror("Error de Validación", "El tiempo disponible debe ser mayor a 0")
                return False
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error de Validación", f"Error al validar datos: {str(e)}")
            return False
    
    def _crear_linea_produccion(self):
        """Crea la línea de producción con los datos ingresados."""
        # Obtener configuración
        config = self.panel_entrada.obtener_configuracion_linea()
        
        # Crear línea de producción
        self.linea_produccion = LineaProduccion(
            demanda_diaria=config['demanda_diaria'],
            tiempo_disponible=config['tiempo_disponible']
        )
        
        # Agregar tareas
        datos_tareas = self.panel_entrada.obtener_datos_tareas()
        for datos in datos_tareas:
            tarea = Tarea(
                id=datos['id'],
                descripcion=datos['descripcion'],
                tiempo=datos['tiempo'],
                precedencias=datos.get('precedencias', [])
            )
            self.linea_produccion.agregar_tarea(tarea)

    def _limpiar_resultados(self):
        """Limpia todos los resultados y datos."""
        try:
            # Limpiar paneles solo si están inicializados
            if hasattr(self, 'panel_resultados') and self.panel_resultados:
                self.panel_resultados.limpiar_resultados()
            if hasattr(self, 'panel_graficos') and self.panel_graficos:
                self.panel_graficos.limpiar_graficos()

            # Limpiar análisis comparativo
            self._limpiar_analisis_comparativo()

            # Resetear estado
            self.datos_balanceados = False
            self.linea_produccion = None
            self.balanceador = None
            self.calculadora_metricas = None

            # Actualizar estado solo si está inicializado
            if hasattr(self, 'label_estado') and self.label_estado:
                self._actualizar_estado("Resultados limpiados - Configure nuevos datos")
            if hasattr(self, 'progreso_var') and self.progreso_var:
                self.progreso_var.set(0)

        except Exception as e:
            self._manejar_error_seguro("Error al limpiar resultados", str(e))

    def _exportar_resultados(self):
        """Exporta los resultados a un archivo."""
        try:
            if not self.datos_balanceados:
                messagebox.showwarning("Exportar Resultados",
                                     "No hay resultados para exportar. Ejecute el balanceamiento primero.")
                return

            # Solicitar archivo de destino
            archivo = filedialog.asksaveasfilename(
                title="Exportar Resultados",
                defaultextension=".txt",
                filetypes=[
                    ("Archivos de texto", "*.txt"),
                    ("Archivos CSV", "*.csv"),
                    ("Todos los archivos", "*.*")
                ]
            )

            if archivo:
                self._generar_reporte_exportacion(archivo)
                messagebox.showinfo("Exportar Resultados",
                                  f"Resultados exportados exitosamente a:\n{archivo}")

        except Exception as e:
            self._manejar_error("Error al exportar resultados", str(e))

    def _generar_reporte_exportacion(self, archivo: str):
        """Genera el reporte de exportación."""
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write("REPORTE DE BALANCEAMIENTO DE LÍNEA - ALGORITMO RPW\n")
                f.write("=" * 60 + "\n\n")

                # Información general
                f.write("CONFIGURACIÓN DE LA LÍNEA:\n")
                f.write(f"Demanda diaria: {self.linea_produccion.demanda_diaria} unidades\n")
                f.write(f"Tiempo disponible: {self.linea_produccion.tiempo_disponible} minutos\n")
                f.write(f"Tiempo de ciclo: {self.linea_produccion.obtener_tiempo_ciclo():.2f} minutos\n\n")

                # Estaciones y asignaciones
                f.write("ESTACIONES Y ASIGNACIONES:\n")
                for estacion in self.linea_produccion.estaciones:
                    f.write(f"Estación {estacion.numero}:\n")
                    f.write(f"  Tareas: {', '.join(estacion.obtener_ids_tareas())}\n")
                    f.write(f"  Tiempo total: {estacion.tiempo_total:.2f} min\n")
                    f.write(f"  Utilización: {estacion.calcular_utilizacion():.1f}%\n")
                    f.write(f"  Tiempo ocioso: {estacion.obtener_tiempo_ocioso():.2f} min\n\n")

                # Métricas
                if self.calculadora_metricas:
                    metricas = self.calculadora_metricas.calcular_todas_las_metricas()
                    f.write("MÉTRICAS DE EFICIENCIA:\n")
                    eficiencia = metricas.get('metricas_eficiencia', {})
                    f.write(f"Eficiencia de línea: {eficiencia.get('eficiencia_linea', 0):.1f}%\n")
                    f.write(f"Balance de suavidad: {eficiencia.get('indice_suavidad', 0):.2f}\n")
                    f.write(f"Tiempo ocioso total: {eficiencia.get('tiempo_ocioso_total', 0):.2f} min\n")

        except Exception as e:
            raise Exception(f"Error al escribir archivo: {str(e)}")

    def _mostrar_ayuda(self):
        """Muestra la ventana de ayuda."""
        try:
            ventana_ayuda = tk.Toplevel(self.root)
            ventana_ayuda.title("Ayuda - Calculadora RPW")
            ventana_ayuda.geometry("800x600")
            ventana_ayuda.configure(bg=COLORES['fondo'])

            # Contenido de ayuda
            texto_ayuda = """
CALCULADORA DE BALANCEAMIENTO DE LÍNEAS - ALGORITMO RPW

¿Qué es el algoritmo RPW?
El algoritmo Ranked Positional Weight (RPW) es un método heurístico para
balancear líneas de producción. Asigna tareas a estaciones de trabajo
minimizando el número de estaciones necesarias.

Cómo usar la aplicación:
1. Configure la demanda diaria y tiempo disponible
2. Agregue tareas con sus tiempos y precedencias
3. Ejecute el balanceamiento (Ctrl+R)
4. Analice los resultados y gráficos
5. Exporte los resultados si es necesario

Atajos de teclado:
- Ctrl+R: Ejecutar balanceamiento
- Ctrl+L: Limpiar resultados
- Ctrl+S: Exportar resultados
- F1: Mostrar esta ayuda
- Esc: Cerrar aplicación

Métricas importantes:
- Eficiencia de línea: % de utilización promedio de las estaciones
- Tiempo de ciclo: Tiempo máximo disponible por estación
- Balance de suavidad: Medida de equilibrio entre estaciones
            """

            # Widget de texto con scroll
            frame_texto = ttk.Frame(ventana_ayuda, padding=20)
            frame_texto.pack(fill='both', expand=True)

            text_widget = tk.Text(frame_texto,
                                wrap='word',
                                font=FUENTES['normal'],
                                bg=COLORES['superficie'],
                                fg=COLORES['texto_primario'])
            scrollbar = ttk.Scrollbar(frame_texto, orient='vertical', command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)

            text_widget.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            text_widget.insert('1.0', texto_ayuda)
            text_widget.configure(state='disabled')

            # Botón cerrar
            btn_cerrar = ttk.Button(ventana_ayuda,
                                  text="Cerrar",
                                  command=ventana_ayuda.destroy)
            btn_cerrar.pack(pady=10)

        except Exception as e:
            self._manejar_error("Error al mostrar ayuda", str(e))

    def _mostrar_resumen_balanceamiento(self, estaciones, metricas):
        """Muestra un resumen del balanceamiento realizado."""
        try:
            eficiencia = metricas.get('metricas_eficiencia', {}).get('eficiencia_linea', 0)
            num_estaciones = len(estaciones)

            mensaje = f"""
✅ BALANCEAMIENTO COMPLETADO

📊 Resultados:
• Número de estaciones: {num_estaciones}
• Eficiencia de línea: {eficiencia:.1f}%
• Tiempo de ciclo: {self.linea_produccion.obtener_tiempo_ciclo():.2f} min

💡 Los resultados se muestran en los paneles de la derecha.
Puede exportar el reporte completo usando Ctrl+S.
            """

            messagebox.showinfo("Balanceamiento Completado", mensaje)

        except Exception as e:
            print(f"Error al mostrar resumen: {e}")  # Log sin mostrar al usuario

    def _actualizar_estado(self, mensaje: str):
        """Actualiza el mensaje de estado."""
        self.label_estado.configure(text=mensaje)
        self.root.update_idletasks()

    def _manejar_error(self, titulo: str, mensaje: str):
        """Maneja errores de la aplicación."""
        if hasattr(self, 'progreso_var') and self.progreso_var:
            self.progreso_var.set(0)
        if hasattr(self, 'label_estado') and self.label_estado:
            self._actualizar_estado(f"❌ Error: {mensaje}")
        messagebox.showerror(titulo, f"Ha ocurrido un error:\n\n{mensaje}")

    def _manejar_error_seguro(self, titulo: str, mensaje: str):
        """Maneja errores de forma segura, incluso si la UI no está completamente inicializada."""
        try:
            # Intentar usar el manejo normal de errores
            if hasattr(self, 'progreso_var') and self.progreso_var:
                self.progreso_var.set(0)
            if hasattr(self, 'label_estado') and self.label_estado:
                self._actualizar_estado(f"❌ Error: {mensaje}")

            # Mostrar mensaje de error
            if hasattr(self, 'root') and self.root:
                messagebox.showerror(titulo, f"Ha ocurrido un error:\n\n{mensaje}")
            else:
                print(f"ERROR: {titulo} - {mensaje}")
        except Exception:
            # Si todo falla, al menos imprimir el error
            print(f"ERROR CRÍTICO: {titulo} - {mensaje}")

    def _on_cerrar_aplicacion(self):
        """Maneja el cierre de la aplicación."""
        try:
            if messagebox.askokcancel("Salir", "¿Está seguro que desea cerrar la aplicación?"):
                self.root.quit()
                self.root.destroy()
        except:
            self.root.quit()

    def ejecutar(self):
        """Ejecuta la aplicación."""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error crítico en la aplicación: {e}")
            messagebox.showerror("Error Crítico",
                               f"Error crítico en la aplicación:\n{e}")


if __name__ == "__main__":
    app = VentanaPrincipal()
    app.ejecutar()