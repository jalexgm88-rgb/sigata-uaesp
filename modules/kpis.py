"""
modules/kpis.py
--------------------------------------------------------------------------------
Calculo centralizado de los indicadores (KPI) que alimentan las tarjetas del
Dashboard Ejecutivo y otros componentes de la aplicacion. Recibe siempre el
DataFrame de acciones afirmativas ya filtrado (segun los filtros inteligentes
seleccionados por el usuario) para que toda la aplicacion reaccione de forma
consistente ante cualquier cambio de filtro.
--------------------------------------------------------------------------------
"""

from datetime import datetime

import pandas as pd


def compute_kpis(df: pd.DataFrame, total_recicladores_maestro: int = None, alertas_activas: int = 0) -> dict:
    """
    Calcula el conjunto completo de KPIs ejecutivos a partir del DataFrame de
    acciones afirmativas (ya filtrado). Retorna un diccionario con valores
    listos para ser mostrados en tarjetas KPI.
    """
    anio_actual = datetime.now().year

    if df.empty:
        return {
            "total_recicladores": total_recicladores_maestro or 0,
            "total_organizaciones": 0,
            "total_acciones": 0,
            "beneficiarios_unicos": 0,
            "cobertura_pct": 0.0,
            "presupuesto_total": 0.0,
            "presupuesto_ejecutado": 0.0,
            "presupuesto_disponible": 0.0,
            "pct_ejecucion_presupuestal": 0.0,
            "acciones_ejecutadas_anio": 0,
            "acciones_pendientes": 0,
            "alertas_activas": alertas_activas,
        }

    beneficiarios_unicos = df["documento"].nunique()
    total_organizaciones = df["organizacion"].replace("", pd.NA).nunique()
    presupuesto_total = float(df["presupuesto"].sum())
    presupuesto_ejecutado = float(df["presupuesto_ejecutado"].sum())
    presupuesto_disponible = max(presupuesto_total - presupuesto_ejecutado, 0)
    pct_ejecucion = (presupuesto_ejecutado / presupuesto_total * 100) if presupuesto_total > 0 else 0.0

    acciones_ejecutadas_anio = int(
        ((df["fecha"].dt.year == anio_actual) & (df["estado"] == "Ejecutada")).sum()
    )
    acciones_pendientes = int(df["estado"].isin(["Planeada", "En ejecucion"]).sum())

    total_recicladores = total_recicladores_maestro if total_recicladores_maestro is not None else beneficiarios_unicos
    cobertura_pct = (beneficiarios_unicos / total_recicladores * 100) if total_recicladores else 0.0

    return {
        "total_recicladores": total_recicladores,
        "total_organizaciones": int(total_organizaciones),
        "total_acciones": int(len(df)),
        "beneficiarios_unicos": int(beneficiarios_unicos),
        "cobertura_pct": round(cobertura_pct, 1),
        "presupuesto_total": presupuesto_total,
        "presupuesto_ejecutado": presupuesto_ejecutado,
        "presupuesto_disponible": presupuesto_disponible,
        "pct_ejecucion_presupuestal": round(pct_ejecucion, 1),
        "acciones_ejecutadas_anio": acciones_ejecutadas_anio,
        "acciones_pendientes": acciones_pendientes,
        "alertas_activas": alertas_activas,
    }


def formatear_moneda(valor: float) -> str:
    """Formatea un valor numerico como pesos colombianos abreviados (ej. $12.4M)."""
    if valor >= 1_000_000_000:
        return f"${valor / 1_000_000_000:,.1f}B"
    if valor >= 1_000_000:
        return f"${valor / 1_000_000:,.1f}M"
    if valor >= 1_000:
        return f"${valor / 1_000:,.0f}K"
    return f"${valor:,.0f}"
