"""
modules/column_mapper.py
--------------------------------------------------------------------------------
Interfaz y logica de mapeo de columnas. Como los archivos Excel de distintas
dependencias/organizaciones pueden nombrar las columnas de forma diferente,
este modulo permite al usuario indicar, una unica vez, cual columna del
archivo cargado corresponde a cada campo canonico de SIGATA.

Una vez guardado el mapeo (persistido en la tabla config_mapeo), el resto de
la aplicacion (dashboard, filtros, mapa, alertas, reportes) funciona de forma
automatica sobre los datos ya normalizados.
--------------------------------------------------------------------------------
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from config.settings import CAMPOS_CANONICOS
from modules.data_loader import sugerir_mapeo_automatico
from modules.database import insert_acciones_bulk, save_column_mapping


def render_mapping_ui(df: pd.DataFrame, hoja_origen: str, archivo_origen: str) -> dict:
    """
    Dibuja la interfaz de mapeo de columnas para un DataFrame dado y retorna
    el diccionario {campo_canonico: columna_seleccionada} construido con las
    selecciones del usuario. No persiste nada por si solo.
    """
    columnas_disponibles = [""] + list(df.columns)
    sugerencia = sugerir_mapeo_automatico(list(df.columns), CAMPOS_CANONICOS)

    st.caption(
        "SIGATA detecto automaticamente posibles coincidencias. Revise y ajuste "
        "cada campo antes de confirmar el mapeo."
    )

    mapeo = {}
    col1, col2 = st.columns(2)
    campos = list(CAMPOS_CANONICOS.items())
    mitad = (len(campos) + 1) // 2

    for idx, (campo, etiqueta) in enumerate(campos):
        contenedor = col1 if idx < mitad else col2
        valor_sugerido = sugerencia.get(campo, "")
        indice_default = (
            columnas_disponibles.index(valor_sugerido) if valor_sugerido in columnas_disponibles else 0
        )
        seleccion = contenedor.selectbox(
            f"{etiqueta}", columnas_disponibles, index=indice_default, key=f"map_{campo}"
        )
        mapeo[campo] = seleccion

    return mapeo


def validar_mapeo(mapeo: dict) -> list:
    """Retorna una lista de advertencias para campos obligatorios sin mapear."""
    obligatorios = ["documento", "nombre", "fecha", "tipo_accion", "estado"]
    faltantes = [CAMPOS_CANONICOS[c] for c in obligatorios if not mapeo.get(c)]
    return faltantes


def aplicar_mapeo(df: pd.DataFrame, mapeo: dict) -> pd.DataFrame:
    """
    Construye un DataFrame con exactamente las columnas canonicas de SIGATA,
    tomando los valores desde las columnas originales indicadas en el mapeo.
    Los campos canonicos sin columna asociada quedan vacios.
    """
    resultado = pd.DataFrame()
    for campo in CAMPOS_CANONICOS:
        columna_origen = mapeo.get(campo, "")
        if columna_origen and columna_origen in df.columns:
            resultado[campo] = df[columna_origen]
        else:
            resultado[campo] = None

    # Normalizacion de tipos
    resultado["fecha"] = pd.to_datetime(resultado["fecha"], errors="coerce").dt.strftime("%Y-%m-%d")
    resultado["presupuesto"] = pd.to_numeric(resultado["presupuesto"], errors="coerce").fillna(0)
    resultado["edad"] = pd.to_numeric(resultado["edad"], errors="coerce").fillna(0).astype(int)
    resultado["presupuesto_ejecutado"] = 0
    resultado["observaciones"] = ""
    for col in ["documento", "nombre", "organizacion", "localidad", "tipo_accion",
                "programa", "proyecto", "responsable", "estado", "beneficio",
                "sexo", "grupo_poblacional"]:
        resultado[col] = resultado[col].astype(str).replace({"None": "", "nan": ""}).str.strip()

    return resultado


def guardar_mapeo_y_cargar(df_mapeado: pd.DataFrame, mapeo: dict, hoja_origen: str, archivo_origen: str):
    """Persiste el mapeo configurado y realiza la carga masiva a la tabla de hechos."""
    save_column_mapping(mapeo, hoja_origen=hoja_origen, archivo_origen=archivo_origen)
    insert_acciones_bulk(df_mapeado, fuente=f"excel:{archivo_origen}:{hoja_origen}")
