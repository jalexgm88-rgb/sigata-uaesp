"""
modules/filtros.py
--------------------------------------------------------------------------------
Filtros inteligentes reutilizables en toda la aplicacion. Se dibujan en la
barra lateral y retornan un diccionario de seleccion que luego se aplica al
DataFrame de acciones afirmativas mediante `aplicar_filtros`. Todas las
paginas (Dashboard, Mapa, Ficha 360, Alertas, Reportes) comparten esta misma
logica para garantizar consistencia en toda la aplicacion.
--------------------------------------------------------------------------------
"""

import pandas as pd
import streamlit as st


def _opciones(df: pd.DataFrame, columna: str) -> list:
    if df.empty or columna not in df.columns:
        return []
    valores = df[columna].dropna().astype(str)
    valores = valores[valores != ""]
    return sorted(valores.unique().tolist())


def render_filtros_sidebar(df: pd.DataFrame, key_prefix: str = "flt") -> dict:
    """Dibuja los filtros inteligentes en la barra lateral y retorna la seleccion."""
    st.markdown("#### Filtros inteligentes")

    anios = sorted(df["fecha"].dt.year.dropna().unique().tolist()) if not df.empty else []
    meses_dict = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
    }

    seleccion = {}
    seleccion["anio"] = st.multiselect("Año", anios, default=[], key=f"{key_prefix}_anio")
    seleccion["mes"] = st.multiselect(
        "Mes", list(meses_dict.keys()), format_func=lambda m: meses_dict[m], default=[], key=f"{key_prefix}_mes"
    )
    seleccion["localidad"] = st.multiselect("Localidad", _opciones(df, "localidad"), key=f"{key_prefix}_localidad")
    seleccion["organizacion"] = st.multiselect("Organizacion", _opciones(df, "organizacion"), key=f"{key_prefix}_org")
    seleccion["programa"] = st.multiselect("Programa", _opciones(df, "programa"), key=f"{key_prefix}_prog")
    seleccion["proyecto"] = st.multiselect("Proyecto", _opciones(df, "proyecto"), key=f"{key_prefix}_proy")
    seleccion["responsable"] = st.multiselect("Responsable", _opciones(df, "responsable"), key=f"{key_prefix}_resp")
    seleccion["estado"] = st.multiselect("Estado", _opciones(df, "estado"), key=f"{key_prefix}_estado")
    seleccion["sexo"] = st.multiselect("Sexo", _opciones(df, "sexo"), key=f"{key_prefix}_sexo")
    seleccion["grupo_poblacional"] = st.multiselect(
        "Grupo poblacional", _opciones(df, "grupo_poblacional"), key=f"{key_prefix}_grupo"
    )
    seleccion["tipo_accion"] = st.multiselect("Tipo de accion afirmativa", _opciones(df, "tipo_accion"), key=f"{key_prefix}_tipo")
    seleccion["reciclador"] = st.multiselect("Reciclador (nombre)", _opciones(df, "nombre"), key=f"{key_prefix}_recic")

    if st.button("Limpiar filtros", use_container_width=True, key=f"{key_prefix}_clear"):
        for k in list(st.session_state.keys()):
            if k.startswith(f"{key_prefix}_"):
                del st.session_state[k]
        st.rerun()

    return seleccion


def aplicar_filtros(df: pd.DataFrame, seleccion: dict) -> pd.DataFrame:
    """Aplica el diccionario de seleccion de filtros sobre el DataFrame de acciones."""
    if df.empty:
        return df
    resultado = df.copy()

    if seleccion.get("anio"):
        resultado = resultado[resultado["fecha"].dt.year.isin(seleccion["anio"])]
    if seleccion.get("mes"):
        resultado = resultado[resultado["fecha"].dt.month.isin(seleccion["mes"])]
    if seleccion.get("localidad"):
        resultado = resultado[resultado["localidad"].isin(seleccion["localidad"])]
    if seleccion.get("organizacion"):
        resultado = resultado[resultado["organizacion"].isin(seleccion["organizacion"])]
    if seleccion.get("programa"):
        resultado = resultado[resultado["programa"].isin(seleccion["programa"])]
    if seleccion.get("proyecto"):
        resultado = resultado[resultado["proyecto"].isin(seleccion["proyecto"])]
    if seleccion.get("responsable"):
        resultado = resultado[resultado["responsable"].isin(seleccion["responsable"])]
    if seleccion.get("estado"):
        resultado = resultado[resultado["estado"].isin(seleccion["estado"])]
    if seleccion.get("sexo"):
        resultado = resultado[resultado["sexo"].isin(seleccion["sexo"])]
    if seleccion.get("grupo_poblacional"):
        resultado = resultado[resultado["grupo_poblacional"].isin(seleccion["grupo_poblacional"])]
    if seleccion.get("tipo_accion"):
        resultado = resultado[resultado["tipo_accion"].isin(seleccion["tipo_accion"])]
    if seleccion.get("reciclador"):
        resultado = resultado[resultado["nombre"].isin(seleccion["reciclador"])]

    return resultado
