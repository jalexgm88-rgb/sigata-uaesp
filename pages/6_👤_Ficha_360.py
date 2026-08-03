"""
pages/6_Ficha_360.py
--------------------------------------------------------------------------------
Ficha 360 grados de un reciclador de oficio: datos personales, organizacion,
localidad, historial completo de acciones afirmativas, beneficios recibidos,
documentos asociados, observaciones y linea de tiempo.
--------------------------------------------------------------------------------
"""

import streamlit as st

from modules import ui
from modules.database import fetch_df, get_acciones_df, init_db
from modules.documentos import listar_documentos_por_reciclador
from modules.ficha360 import construir_linea_tiempo, obtener_perfil_reciclador

init_db()
st.set_page_config(page_title="SIGATA | Ficha 360", page_icon="👤", layout="wide")
ui.inject_global_css()
ui.render_header("Ficha 360° del reciclador")

df_acciones = get_acciones_df()
df_recicladores = fetch_df("recicladores")

if df_acciones.empty and df_recicladores.empty:
    st.info("Aun no hay recicladores ni acciones afirmativas registradas.")
    st.stop()

documentos_disponibles = sorted(set(
    df_recicladores["documento"].tolist() + (df_acciones["documento"].tolist() if not df_acciones.empty else [])
))
busqueda = st.selectbox("Buscar reciclador por documento", documentos_disponibles)

perfil = obtener_perfil_reciclador(busqueda, df_recicladores, df_acciones)

col_foto, col_datos, col_metricas = st.columns([1, 2, 1.4])
with col_foto:
    if perfil.get("foto_path"):
        st.image(perfil["foto_path"], width=180)
    else:
        st.markdown(
            "<div style='width:160px;height:160px;border-radius:50%;background:#E5F2ED;"
            "display:flex;align-items:center;justify-content:center;font-size:52px;'>♻</div>",
            unsafe_allow_html=True,
        )
with col_datos:
    st.markdown(f"### {perfil.get('nombre', 'Sin nombre registrado')}")
    st.write(f"**Documento:** {busqueda}")
    st.write(f"**Organizacion:** {perfil.get('organizacion', 'No registrada')}")
    st.write(f"**Localidad:** {perfil.get('localidad', 'No registrada')}")
    st.write(f"**Telefono:** {perfil.get('telefono', 'No registrado')}")
    st.write(f"**Fecha de ingreso:** {perfil.get('fecha_ingreso', 'No registrada')}")
    st.write(f"**Grupo poblacional:** {perfil.get('grupo_poblacional', 'No registrado')}")
with col_metricas:
    st.metric("Acciones afirmativas", perfil.get("total_acciones", 0))
    st.metric("Presupuesto ejecutado", f"${perfil.get('presupuesto_ejecutado', 0):,.0f}")

if perfil.get("observaciones"):
    ui.section_title("Observaciones")
    st.write(perfil["observaciones"])

ui.section_title("Beneficios recibidos")
if perfil.get("beneficios_recibidos"):
    for beneficio, cantidad in perfil["beneficios_recibidos"].items():
        st.write(f"- {beneficio}: {cantidad}")
else:
    st.info("Este reciclador aun no registra beneficios.")

ui.section_title("Historial completo de acciones afirmativas")
historial = perfil.get("historial")
if historial is not None and not historial.empty:
    st.dataframe(
        historial[["fecha", "tipo_accion", "programa", "proyecto", "estado", "presupuesto", "beneficio"]],
        use_container_width=True, hide_index=True,
    )
else:
    st.info("No hay acciones afirmativas registradas para este reciclador.")

ui.section_title("Linea de tiempo")
eventos = construir_linea_tiempo(historial) if historial is not None and not historial.empty else []
if eventos:
    for evento in eventos:
        st.markdown(
            f"**{evento['fecha'].strftime('%Y-%m-%d')}** — {evento['titulo']}  \n{evento['detalle']}"
        )
        st.markdown("---")
else:
    st.info("Sin eventos para construir la linea de tiempo.")

ui.section_title("Documentos asociados")
documentos = listar_documentos_por_reciclador(busqueda)
if documentos.empty:
    st.info("Este reciclador no tiene documentos cargados.")
else:
    st.dataframe(
        documentos[["nombre_archivo", "tipo_documento", "fecha_carga"]],
        use_container_width=True, hide_index=True,
    )


ui.render_footer()
