import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Callable
from utils.estilos import EstilosModernos, COLORES, FUENTES, ESPACIADO, UtilsUI
from utils.validacion import Validador, ValidacionError


class PanelEntradaDatos:
    """
    Panel para capturar datos de tareas y configuración de línea de producción.
    """
    
    def __init__(self, parent, callback_datos_actualizados: Callable = None):
        self.parent = parent
        self.callback_datos_actualizados = callback_datos_actualizados
        self.tareas_data = []  # Lista de diccionarios con datos de tareas
        
        self.frame_principal = None
        self.tree_tareas = None
        self.entry_demanda = None
        self.entry_tiempo_disponible = None
        
        self._crear_interfaz()
        self._configurar_validaciones()
    
    def _crear_interfaz(self):
        """Crea la interfaz del panel de entrada."""
        # Frame principal con estilo card
        card_frame, shadow_frame = EstilosModernos.crear_frame_card(self.parent, ESPACIADO['normal'])
        self.frame_principal = card_frame
        
        # Título del panel
        titulo = ttk.Label(self.frame_principal, 
                          text="📝 Configuración de Datos", 
                          style='Subtitulo.TLabel')
        titulo.pack(anchor='w', pady=(0, ESPACIADO['normal']))
        
        # Crear notebook para organizar secciones
        notebook = ttk.Notebook(self.frame_principal)
        notebook.pack(fill='both', expand=True)
        
        # Pestaña de configuración general
        self._crear_pestana_configuracion(notebook)
        
        # Pestaña de tareas
        self._crear_pestana_tareas(notebook)
        
        # Botones de acción
        self._crear_botones_accion()
        
        # Empaquetar frame principal
        shadow_frame.pack(fill='both', expand=True, padx=2, pady=2)
        card_frame.pack(fill='both', expand=True)
    
    def _crear_pestana_configuracion(self, notebook):
        """Crea la pestaña de configuración general."""
        frame_config = ttk.Frame(notebook, style='Superficie.TFrame', padding=ESPACIADO['normal'])
        notebook.add(frame_config, text='⚙️ Configuración General')
        
        # Frame para datos de producción
        frame_produccion = ttk.LabelFrame(frame_config, text="Datos de Producción", padding=ESPACIADO['normal'])
        frame_produccion.pack(fill='x', pady=(0, ESPACIADO['normal']))
        
        # Demanda diaria
        frame_demanda = ttk.Frame(frame_produccion)
        frame_demanda.pack(fill='x', pady=ESPACIADO['pequeno'])
        
        ttk.Label(frame_demanda, text="Demanda Diaria (unidades):", style='Normal.TLabel').pack(side='left')
        self.entry_demanda = ttk.Entry(frame_demanda, width=15, validate='key')
        self.entry_demanda.pack(side='right')
        self.entry_demanda.insert(0, "100")  # Valor por defecto
        
        # Tiempo disponible
        frame_tiempo = ttk.Frame(frame_produccion)
        frame_tiempo.pack(fill='x', pady=ESPACIADO['pequeno'])
        
        ttk.Label(frame_tiempo, text="Tiempo Disponible (minutos):", style='Normal.TLabel').pack(side='left')
        self.entry_tiempo_disponible = ttk.Entry(frame_tiempo, width=15, validate='key')
        self.entry_tiempo_disponible.pack(side='right')
        self.entry_tiempo_disponible.insert(0, "480")  # 8 horas por defecto
        
        # Información calculada
        frame_info = ttk.LabelFrame(frame_config, text="Información Calculada", padding=ESPACIADO['normal'])
        frame_info.pack(fill='x')
        
        self.label_tiempo_ciclo = ttk.Label(frame_info, text="Tiempo de Ciclo: --", style='Normal.TLabel')
        self.label_tiempo_ciclo.pack(anchor='w')
        
        self.label_estaciones_min = ttk.Label(frame_info, text="Estaciones Mínimas: --", style='Normal.TLabel')
        self.label_estaciones_min.pack(anchor='w')
    
    def _crear_pestana_tareas(self, notebook):
        """Crea la pestaña de gestión de tareas."""
        frame_tareas = ttk.Frame(notebook, style='Superficie.TFrame', padding=ESPACIADO['normal'])
        notebook.add(frame_tareas, text='📋 Gestión de Tareas')
        
        # Frame superior para formulario de nueva tarea
        frame_nueva_tarea = ttk.LabelFrame(frame_tareas, text="Agregar Nueva Tarea", padding=ESPACIADO['normal'])
        frame_nueva_tarea.pack(fill='x', pady=(0, ESPACIADO['normal']))
        
        # Primera fila: ID y Descripción
        frame_fila1 = ttk.Frame(frame_nueva_tarea)
        frame_fila1.pack(fill='x', pady=ESPACIADO['pequeno'])
        
        ttk.Label(frame_fila1, text="ID:", style='Normal.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.entry_id = ttk.Entry(frame_fila1, width=12)
        self.entry_id.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(frame_fila1, text="Descripción:", style='Normal.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.entry_descripcion = ttk.Entry(frame_fila1, width=30)
        self.entry_descripcion.grid(row=0, column=3, padx=(0, 20))
        
        # Segunda fila: Tiempo y Precedencias
        frame_fila2 = ttk.Frame(frame_nueva_tarea)
        frame_fila2.pack(fill='x', pady=ESPACIADO['pequeno'])
        
        ttk.Label(frame_fila2, text="Tiempo (min):", style='Normal.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.entry_tiempo = ttk.Entry(frame_fila2, width=12, validate='key')
        self.entry_tiempo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(frame_fila2, text="Precedencias:", style='Normal.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.entry_precedencias = ttk.Entry(frame_fila2, width=30)
        self.entry_precedencias.grid(row=0, column=3, padx=(0, 20))
        
        # Ayuda para precedencias
        help_text = ttk.Label(frame_nueva_tarea, 
                             text="💡 Precedencias: separar IDs con comas (ej: A,B,C)", 
                             style='Secundario.TLabel')
        help_text.pack(anchor='w', pady=(5, 0))
        
        # Botones para gestión de tareas
        frame_botones_tarea = ttk.Frame(frame_nueva_tarea)
        frame_botones_tarea.pack(fill='x', pady=(ESPACIADO['normal'], 0))
        
        btn_agregar = ttk.Button(frame_botones_tarea, text="➕ Agregar Tarea", 
                                style='Primario.TButton', command=self._agregar_tarea)
        btn_agregar.pack(side='left', padx=(0, 10))
        
        btn_modificar = ttk.Button(frame_botones_tarea, text="✏️ Modificar", 
                                  style='Secundario.TButton', command=self._modificar_tarea)
        btn_modificar.pack(side='left', padx=(0, 10))
        
        btn_eliminar = ttk.Button(frame_botones_tarea, text="🗑️ Eliminar", 
                                 style='Error.TButton', command=self._eliminar_tarea)
        btn_eliminar.pack(side='left')
        
        # Tabla de tareas
        frame_tabla = ttk.LabelFrame(frame_tareas, text="Tareas Definidas", padding=ESPACIADO['normal'])
        frame_tabla.pack(fill='both', expand=True)
        
        self._crear_tabla_tareas(frame_tabla)
    
    def _crear_tabla_tareas(self, parent):
        """Crea la tabla para mostrar las tareas."""
        # Frame para tabla con scrollbar
        frame_tree = ttk.Frame(parent)
        frame_tree.pack(fill='both', expand=True)
        
        # Crear Treeview
        columnas = ('ID', 'Descripción', 'Tiempo', 'Precedencias')
        self.tree_tareas = ttk.Treeview(frame_tree, columns=columnas, show='headings', height=8)

        # Configurar columnas
        self.tree_tareas.heading('ID', text='ID')
        self.tree_tareas.heading('Descripción', text='Descripción')
        self.tree_tareas.heading('Tiempo', text='Tiempo (min)')
        self.tree_tareas.heading('Precedencias', text='Precedencias')

        # Ajustar ancho de columnas
        self.tree_tareas.column('ID', width=60, anchor='center')
        self.tree_tareas.column('Descripción', width=250)
        self.tree_tareas.column('Tiempo', width=100, anchor='center')
        self.tree_tareas.column('Precedencias', width=130, anchor='center')
        
        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(frame_tree, orient='vertical', command=self.tree_tareas.yview)
        self.tree_tareas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        self.tree_tareas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind para selección
        self.tree_tareas.bind('<<TreeviewSelect>>', self._on_seleccionar_tarea)
    
    def _crear_botones_accion(self):
        """Crea los botones de acción principales."""
        frame_botones = ttk.Frame(self.frame_principal)
        frame_botones.pack(fill='x', pady=(ESPACIADO['normal'], 0))
        
        # Separador
        separador = EstilosModernos.crear_separador_horizontal(frame_botones)
        separador.pack(fill='x', pady=(0, ESPACIADO['normal']))
        
        # Botones
        btn_cargar_ejemplo = ttk.Button(frame_botones, text="📄 Cargar Ejemplo", 
                                       style='Acento.TButton', command=self._cargar_ejemplo)
        btn_cargar_ejemplo.pack(side='left')
        
        btn_limpiar = ttk.Button(frame_botones, text="🧹 Limpiar Todo", 
                                style='Error.TButton', command=self._limpiar_datos)
        btn_limpiar.pack(side='left', padx=(10, 0))
        
        btn_validar = ttk.Button(frame_botones, text="✅ Validar Datos", 
                                style='Exito.TButton', command=self._validar_todos_datos)
        btn_validar.pack(side='right')
    
    def _configurar_validaciones(self):
        """Configura las validaciones para los campos de entrada."""
        # Validación para campos numéricos
        vcmd_numerico = (self.parent.register(UtilsUI.validar_entrada_numerica), '%P')
        
        self.entry_demanda.configure(validatecommand=vcmd_numerico)
        self.entry_tiempo_disponible.configure(validatecommand=vcmd_numerico)
        self.entry_tiempo.configure(validatecommand=vcmd_numerico)
        
        # Bind para actualización automática
        self.entry_demanda.bind('<KeyRelease>', self._actualizar_calculos)
        self.entry_tiempo_disponible.bind('<KeyRelease>', self._actualizar_calculos)
    
    def _agregar_tarea(self):
        """Agrega una nueva tarea a la lista."""
        try:
            # Obtener datos del formulario
            id_tarea = self.entry_id.get().strip()
            descripcion = self.entry_descripcion.get().strip()
            tiempo_str = self.entry_tiempo.get().strip()
            precedencias_str = self.entry_precedencias.get().strip()
            
            # Procesar precedencias
            precedencias = []
            if precedencias_str:
                precedencias = [p.strip() for p in precedencias_str.split(',') if p.strip()]
            
            # Validar datos
            errores = Validador.validar_datos_completos_tarea(id_tarea, descripcion, tiempo_str, precedencias)
            
            # Verificar que el ID no esté duplicado
            if any(tarea['id'] == id_tarea for tarea in self.tareas_data):
                errores.append(f"Ya existe una tarea con ID '{id_tarea}'")
            
            if errores:
                messagebox.showerror("Error de Validación", "\n".join(errores))
                return
            
            # Convertir tiempo a float
            tiempo = float(tiempo_str)
            
            # Crear datos de tarea
            tarea_data = {
                'id': id_tarea,
                'descripcion': descripcion,
                'tiempo': tiempo,
                'precedencias': precedencias,
                'peso_posicional': 0.0  # Se calculará después
            }
            
            # Agregar a la lista
            self.tareas_data.append(tarea_data)
            
            # Actualizar tabla
            self._actualizar_tabla_tareas()
            
            # Limpiar formulario
            self._limpiar_formulario_tarea()
            
            # Actualizar cálculos
            self._actualizar_calculos()
            
            # Notificar cambios
            self._notificar_cambios()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar tarea: {str(e)}")
    
    def _modificar_tarea(self):
        """Modifica la tarea seleccionada."""
        seleccion = self.tree_tareas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una tarea para modificar")
            return
        
        # Obtener índice de la tarea seleccionada
        item = seleccion[0]
        indices = self.tree_tareas.get_children()
        indice = list(indices).index(item)
        
        # Obtener datos del formulario (similar a agregar_tarea pero modificando)
        try:
            id_tarea = self.entry_id.get().strip()
            descripcion = self.entry_descripcion.get().strip()
            tiempo_str = self.entry_tiempo.get().strip()
            precedencias_str = self.entry_precedencias.get().strip()
            
            precedencias = []
            if precedencias_str:
                precedencias = [p.strip() for p in precedencias_str.split(',') if p.strip()]
            
            # Validar datos
            errores = Validador.validar_datos_completos_tarea(id_tarea, descripcion, tiempo_str, precedencias)
            
            # Verificar duplicado de ID (excepto la tarea actual)
            for i, tarea in enumerate(self.tareas_data):
                if i != indice and tarea['id'] == id_tarea:
                    errores.append(f"Ya existe una tarea con ID '{id_tarea}'")
                    break
            
            if errores:
                messagebox.showerror("Error de Validación", "\n".join(errores))
                return
            
            # Actualizar datos
            self.tareas_data[indice] = {
                'id': id_tarea,
                'descripcion': descripcion,
                'tiempo': float(tiempo_str),
                'precedencias': precedencias,
                'peso_posicional': 0.0
            }
            
            # Actualizar tabla
            self._actualizar_tabla_tareas()
            
            # Limpiar formulario
            self._limpiar_formulario_tarea()
            
            # Actualizar cálculos
            self._actualizar_calculos()
            
            # Notificar cambios
            self._notificar_cambios()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al modificar tarea: {str(e)}")
    
    def _eliminar_tarea(self):
        """Elimina la tarea seleccionada."""
        seleccion = self.tree_tareas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una tarea para eliminar")
            return
        
        # Confirmar eliminación
        item = seleccion[0]
        id_tarea = self.tree_tareas.item(item)['values'][0]
        
        respuesta = messagebox.askyesno("Confirmar Eliminación", 
                                       f"¿Está seguro de eliminar la tarea '{id_tarea}'?")
        if not respuesta:
            return
        
        # Obtener índice y eliminar
        indices = self.tree_tareas.get_children()
        indice = list(indices).index(item)
        del self.tareas_data[indice]
        
        # Actualizar tabla
        self._actualizar_tabla_tareas()
        
        # Limpiar formulario
        self._limpiar_formulario_tarea()
        
        # Actualizar cálculos
        self._actualizar_calculos()
        
        # Notificar cambios
        self._notificar_cambios()
    
    def _on_seleccionar_tarea(self, event):
        """Maneja la selección de una tarea en la tabla."""
        seleccion = self.tree_tareas.selection()
        if not seleccion:
            return
        
        # Obtener datos de la tarea seleccionada
        item = seleccion[0]
        indices = self.tree_tareas.get_children()
        indice = list(indices).index(item)
        
        if indice < len(self.tareas_data):
            tarea = self.tareas_data[indice]
            
            # Cargar datos en el formulario
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, tarea['id'])
            
            self.entry_descripcion.delete(0, tk.END)
            self.entry_descripcion.insert(0, tarea['descripcion'])
            
            self.entry_tiempo.delete(0, tk.END)
            self.entry_tiempo.insert(0, str(tarea['tiempo']))
            
            self.entry_precedencias.delete(0, tk.END)
            if tarea['precedencias']:
                self.entry_precedencias.insert(0, ','.join(tarea['precedencias']))
    
    def _actualizar_tabla_tareas(self):
        """Actualiza la tabla de tareas."""
        # Limpiar tabla existente
        for item in self.tree_tareas.get_children():
            self.tree_tareas.delete(item)
        
        # Agregar tareas actuales
        for tarea in self.tareas_data:
            precedencias_str = ','.join(tarea['precedencias']) if tarea['precedencias'] else '-'

            self.tree_tareas.insert('', 'end', values=(
                tarea['id'],
                tarea['descripcion'],
                f"{tarea['tiempo']:.1f}",
                precedencias_str
            ))
    
    def _limpiar_formulario_tarea(self):
        """Limpia el formulario de nueva tarea."""
        self.entry_id.delete(0, tk.END)
        self.entry_descripcion.delete(0, tk.END)
        self.entry_tiempo.delete(0, tk.END)
        self.entry_precedencias.delete(0, tk.END)
    
    def _actualizar_calculos(self, event=None):
        """Actualiza los cálculos mostrados."""
        try:
            demanda = float(self.entry_demanda.get() or 0)
            tiempo_disponible = float(self.entry_tiempo_disponible.get() or 0)
            
            if demanda > 0 and tiempo_disponible > 0:
                tiempo_ciclo = tiempo_disponible / demanda
                self.label_tiempo_ciclo.config(text=f"Tiempo de Ciclo: {tiempo_ciclo:.2f} min/unidad")
                
                # Calcular estaciones mínimas
                tiempo_total = sum(tarea['tiempo'] for tarea in self.tareas_data)
                if tiempo_total > 0 and tiempo_ciclo > 0:
                    import math
                    estaciones_min = math.ceil(tiempo_total / tiempo_ciclo)
                    self.label_estaciones_min.config(text=f"Estaciones Mínimas: {estaciones_min}")
                else:
                    self.label_estaciones_min.config(text="Estaciones Mínimas: --")
            else:
                self.label_tiempo_ciclo.config(text="Tiempo de Ciclo: --")
                self.label_estaciones_min.config(text="Estaciones Mínimas: --")
                
        except ValueError:
            self.label_tiempo_ciclo.config(text="Tiempo de Ciclo: --")
            self.label_estaciones_min.config(text="Estaciones Mínimas: --")
    
    def _cargar_ejemplo(self):
        """Carga el ejemplo de la imagen (datos reales de balanceamiento)."""
        if self.tareas_data:
            respuesta = messagebox.askyesno("Confirmar", "¿Desea reemplazar los datos actuales con el ejemplo?")
            if not respuesta:
                return
        
        # Datos del ejemplo de la imagen
        ejemplo_tareas = [
            {'id': 'A', 'descripcion': 'Preparar material', 'tiempo': 0.7, 'precedencias': []},
            {'id': 'B', 'descripcion': 'Cortar piezas', 'tiempo': 0.6, 'precedencias': ['A']},
            {'id': 'C', 'descripcion': 'Ensamblar base', 'tiempo': 0.8, 'precedencias': ['A']},
            {'id': 'D', 'descripcion': 'Instalar componentes', 'tiempo': 0.7, 'precedencias': ['B']},
            {'id': 'E', 'descripcion': 'Soldadura', 'tiempo': 0.1, 'precedencias': ['B']},
            {'id': 'F', 'descripcion': 'Pintura', 'tiempo': 0.4, 'precedencias': ['C']},
            {'id': 'G', 'descripcion': 'Inspección final', 'tiempo': 0.2, 'precedencias': ['C']},
            {'id': 'H', 'descripcion': 'Empaque', 'tiempo': 0.3, 'precedencias': ['D', 'F']},
            {'id': 'I', 'descripcion': 'Traslados', 'tiempo': 0.8, 'precedencias': ['G', 'F', 'H']}
        ]
        
        # Agregar peso posicional inicial (se calculará después)
        for tarea in ejemplo_tareas:
            tarea['peso_posicional'] = 0.0
        
        # Cargar datos de tareas
        self.tareas_data = ejemplo_tareas.copy()
        
        # Configurar parámetros de la línea
        self.entry_demanda.delete(0, tk.END)
        self.entry_demanda.insert(0, "480")

        self.entry_tiempo_disponible.delete(0, tk.END)
        self.entry_tiempo_disponible.insert(0, "600")
        
        # Actualizar tabla
        self._actualizar_tabla_tareas()
        
        # Actualizar cálculos
        self._actualizar_calculos()
        
        # Notificar cambios
        self._notificar_cambios()
        
        messagebox.showinfo("Éxito", "Ejemplo cargado correctamente")
    
    def _limpiar_datos(self):
        """Limpia todos los datos."""
        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de limpiar todos los datos?")
        if not respuesta:
            return
        
        # Limpiar lista de tareas
        self.tareas_data.clear()
        
        # Actualizar tabla
        self._actualizar_tabla_tareas()
        
        # Limpiar formulario
        self._limpiar_formulario_tarea()
        
        # Actualizar cálculos
        self._actualizar_calculos()
        
        # Notificar cambios
        self._notificar_cambios()
    
    def _validar_todos_datos(self):
        """Valida todos los datos ingresados."""
        errores = []
        
        # Validar configuración general
        try:
            demanda = float(self.entry_demanda.get())
            tiempo_disponible = float(self.entry_tiempo_disponible.get())
            
            errores_config = Validador.validar_datos_linea_produccion(demanda, tiempo_disponible)
            errores.extend(errores_config)
            
        except ValueError:
            errores.append("Demanda diaria y tiempo disponible deben ser números válidos")
        
        # Validar tareas
        if not self.tareas_data:
            errores.append("Debe definir al menos una tarea")
        else:
            # Validar precedencias
            ids_existentes = [tarea['id'] for tarea in self.tareas_data]
            for tarea in self.tareas_data:
                for precedencia in tarea['precedencias']:
                    if precedencia not in ids_existentes:
                        errores.append(f"Tarea {tarea['id']}: precedencia '{precedencia}' no existe")
        
        # Mostrar resultados
        if errores:
            messagebox.showerror("Errores de Validación", "\n".join(errores))
        else:
            messagebox.showinfo("Validación Exitosa", "Todos los datos son válidos ✅")
    
    def _notificar_cambios(self):
        """Notifica cambios a través del callback."""
        if self.callback_datos_actualizados:
            self.callback_datos_actualizados()
    
    # Métodos públicos para obtener datos
    def obtener_datos_tareas(self) -> List[Dict]:
        """Retorna la lista de tareas."""
        return self.tareas_data.copy()
    
    def obtener_configuracion_linea(self) -> Dict:
        """Retorna la configuración de la línea de producción."""
        try:
            return {
                'demanda_diaria': int(float(self.entry_demanda.get())),
                'tiempo_disponible': float(self.entry_tiempo_disponible.get())
            }
        except ValueError:
            return {'demanda_diaria': 0, 'tiempo_disponible': 0}
    
    def establecer_datos_tareas(self, tareas: List[Dict]):
        """Establece los datos de tareas desde fuente externa."""
        self.tareas_data = tareas.copy()
        self._actualizar_tabla_tareas()
        self._actualizar_calculos()