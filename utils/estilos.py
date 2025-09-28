import tkinter as tk
from tkinter import ttk


# Paleta de colores moderna
COLORES = {
    'primario': '#2E86AB',      # Azul profesional
    'secundario': '#A23B72',    # Magenta elegante
    'acento': '#F18F01',        # Naranja vibrante
    'fondo': '#F8F9FA',         # Gris claro
    'superficie': '#FFFFFF',     # Blanco
    'superficie_hover': '#E9ECEF', # Gris muy claro para hover
    'texto_primario': '#212529', # Gris oscuro
    'texto_secundario': '#6C757D', # Gris medio
    'exito': '#28A745',         # Verde
    'error': '#DC3545',         # Rojo
    'advertencia': '#FFC107',   # Amarillo
    'info': '#17A2B8',          # Cian
    'borde': '#DEE2E6',         # Gris claro para bordes
    'sombra': '#D0D0D0'         # Gris para sombras (compatible con tkinter)
}

# Configuraciones de fuentes
FUENTES = {
    'titulo': ('Segoe UI', 18, 'bold'),
    'subtitulo': ('Segoe UI', 14, 'bold'),
    'normal': ('Segoe UI', 10),
    'pequena': ('Segoe UI', 9),
    'monospace': ('Consolas', 10)
}

# Configuraciones de padding y márgenes
ESPACIADO = {
    'pequeno': 5,
    'normal': 10,
    'grande': 20,
    'extra_grande': 30
}


class EstilosModernos:
    """
    Clase para aplicar estilos modernos consistentes a la interfaz.
    """
    
    @staticmethod
    def configurar_tema_principal():
        """Configura el tema principal de la aplicación."""
        style = ttk.Style()
        
        # Configurar tema base
        style.theme_use('clam')
        
        # Configurar estilos para botones
        EstilosModernos._configurar_botones(style)
        
        # Configurar estilos para frames
        EstilosModernos._configurar_frames(style)
        
        # Configurar estilos para labels
        EstilosModernos._configurar_labels(style)
        
        # Configurar estilos para entry
        EstilosModernos._configurar_entries(style)
        
        # Configurar estilos para treeview (tablas)
        EstilosModernos._configurar_treeview(style)
        
        # Configurar estilos para progress bars
        EstilosModernos._configurar_progressbar(style)
    
    @staticmethod
    def _configurar_botones(style):
        """Configura estilos para botones."""
        # Botón primario
        style.configure('Primario.TButton',
                       background=COLORES['primario'],
                       foreground='white',
                       font=FUENTES['normal'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10))
        
        style.map('Primario.TButton',
                 background=[('active', '#1F5F80'),
                            ('pressed', '#1A4D6B')])
        
        # Botón secundario
        style.configure('Secundario.TButton',
                       background=COLORES['secundario'],
                       foreground='white',
                       font=FUENTES['normal'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10))
        
        style.map('Secundario.TButton',
                 background=[('active', '#7A2B56'),
                            ('pressed', '#5C1F41')])
        
        # Botón de acento
        style.configure('Acento.TButton',
                       background=COLORES['acento'],
                       foreground='white',
                       font=FUENTES['normal'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Acento.TButton',
                 background=[('active', '#D17600'),
                            ('pressed', '#B85F00')])
        
        # Botón de éxito
        style.configure('Exito.TButton',
                       background=COLORES['exito'],
                       foreground='white',
                       font=FUENTES['normal'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        # Botón de error
        style.configure('Error.TButton',
                       background=COLORES['error'],
                       foreground='white',
                       font=FUENTES['normal'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
    
    @staticmethod
    def _configurar_frames(style):
        """Configura estilos para frames."""
        style.configure('Superficie.TFrame',
                       background=COLORES['superficie'],
                       relief='flat',
                       borderwidth=1,
                       bordercolor=COLORES['borde'])
        
        style.configure('Fondo.TFrame',
                       background=COLORES['fondo'],
                       relief='flat')
        
        style.configure('Card.TFrame',
                       background=COLORES['superficie'],
                       relief='solid',
                       borderwidth=1,
                       bordercolor=COLORES['borde'])

        style.configure('Card.TLabelframe',
                       background=COLORES['superficie'],
                       relief='solid',
                       borderwidth=1,
                       bordercolor=COLORES['borde'])

        style.configure('Card.TLabelframe.Label',
                       background=COLORES['superficie'],
                       foreground=COLORES['texto_primario'],
                       font=FUENTES['subtitulo'])
    
    @staticmethod
    def _configurar_labels(style):
        """Configura estilos para labels."""
        style.configure('Titulo.TLabel',
                       background=COLORES['fondo'],
                       foreground=COLORES['texto_primario'],
                       font=FUENTES['titulo'])
        
        style.configure('Subtitulo.TLabel',
                       background=COLORES['superficie'],
                       foreground=COLORES['texto_primario'],
                       font=FUENTES['subtitulo'])
        
        style.configure('Normal.TLabel',
                       background=COLORES['superficie'],
                       foreground=COLORES['texto_primario'],
                       font=FUENTES['normal'])
        
        style.configure('Secundario.TLabel',
                       background=COLORES['superficie'],
                       foreground=COLORES['texto_secundario'],
                       font=FUENTES['normal'])
        
        style.configure('Exito.TLabel',
                       background=COLORES['superficie'],
                       foreground=COLORES['exito'],
                       font=FUENTES['normal'])
        
        style.configure('Error.TLabel',
                       background=COLORES['superficie'],
                       foreground=COLORES['error'],
                       font=FUENTES['normal'])
    
    @staticmethod
    def _configurar_entries(style):
        """Configura estilos para campos de entrada."""
        style.configure('TEntry',
                       fieldbackground=COLORES['superficie'],
                       borderwidth=1,
                       bordercolor=COLORES['borde'],
                       focuscolor=COLORES['primario'],
                       font=FUENTES['normal'],
                       padding=8)
        
        style.map('TEntry',
                 bordercolor=[('focus', COLORES['primario'])])
    
    @staticmethod
    def _configurar_treeview(style):
        """Configura estilos para tablas (Treeview)."""
        style.configure('Treeview',
                       background=COLORES['superficie'],
                       foreground=COLORES['texto_primario'],
                       fieldbackground=COLORES['superficie'],
                       borderwidth=1,
                       bordercolor=COLORES['borde'],
                       font=FUENTES['normal'])
        
        style.configure('Treeview.Heading',
                       background=COLORES['primario'],
                       foreground='white',
                       font=FUENTES['subtitulo'],
                       borderwidth=1,
                       bordercolor=COLORES['borde'])
        
        style.map('Treeview',
                 background=[('selected', COLORES['primario'])],
                 foreground=[('selected', 'white')])
    
    @staticmethod
    def _configurar_progressbar(style):
        """Configura estilos para barras de progreso."""
        style.configure('TProgressbar',
                       background=COLORES['primario'],
                       borderwidth=0,
                       lightcolor=COLORES['primario'],
                       darkcolor=COLORES['primario'])
    
    @staticmethod
    def crear_frame_card(parent, padding=ESPACIADO['normal']):
        """
        Crea un frame con estilo de card (tarjeta) con sombra visual.
        """
        # Frame contenedor para simular sombra (usar color válido)
        shadow_frame = tk.Frame(parent,
                               bg='#E0E0E0',  # Gris claro para sombra
                               height=2, width=2)

        # Frame principal (card)
        card_frame = ttk.Frame(shadow_frame, style='Card.TFrame', padding=padding)
        card_frame.pack(fill='both', expand=True, padx=1, pady=1)

        return card_frame, shadow_frame
    
    @staticmethod
    def aplicar_hover_efecto(widget, color_normal, color_hover):
        """
        Aplica efecto hover a un widget.
        """
        def on_enter(event):
            widget.configure(bg=color_hover)
        
        def on_leave(event):
            widget.configure(bg=color_normal)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    @staticmethod
    def crear_separador_horizontal(parent, color=None):
        """Crea un separador horizontal."""
        if color is None:
            color = COLORES['borde']
        
        separator = tk.Frame(parent, height=1, bg=color)
        return separator
    
    @staticmethod
    def crear_tooltip(widget, texto):
        """
        Crea un tooltip simple para un widget.
        """
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, 
                           text=texto,
                           background=COLORES['texto_primario'],
                           foreground='white',
                           font=FUENTES['pequena'],
                           padx=8, pady=4)
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)


class UtilsUI:
    """
    Utilidades adicionales para la interfaz de usuario.
    """
    
    @staticmethod
    def centrar_ventana(ventana, ancho, alto):
        """Centra una ventana en la pantalla."""
        # Obtener dimensiones de la pantalla
        ancho_pantalla = ventana.winfo_screenwidth()
        alto_pantalla = ventana.winfo_screenheight()
        
        # Calcular posición
        x = (ancho_pantalla - ancho) // 2
        y = (alto_pantalla - alto) // 2
        
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    @staticmethod
    def validar_entrada_numerica(texto):
        """
        Función de validación para campos numéricos.
        Permite solo números y punto decimal.
        """
        if texto == "":
            return True
        try:
            float(texto)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def formatear_numero(numero, decimales=1):
        """Formatea un número para mostrar."""
        try:
            return f"{float(numero):.{decimales}f}"
        except (ValueError, TypeError):
            return "0.0"
    
    @staticmethod
    def formatear_porcentaje(numero, decimales=1):
        """Formatea un número como porcentaje."""
        try:
            return f"{float(numero):.{decimales}f}%"
        except (ValueError, TypeError):
            return "0.0%"