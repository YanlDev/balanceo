"""
Generador de Reportes PDF Profesionales para Balanceamiento de Líneas
Utiliza ReportLab para crear reportes corporativos con diseño limpio y datos estructurados
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics import renderPDF

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from io import BytesIO

from modelos.estacion import Estacion
from modelos.linea_produccion import LineaProduccion


class GeneradorReportePDF:
    """
    Generador de reportes PDF profesionales para balanceamiento de líneas.
    Crea documentos con diseño corporativo limpio y datos bien estructurados.
    """

    def __init__(self):
        # Configuración de página
        self.pagesize = A4
        self.width, self.height = self.pagesize

        # Configuración de márgenes
        self.margin_left = 2.5 * cm
        self.margin_right = 2.5 * cm
        self.margin_top = 3 * cm
        self.margin_bottom = 2.5 * cm

        # Área de contenido
        self.content_width = self.width - self.margin_left - self.margin_right
        self.content_height = self.height - self.margin_top - self.margin_bottom

        # Colores corporativos
        self.colors = {
            'primary': colors.Color(0.1, 0.3, 0.6),      # Azul corporativo
            'secondary': colors.Color(0.2, 0.4, 0.7),    # Azul claro
            'accent': colors.Color(0.8, 0.9, 1.0),       # Azul muy claro
            'success': colors.Color(0.1, 0.6, 0.1),      # Verde
            'warning': colors.Color(0.9, 0.6, 0.1),      # Naranja
            'danger': colors.Color(0.8, 0.1, 0.1),       # Rojo
            'text_dark': colors.Color(0.2, 0.2, 0.2),    # Gris oscuro
            'text_light': colors.Color(0.5, 0.5, 0.5),   # Gris claro
            'border': colors.Color(0.8, 0.8, 0.8),       # Gris borde
            'background': colors.Color(0.97, 0.97, 0.97) # Fondo claro
        }

        # Configurar estilos
        self._configurar_estilos()

    def _configurar_estilos(self):
        """Configura los estilos para el documento."""
        self.styles = getSampleStyleSheet()

        # Estilo para el título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Title'],
            fontSize=22,
            textColor=self.colors['primary'],
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

        # Estilo para secciones
        self.styles.add(ParagraphStyle(
            name='Seccion',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.colors['secondary'],
            spaceAfter=8,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))

        # Estilo para texto normal corporativo
        self.styles.add(ParagraphStyle(
            name='TextoCorporativo',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.colors['text_dark'],
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))

        # Estilo para texto destacado
        self.styles.add(ParagraphStyle(
            name='TextoDestacado',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.colors['primary'],
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))

        # Estilo para pie de página
        self.styles.add(ParagraphStyle(
            name='PiePagina',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.colors['text_light'],
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

    def generar_reporte_completo(self,
                               linea_produccion: LineaProduccion,
                               estaciones: List[Estacion],
                               metricas: Dict[str, Any],
                               archivo_destino: str) -> str:
        """
        Genera un reporte PDF completo con todos los análisis.

        Args:
            linea_produccion: Línea de producción balanceada
            estaciones: Lista de estaciones con asignaciones
            metricas: Métricas calculadas del balanceamiento
            archivo_destino: Ruta del archivo PDF a generar

        Returns:
            Ruta del archivo generado
        """
        try:
            # Validaciones previas
            if not linea_produccion or not estaciones or not metricas:
                raise ValueError("Datos de entrada incompletos para generar el reporte")

            # Verificar que los pesos posicionales estén calculados
            # Un método más robusto: verificar si alguna tarea no tiene peso calculado
            pesos_faltantes = any(not hasattr(tarea, '_peso_calculado') or not tarea._peso_calculado
                                for tarea in linea_produccion.tareas.values())

            if pesos_faltantes:
                # Calcular pesos si no están disponibles
                for tarea in linea_produccion.tareas.values():
                    tarea._peso_calculado = False
                for tarea in linea_produccion.tareas.values():
                    tarea.calcular_peso_posicional(linea_produccion.tareas)
            # Crear documento PDF
            doc = SimpleDocTemplate(
                archivo_destino,
                pagesize=self.pagesize,
                leftMargin=self.margin_left,
                rightMargin=self.margin_right,
                topMargin=self.margin_top,
                bottomMargin=self.margin_bottom
            )

            # Lista de elementos del documento
            story = []

            # 1. Header corporativo
            story.extend(self._crear_header_corporativo())
            story.append(Spacer(1, 20))

            # 2. Resumen ejecutivo
            story.extend(self._crear_resumen_ejecutivo(linea_produccion, estaciones, metricas))
            story.append(PageBreak())

            # 3. Configuración de línea
            story.extend(self._crear_seccion_configuracion(linea_produccion))
            story.append(Spacer(1, 20))

            # 4. Tabla detallada de tareas
            story.extend(self._crear_tabla_tareas(linea_produccion))
            story.append(PageBreak())

            # 5. Resultados del balanceamiento
            story.extend(self._crear_resultados_balanceamiento(estaciones, linea_produccion))
            story.append(Spacer(1, 20))

            # 6. Métricas de eficiencia
            story.extend(self._crear_metricas_eficiencia(metricas))
            story.append(PageBreak())

            # 7. Análisis de estaciones
            story.extend(self._crear_analisis_estaciones(estaciones, linea_produccion))
            story.append(Spacer(1, 20))

            # 8. Recomendaciones
            story.extend(self._crear_recomendaciones(metricas, estaciones))

            # 9. Anexos
            story.append(PageBreak())
            story.extend(self._crear_anexos(linea_produccion, metricas))

            # Construir documento
            doc.build(story, onFirstPage=self._agregar_pie_pagina,
                     onLaterPages=self._agregar_pie_pagina)

            return archivo_destino

        except Exception as e:
            raise Exception(f"Error al generar reporte PDF: {str(e)}")

    def _crear_header_corporativo(self) -> List:
        """Crea el header corporativo del documento."""
        elementos = []

        # Título principal
        titulo = Paragraph(
            "REPORTE DE BALANCEAMIENTO DE LÍNEA DE PRODUCCIÓN",
            self.styles['TituloPrincipal']
        )
        elementos.append(titulo)

        # Subtítulo con algoritmo
        subtitulo = Paragraph(
            "Análisis con Algoritmo Ranked Positional Weight (RPW)",
            self.styles['TextoDestacado']
        )
        elementos.append(subtitulo)

        # Información de generación
        fecha_actual = datetime.now().strftime("%d de %B de %Y - %H:%M")
        info_generacion = Paragraph(
            f"<b>Fecha de generación:</b> {fecha_actual}",
            self.styles['TextoCorporativo']
        )
        elementos.append(info_generacion)

        # Línea separadora
        elementos.append(Spacer(1, 10))

        return elementos

    def _crear_resumen_ejecutivo(self, linea_produccion: LineaProduccion,
                                estaciones: List[Estacion],
                                metricas: Dict[str, Any]) -> List:
        """Crea el resumen ejecutivo."""
        elementos = []

        elementos.append(Paragraph("RESUMEN EJECUTIVO", self.styles['Subtitulo']))

        # Extraer métricas clave
        metricas_ef = metricas.get('metricas_eficiencia', {})
        metricas_bas = metricas.get('metricas_basicas', {})

        eficiencia_linea = metricas_ef.get('eficiencia_linea', 0)
        num_estaciones = metricas_bas.get('numero_estaciones', len(estaciones))
        tiempo_ciclo = linea_produccion.obtener_tiempo_ciclo()

        # Tabla de resumen con anchos ajustados
        datos_resumen = [
            ['Métrica', 'Valor', 'Evaluación'],
            ['Número de Estaciones', f'{num_estaciones}', self._evaluar_estaciones(num_estaciones, metricas_bas)],
            ['Eficiencia de Línea', f'{eficiencia_linea:.1f}%', self._evaluar_eficiencia(eficiencia_linea)],
            ['Tiempo de Ciclo', f'{tiempo_ciclo:.2f} min', 'Calculado'],
            ['Demanda Diaria', f'{linea_produccion.demanda_diaria} und', 'Objetivo'],
            ['Índice de Suavidad', f'{metricas_ef.get("indice_suavidad", 0):.2f}', self._evaluar_suavidad(metricas_ef.get("indice_suavidad", 0))]
        ]

        tabla_resumen = Table(datos_resumen, colWidths=[6*cm, 3*cm, 3*cm])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors['accent']),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['background']]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ]))

        elementos.append(tabla_resumen)
        elementos.append(Spacer(1, 15))

        # Conclusión ejecutiva
        conclusion = self._generar_conclusion_ejecutiva(eficiencia_linea, num_estaciones, metricas)
        elementos.append(Paragraph("CONCLUSIÓN EJECUTIVA", self.styles['Seccion']))
        elementos.append(Paragraph(conclusion, self.styles['TextoCorporativo']))

        return elementos

    def _crear_seccion_configuracion(self, linea_produccion: LineaProduccion) -> List:
        """Crea la sección de configuración de línea."""
        elementos = []

        elementos.append(Paragraph("CONFIGURACIÓN DE LA LÍNEA DE PRODUCCIÓN", self.styles['Subtitulo']))

        # Datos de configuración con anchos ajustados
        config_datos = [
            ['Parámetro', 'Valor', 'Unidad'],
            ['Demanda Diaria Objetivo', f'{linea_produccion.demanda_diaria:,}', 'unidades'],
            ['Tiempo Disponible por Día', f'{linea_produccion.tiempo_disponible:,}', 'minutos'],
            ['Tiempo de Ciclo Calculado', f'{linea_produccion.obtener_tiempo_ciclo():.2f}', 'minutos'],
            ['Número Total de Tareas', f'{len(linea_produccion.tareas)}', 'tareas'],
            ['Tiempo Total de Tareas', f'{sum(t.tiempo for t in linea_produccion.tareas.values()):.2f}', 'minutos']
        ]

        # CORRECCIÓN: Anchos ajustados - Total ~14cm
        tabla_config = Table(config_datos, colWidths=[7*cm, 4*cm, 3*cm])
        tabla_config.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Parámetro alineado a la izquierda
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['background']]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))

        elementos.append(tabla_config)

        return elementos

    def _crear_tabla_tareas(self, linea_produccion: LineaProduccion) -> List:
        """Crea la tabla detallada de tareas con pesos posicionales."""
        elementos = []

        elementos.append(Paragraph("DETALLE DE TAREAS Y PESOS POSICIONALES", self.styles['Subtitulo']))

        # Encabezados de tabla
        datos_tareas = [['ID', 'Descripción', 'Tiempo (min)', 'Precedencias', 'Peso Posicional']]

        # Ordenar tareas por peso posicional (descendente)
        # Los pesos ya deben estar calculados por el balanceador
        # Usar el mismo criterio de ordenación que el balanceador
        tareas_ordenadas = sorted(
            linea_produccion.tareas.values(),
            key=lambda t: (-t.peso_posicional, len(t.precedencias), t.id)
        )

        for tarea in tareas_ordenadas:
            # Usar peso calculado, o calcular si no existe
            peso_posicional = tarea.peso_posicional if tarea.peso_posicional > 0 else tarea.tiempo
            precedencias_str = ', '.join(tarea.precedencias) if tarea.precedencias else 'Ninguna'

            # Truncar descripción si es muy larga
            descripcion = tarea.descripcion
            if len(descripcion) > 30:
                descripcion = descripcion[:27] + '...'

            datos_tareas.append([
                tarea.id,
                descripcion,
                f'{tarea.tiempo:.1f}',
                precedencias_str,
                f'{peso_posicional:.1f}'
            ])

        tabla_tareas = Table(datos_tareas, colWidths=[2*cm, 6*cm, 2.5*cm, 4*cm, 2.5*cm])
        tabla_tareas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Descripción alineada a la izquierda
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['background']]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))

        elementos.append(tabla_tareas)

        return elementos

    def _crear_resultados_balanceamiento(self, estaciones: List[Estacion],
                                       linea_produccion: LineaProduccion) -> List:
        """Crea la sección de resultados del balanceamiento."""
        elementos = []

        elementos.append(Paragraph("RESULTADOS DEL BALANCEAMIENTO POR ESTACIÓN", self.styles['Subtitulo']))

        # Encabezados
        datos_estaciones = [['Estación', 'Tareas', 'Tiempo', 'Utilización', 'Ocioso', 'Estado']]

        tiempo_ciclo = linea_produccion.obtener_tiempo_ciclo()
        estilos_especiales = []

        for i, estacion in enumerate(estaciones):
            utilizacion = estacion.calcular_utilizacion()
            tiempo_ocioso = estacion.obtener_tiempo_ocioso()
            tareas_asignadas = ', '.join(estacion.obtener_ids_tareas())

            # Determinar estado y color
            if utilizacion >= 90:
                estado = "Sobrecargada"
                color_fondo = colors.Color(1.0, 0.9, 0.9)
            elif utilizacion >= 75:
                estado = "Alta Util."
                color_fondo = colors.Color(1.0, 0.95, 0.8)
            elif utilizacion >= 50:
                estado = "Óptima"
                color_fondo = colors.Color(0.9, 1.0, 0.9)
            else:
                estado = "Baja Util."
                color_fondo = colors.Color(0.95, 0.95, 1.0)

            fila_idx = i + 1
            estilos_especiales.append(('BACKGROUND', (0, fila_idx), (-1, fila_idx), color_fondo))

            datos_estaciones.append([
                f'E-{estacion.numero}',
                tareas_asignadas,
                f'{estacion.tiempo_total:.1f}',
                f'{utilizacion:.1f}%',
                f'{tiempo_ocioso:.1f}',
                estado
            ])

        # CORRECCIÓN: Anchos ajustados para 6 columnas - Total ~17cm
        tabla_estaciones = Table(datos_estaciones, colWidths=[1.5*cm, 5*cm, 2*cm, 2.5*cm, 2*cm, 3*cm])

        estilos_tabla = [
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]

        estilos_tabla.extend(estilos_especiales)
        tabla_estaciones.setStyle(TableStyle(estilos_tabla))

        elementos.append(tabla_estaciones)

        return elementos

    def _crear_metricas_eficiencia(self, metricas: Dict[str, Any]) -> List:
        """Crea la sección de métricas de eficiencia."""
        elementos = []

        elementos.append(Paragraph("MÉTRICAS DE EFICIENCIA PRINCIPALES", self.styles['Subtitulo']))

        metricas_ef = metricas.get('metricas_eficiencia', {})
        metricas_bas = metricas.get('metricas_basicas', {})
        metricas_prod = metricas.get('metricas_produccion', {})

        # Crear tabla de métricas principales con descripciones más cortas
        datos_metricas = [
            ['Métrica', 'Valor', 'Descripción', 'Evaluación'],
            [
                'Eficiencia de Línea',
                f'{metricas_ef.get("eficiencia_linea", 0):.1f}%',
                'Utilización promedio de estaciones',
                self._evaluar_eficiencia(metricas_ef.get("eficiencia_linea", 0))
            ],
            [
                'Índice de Suavidad',
                f'{metricas_ef.get("indice_suavidad", 0):.2f}',
                'Balance entre estaciones',
                self._evaluar_suavidad(metricas_ef.get("indice_suavidad", 0))
            ],
            [
                'Tiempo Ocioso Total',
                f'{metricas_ef.get("tiempo_ocioso_total", 0):.1f} min',
                'Tiempo no utilizado total',
                'Información'
            ],
            [
                'Throughput Máximo',
                f'{metricas_prod.get("capacidad_maxima_diaria", 0):.0f} und/día',
                'Capacidad máxima diaria',
                'Información'
            ],
            [
                'Número de Estaciones',
                f'{metricas_bas.get("numero_estaciones", 0)}',
                'Total de estaciones usadas',
                self._evaluar_estaciones(metricas_bas.get("numero_estaciones", 0), metricas_bas)
            ]
        ]

        # Ajustar anchos de columna para evitar solapamiento
        tabla_metricas = Table(datos_metricas, colWidths=[3.5*cm, 2.5*cm, 5.5*cm, 3.5*cm])
        tabla_metricas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Descripción alineada a la izquierda
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['border']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['background']]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alineación superior para mejor distribución
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ]))

        elementos.append(tabla_metricas)

        return elementos

    def _crear_analisis_estaciones(self, estaciones: List[Estacion],
                                 linea_produccion: LineaProduccion) -> List:
        """Crea el análisis detallado por estación."""
        elementos = []

        elementos.append(Paragraph("ANÁLISIS DETALLADO POR ESTACIÓN", self.styles['Subtitulo']))

        tiempo_ciclo = linea_produccion.obtener_tiempo_ciclo()

        for estacion in estaciones:
            # Crear sub-sección para cada estación
            elementos.append(Paragraph(f"Estación {estacion.numero}", self.styles['Seccion']))

            utilizacion = estacion.calcular_utilizacion()
            tiempo_ocioso = estacion.obtener_tiempo_ocioso()

            # CORRECCIÓN: usar tareas_asignadas en lugar de tareas
            num_tareas = len(estacion.tareas_asignadas)

            # Información detallada de la estación
            info_estacion = f"""
            <b>Tiempo total asignado:</b> {estacion.tiempo_total:.2f} minutos<br/>
            <b>Utilización:</b> {utilizacion:.1f}%<br/>
            <b>Tiempo ocioso:</b> {tiempo_ocioso:.2f} minutos<br/>
            <b>Número de tareas:</b> {num_tareas}<br/>
            """

            elementos.append(Paragraph(info_estacion, self.styles['TextoCorporativo']))

            # Tabla de tareas de la estación
            # CORRECCIÓN: usar tareas_asignadas en lugar de tareas
            if estacion.tareas_asignadas:
                datos_tareas_est = [['Tarea ID', 'Descripción', 'Tiempo (min)', '% del Ciclo']]

                for tarea in estacion.tareas_asignadas:
                    porcentaje_ciclo = (tarea.tiempo / tiempo_ciclo) * 100 if tiempo_ciclo > 0 else 0
                    descripcion = tarea.descripcion
                    if len(descripcion) > 40:
                        descripcion = descripcion[:37] + '...'

                    datos_tareas_est.append([
                        tarea.id,
                        descripcion,
                        f'{tarea.tiempo:.1f}',
                        f'{porcentaje_ciclo:.1f}%'
                    ])

                tabla_tareas_est = Table(datos_tareas_est, colWidths=[2*cm, 7*cm, 2.5*cm, 2.5*cm])
                tabla_tareas_est.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
                    ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['text_dark']),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))

                elementos.append(tabla_tareas_est)

            elementos.append(Spacer(1, 10))

        return elementos

    def _crear_recomendaciones(self, metricas: Dict[str, Any],
                             estaciones: List[Estacion]) -> List:
        """Crea la sección de recomendaciones basadas en el análisis."""
        elementos = []

        elementos.append(Paragraph("RECOMENDACIONES DE MEJORA", self.styles['Subtitulo']))

        metricas_ef = metricas.get('metricas_eficiencia', {})
        metricas_bas = metricas.get('metricas_basicas', {})

        recomendaciones = []

        # Analizar eficiencia de línea
        eficiencia = metricas_ef.get('eficiencia_linea', 0)
        if eficiencia < 70:
            recomendaciones.append(
                "Eficiencia baja detectada. Considere redistribuir tareas entre estaciones "
                "o revisar la secuencia de precedencias para mejorar el balance."
            )
        elif eficiencia >= 85:
            recomendaciones.append(
                "Excelente eficiencia de línea alcanzada. El balanceamiento es óptimo."
            )

        # Analizar balance de suavidad
        suavidad = metricas_ef.get('indice_suavidad', 0)
        if suavidad > 2.0:
            recomendaciones.append(
                "Índice de suavidad elevado indica desbalance significativo. "
                "Revise la distribución de tiempos entre estaciones."
            )
        elif suavidad <= 1.0:
            recomendaciones.append(
                "Excelente balance entre estaciones. Las cargas de trabajo están bien distribuidas."
            )

        # Analizar número de estaciones
        num_estaciones = metricas_bas.get('numero_estaciones', 0)
        num_optimo = metricas_bas.get('numero_estaciones_minimo_teorico', 0)
        if num_estaciones > num_optimo + 2:
            recomendaciones.append(
                f"Se utilizan {num_estaciones - num_optimo} estaciones adicionales al mínimo teórico. "
                "Existe potencial de optimización mediante reorganización de tareas."
            )

        # Analizar estaciones individuales
        estaciones_sobrecargadas = [e for e in estaciones if e.calcular_utilizacion() > 90]
        if estaciones_sobrecargadas:
            ids_sobrecargadas = [str(e.numero) for e in estaciones_sobrecargadas]
            recomendaciones.append(
                f"Estaciones sobrecargadas detectadas: {', '.join(ids_sobrecargadas)}. "
                "Considere redistribuir algunas tareas a estaciones con menor carga."
            )

        estaciones_subutilizadas = [e for e in estaciones if e.calcular_utilizacion() < 50]
        if estaciones_subutilizadas:
            ids_subutilizadas = [str(e.numero) for e in estaciones_subutilizadas]
            recomendaciones.append(
                f"Estaciones subutilizadas: {', '.join(ids_subutilizadas)}. "
                "Evalúe la posibilidad de consolidar tareas o reasignar personal."
            )

        # Si no hay problemas principales
        if not recomendaciones:
            recomendaciones.append(
                "El balanceamiento actual presenta un buen desempeño general. "
                "Monitoree continuamente las métricas de producción para mantener la eficiencia."
            )

        # Recomendaciones generales
        recomendaciones.extend([
            "Implemente un sistema de monitoreo continuo de métricas de producción.",
            "Considere la capacitación cruzada del personal para mayor flexibilidad operativa.",
            "Evalúe periódicamente si cambios en la demanda requieren rebalanceamiento."
        ])

        # Crear lista numerada de recomendaciones
        for i, recomendacion in enumerate(recomendaciones, 1):
            elementos.append(Paragraph(
                f"<b>{i}.</b> {recomendacion}",
                self.styles['TextoCorporativo']
            ))
            elementos.append(Spacer(1, 8))

        return elementos

    def _crear_anexos(self, linea_produccion: LineaProduccion,
                     metricas: Dict[str, Any]) -> List:
        """Crea la sección de anexos con información técnica."""
        elementos = []

        elementos.append(Paragraph("ANEXOS TÉCNICOS", self.styles['Subtitulo']))

        # Anexo A: Metodología RPW
        elementos.append(Paragraph("Anexo A: Metodología del Algoritmo RPW", self.styles['Seccion']))

        metodologia = """
        El algoritmo Ranked Positional Weight (RPW) es un método heurístico para el balanceamiento
        de líneas de ensamble que sigue estos pasos fundamentales:

        1. Calcular el peso posicional de cada tarea como la suma de su tiempo de procesamiento
           más el tiempo de todas las tareas que la suceden en la red de precedencias.

        2. Ordenar las tareas en orden descendente según su peso posicional.

        3. Asignar tareas a estaciones siguiendo el orden establecido, respetando las
           restricciones de precedencia y capacidad de tiempo de ciclo.

        4. Crear una nueva estación cuando ninguna tarea pueda ser asignada a las existentes.

        Este método tiende a producir soluciones eficientes al priorizar tareas críticas que
        impactan múltiples operaciones posteriores.
        """

        elementos.append(Paragraph(metodologia, self.styles['TextoCorporativo']))
        elementos.append(Spacer(1, 15))

        # Anexo B: Definiciones de métricas
        elementos.append(Paragraph("Anexo B: Definiciones de Métricas", self.styles['Seccion']))

        definiciones = [
            ('Eficiencia de Línea', 'Porcentaje promedio de utilización de todas las estaciones de trabajo.'),
            ('Tiempo de Ciclo', 'Tiempo máximo disponible en cada estación para completar sus tareas asignadas.'),
            ('Índice de Suavidad', 'Medida de variabilidad en los tiempos de las estaciones; valores menores indican mejor balance.'),
            ('Tiempo Ocioso', 'Tiempo no utilizado en cada estación debido a restricciones de precedencia o capacidad.'),
            ('Throughput', 'Capacidad de producción máxima del sistema en unidades por período de tiempo.'),
            ('Peso Posicional', 'Valor calculado para priorizar tareas basado en su impacto en operaciones posteriores.')
        ]

        for termino, definicion in definiciones:
            elementos.append(Paragraph(f"<b>{termino}:</b> {definicion}", self.styles['TextoCorporativo']))
            elementos.append(Spacer(1, 6))

        return elementos

    def _agregar_pie_pagina(self, canvas, doc):
        """Agrega pie de página a cada página."""
        canvas.saveState()

        # Información del pie
        fecha = datetime.now().strftime("%d/%m/%Y")
        texto_pie = f"Reporte generado el {fecha} | Calculadora RPW | Página {doc.page}"

        # Configurar fuente
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.colors['text_light'])

        # Dibujar texto centrado
        canvas.drawCentredString(
            self.width / 2,
            self.margin_bottom / 2,
            texto_pie
        )

        # Línea superior del pie
        canvas.setStrokeColor(self.colors['border'])
        canvas.setLineWidth(0.5)
        canvas.line(
            self.margin_left,
            self.margin_bottom - 10,
            self.width - self.margin_right,
            self.margin_bottom - 10
        )

        canvas.restoreState()

    def _evaluar_eficiencia(self, eficiencia: float) -> str:
        """Evalúa el nivel de eficiencia."""
        if eficiencia >= 85:
            return "Excelente"
        elif eficiencia >= 75:
            return "Buena"
        elif eficiencia >= 60:
            return "Aceptable"
        else:
            return "Requiere Mejora"

    def _evaluar_suavidad(self, suavidad: float) -> str:
        """Evalúa el índice de suavidad."""
        if suavidad <= 1.0:
            return "Excelente"
        elif suavidad <= 2.0:
            return "Bueno"
        elif suavidad <= 3.0:
            return "Aceptable"
        else:
            return "Desbalanceado"

    def _evaluar_estaciones(self, num_estaciones: int, metricas_basicas: Dict) -> str:
        """Evalúa el número de estaciones respecto al óptimo."""
        num_optimo = metricas_basicas.get('numero_estaciones_minimo_teorico', num_estaciones)
        diferencia = num_estaciones - num_optimo

        if diferencia == 0:
            return "Óptimo"
        elif diferencia == 1:
            return "Muy Bueno"
        elif diferencia <= 2:
            return "Aceptable"
        else:
            return "Excesivo"

    def _generar_conclusion_ejecutiva(self, eficiencia: float, num_estaciones: int,
                                    metricas: Dict[str, Any]) -> str:
        """Genera la conclusión ejecutiva del análisis."""
        metricas_bas = metricas.get('metricas_basicas', {})
        num_optimo = metricas_bas.get('numero_estaciones_minimo_teorico', num_estaciones)

        conclusion = f"""
        El análisis de balanceamiento de línea utilizando el algoritmo RPW ha resultado en una
        configuración de {num_estaciones} estaciones de trabajo con una eficiencia de línea del
        {eficiencia:.1f}%.
        """

        if eficiencia >= 80:
            conclusion += """
            La eficiencia alcanzada se considera excelente, indicando un balanceamiento óptimo
            que maximiza la utilización de recursos disponibles.
            """
        elif eficiencia >= 70:
            conclusion += """
            La eficiencia obtenida es satisfactoria, aunque existe margen para optimizaciones
            menores que podrían mejorar el desempeño general.
            """
        else:
            conclusion += """
            La eficiencia actual sugiere oportunidades significativas de mejora mediante
            redistribución de tareas y optimización del balance entre estaciones.
            """

        if num_estaciones == num_optimo:
            conclusion += " El número de estaciones utilizado coincide con el mínimo teórico, "
            conclusion += "lo que indica una solución altamente eficiente."
        elif num_estaciones <= num_optimo + 1:
            conclusion += " El número de estaciones está muy próximo al mínimo teórico, "
            conclusion += "representando una solución práctica y eficiente."
        else:
            conclusion += f" Se utilizan {num_estaciones - num_optimo} estaciones adicionales "
            conclusion += "al mínimo teórico, sugiriendo potencial de consolidación."

        return conclusion