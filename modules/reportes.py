"""
modules/reportes.py
--------------------------------------------------------------------------------
Generacion automatica de reportes ejecutivos en PDF, Excel y Word a partir del
DataFrame de acciones afirmativas ya filtrado, respetando siempre los filtros
inteligentes aplicados por el usuario en el momento de la exportacion.
--------------------------------------------------------------------------------
"""

from datetime import datetime
from io import BytesIO

import pandas as pd
from docx import Document
from docx.shared import Pt, RGBColor
from fpdf import FPDF

from config.settings import APP_ENTITY, APP_FULL_NAME, APP_NAME


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
        pdf.multi_cell(0, 6, analisis_texto)
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(14, 110, 79)
    pdf.cell(0, 8, "Recomendaciones", ln=1)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 10)
    for r in recomendaciones:
        pdf.multi_cell(0, 6, f"- {r}")
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
