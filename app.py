"""
app.py
--------------------------------------------------------------------------------
SIGATA - Sistema Integral para la Gestion y Trazabilidad de las Acciones
Afirmativas. Punto de entrada de la aplicacion Streamlit.

Esta pagina actua como "Inicio" del sistema y muestra el Dashboard Ejecutivo:
tarjetas KPI, visualizaciones principales con analisis automatico en lenguaje
natural y recomendaciones accionables. El resto de funcionalidades (carga de
datos, mapeo, registro, documentos, mapa, ficha 360, alertas y reportes) se
encuentran organizadas como paginas independientes en la carpeta `pages/`,
siguiendo el mecanismo nativo de multipagina de Streamlit.

Ejecucion:
    streamlit run app.py
--------------------------------------------------------------------------------
"""

import streamlit as st

from config.settings import APP_NAME, APP_PROJECT
from modules import charts, kpis, ui
from modules.alertas import generar_alertas
from modules.database import get_acciones_df, get_documentos_df, get_metadata, init_db
from modules.demo_data_generator import generar_datos_demo
from modules.filtros import aplicar_filtros, render_filtros_sidebar
from modules.analisis import (
    analizar_beneficios, analizar_cobertura_localidad, analizar_evolucion,
    analizar_presupuesto, analizar_tipo_accion, generar_recomendaciones,
)

st.set_page_config(
    page_title=f"{APP_NAME} | Dashboard Ejecutivo",
    page_icon="♻",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------------
# Inicializacion: base de datos y datos demo (solo la primera vez)
# --------------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _inicializar_sistema():
    init_db()
    if get_metadata("datos_demo_generados") != "true":
        generar_datos_demo()
    return True


_inicializar_sistema()
ui.inject_global_css()

# --------------------------------------------------------------------------------
# Encabezado
# --------------------------------------------------------------------------------
ui.render_header("Dashboard Ejecutivo - Subdireccion de Aprovechamiento")

with st.expander("Sobre el proyecto de investigacion", expanded=False):
    st.write(APP_PROJECT)

# --------------------------------------------------------------------------------
# Carga de datos y filtros
# --------------------------------------------------------------------------------
df_completo = get_acciones_df()
df_documentos = get_documentos_df()

with st.sidebar:
    st.markdown(f"### ♻ {APP_NAME}")
    st.caption("Navegue usando el menu de paginas para cargar datos, registrar "
               "informacion, ver el mapa, la ficha 360 y generar reportes.")
    st.divider()
    filtros_sel = render_filtros_sidebar(df_completo, key_prefix="home")

df = aplicar_filtros(df_completo, filtros_sel)

if df_completo.empty:
    st.info(
        "Aun no hay acciones afirmativas registradas. Use la pagina "
        "**'Carga de Datos'** para importar un archivo Excel o registre "
        "informacion desde la pagina **'Registro'**."
    )
    st.stop()

alertas = generar_alertas(df, df_documentos)
total_recicladores_maestro = df_completo["documento"].nunique()
kpi = kpis.compute_kpis(df, total_recicladores_maestro=total_recicladores_maestro, alertas_activas=len(alertas))

# --------------------------------------------------------------------------------
# Tarjetas KPI
# --------------------------------------------------------------------------------
ui.section_title("Indicadores clave")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    ui.render_kpi_card("Recicladores registrados", f"{kpi['total_recicladores']:,}")
with c2:
    ui.render_kpi_card("Organizaciones (ORO)", f"{kpi['total_organizaciones']:,}", variant="blue")
with c3:
    ui.render_kpi_card("Acciones afirmativas", f"{kpi['total_acciones']:,}")
with c4:
    ui.render_kpi_card("Beneficiarios unicos", f"{kpi['beneficiarios_unicos']:,}", variant="blue")
with c5:
    ui.render_kpi_card("Cobertura", f"{kpi['cobertura_pct']:.1f}%", "sobre poblacion registrada")

c6, c7, c8, c9, c10 = st.columns(5)
with c6:
    ui.render_kpi_card("Presupuesto ejecutado", kpis.formatear_moneda(kpi["presupuesto_ejecutado"]),
                        f"{kpi['pct_ejecucion_presupuestal']:.1f}% del total")
with c7:
    ui.render_kpi_card("Presupuesto disponible", kpis.formatear_moneda(kpi["presupuesto_disponible"]), variant="blue")
with c8:
    ui.render_kpi_card("Ejecutadas este año", f"{kpi['acciones_ejecutadas_anio']:,}")
with c9:
    ui.render_kpi_card("Acciones pendientes", f"{kpi['acciones_pendientes']:,}", variant="warning")
with c10:
    ui.render_kpi_card("Alertas activas", f"{kpi['alertas_activas']:,}",
                        "revisar pagina de Alertas", variant="danger" if kpi["alertas_activas"] > 3 else "warning")

# --------------------------------------------------------------------------------
# Evolucion historica
# --------------------------------------------------------------------------------
ui.section_title("Evolucion historica de acciones afirmativas")
st.plotly_chart(charts.evolucion_historica(df), use_container_width=True)
ui.render_analysis(analizar_evolucion(df))

# --------------------------------------------------------------------------------
# Fila: tipo de accion / cobertura por localidad
# --------------------------------------------------------------------------------
col_izq, col_der = st.columns(2)
with col_izq:
    ui.section_title("Acciones afirmativas por tipo")
    st.plotly_chart(charts.acciones_por_tipo(df), use_container_width=True)
    ui.render_analysis(analizar_tipo_accion(df))
with col_der:
    ui.section_title("Cobertura por localidad")
    st.plotly_chart(charts.cobertura_por_localidad(df), use_container_width=True)
    ui.render_analysis(analizar_cobertura_localidad(df))

# --------------------------------------------------------------------------------
# Fila: cobertura por organizacion / distribucion de beneficios
# --------------------------------------------------------------------------------
col_izq2, col_der2 = st.columns(2)
with col_izq2:
    ui.section_title("Cobertura por organizacion (Top 10)")
    st.plotly_chart(charts.cobertura_por_organizacion(df), use_container_width=True)
with col_der2:
    ui.section_title("Distribucion de beneficios")
    st.plotly_chart(charts.distribucion_beneficios(df), use_container_width=True)
    ui.render_analysis(analizar_beneficios(df))

# --------------------------------------------------------------------------------
# Fila: ejecucion presupuestal / indicadores ODS 12
# --------------------------------------------------------------------------------
col_izq3, col_der3 = st.columns(2)
with col_izq3:
    ui.section_title("Ejecucion presupuestal")
    st.plotly_chart(charts.ejecucion_presupuestal(df), use_container_width=True)
    ui.render_analysis(analizar_presupuesto(df))
with col_der3:
    ui.section_title("Indicadores ODS 12 (acciones ejecutadas por programa)")
    st.plotly_chart(charts.indicadores_ods12(df), use_container_width=True)

# --------------------------------------------------------------------------------
# Fila: evolucion anual / mensual
# --------------------------------------------------------------------------------
col_izq4, col_der4 = st.columns(2)
with col_izq4:
    ui.section_title("Evolucion anual")
    st.plotly_chart(charts.evolucion_anual(df), use_container_width=True)
with col_der4:
    ui.section_title("Evolucion mensual (estacionalidad)")
    st.plotly_chart(charts.evolucion_mensual(df), use_container_width=True)

# --------------------------------------------------------------------------------
# Fila: indicadores por programa / proyecto
# --------------------------------------------------------------------------------
col_izq5, col_der5 = st.columns(2)
with col_izq5:
    ui.section_title("Indicadores por programa")
    st.plotly_chart(charts.indicadores_por_programa(df), use_container_width=True)
with col_der5:
    ui.section_title("Indicadores por proyecto")
    st.plotly_chart(charts.indicadores_por_proyecto(df), use_container_width=True)

# --------------------------------------------------------------------------------
# Recomendaciones automaticas
# --------------------------------------------------------------------------------
recomendaciones = generar_recomendaciones(df, kpi)
ui.render_recomendaciones(recomendaciones)

st.caption(
    "SIGATA | Producto Minimo Viable desarrollado para la estrategia de innovacion de la "
    "Subdireccion de Aprovechamiento - UAESP. Los datos mostrados por defecto son ilustrativos."
)

ui.render_footer()
