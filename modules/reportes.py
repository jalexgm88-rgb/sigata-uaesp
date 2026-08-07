"""
modules/reportes.py
--------------------------------------------------------------------------------
Generacion automatica de reportes ejecutivos en PDF, Excel y Word a partir del
DataFrame de acciones afirmativas ya filtrado, respetando siempre los filtros
inteligentes aplicados por el usuario en el momento de la exportacion.
--------------------------------------------------------------------------------
"""

import textwrap
from datetime import datetime
from io import BytesIO

import pandas as pd
from docx import Document
from docx.shared import Pt, RGBColor
from fpdf import FPDF

from config.settings import (
    APP_ENTITY, APP_FULL_NAME, APP_NAME, APP_VERSION, LOGO_PATH,
    PROYECTO_INVERSION, USUARIO_CONECTADO,
)
from modules.ui import fecha_larga_es


# Equivalencias en texto plano para simbolos Unicode usados en la interfaz
# (flechas de tendencia, semaforos) que las fuentes core de PDF (Helvetica)
# no pueden representar, ya que solo soportan el conjunto de caracteres
# Latin-1/cp1252.
_PDF_EQUIVALENCIAS_UNICODE = {
    "▲": "+", "▼": "-", "▬": "=",
    "🟢": "", "🟡": "", "🔴": "",
    "–": "-", "—": "-", "’": "'", "“": '"', "”": '"',
}


def _pdf_safe_text(texto: str) -> str:
    """
    Convierte un texto arbitrario (que puede provenir de datos cargados por
    el usuario o de textos generados dinamicamente) a una version segura
    para las fuentes core de fpdf2. Sustituye simbolos conocidos por su
    equivalente en texto plano y, como salvaguarda final, reemplaza
    cualquier caracter restante fuera de Latin-1 para evitar que
    `FPDFUnicodeEncodingException` interrumpa la generacion del informe.
    """
    texto = str(texto) if texto is not None else ""
    for simbolo, equivalente in _PDF_EQUIVALENCIAS_UNICODE.items():
        texto = texto.replace(simbolo, equivalente)
    return texto.encode("latin-1", errors="replace").decode("latin-1")


def _write_wrapped(pdf: FPDF, texto: str, ancho_caracteres: int = 100, alto_linea: int = 6):
    """
    Escribe texto envolviendo lineas manualmente con textwrap y dibujando cada
    linea con pdf.cell(). Evita un problema conocido de fpdf2 en el que
    multi_cell() puede lanzar FPDFException ("Not enough horizontal space to
    render a single character") en ciertas combinaciones de texto y ancho.
    El texto se sanea con `_pdf_safe_text()` antes de envolverlo.
    """
    texto = _pdf_safe_text(texto)
    lineas = textwrap.wrap(texto, width=ancho_caracteres) or [""]
    for linea in lineas:
        pdf.cell(0, alto_linea, linea, ln=1)


# --------------------------------------------------------------------------------
# Excel
# --------------------------------------------------------------------------------
def generar_reporte_excel(df: pd.DataFrame, kpis: dict) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        resumen = pd.DataFrame([
            {"Indicador": "Recicladores registrados", "Valor": kpis.get("total_recicladores", 0)},
            {"Indicador": "Organizaciones", "Valor": kpis.get("total_organizaciones", 0)},
            {"Indicador": "Acciones afirmativas", "Valor": kpis.get("total_acciones", 0)},
            {"Indicador": "Beneficiarios unicos", "Valor": kpis.get("beneficiarios_unicos", 0)},
            {"Indicador": "Cobertura (%)", "Valor": kpis.get("cobertura_pct", 0)},
            {"Indicador": "Presupuesto total", "Valor": kpis.get("presupuesto_total", 0)},
            {"Indicador": "Presupuesto ejecutado", "Valor": kpis.get("presupuesto_ejecutado", 0)},
            {"Indicador": "Presupuesto disponible", "Valor": kpis.get("presupuesto_disponible", 0)},
            {"Indicador": "Acciones ejecutadas este ano", "Valor": kpis.get("acciones_ejecutadas_anio", 0)},
            {"Indicador": "Acciones pendientes", "Valor": kpis.get("acciones_pendientes", 0)},
            {"Indicador": "Alertas activas", "Valor": kpis.get("alertas_activas", 0)},
        ])
        resumen.to_excel(writer, sheet_name="Resumen KPI", index=False)

        columnas_detalle = [
            "fecha", "documento", "nombre", "organizacion", "localidad", "tipo_accion",
            "programa", "proyecto", "responsable", "estado", "presupuesto",
            "presupuesto_ejecutado", "beneficio", "sexo", "edad", "grupo_poblacional",
        ]
        columnas_detalle = [c for c in columnas_detalle if c in df.columns]
        df[columnas_detalle].to_excel(writer, sheet_name="Detalle de acciones", index=False)

        if "localidad" in df.columns and not df.empty:
            por_localidad = df.groupby("localidad").agg(
                acciones=("id", "count"), beneficiarios=("documento", "nunique"),
                presupuesto=("presupuesto", "sum"),
            ).reset_index()
            por_localidad.to_excel(writer, sheet_name="Por localidad", index=False)

    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------------
class ReportePDF(FPDF):
    def header(self):
        self.set_fill_color(14, 110, 79)
        self.rect(0, 0, 210, 22, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 15)
        self.set_xy(10, 6)
        self.cell(0, 8, f"{APP_NAME} - Reporte Ejecutivo", ln=1)
        self.set_font("Helvetica", "", 9)
        self.set_x(10)
        self.cell(0, 6, APP_ENTITY, ln=1)
        self.ln(6)
        self.set_text_color(30, 30, 30)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Pagina {self.page_no()} | Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")


def generar_reporte_pdf(df: pd.DataFrame, kpis: dict, recomendaciones: list, analisis_texto: str = "") -> bytes:
    pdf = ReportePDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(14, 110, 79)
    pdf.cell(0, 8, "Indicadores clave", ln=1)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 10)

    filas_kpi = [
        ("Recicladores registrados", kpis.get("total_recicladores", 0)),
        ("Organizaciones", kpis.get("total_organizaciones", 0)),
        ("Acciones afirmativas", kpis.get("total_acciones", 0)),
        ("Beneficiarios unicos", kpis.get("beneficiarios_unicos", 0)),
        ("Cobertura (%)", f"{kpis.get('cobertura_pct', 0)}%"),
        ("Presupuesto total", f"${kpis.get('presupuesto_total', 0):,.0f}"),
        ("Presupuesto ejecutado", f"${kpis.get('presupuesto_ejecutado', 0):,.0f}"),
        ("Acciones pendientes", kpis.get("acciones_pendientes", 0)),
        ("Alertas activas", kpis.get("alertas_activas", 0)),
    ]
    for etiqueta, valor in filas_kpi:
        pdf.cell(90, 7, etiqueta, border=1)
        pdf.cell(0, 7, str(valor), border=1, ln=1)

    pdf.ln(4)
    if analisis_texto:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(14, 110, 79)
        pdf.cell(0, 8, "Analisis ejecutivo", ln=1)
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "", 10)
        _write_wrapped(pdf, analisis_texto)
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(14, 110, 79)
    pdf.cell(0, 8, "Recomendaciones", ln=1)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 10)
    for r in recomendaciones:
        _write_wrapped(pdf, f"- {r}")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(14, 110, 79)
    pdf.cell(0, 8, f"Detalle de acciones afirmativas (primeros 40 registros de {len(df)})", ln=1)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "B", 8)
    encabezados = ["Fecha", "Nombre", "Localidad", "Tipo de accion", "Estado", "Presupuesto"]
    anchos = [20, 45, 30, 45, 25, 25]
    for h, w in zip(encabezados, anchos):
        pdf.cell(w, 6, h, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 7.5)
    for _, fila in df.head(40).iterrows():
        valores = [
            str(fila["fecha"].date()) if pd.notna(fila["fecha"]) else "",
            str(fila["nombre"])[:28],
            str(fila["localidad"])[:18],
            str(fila["tipo_accion"])[:28],
            str(fila["estado"])[:15],
            f"${fila['presupuesto']:,.0f}",
        ]
        for v, w in zip(valores, anchos):
            pdf.cell(w, 6, v, border=1)
        pdf.ln()

    return bytes(pdf.output())


# --------------------------------------------------------------------------------
# Word
# --------------------------------------------------------------------------------
def generar_reporte_word(df: pd.DataFrame, kpis: dict, recomendaciones: list, analisis_texto: str = "") -> bytes:
    doc = Document()

    titulo = doc.add_heading(f"{APP_NAME} — Reporte Ejecutivo", level=0)
    titulo.runs[0].font.color.rgb = RGBColor(0x0E, 0x6E, 0x4F)

    doc.add_paragraph(APP_FULL_NAME)
    doc.add_paragraph(APP_ENTITY)
    doc.add_paragraph(f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    doc.add_heading("Indicadores clave", level=1)
    tabla = doc.add_table(rows=1, cols=2)
    tabla.style = "Light Grid Accent 1"
    hdr = tabla.rows[0].cells
    hdr[0].text, hdr[1].text = "Indicador", "Valor"
    filas_kpi = [
        ("Recicladores registrados", kpis.get("total_recicladores", 0)),
        ("Organizaciones", kpis.get("total_organizaciones", 0)),
        ("Acciones afirmativas", kpis.get("total_acciones", 0)),
        ("Beneficiarios unicos", kpis.get("beneficiarios_unicos", 0)),
        ("Cobertura (%)", f"{kpis.get('cobertura_pct', 0)}%"),
        ("Presupuesto total", f"${kpis.get('presupuesto_total', 0):,.0f}"),
        ("Presupuesto ejecutado", f"${kpis.get('presupuesto_ejecutado', 0):,.0f}"),
        ("Acciones pendientes", kpis.get("acciones_pendientes", 0)),
        ("Alertas activas", kpis.get("alertas_activas", 0)),
    ]
    for etiqueta, valor in filas_kpi:
        fila = tabla.add_row().cells
        fila[0].text, fila[1].text = etiqueta, str(valor)

    if analisis_texto:
        doc.add_heading("Analisis ejecutivo", level=1)
        doc.add_paragraph(analisis_texto)

    doc.add_heading("Recomendaciones", level=1)
    for r in recomendaciones:
        doc.add_paragraph(r, style="List Bullet")

    doc.add_heading(f"Detalle de acciones afirmativas (primeros 40 de {len(df)})", level=1)
    columnas = ["fecha", "nombre", "localidad", "tipo_accion", "estado", "presupuesto"]
    columnas = [c for c in columnas if c in df.columns]
    tabla2 = doc.add_table(rows=1, cols=len(columnas))
    tabla2.style = "Light List Accent 1"
    for i, c in enumerate(columnas):
        tabla2.rows[0].cells[i].text = c.replace("_", " ").title()
    for _, fila in df.head(40).iterrows():
        celdas = tabla2.add_row().cells
        for i, c in enumerate(columnas):
            valor = fila[c]
            if c == "fecha" and pd.notna(valor):
                valor = valor.strftime("%Y-%m-%d")
            celdas[i].text = str(valor)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------------------------------------
# Informe Ejecutivo (PDF institucional para Alta Direccion)
# --------------------------------------------------------------------------------
# Colores RGB usados para dibujar el semaforo del Valor Publico Generado
# como un circulo (en vez del caracter emoji devuelto por
# `modules.analisis.calcular_valor_publico`).
_SEMAFORO_COLORES = {
    "🟢": (30, 158, 90),
    "🟡": (224, 161, 0),
    "🔴": (192, 57, 43),
}


def _asegurar_espacio(pdf: FPDF, alto_necesario: float):
    """
    Fuerza un salto de pagina manual si el bloque que sigue (de alto
    aproximado `alto_necesario` en mm) no cabe en el espacio restante de la
    pagina actual. Es necesario porque las barras dibujadas con rect() en
    `_draw_barra_horizontal` no activan el salto de pagina automatico de
    fpdf2 (que solo se dispara con cell()/multi_cell()).
    """
    espacio_restante = pdf.h - pdf.b_margin - pdf.get_y()
    if alto_necesario > espacio_restante:
        pdf.add_page()


def _draw_barra_horizontal(pdf: FPDF, etiqueta: str, valor: float, valor_max: float,
                            x: float, y: float, ancho_total: float = 110,
                            alto: float = 5.4, color: tuple = (14, 110, 79)):
    """
    Dibuja una fila de grafico de barras horizontal simple usando primitivas
    nativas de fpdf2 (rect + texto), evitando depender de una libreria de
    graficos adicional (matplotlib/kaleido) que no forma parte del stack
    actual del proyecto.
    """
    pdf.set_xy(x, y)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(46, alto, _pdf_safe_text(etiqueta)[:30], ln=0)

    barra_x = x + 47
    barra_ancho = (valor / valor_max * ancho_total) if valor_max else 0
    pdf.set_fill_color(*color)
    pdf.rect(barra_x, y + 0.4, max(barra_ancho, 0.5), alto - 1.2, "F")

    pdf.set_xy(barra_x + ancho_total + 3, y)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(20, alto, f"{valor:,.0f}", ln=1)


class InformeEjecutivoPDF(FPDF):
    """
    Documento PDF de informe ejecutivo para Alta Direccion. A diferencia de
    `ReportePDF` (reporte operativo de la pagina Reportes), este documento
    incluye una portada institucional propia; por eso el banner verde de
    encabezado solo se dibuja a partir de la segunda pagina.
    """

    def header(self):
        if self.page_no() == 1:
            return  # La portada dibuja su propio encabezado institucional.
        self.set_fill_color(14, 110, 79)
        self.rect(0, 0, 210, 18, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 12)
        self.set_xy(10, 5)
        self.cell(0, 8, f"{APP_NAME} - Informe Ejecutivo", ln=1)
        self.ln(4)
        self.set_text_color(30, 30, 30)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(
            0, 10,
            f"Pagina {self.page_no()} | Documento generado automaticamente por {APP_NAME} v{APP_VERSION} "
            f"el {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            align="C",
        )

    def seccion(self, titulo: str):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(14, 110, 79)
        self.cell(0, 8, titulo, ln=1)
        self.set_text_color(30, 30, 30)
        self.set_font("Helvetica", "", 10)


def generar_informe_ejecutivo_pdf(
    df: pd.DataFrame,
    kpi: dict,
    valor_publico: dict,
    alertas: list,
    recomendaciones: list,
    analisis_texto: str,
) -> bytes:
    """
    Genera el 'Informe Ejecutivo' en PDF con diseno institucional, pensado
    para presentarse ante Alta Direccion / el Comite Institucional de Gestion
    y Desempeno. Incluye: portada, indicadores estrategicos (incluyendo el
    Valor Publico Generado), contexto del proyecto de inversion, resumen
    ejecutivo, graficos principales (representados como barras nativas),
    cobertura territorial (a modo de sintesis del mapa), alertas
    identificadas y recomendaciones automaticas.
    """
    pdf = InformeEjecutivoPDF()
    usuario = USUARIO_CONECTADO

    # -------------------- Portada institucional --------------------
    pdf.add_page()
    pdf.set_fill_color(9, 74, 53)
    pdf.rect(0, 0, 210, 297, "F")
    pdf.set_fill_color(14, 110, 79)
    pdf.rect(0, 0, 210, 90, "F")

    try:
        if LOGO_PATH.exists():
            pdf.image(str(LOGO_PATH), x=15, y=15, w=70)
    except Exception:
        pass  # La portada se muestra igual si el logo no esta disponible.

    # Se usa _write_wrapped() (envoltura manual con cell(), no multi_cell())
    # para evitar el FPDFException ya conocido en multi_cell() con fpdf2, y se
    # ajusta el margen izquierdo a 15mm para que las lineas envueltas
    # continuen alineadas con el resto de la portada.
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(15, 100)
    pdf.set_font("Helvetica", "B", 26)
    _write_wrapped(pdf, "Informe Ejecutivo", ancho_caracteres=20, alto_linea=12)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 13)
    _write_wrapped(pdf, APP_FULL_NAME, ancho_caracteres=48, alto_linea=7)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 11)
    _write_wrapped(pdf, APP_ENTITY, ancho_caracteres=58, alto_linea=6)

    pdf.set_xy(15, 230)
    pdf.set_draw_color(255, 255, 255)
    pdf.set_line_width(0.3)
    pdf.line(15, 228, 195, 228)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(15, 232)
    pdf.cell(90, 6, "Proyecto de Inversion", ln=0)
    pdf.cell(90, 6, "Fecha del informe", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(15)
    texto_proyecto = _pdf_safe_text(f"{PROYECTO_INVERSION['codigo']} - {PROYECTO_INVERSION['nombre']}")[:55]
    pdf.cell(90, 6, texto_proyecto, ln=0)
    pdf.cell(90, 6, fecha_larga_es(), ln=1)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_x(15)
    pdf.cell(90, 6, "Generado por", ln=0)
    pdf.cell(90, 6, "Cargo", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(15)
    pdf.cell(90, 6, _pdf_safe_text(usuario["nombre"]), ln=0)
    pdf.cell(90, 6, _pdf_safe_text(usuario["cargo"]), ln=1)

    # -------------------- Pagina 2: indicadores estrategicos --------------------
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()
    pdf.set_text_color(30, 30, 30)

    pdf.seccion("Indicadores estrategicos")
    filas_kpi = [
        ("Recicladores registrados", f"{kpi.get('total_recicladores', 0):,}"),
        ("Organizaciones (ORO)", f"{kpi.get('total_organizaciones', 0):,}"),
        ("Acciones afirmativas", f"{kpi.get('total_acciones', 0):,}"),
        ("Beneficiarios unicos", f"{kpi.get('beneficiarios_unicos', 0):,}"),
        ("Cobertura (%)", f"{kpi.get('cobertura_pct', 0)}%"),
        ("Presupuesto ejecutado", f"${kpi.get('presupuesto_ejecutado', 0):,.0f} "
                                   f"({kpi.get('pct_ejecucion_presupuestal', 0)}%)"),
        ("Acciones pendientes", f"{kpi.get('acciones_pendientes', 0):,}"),
        ("Alertas activas", f"{kpi.get('alertas_activas', 0):,}"),
    ]
    for etiqueta, valor in filas_kpi:
        pdf.cell(95, 7, etiqueta, border=1)
        pdf.cell(0, 7, str(valor), border=1, ln=1)
    pdf.ln(4)

    # -------------------- Valor Publico Generado --------------------
    # El semaforo se dibuja como un circulo de color (en vez de incrustar el
    # caracter emoji, que las fuentes core de fpdf2 no pueden representar).
    pdf.seccion("Valor Publico Generado")
    y_fila = pdf.get_y()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(14, 110, 79)
    pdf.cell(45, 12, f"{valor_publico['valor_pct']:.0f}%", ln=0)

    color_semaforo = _SEMAFORO_COLORES.get(valor_publico["semaforo"], (140, 140, 140))
    pdf.set_fill_color(*color_semaforo)
    pdf.ellipse(pdf.get_x() + 1, y_fila + 4, 5, 5, style="F")
    pdf.set_xy(pdf.get_x() + 9, y_fila)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 12, _pdf_safe_text(valor_publico["interpretacion"]), ln=1)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(90, 90, 90)
    _write_wrapped(pdf, valor_publico["tendencia_texto"], ancho_caracteres=110)
    _write_wrapped(
        pdf,
        "Indicador sintetico calculado a partir de cobertura de beneficiarios, trazabilidad de las "
        "acciones, completitud de los registros, evidencia documental y oportunidad del seguimiento. "
        "No corresponde a una cifra financiera.",
        ancho_caracteres=110,
    )
    pdf.set_text_color(30, 30, 30)
    pdf.ln(2)

    # -------------------- Resumen ejecutivo --------------------
    pdf.seccion("Resumen ejecutivo")
    _write_wrapped(pdf, analisis_texto)
    pdf.ln(3)

    # -------------------- Graficos principales (acciones por tipo) --------------------
    pdf.seccion("Graficos principales: acciones afirmativas por tipo")
    if "tipo_accion" in df.columns and not df.empty:
        conteo_tipo = df["tipo_accion"].value_counts().head(6)
        if not conteo_tipo.empty:
            _asegurar_espacio(pdf, 10 + len(conteo_tipo) * 7)
            max_val = conteo_tipo.max()
            y0 = pdf.get_y() + 2
            for i, (etiqueta, valor) in enumerate(conteo_tipo.items()):
                _draw_barra_horizontal(pdf, str(etiqueta), valor, max_val, x=10, y=y0 + i * 7)
            pdf.set_y(y0 + len(conteo_tipo) * 7 + 4)
    pdf.ln(2)

    # -------------------- Cobertura territorial (sintesis del mapa) --------------------
    pdf.seccion("Cobertura territorial (sintesis del mapa)")
    pdf.set_font("Helvetica", "", 8.5)
    _write_wrapped(
        pdf,
        "El mapa interactivo completo, con la ubicacion de organizaciones y recicladores por localidad, "
        "esta disponible dentro de la aplicacion en la pagina 'Mapa'. A continuacion se resume la "
        "cobertura de beneficiarios por localidad.",
        ancho_caracteres=110,
    )
    if "localidad" in df.columns and not df.empty:
        conteo_loc = df.groupby("localidad")["documento"].nunique().sort_values(ascending=False).head(8)
        conteo_loc = conteo_loc[conteo_loc.index != ""]
        if not conteo_loc.empty:
            _asegurar_espacio(pdf, 10 + len(conteo_loc) * 7)
            max_val = conteo_loc.max()
            y0 = pdf.get_y() + 3
            for i, (etiqueta, valor) in enumerate(conteo_loc.items()):
                _draw_barra_horizontal(pdf, str(etiqueta), valor, max_val, x=10, y=y0 + i * 7,
                                        color=(36, 100, 180))
            pdf.set_y(y0 + len(conteo_loc) * 7 + 4)

    # -------------------- Pagina 3: alertas y recomendaciones --------------------
    pdf.add_page()
    pdf.seccion("Alertas identificadas")
    if alertas:
        for a in alertas:
            pdf.set_font("Helvetica", "B", 9)
            _write_wrapped(pdf, f"[{a['severidad'].upper()}] {a['tipo']}", ancho_caracteres=105)
            pdf.set_font("Helvetica", "", 9)
            _write_wrapped(pdf, a["mensaje"], ancho_caracteres=105)
            pdf.ln(1)
    else:
        _write_wrapped(pdf, "No se identifican alertas activas para el periodo y filtros seleccionados.")
    pdf.ln(3)

    pdf.seccion("Recomendaciones automaticas")
    for r in recomendaciones:
        _write_wrapped(pdf, f"- {r}")

    return bytes(pdf.output())
