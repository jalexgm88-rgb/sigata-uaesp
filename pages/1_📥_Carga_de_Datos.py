"""
pages/1_Carga_de_Datos.py
--------------------------------------------------------------------------------
Pagina de carga de archivos Excel. Permite al usuario subir un libro de Excel
y detecta automaticamente hojas, columnas, tipos de dato y cantidad de
registros, dejando el resultado disponible en `st.session_state` para que la
pagina de Configuracion / Mapeo continue el flujo de carga.
--------------------------------------------------------------------------------
"""

import streamlit as st

from modules import ui
from modules.data_loader import get_column_profile, get_sheet_summary, load_excel_file
from modules.database import init_db

init_db()
st.set_page_config(page_title="SIGATA | Carga de Datos", page_icon="📥", layout="wide")
ui.inject_global_css()
ui.render_header("Carga de informacion desde Excel")

st.write(
    "Cargue un archivo Excel (.xlsx) con la informacion de acciones afirmativas. "
    "SIGATA identificara automaticamente las hojas disponibles, los nombres de "
    "columnas, el tipo de dato de cada una y la cantidad de registros."
)

archivo = st.file_uploader("Seleccione el archivo Excel", type=["xlsx", "xls"])

if archivo is not None:
    with st.spinner("Analizando el archivo..."):
        hojas = load_excel_file(archivo)
        st.session_state["sigata_hojas"] = hojas
        st.session_state["sigata_archivo_nombre"] = archivo.name

    ui.section_title("Hojas detectadas")
    resumen = get_sheet_summary(hojas)
    st.dataframe(resumen, use_container_width=True, hide_index=True)

    hoja_seleccionada = st.selectbox("Seleccione la hoja a explorar / cargar", list(hojas.keys()))
    df_hoja = hojas[hoja_seleccionada]
    st.session_state["sigata_hoja_activa"] = hoja_seleccionada

    ui.section_title(f"Perfil de columnas — {hoja_seleccionada}")
    perfil = get_column_profile(df_hoja)
    st.dataframe(perfil, use_container_width=True, hide_index=True)

    ui.section_title("Vista previa de los datos")
    st.dataframe(df_hoja.head(20), use_container_width=True)

    st.success(
        f"Archivo analizado correctamente: {df_hoja.shape[0]} registros y "
        f"{df_hoja.shape[1]} columnas en la hoja '{hoja_seleccionada}'. "
        "Continue en la pagina **'Configuracion Mapeo'** para asociar las columnas "
        "de este archivo con los campos de SIGATA."
    )
else:
    st.info("Aun no se ha cargado ningun archivo en esta sesion.")


ui.render_footer()
