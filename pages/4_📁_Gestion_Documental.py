"""
pages/4_Gestion_Documental.py
--------------------------------------------------------------------------------
Pagina de gestion documental. Permite cargar PDF, imagenes, fotografias, actas
y soportes, asociando cada documento a una accion afirmativa especifica, y
consultar / eliminar los documentos ya cargados.
--------------------------------------------------------------------------------
"""

import streamlit as st

from config.settings import TIPOS_DOCUMENTO_SOPORTE
from modules import ui
from modules.database import get_acciones_df, init_db
from modules.documentos import eliminar_documento, guardar_documento, listar_documentos_por_accion

init_db()
st.set_page_config(page_title="SIGATA | Gestion Documental", page_icon="📁", layout="wide")
ui.inject_global_css()
ui.render_header("Gestion documental")

df = get_acciones_df()
if df.empty:
    st.info("Aun no hay acciones afirmativas registradas para asociar documentos.")
    st.stop()

df["etiqueta"] = df["id"].astype(str) + " — " + df["nombre"].fillna("") + " — " + df["tipo_accion"].fillna("")
etiqueta_seleccionada = st.selectbox("Seleccione la accion afirmativa", df["etiqueta"].tolist())
accion_id = int(etiqueta_seleccionada.split(" — ")[0])
registro = df[df["id"] == accion_id].iloc[0]

col_info, col_carga = st.columns([1, 1.4])
with col_info:
    ui.section_title("Detalle de la accion")
    st.write(f"**Reciclador:** {registro['nombre']}")
    st.write(f"**Documento:** {registro['documento']}")
    st.write(f"**Organizacion:** {registro['organizacion']}")
    st.write(f"**Tipo de accion:** {registro['tipo_accion']}")
    st.write(f"**Estado:** {registro['estado']}")

with col_carga:
    ui.section_title("Cargar nuevo documento")
    with st.form("form_carga_documento", clear_on_submit=True):
        tipo_doc = st.selectbox("Tipo de documento", TIPOS_DOCUMENTO_SOPORTE)
        observaciones = st.text_area("Observaciones (opcional)")
        archivo = st.file_uploader(
            "Seleccione el archivo", type=["pdf", "png", "jpg", "jpeg"], key="uploader_doc"
        )
        enviar = st.form_submit_button("Cargar documento", use_container_width=True, type="primary")
        if enviar:
            if archivo is None:
                st.error("Debe seleccionar un archivo antes de cargar.")
            else:
                guardar_documento(accion_id, registro["documento"], archivo, tipo_doc, observaciones)
                st.success("Documento cargado y asociado correctamente.")
                st.rerun()

ui.section_title("Documentos asociados a esta accion")
documentos = listar_documentos_por_accion(accion_id)
if documentos.empty:
    st.info("Esta accion afirmativa aun no tiene documentos asociados.")
else:
    for _, doc in documentos.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"**{doc['nombre_archivo']}**")
            c2.write(f"Tipo: {doc['tipo_documento']} · Cargado: {doc['fecha_carga']}")
            if str(doc["ruta_archivo"]).lower().endswith((".png", ".jpg", ".jpeg")):
                st.image(doc["ruta_archivo"], width=220)
            if c3.button("Eliminar", key=f"del_doc_{doc['id']}"):
                eliminar_documento(int(doc["id"]), doc["ruta_archivo"])
                st.rerun()


ui.render_footer()
