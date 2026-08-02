"""
modules/ficha360.py
--------------------------------------------------------------------------------
Construye la vista de "Ficha 360" de un reciclador: datos personales, historial
completo de acciones afirmativas, beneficios recibidos, documentos asociados y
linea de tiempo, cruzando la tabla maestra de recicladores con la tabla de
hechos de acciones afirmativas por numero de documento.
--------------------------------------------------------------------------------
"""

import pandas as pd


def obtener_perfil_reciclador(documento: str, df_recicladores: pd.DataFrame, df_acciones: pd.DataFrame) -> dict:
    """Construye el perfil consolidado de un reciclador a partir de su documento."""
    perfil = {}

    maestro = df_recicladores[df_recicladores["documento"] == documento]
    if not maestro.empty:
        perfil.update(maestro.iloc[0].to_dict())

    historial = df_acciones[df_acciones["documento"] == documento].sort_values("fecha", ascending=False)
    perfil["historial"] = historial

    if not historial.empty:
        if not perfil.get("nombre"):
            perfil["nombre"] = historial.iloc[0]["nombre"]
        if not perfil.get("organizacion"):
            perfil["organizacion"] = historial.iloc[0]["organizacion"]
        if not perfil.get("localidad"):
            perfil["localidad"] = historial.iloc[0]["localidad"]

    perfil["total_acciones"] = len(historial)
    perfil["beneficios_recibidos"] = historial["beneficio"].value_counts().to_dict() if not historial.empty else {}
    perfil["presupuesto_total"] = float(historial["presupuesto"].sum()) if not historial.empty else 0.0
    perfil["presupuesto_ejecutado"] = float(historial["presupuesto_ejecutado"].sum()) if not historial.empty else 0.0

    return perfil


def construir_linea_tiempo(historial: pd.DataFrame) -> list:
    """Retorna una lista de eventos ordenados cronologicamente para la linea de tiempo."""
    eventos = []
    for _, fila in historial.sort_values("fecha").iterrows():
        eventos.append({
            "fecha": fila["fecha"],
            "titulo": fila["tipo_accion"],
            "detalle": f"Programa: {fila['programa']} · Estado: {fila['estado']} · Beneficio: {fila['beneficio']}",
        })
    return eventos
