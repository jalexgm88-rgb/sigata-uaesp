"""
modules/forms.py
--------------------------------------------------------------------------------
Componente generico de formularios CRUD (Crear, Consultar, Actualizar,
Eliminar). Una unica funcion `render_entity_crud` es reutilizada por la pagina
de Registro para las ocho entidades solicitadas: acciones afirmativas,
recicladores, organizaciones de recicladores de oficio (ORO), programas,
proyectos, incentivos, lineas de accion y responsables.

La configuracion de cada entidad (campos, tipos de dato, opciones de listas
desplegables) se declara de forma declarativa en un diccionario `campos`, lo
que hace que agregar una nueva entidad en el futuro sea tan simple como
declarar su configuracion, sin duplicar codigo de interfaz.
--------------------------------------------------------------------------------
"""

from datetime import date, datetime

import pandas as pd
import streamlit as st

from modules.database import delete_row, fetch_df, insert_row, update_row


def _render_field(campo: dict, valor_actual=None, key_suffix: str = ""):
    """Dibuja un widget de entrada segun el tipo declarado del campo y retorna el valor capturado."""
    key = f"{campo['key']}_{key_suffix}"
    tipo = campo.get("tipo", "texto")
    label = campo["label"]

    if tipo == "texto":
        return st.text_input(label, value=valor_actual or "", key=key)
    if tipo == "area":
        return st.text_area(label, value=valor_actual or "", key=key)
    if tipo == "numero":
        val = float(valor_actual) if valor_actual not in (None, "") else 0.0
        return st.number_input(label, value=val, step=campo.get("paso", 1.0), key=key)
    if tipo == "entero":
        val = int(float(valor_actual)) if valor_actual not in (None, "") else 0
        return st.number_input(label, value=val, step=1, key=key, format="%d")
    if tipo == "fecha":
        if valor_actual:
            try:
                val = pd.to_datetime(valor_actual).date()
            except Exception:
                val = date.today()
        else:
            val = date.today()
        return st.date_input(label, value=val, key=key)
    if tipo == "select":
        opciones = campo.get("opciones", [])
        indice = opciones.index(valor_actual) if valor_actual in opciones else 0
        return st.selectbox(label, opciones, index=indice, key=key)
    return st.text_input(label, value=valor_actual or "", key=key)


def render_entity_crud(table: str, titulo: str, campos: list, columnas_tabla: list = None):
    """
    Dibuja el modulo CRUD completo (Registrar / Consultar-Editar / Eliminar)
    para una entidad dada, respaldada por una tabla de SQLite.
    """
    st.markdown(f"### {titulo}")
    tab_registrar, tab_consultar, tab_eliminar = st.tabs(
        ["➕ Registrar nuevo", "🔎 Consultar y editar", "🗑️ Eliminar"]
    )

    # ---------------------------- Registrar ----------------------------
    with tab_registrar:
        with st.form(key=f"form_new_{table}", clear_on_submit=True):
            valores = {}
            cols = st.columns(2)
            for i, campo in enumerate(campos):
                with cols[i % 2]:
                    valores[campo["key"]] = _render_field(campo, key_suffix=f"new_{table}")
            enviado = st.form_submit_button("Guardar registro", use_container_width=True)
            if enviado:
                for k, v in valores.items():
                    if isinstance(v, date):
                        valores[k] = v.strftime("%Y-%m-%d")
                insert_row(table, valores)
                st.success(f"Registro guardado correctamente en '{titulo}'.")
                st.rerun()

    # ---------------------------- Consultar / Editar ----------------------------
    with tab_consultar:
        df = fetch_df(table)
        if df.empty:
            st.info("Aun no hay registros para consultar.")
        else:
            columnas_mostrar = columnas_tabla or df.columns.tolist()
            st.dataframe(df[columnas_mostrar], use_container_width=True, hide_index=True, height=260)

            opciones_id = df["id"].tolist()
            id_seleccionado = st.selectbox(
                "Seleccione el registro a editar (por ID)", opciones_id, key=f"edit_select_{table}"
            )
            registro = df[df["id"] == id_seleccionado].iloc[0].to_dict()

            with st.form(key=f"form_edit_{table}"):
                nuevos_valores = {}
                cols = st.columns(2)
                for i, campo in enumerate(campos):
                    with cols[i % 2]:
                        nuevos_valores[campo["key"]] = _render_field(
                            campo, valor_actual=registro.get(campo["key"]), key_suffix=f"edit_{table}"
                        )
                actualizar = st.form_submit_button("Actualizar registro", use_container_width=True)
                if actualizar:
                    for k, v in nuevos_valores.items():
                        if isinstance(v, date):
                            nuevos_valores[k] = v.strftime("%Y-%m-%d")
                    update_row(table, int(id_seleccionado), nuevos_valores)
                    st.success("Registro actualizado correctamente.")
                    st.rerun()

    # ---------------------------- Eliminar ----------------------------
    with tab_eliminar:
        df = fetch_df(table)
        if df.empty:
            st.info("Aun no hay registros para eliminar.")
        else:
            id_borrar = st.selectbox("Seleccione el ID a eliminar", df["id"].tolist(), key=f"del_select_{table}")
            st.warning("Esta accion no se puede deshacer.")
            if st.button("Confirmar eliminacion", key=f"del_btn_{table}", type="primary"):
                delete_row(table, int(id_borrar))
                st.success("Registro eliminado.")
                st.rerun()
