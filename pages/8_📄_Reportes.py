"""
pages/8_Reportes.py
--------------------------------------------------------------------------------
Pagina de generacion automatica de reportes en PDF, Excel y Word. Todos los
reportes respetan los filtros inteligentes aplicados por el usuario en esta
misma pagina, garantizando que el documento exportado refleje exactamente lo
que el usuario esta viendo.
--------------------------------------------------------------------------------
"""

from datetime import datetime

import streamlit as st

from modules import kpis, ui
from modules.alertas import generar_alertas
from modules.analisis import analizar_evolucion, generar_recomendaciones
from modules.database import get_acciones_df, get_documentos_df, init_db
from modules.filtros import aplicar_filtros, render_filtros_sidebar
from modules.reportes import generar_reporte_excel, generar_reporte_pdf, generar_reporte_word

init_db()
st.set_page_config(page_title="SIGATA | Reportes", page_icon="📄", layout="wide")
ui.inject_global_css()
ui.render_header("Generacion de reportes")

df_completo = get_acciones_df()
df_documentos = get_documentos_df()

with st.sidebar:
    st.markdown("### Filtros del reporte")
    filtros_sel = render_filtros_sidebar(df_completo, key_prefix="reportes")

df = aplicar_filtros(df_completo, filtros_sel)

if df.empty:
    st.info("No hay informacion disponible para generar reportes con los filtros seleccionados.")
    st.stop()

alertas = generar_alertas(df, df_documentos)
kpi = kpis.compute_kpis(df, total_recicladores_maestro=df_completo["documento"].nunique(), alertas_activas=len(alertas))
recomendaciones = generar_recomendaciones(df, kpi)
analisis_texto = analizar_evolucion(df)

st.write(f"El reporte se generara con **{len(df)} registros** segun los filtros actualmente seleccionados.")

ui.section_title("Vista previa del resumen ejecutivo")
st.write(analisis_texto)
for r in recomendaciones:
    st.write(f"- {r}")

st.divider()
fecha_str = datetime.now().strftime("%Y%m%d_%H%M")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### 📊 Excel")
    st.caption("Resumen KPI, detalle de acciones y agregados por localidad.")
    excel_bytes = generar_reporte_excel(df, kpi)
    st.download_button(
        "Descargar reporte Excel", data=excel_bytes,
        file_name=f"SIGATA_reporte_{fecha_str}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
with col2:
    st.markdown("#### 📕 PDF")
    st.caption("Reporte ejecutivo con KPIs, analisis, recomendaciones y detalle.")
    pdf_bytes = generar_reporte_pdf(df, kpi, recomendaciones, analisis_texto)
    st.download_button(
        "Descargar reporte PDF", data=pdf_bytes,
        file_name=f"SIGATA_reporte_{fecha_str}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
with col3:
    st.markdown("#### 📝 Word")
    st.caption("Documento editable con indicadores, analisis y recomendaciones.")
    word_bytes = generar_reporte_word(df, kpi, recomendaciones, analisis_texto)
    st.download_button(
        "Descargar reporte Word", data=word_bytes,
        file_name=f"SIGATA_reporte_{fecha_str}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )


ui.render_footer()
