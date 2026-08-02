"""
pages/2_Configuracion_Mapeo.py
--------------------------------------------------------------------------------
Pagina de configuracion automatica / mapeo de columnas. Traduce las columnas
reales del archivo Excel cargado (que pueden variar de un archivo a otro)
hacia los campos canonicos de SIGATA. Una vez guardado, el mapeo queda
persistido y toda la aplicacion (dashboard, filtros, mapa, alertas, reportes)
funciona automaticamente sobre los datos ya normalizados.
--------------------------------------------------------------------------------
"""

import streamlit as st

from modules import ui
from modules.column_mapper import (
    aplicar_mapeo, guardar_mapeo_y_cargar, render_mapping_ui, validar_mapeo,
)
from modules.database import init_db, load_column_mapping

init_db()
st.set_page_config(page_title="SIGATA | Configuracion y Mapeo", page_icon="⚙️", layout="wide")
ui.inject_global_css()
ui.render_header("Configuracion automatica de columnas")

st.write(
    "Como los nombres de columnas pueden variar entre archivos de diferentes "
    "organizaciones o dependencias, indique aqui cual columna del archivo "
    "cargado corresponde a cada campo de SIGATA."
)

hojas = st.session_state.get("sigata_hojas")
if not hojas:
    st.warning("Primero debe cargar un archivo Excel en la pagina **'Carga de Datos'**.")
    st.stop()

hoja_activa = st.session_state.get("sigata_hoja_activa", list(hojas.keys())[0])
hoja_activa = st.selectbox("Hoja a mapear", list(hojas.keys()), index=list(hojas.keys()).index(hoja_activa))
df_hoja = hojas[hoja_activa]
archivo_nombre = st.session_state.get("sigata_archivo_nombre", "archivo.xlsx")

mapeo_previo = load_column_mapping()
if mapeo_previo:
    st.caption("Se encontro un mapeo guardado previamente. Puede ajustarlo si lo requiere.")

ui.section_title("Mapeo de columnas")
mapeo = render_mapping_ui(df_hoja, hoja_activa, archivo_nombre)

faltantes = validar_mapeo(mapeo)
if faltantes:
    st.warning(f"Campos obligatorios sin mapear: {', '.join(faltantes)}.")

if st.button("Confirmar mapeo y cargar datos a SIGATA", type="primary", use_container_width=True):
    df_mapeado = aplicar_mapeo(df_hoja, mapeo)
    guardar_mapeo_y_cargar(df_mapeado, mapeo, hoja_activa, archivo_nombre)
    st.success(
        f"Se cargaron {len(df_mapeado)} registros a SIGATA con el mapeo configurado. "
        "El Dashboard Ejecutivo y las demas paginas ya reflejan esta informacion."
    )
    st.dataframe(df_mapeado.head(15), use_container_width=True)
