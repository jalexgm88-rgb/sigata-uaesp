"""
pages/7_Alertas.py
--------------------------------------------------------------------------------
Pagina de alertas inteligentes. Muestra de forma automatica las situaciones
detectadas por el motor de alertas (modules/alertas.py) que requieren
atencion de gestion: acciones vencidas, beneficiarios duplicados, documentos
faltantes, informacion incompleta, organizaciones sin seguimiento,
presupuestos agotados y acciones pendientes.
--------------------------------------------------------------------------------
"""

import streamlit as st

from modules import ui
from modules.alertas import generar_alertas
from modules.database import get_acciones_df, get_documentos_df, init_db
from modules.filtros import aplicar_filtros, render_filtros_sidebar

init_db()
st.set_page_config(page_title="SIGATA | Alertas", page_icon="🔔", layout="wide")
ui.inject_global_css()
ui.render_header("Alertas inteligentes")

df_completo = get_acciones_df()
df_documentos = get_documentos_df()

with st.sidebar:
    st.markdown("### Filtros de alertas")
    filtros_sel = render_filtros_sidebar(df_completo, key_prefix="alertas")

df = aplicar_filtros(df_completo, filtros_sel)

if df.empty:
    st.info("No hay informacion disponible para evaluar alertas con los filtros seleccionados.")
    st.stop()

alertas = generar_alertas(df, df_documentos)

colores_severidad = {"alta": "danger", "media": "warning", "baja": ""}
iconos_severidad = {"alta": "🔴", "media": "🟠", "baja": "🟢"}

c1, c2, c3 = st.columns(3)
c1.metric("Alertas totales", len(alertas))
c2.metric("Severidad alta", sum(1 for a in alertas if a["severidad"] == "alta"))
c3.metric("Severidad media", sum(1 for a in alertas if a["severidad"] == "media"))

ui.section_title("Detalle de alertas activas")
if not alertas:
    st.success("No se detectaron alertas para los filtros seleccionados. La gestion se encuentra al dia.")
else:
    for alerta in alertas:
        variante = colores_severidad.get(alerta["severidad"], "")
        icono = iconos_severidad.get(alerta["severidad"], "⚪")
        st.markdown(
            f"""
            <div class="kpi-card {variante}" style="height:auto;padding:14px 18px;margin-bottom:10px;">
                <div class="kpi-label">{icono} {alerta['tipo']} · severidad {alerta['severidad']}</div>
                <div style="font-size:15px;color:#3B4148;margin-top:4px;">{alerta['mensaje']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
