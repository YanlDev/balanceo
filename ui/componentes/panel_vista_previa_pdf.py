"""
Panel de Vista Previa de PDF con controles de zoom y navegación
Utiliza PyMuPDF (fitz) para renderizar PDFs y Pillow para manejo de imágenes
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None
import io
import os
from typing import Optional, List, Callable
import threading

from utils.estilos import EstilosModernos, COLORES, FUENTES, ESPACIADO, UtilsUI
from servicios.generador_reporte_pdf import GeneradorReportePDF


class PanelVistaPrevia:
    """
    Panel para vista previa de PDF con controles de zoom y navegación de páginas.
    Permite visualizar reportes antes de exportar y controlar la exportación.
    """

    def __init__(self, parent, callback_estado_actualizado: Optional[Callable] = None):
        self.parent = parent
        self.callback_estado = callback_estado_actualizado

        # Verificar dependencias
        self.dependencias_disponibles = self._verificar_dependencias()

        # Variables de estado
        self.pdf_documento = None
        self.pagina_actual = 0
        self.total_paginas = 0
        self.zoom_actual = 1.0
        self.archivo_temporal = None

        # Variables de datos para generar reporte
        self.linea_produccion = None
        self.estaciones = None
        self.metricas = None

        # Configuración de zoom
        self.zoom_min = 0.25
        self.zoom_max = 3.0
        self.zoom_step = 0.25

        # UI elementos
        self.canvas_vista_previa = None
        self.scrollbar_v = None
        self.scrollbar_h = None
        self.label_pagina = None
        self.label_zoom = None
        self.btn_anterior = None
        self.btn_siguiente = None
        self.btn_zoom_in = None
        self.btn_zoom_out = None
        self.btn_zoom_fit = None
        self.btn_generar_reporte = None
        self.btn_exportar_pdf = None
        self.progress_var = None
        self.progress_bar = None

        self._crear_interfaz()
        self._configurar_eventos()

    def _verificar_dependencias(self) -> bool:
        """Verifica que las dependencias necesarias estén disponibles."""
        try:
            from servicios.generador_reporte_pdf import GeneradorReportePDF
            if fitz is None:
                return False
            if Image is None or ImageTk is None:
                return False
            return True
        except ImportError:
            return False

    def _crear_interfaz(self):
        """Crea la interfaz del panel de vista previa."""
        # Frame principal
        self.frame_principal = ttk.Frame(self.parent, style='Fondo.TFrame')
        self.frame_principal.pack(fill='both', expand=True, padx=ESPACIADO['normal'], pady=ESPACIADO['normal'])

        # Crear barra de herramientas superior
        self._crear_barra_herramientas()

        # Crear área de vista previa
        self._crear_area_vista_previa()

        # Crear barra de estado
        self._crear_barra_estado()

        # Mostrar mensaje inicial
        self._mostrar_mensaje_inicial()

    def _crear_barra_herramientas(self):
        """Crea la barra de herramientas con controles."""
        frame_herramientas = ttk.Frame(self.frame_principal, style='Superficie.TFrame', padding=ESPACIADO['normal'])
        frame_herramientas.pack(fill='x', pady=(0, ESPACIADO['normal']))

        # Grupo de generación de reporte
        frame_generacion = ttk.LabelFrame(frame_herramientas, text="Generación de Reporte",
                                        style='Card.TLabelframe', padding=ESPACIADO['pequeno'])
        frame_generacion.pack(side='left', padx=(0, ESPACIADO['normal']))

        self.btn_generar_reporte = ttk.Button(frame_generacion,
                                             text="📄 Generar Vista Previa",
                                             style='Primario.TButton',
                                             command=self._generar_vista_previa)
        self.btn_generar_reporte.pack(side='left', padx=(0, ESPACIADO['pequeno']))

        # Grupo de navegación
        frame_navegacion = ttk.LabelFrame(frame_herramientas, text="Navegación",
                                        style='Card.TLabelframe', padding=ESPACIADO['pequeno'])
        frame_navegacion.pack(side='left', padx=(0, ESPACIADO['normal']))

        self.btn_anterior = ttk.Button(frame_navegacion,
                                      text="◀ Anterior",
                                      style='Secundario.TButton',
                                      command=self._pagina_anterior,
                                      state='disabled')
        self.btn_anterior.pack(side='left', padx=(0, 5))

        self.label_pagina = ttk.Label(frame_navegacion, text="0 / 0", style='Normal.TLabel')
        self.label_pagina.pack(side='left', padx=5)

        self.btn_siguiente = ttk.Button(frame_navegacion,
                                       text="Siguiente ▶",
                                       style='Secundario.TButton',
                                       command=self._pagina_siguiente,
                                       state='disabled')
        self.btn_siguiente.pack(side='left', padx=(5, 0))

        # Grupo de zoom
        frame_zoom = ttk.LabelFrame(frame_herramientas, text="Zoom",
                                   style='Card.TLabelframe', padding=ESPACIADO['pequeno'])
        frame_zoom.pack(side='left', padx=(0, ESPACIADO['normal']))

        self.btn_zoom_out = ttk.Button(frame_zoom,
                                      text="🔍−",
                                      style='Secundario.TButton',
                                      command=self._zoom_out,
                                      state='disabled')
        self.btn_zoom_out.pack(side='left', padx=(0, 5))

        self.label_zoom = ttk.Label(frame_zoom, text="100%", style='Normal.TLabel')
        self.label_zoom.pack(side='left', padx=5)

        self.btn_zoom_in = ttk.Button(frame_zoom,
                                     text="🔍+",
                                     style='Secundario.TButton',
                                     command=self._zoom_in,
                                     state='disabled')
        self.btn_zoom_in.pack(side='left', padx=(5, 0))

        self.btn_zoom_fit = ttk.Button(frame_zoom,
                                      text="📐 Ajustar",
                                      style='Secundario.TButton',
                                      command=self._zoom_fit,
                                      state='disabled')
        self.btn_zoom_fit.pack(side='left', padx=(10, 0))

        # Grupo de exportación
        frame_exportacion = ttk.LabelFrame(frame_herramientas, text="Exportación",
                                         style='Card.TLabelframe', padding=ESPACIADO['pequeno'])
        frame_exportacion.pack(side='right')

        self.btn_exportar_pdf = ttk.Button(frame_exportacion,
                                          text="💾 Exportar PDF",
                                          style='Acento.TButton',
                                          command=self._exportar_pdf,
                                          state='disabled')
        self.btn_exportar_pdf.pack(side='left')

    def _crear_area_vista_previa(self):
        """Crea el área de vista previa con scrollbars."""
        # Frame contenedor con scrollbars
        frame_contenedor = ttk.Frame(self.frame_principal, style='Superficie.TFrame')
        frame_contenedor.pack(fill='both', expand=True)

        # Canvas para la vista previa
        self.canvas_vista_previa = tk.Canvas(frame_contenedor,
                                           bg=COLORES['superficie'],
                                           highlightthickness=0)

        # Scrollbars
        self.scrollbar_v = ttk.Scrollbar(frame_contenedor, orient='vertical',
                                        command=self.canvas_vista_previa.yview)
        self.scrollbar_h = ttk.Scrollbar(frame_contenedor, orient='horizontal',
                                        command=self.canvas_vista_previa.xview)

        # Configurar canvas con scrollbars
        self.canvas_vista_previa.configure(yscrollcommand=self.scrollbar_v.set,
                                         xscrollcommand=self.scrollbar_h.set)

        # Layout de componentes
        self.canvas_vista_previa.pack(side='left', fill='both', expand=True)
        self.scrollbar_v.pack(side='right', fill='y')
        self.scrollbar_h.pack(side='bottom', fill='x')

    def _crear_barra_estado(self):
        """Crea la barra de estado inferior."""
        frame_estado = ttk.Frame(self.frame_principal, style='Superficie.TFrame', padding=ESPACIADO['pequeno'])
        frame_estado.pack(fill='x', side='bottom', pady=(ESPACIADO['normal'], 0))

        # Separador
        separador = EstilosModernos.crear_separador_horizontal(frame_estado)
        separador.pack(fill='x', pady=(0, ESPACIADO['pequeno']))

        # Label de estado
        self.label_estado = ttk.Label(frame_estado,
                                     text="Listo para generar vista previa del reporte PDF",
                                     style='Secundario.TLabel')
        self.label_estado.pack(side='left')

        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame_estado,
                                          variable=self.progress_var,
                                          maximum=100,
                                          length=200)
        self.progress_bar.pack(side='right', padx=(10, 0))

    def _configurar_eventos(self):
        """Configura los eventos del panel."""
        # Eventos del canvas
        self.canvas_vista_previa.bind('<Button-4>', self._on_mousewheel)  # Linux
        self.canvas_vista_previa.bind('<Button-5>', self._on_mousewheel)  # Linux
        self.canvas_vista_previa.bind('<MouseWheel>', self._on_mousewheel)  # Windows

        # Eventos de teclado
        self.canvas_vista_previa.bind('<Key>', self._on_key_press)
        self.canvas_vista_previa.focus_set()

        # Evento de redimensión
        self.canvas_vista_previa.bind('<Configure>', self._on_canvas_configure)

    def _mostrar_mensaje_inicial(self):
        """Muestra el mensaje inicial en el área de vista previa."""
        self.canvas_vista_previa.delete('all')

        # Verificar dependencias
        if not self.dependencias_disponibles:
            mensaje = """
            Vista Previa de Reporte PDF - Dependencias Faltantes

            Para usar esta funcionalidad, instale las dependencias necesarias:

            1. Abra una terminal/comando
            2. Ejecute: pip install -r requirements.txt
            3. Reinicie la aplicación

            Dependencias necesarias:
            • reportlab (generación de PDF)
            • PyMuPDF (visualización de PDF)
            • Pillow (manejo de imágenes)

            Una vez instaladas las dependencias, podrá:
            • Generar reportes PDF profesionales
            • Vista previa con zoom y navegación
            • Exportar reportes con diseño corporativo
            """
        else:
            # Texto informativo normal
            mensaje = """
            Vista Previa de Reporte PDF

            Para comenzar:
            1. Complete el balanceamiento de línea en la pestaña de configuración
            2. Haga clic en "Generar Vista Previa" para crear el reporte
            3. Use los controles de navegación y zoom para revisar el documento
            4. Exporte el PDF final cuando esté satisfecho con el resultado

            Controles disponibles:
            • Teclas de flecha o botones para navegar entre páginas
            • Rueda del ratón para hacer zoom
            • Botón "Ajustar" para optimizar el tamaño de visualización
            """

        # Centrar texto en el canvas
        canvas_width = self.canvas_vista_previa.winfo_width()
        canvas_height = self.canvas_vista_previa.winfo_height()

        if canvas_width > 1 and canvas_height > 1:  # Verificar que el canvas esté inicializado
            self.canvas_vista_previa.create_text(
                canvas_width // 2,
                canvas_height // 2,
                text=mensaje,
                font=FUENTES['normal'],
                fill=COLORES['texto_secundario'],
                justify='center',
                width=canvas_width - 100
            )

    def actualizar_datos(self, linea_produccion, estaciones, metricas):
        """Actualiza los datos para generar el reporte."""
        self.linea_produccion = linea_produccion
        self.estaciones = estaciones
        self.metricas = metricas

        # Habilitar botón de generar si tenemos datos y dependencias
        if all([linea_produccion, estaciones, metricas]) and self.dependencias_disponibles:
            self.btn_generar_reporte.configure(state='normal')
            self._actualizar_estado("Datos actualizados - Listo para generar vista previa")
        else:
            self.btn_generar_reporte.configure(state='disabled')
            if not self.dependencias_disponibles:
                self._actualizar_estado("Instale las dependencias (pip install -r requirements.txt)")
            else:
                self._actualizar_estado("Datos incompletos - Complete el balanceamiento primero")

    def _generar_vista_previa(self):
        """Genera la vista previa del reporte PDF."""
        if not self.dependencias_disponibles:
            messagebox.showwarning("Vista Previa",
                                 "Instale las dependencias necesarias primero:\n\n"
                                 "pip install -r requirements.txt\n\n"
                                 "Luego reinicie la aplicación.")
            return

        if not all([self.linea_produccion, self.estaciones, self.metricas]):
            messagebox.showwarning("Vista Previa",
                                 "Complete el balanceamiento de línea antes de generar la vista previa.")
            return

        # Ejecutar generación en hilo separado
        threading.Thread(target=self._generar_vista_previa_async, daemon=True).start()

    def _generar_vista_previa_async(self):
        """Genera la vista previa de forma asíncrona."""
        try:
            # Actualizar estado
            self.parent.after(0, lambda: self._actualizar_estado("Generando reporte PDF..."))
            self.parent.after(0, lambda: self.progress_var.set(20))

            # Crear archivo temporal
            import tempfile
            temp_dir = tempfile.gettempdir()
            self.archivo_temporal = os.path.join(temp_dir, "reporte_balanceo_preview.pdf")

            # Generar PDF
            generador = GeneradorReportePDF()
            self.parent.after(0, lambda: self.progress_var.set(60))

            generador.generar_reporte_completo(
                self.linea_produccion,
                self.estaciones,
                self.metricas,
                self.archivo_temporal
            )

            self.parent.after(0, lambda: self.progress_var.set(80))

            # Cargar PDF en el visor
            self.parent.after(0, lambda: self._cargar_pdf(self.archivo_temporal))

        except Exception as e:
            error_msg = str(e)
            self.parent.after(0, lambda: self._manejar_error("Error al generar vista previa", error_msg))

    def _cargar_pdf(self, ruta_archivo: str):
        """Carga un archivo PDF en el visor."""
        try:
            # Cerrar documento anterior si existe
            if self.pdf_documento:
                self.pdf_documento.close()

            # Abrir nuevo documento
            self.pdf_documento = fitz.open(ruta_archivo)
            self.total_paginas = len(self.pdf_documento)
            self.pagina_actual = 0

            # Actualizar controles
            self._actualizar_controles()

            # Mostrar primera página
            self._mostrar_pagina_actual()

            # Actualizar estado
            self._actualizar_estado(f"Vista previa cargada - {self.total_paginas} páginas")
            self.progress_var.set(100)

            # Limpiar progreso después de un momento
            self.parent.after(2000, lambda: self.progress_var.set(0))

        except Exception as e:
            self._manejar_error("Error al cargar PDF", str(e))

    def _mostrar_pagina_actual(self):
        """Muestra la página actual del PDF."""
        if not self.pdf_documento or self.pagina_actual >= self.total_paginas:
            return

        try:
            # Obtener página
            pagina = self.pdf_documento[self.pagina_actual]

            # Crear matriz de transformación para zoom
            matriz = fitz.Matrix(self.zoom_actual, self.zoom_actual)

            # Renderizar página como imagen
            pix = pagina.get_pixmap(matrix=matriz)
            img_data = pix.tobytes("ppm")

            # Convertir a imagen PIL
            img_pil = Image.open(io.BytesIO(img_data))

            # Convertir a ImageTk para mostrar en tkinter
            self.img_tk = ImageTk.PhotoImage(img_pil)

            # Limpiar canvas y mostrar imagen
            self.canvas_vista_previa.delete('all')
            self.canvas_vista_previa.create_image(0, 0, anchor='nw', image=self.img_tk)

            # Configurar región de scroll
            self.canvas_vista_previa.configure(scrollregion=self.canvas_vista_previa.bbox('all'))

            # Actualizar información de página
            self._actualizar_info_pagina()

        except Exception as e:
            self._manejar_error("Error al mostrar página", str(e))

    def _actualizar_controles(self):
        """Actualiza el estado de los controles."""
        tiene_pdf = self.pdf_documento is not None

        # Controles de navegación
        estado_nav = 'normal' if tiene_pdf else 'disabled'
        self.btn_anterior.configure(state='normal' if tiene_pdf and self.pagina_actual > 0 else 'disabled')
        self.btn_siguiente.configure(state='normal' if tiene_pdf and self.pagina_actual < self.total_paginas - 1 else 'disabled')

        # Controles de zoom
        self.btn_zoom_in.configure(state='normal' if tiene_pdf and self.zoom_actual < self.zoom_max else 'disabled')
        self.btn_zoom_out.configure(state='normal' if tiene_pdf and self.zoom_actual > self.zoom_min else 'disabled')
        self.btn_zoom_fit.configure(state=estado_nav)

        # Control de exportación
        self.btn_exportar_pdf.configure(state=estado_nav)

    def _actualizar_info_pagina(self):
        """Actualiza la información de página y zoom."""
        if self.pdf_documento:
            self.label_pagina.configure(text=f"{self.pagina_actual + 1} / {self.total_paginas}")
        else:
            self.label_pagina.configure(text="0 / 0")

        self.label_zoom.configure(text=f"{int(self.zoom_actual * 100)}%")

    def _pagina_anterior(self):
        """Navega a la página anterior."""
        if self.pdf_documento and self.pagina_actual > 0:
            self.pagina_actual -= 1
            self._mostrar_pagina_actual()
            self._actualizar_controles()

    def _pagina_siguiente(self):
        """Navega a la página siguiente."""
        if self.pdf_documento and self.pagina_actual < self.total_paginas - 1:
            self.pagina_actual += 1
            self._mostrar_pagina_actual()
            self._actualizar_controles()

    def _zoom_in(self):
        """Aumenta el zoom."""
        if self.zoom_actual < self.zoom_max:
            self.zoom_actual = min(self.zoom_actual + self.zoom_step, self.zoom_max)
            self._mostrar_pagina_actual()
            self._actualizar_controles()

    def _zoom_out(self):
        """Disminuye el zoom."""
        if self.zoom_actual > self.zoom_min:
            self.zoom_actual = max(self.zoom_actual - self.zoom_step, self.zoom_min)
            self._mostrar_pagina_actual()
            self._actualizar_controles()

    def _zoom_fit(self):
        """Ajusta el zoom para que la página se vea completa."""
        if not self.pdf_documento:
            return

        try:
            # Obtener dimensiones de la página
            pagina = self.pdf_documento[self.pagina_actual]
            rect_pagina = pagina.rect

            # Obtener dimensiones del canvas
            canvas_width = self.canvas_vista_previa.winfo_width()
            canvas_height = self.canvas_vista_previa.winfo_height()

            if canvas_width > 1 and canvas_height > 1:
                # Calcular zoom para ajustar
                zoom_x = (canvas_width - 50) / rect_pagina.width
                zoom_y = (canvas_height - 50) / rect_pagina.height

                # Usar el menor zoom para que quepa completo
                self.zoom_actual = min(zoom_x, zoom_y, self.zoom_max)
                self.zoom_actual = max(self.zoom_actual, self.zoom_min)

                self._mostrar_pagina_actual()
                self._actualizar_controles()

        except Exception as e:
            print(f"Error en zoom fit: {e}")

    def _exportar_pdf(self):
        """Exporta el PDF a un archivo seleccionado por el usuario."""
        if not self.archivo_temporal or not os.path.exists(self.archivo_temporal):
            messagebox.showerror("Exportar PDF", "No hay vista previa generada para exportar.")
            return

        try:
            # Solicitar ubicación de guardado
            archivo_destino = filedialog.asksaveasfilename(
                title="Exportar Reporte PDF",
                defaultextension=".pdf",
                filetypes=[
                    ("Archivos PDF", "*.pdf"),
                    ("Todos los archivos", "*.*")
                ],
                initialname=f"reporte_balanceo_{self._obtener_timestamp()}.pdf"
            )

            if archivo_destino:
                # Copiar archivo temporal al destino
                import shutil
                shutil.copy2(self.archivo_temporal, archivo_destino)

                self._actualizar_estado(f"PDF exportado exitosamente: {os.path.basename(archivo_destino)}")
                messagebox.showinfo("Exportar PDF",
                                  f"Reporte exportado exitosamente a:\n{archivo_destino}")

        except Exception as e:
            self._manejar_error("Error al exportar PDF", str(e))

    def _obtener_timestamp(self):
        """Obtiene un timestamp para nombres de archivo."""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _on_mousewheel(self, event):
        """Maneja el evento de rueda del ratón para zoom."""
        if not self.pdf_documento:
            return

        # Determinar dirección del scroll
        if event.delta > 0 or event.num == 4:  # Scroll hacia arriba
            if event.state & 0x4:  # Ctrl presionado
                self._zoom_in()
            else:
                self.canvas_vista_previa.yview_scroll(-1, "units")
        else:  # Scroll hacia abajo
            if event.state & 0x4:  # Ctrl presionado
                self._zoom_out()
            else:
                self.canvas_vista_previa.yview_scroll(1, "units")

    def _on_key_press(self, event):
        """Maneja eventos de teclado."""
        if not self.pdf_documento:
            return

        if event.keysym == 'Left':
            self._pagina_anterior()
        elif event.keysym == 'Right':
            self._pagina_siguiente()
        elif event.keysym == 'plus' or event.keysym == 'equal':
            self._zoom_in()
        elif event.keysym == 'minus':
            self._zoom_out()
        elif event.keysym == 'Home':
            if self.pagina_actual != 0:
                self.pagina_actual = 0
                self._mostrar_pagina_actual()
                self._actualizar_controles()
        elif event.keysym == 'End':
            if self.pagina_actual != self.total_paginas - 1:
                self.pagina_actual = self.total_paginas - 1
                self._mostrar_pagina_actual()
                self._actualizar_controles()

    def _on_canvas_configure(self, event):
        """Maneja el evento de redimensión del canvas."""
        # Si no hay PDF cargado, mostrar mensaje inicial
        if not self.pdf_documento:
            self.parent.after(100, self._mostrar_mensaje_inicial)

    def _actualizar_estado(self, mensaje: str):
        """Actualiza el mensaje de estado."""
        self.label_estado.configure(text=mensaje)
        if self.callback_estado:
            self.callback_estado(mensaje)

    def _manejar_error(self, titulo: str, mensaje: str):
        """Maneja errores del panel."""
        self.progress_var.set(0)
        self._actualizar_estado(f"Error: {mensaje}")
        messagebox.showerror(titulo, f"Ha ocurrido un error:\n\n{mensaje}")

    def limpiar_vista_previa(self):
        """Limpia la vista previa actual."""
        try:
            # Cerrar documento PDF
            if self.pdf_documento:
                self.pdf_documento.close()
                self.pdf_documento = None

            # Limpiar variables
            self.pagina_actual = 0
            self.total_paginas = 0
            self.zoom_actual = 1.0

            # Eliminar archivo temporal
            if self.archivo_temporal and os.path.exists(self.archivo_temporal):
                try:
                    os.remove(self.archivo_temporal)
                except:
                    pass
                self.archivo_temporal = None

            # Limpiar datos
            self.linea_produccion = None
            self.estaciones = None
            self.metricas = None

            # Actualizar interfaz
            self._actualizar_controles()
            self._mostrar_mensaje_inicial()
            self._actualizar_estado("Vista previa limpiada")
            self.progress_var.set(0)

        except Exception as e:
            print(f"Error al limpiar vista previa: {e}")

    def __del__(self):
        """Destructor para limpiar recursos."""
        try:
            if hasattr(self, 'pdf_documento') and self.pdf_documento:
                self.pdf_documento.close()
            if hasattr(self, 'archivo_temporal') and self.archivo_temporal:
                if os.path.exists(self.archivo_temporal):
                    os.remove(self.archivo_temporal)
        except:
            pass