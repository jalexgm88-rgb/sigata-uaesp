"""
modules/charts.py
--------------------------------------------------------------------------------
Fabrica de visualizaciones Plotly usadas en el Dashboard Ejecutivo y en las
demas paginas de la aplicacion. Todas las funciones reciben el DataFrame de
acciones afirmativas ya filtrado y retornan una figura de Plotly lista para
ser mostrada con st.plotly_chart, manteniendo una identidad visual consistente
(paleta institucional, plantilla clara, tipografia limpia).
--------------------------------------------------------------------------------
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.settings import CHART_COLOR_SEQUENCE, PLOTLY_TEMPLATE, COLOR_PRIMARY_GREEN, COLOR_ACCENT_BLUE, COLOR_GRAY_MEDIUM


def _base_layout(fig, height=360):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(family="Segoe UI, Arial", size=13, color="#3B4148"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def evolucion_historica(df: pd.DataFrame):
    """Linea de evolucion mensual del numero de acciones afirmativas en el tiempo."""
    if df.empty:
        return None
    serie = df.set_index("fecha").resample("MS").size().reset_index(name="acciones")
    fig = px.area(
        serie, x="fecha", y="acciones",
        color_discrete_sequence=[COLOR_PRIMARY_GREEN],
        labels={"fecha": "Periodo", "acciones": "Acciones afirmativas"},
    )
    fig.update_traces(line=dict(width=3))
    return _base_layout(fig)


def acciones_por_tipo(df: pd.DataFrame):
    if df.empty:
        return None
    conteo = df["tipo_accion"].value_counts().reset_index()
    conteo.columns = ["tipo_accion", "acciones"]
    fig = px.bar(
        conteo.sort_values("acciones"), x="acciones", y="tipo_accion", orientation="h",
        color_discrete_sequence=[COLOR_PRIMARY_GREEN],
        labels={"tipo_accion": "Tipo de accion afirmativa", "acciones": "Acciones"},
    )
    return _base_layout(fig, height=380)


def cobertura_por_localidad(df: pd.DataFrame):
    if df.empty:
        return None
    conteo = df.groupby("localidad")["documento"].nunique().reset_index(name="beneficiarios")
    conteo = conteo.sort_values("beneficiarios", ascending=False)
    fig = px.bar(
        conteo, x="localidad", y="beneficiarios",
        color="beneficiarios", color_continuous_scale=["#CDE8DC", COLOR_PRIMARY_GREEN],
        labels={"localidad": "Localidad", "beneficiarios": "Beneficiarios unicos"},
    )
    fig.update_layout(coloraxis_showscale=False)
    return _base_layout(fig)


def cobertura_por_organizacion(df: pd.DataFrame, top_n=10):
    if df.empty:
        return None
    conteo = df.groupby("organizacion")["documento"].nunique().reset_index(name="beneficiarios")
    conteo = conteo[conteo["organizacion"] != ""].sort_values("beneficiarios", ascending=False).head(top_n)
    fig = px.bar(
        conteo.sort_values("beneficiarios"), x="beneficiarios", y="organizacion", orientation="h",
        color_discrete_sequence=[COLOR_ACCENT_BLUE],
        labels={"organizacion": "Organizacion", "beneficiarios": "Beneficiarios unicos"},
    )
    return _base_layout(fig, height=380)


def distribucion_beneficios(df: pd.DataFrame):
    if df.empty:
        return None
    conteo = df["beneficio"].value_counts().reset_index()
    conteo.columns = ["beneficio", "acciones"]
    fig = px.pie(
        conteo, names="beneficio", values="acciones", hole=0.55,
        color_discrete_sequence=CHART_COLOR_SEQUENCE,
    )
    fig.update_traces(textinfo="percent+label")
    return _base_layout(fig)


def ejecucion_presupuestal(df: pd.DataFrame):
    if df.empty:
        return None
    total = df["presupuesto"].sum()
    ejecutado = df["presupuesto_ejecutado"].sum()
    disponible = max(total - ejecutado, 0)
    fig = go.Figure(data=[go.Pie(
        labels=["Ejecutado", "Disponible"], values=[ejecutado, disponible], hole=0.6,
        marker=dict(colors=[COLOR_PRIMARY_GREEN, COLOR_GRAY_MEDIUM]),
    )])
    fig.update_traces(textinfo="percent+label")
    return _base_layout(fig)


def indicadores_ods12(df: pd.DataFrame):
    """Aporte de cada programa a las metas ODS 12 (proxy: acciones ejecutadas por programa)."""
    if df.empty:
        return None
    conteo = df[df["estado"] == "Ejecutada"].groupby("programa").size().reset_index(name="acciones_ejecutadas")
    fig = px.bar(
        conteo.sort_values("acciones_ejecutadas"), x="acciones_ejecutadas", y="programa", orientation="h",
        color_discrete_sequence=[COLOR_PRIMARY_GREEN],
        labels={"programa": "Programa (ODS 12)", "acciones_ejecutadas": "Acciones ejecutadas"},
    )
    return _base_layout(fig, height=340)


def evolucion_anual(df: pd.DataFrame):
    if df.empty:
        return None
    conteo = df.groupby(df["fecha"].dt.year).size().reset_index(name="acciones")
    conteo.columns = ["anio", "acciones"]
    fig = px.bar(
        conteo, x="anio", y="acciones", text="acciones",
        color_discrete_sequence=[COLOR_ACCENT_BLUE],
        labels={"anio": "Ano", "acciones": "Acciones afirmativas"},
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(type="category")
    return _base_layout(fig, height=320)


def evolucion_mensual(df: pd.DataFrame):
    if df.empty:
        return None
    d = df.copy()
    d["mes"] = d["fecha"].dt.month
    conteo = d.groupby("mes").size().reindex(range(1, 13), fill_value=0).reset_index(name="acciones")
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    conteo["mes_nombre"] = conteo["mes"].apply(lambda m: meses[m - 1])
    fig = px.line(
        conteo, x="mes_nombre", y="acciones", markers=True,
        color_discrete_sequence=[COLOR_PRIMARY_GREEN],
        labels={"mes_nombre": "Mes", "acciones": "Acciones afirmativas"},
    )
    return _base_layout(fig, height=320)


def indicadores_por_programa(df: pd.DataFrame):
    if df.empty:
        return None
    conteo = df.groupby("programa").agg(
        acciones=("id", "count"), presupuesto=("presupuesto", "sum")
    ).reset_index()
    fig = px.bar(
        conteo.sort_values("acciones"), x="acciones", y="programa", orientation="h",
        color_discrete_sequence=[COLOR_PRIMARY_GREEN],
        labels={"programa": "Programa", "acciones": "Acciones"},
    )
    return _base_layout(fig, height=340)


def indicadores_por_proyecto(df: pd.DataFrame):
    if df.empty:
        return None
    conteo = df.groupby("proyecto").agg(
        acciones=("id", "count"), presupuesto=("presupuesto", "sum")
    ).reset_index()
    fig = px.bar(
        conteo.sort_values("acciones"), x="acciones", y="proyecto", orientation="h",
        color_discrete_sequence=[COLOR_ACCENT_BLUE],
        labels={"proyecto": "Proyecto", "acciones": "Acciones"},
    )
    return _base_layout(fig, height=340)


def distribucion_sexo(df: pd.DataFrame):
    if df.empty:
        return None
    conteo = df.drop_duplicates("documento")["sexo"].value_counts().reset_index()
    conteo.columns = ["sexo", "beneficiarios"]
    fig = px.pie(
        conteo, names="sexo", values="beneficiarios", hole=0.5,
        color_discrete_sequence=CHART_COLOR_SEQUENCE,
    )
    fig.update_traces(textinfo="percent+label")
    return _base_layout(fig, height=320)


def distribucion_grupo_poblacional(df: pd.DataFrame):
    if df.empty:
        return None
    conteo = df.drop_duplicates("documento")["grupo_poblacional"].value_counts().reset_index()
    conteo.columns = ["grupo", "beneficiarios"]
    fig = px.bar(
        conteo.sort_values("beneficiarios"), x="beneficiarios", y="grupo", orientation="h",
        color_discrete_sequence=[COLOR_ACCENT_BLUE],
        labels={"grupo": "Grupo poblacional", "beneficiarios": "Beneficiarios"},
    )
    return _base_layout(fig, height=340)
