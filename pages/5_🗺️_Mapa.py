"""
pages/5_Mapa.py
--------------------------------------------------------------------------------
Pagina de mapa geografico de Bogota. Visualiza organizaciones, recicladores,
cobertura territorial y concentracion de beneficios de las acciones
afirmativas, respetando los filtros inteligentes seleccionados por el
usuario.
--------------------------------------------------------------------------------
"""

import streamlit as st
from streamlit_folium import st_folium

from modules import ui
from modules.database import fetch_df, get_acciones_df, init_db
from modules.filtros import aplicar_filtros, render_filtros_sidebar
from modules.mapa import construir_mapa

init_db()
st.set_page_config(page_title="SIGATA | Mapa", page_icon="🗺️", layout="wide")
ui.inject_global_css()
ui.render_header("Mapa de Bogota — Organizaciones, recicladores y cobertura")

df_completo = get_acciones_df()
df_organizaciones = fetch_df("organizaciones")

with st.sidebar:
    st.markdown("### Filtros del mapa")
    filtros_sel = render_filtros_sidebar(df_completo, key_prefix="mapa")

df = aplicar_filtros(df_completo, filtros_sel)

if df.empty:
    st.info("No hay informacion geografica para los filtros seleccionados.")
    st.stop()

col_a, col_b, col_c = st.columns(3)
col_a.metric("Localidades con cobertura", df["localidad"].replace("", None).nunique())
col_b.metric("Organizaciones visibles", df_organizaciones.shape[0] if not df_organizaciones.empty else 0)
col_c.metric("Beneficiarios georreferenciados", df["documento"].nunique())

mapa = construir_mapa(df, df_organizaciones)
st_folium(mapa, use_container_width=True, height=620, returned_objects=[])

st.caption(
    "Las coordenadas se ubican alrededor del centroide de cada localidad (no se captura "
    "direccion exacta), con el fin de representar de forma visual la concentracion territorial "
    "de organizaciones, recicladores y beneficios."
)
