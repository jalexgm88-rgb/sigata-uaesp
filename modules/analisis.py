"""
modules/analisis.py
--------------------------------------------------------------------------------
Motor de analisis inteligente y de recomendaciones automaticas.

Genera, en lenguaje natural y sin plantillas de relleno (no Lorem Ipsum),
parrafos ejecutivos que interpretan el comportamiento de los datos filtrados
en cada momento. La logica es enteramente basada en reglas deterministicas
sobre los propios datos (comparacion de periodos, identificacion de maximos y
minimos, calculo de variaciones porcentuales), de forma que el texto se
actualiza automaticamente cuando cambian los filtros, sin requerir modelos de
lenguaje externos ni conexion a internet.
--------------------------------------------------------------------------------
"""

from datetime import datetime

import pandas as pd


def _trimestre(fecha: pd.Timestamp) -> int:
    return (fecha.month - 1) // 3 + 1


def analizar_evolucion(df: pd.DataFrame) -> str:
    """Analisis ejecutivo de la evolucion temporal y focalizacion territorial."""
    if df.empty or df["fecha"].isna().all():
        return "No hay informacion suficiente en el periodo seleccionado para generar un analisis."

    d = df.dropna(subset=["fecha"]).copy()
    ultima_fecha = d["fecha"].max()
    d["periodo"] = d["fecha"].apply(lambda f: (f.year, _trimestre(f)))
    periodos_ordenados = sorted(d["periodo"].unique())
    if len(periodos_ordenados) < 2:
        periodo_actual = periodos_ordenados[-1]
        actual = d[d["periodo"] == periodo_actual]
        top_loc = actual["localidad"].value_counts().head(2).index.tolist()
        texto = (
            f"En el periodo analizado se registran {len(actual)} acciones afirmativas, "
            f"concentradas principalmente en {', '.join(top_loc) if top_loc else 'las localidades priorizadas'}. "
            "Se recomienda ampliar el periodo de analisis para identificar tendencias comparativas."
        )
        return texto

    periodo_actual = periodos_ordenados[-1]
    periodo_anterior = periodos_ordenados[-2]
    actual = d[d["periodo"] == periodo_actual]
    anterior = d[d["periodo"] == periodo_anterior]

    variacion = len(actual) - len(anterior)
    variacion_pct = (variacion / len(anterior) * 100) if len(anterior) > 0 else 0

    conteo_loc_actual = actual["localidad"].value_counts()
    conteo_loc_anterior = anterior["localidad"].value_counts()
    incrementos = (conteo_loc_actual.subtract(conteo_loc_anterior, fill_value=0)).sort_values(ascending=False)
    localidades_incremento = [loc for loc in incrementos.head(2).index if incrementos[loc] > 0]

    cobertura_actual = actual["documento"].nunique()
    cobertura_anterior = anterior["documento"].nunique()
    variacion_cobertura = cobertura_actual - cobertura_anterior

    conteo_org = actual["organizacion"].value_counts()
    organizaciones_baja_frecuencia = conteo_org[conteo_org <= max(1, conteo_org.median())].index.tolist()[:2]

    tendencia = "un incremento" if variacion > 0 else ("una disminucion" if variacion < 0 else "una estabilidad")
    anio_q = f"{periodo_actual[0]} (T{periodo_actual[1]})"

    texto = (
        f"Durante el periodo {anio_q} se evidencia {tendencia} del numero de acciones afirmativas ejecutadas "
        f"({len(actual)} frente a {len(anterior)} del periodo anterior, variacion de {variacion_pct:+.1f}%)"
    )
    if localidades_incremento:
        texto += f", con mayor dinamismo en las localidades de {' y '.join(localidades_incremento)}"
    texto += (
        f". La cobertura de beneficiarios unicos paso de {cobertura_anterior} a {cobertura_actual} personas "
        f"({variacion_cobertura:+d})."
    )
    if organizaciones_baja_frecuencia:
        texto += (
            f" No obstante, se identifican organizaciones con menor frecuencia de intervencion, entre ellas "
            f"{' y '.join(organizaciones_baja_frecuencia)}, lo que representa una oportunidad para fortalecer "
            f"la focalizacion de futuras acciones."
        )
    return texto


def analizar_cobertura_localidad(df: pd.DataFrame) -> str:
    if df.empty:
        return "No hay datos de cobertura disponibles para el periodo y filtros seleccionados."
    conteo = df.groupby("localidad")["documento"].nunique().sort_values(ascending=False)
    conteo = conteo[conteo.index != ""]
    if conteo.empty:
        return "No hay localidades con informacion de cobertura registrada."
    top = conteo.index[0]
    bottom = conteo.index[-1]
    total = conteo.sum()
    participacion_top = conteo.iloc[0] / total * 100 if total else 0
    return (
        f"La localidad de {top} concentra la mayor cobertura de beneficiarios, con {conteo.iloc[0]} personas "
        f"({participacion_top:.1f}% del total). En contraste, {bottom} presenta la menor cobertura relativa "
        f"({conteo.iloc[-1]} beneficiarios), lo que sugiere revisar la focalizacion territorial de la estrategia."
    )


def analizar_presupuesto(df: pd.DataFrame) -> str:
    if df.empty:
        return "No hay ejecucion presupuestal registrada para el periodo seleccionado."
    total = df["presupuesto"].sum()
    ejecutado = df["presupuesto_ejecutado"].sum()
    pct = (ejecutado / total * 100) if total else 0
    disponible = max(total - ejecutado, 0)
    calificacion = "un nivel de ejecucion adecuado" if pct >= 70 else (
        "un nivel de ejecucion moderado" if pct >= 40 else "un nivel de ejecucion bajo que requiere atencion"
    )
    return (
        f"El presupuesto asociado a las acciones afirmativas asciende a ${total:,.0f}, de los cuales se han "
        f"ejecutado ${ejecutado:,.0f} ({pct:.1f}%), lo que representa {calificacion}. "
        f"El saldo disponible es de ${disponible:,.0f}, pendiente de asignacion a nuevas acciones o proyectos."
    )


def analizar_tipo_accion(df: pd.DataFrame) -> str:
    if df.empty:
        return "No hay acciones afirmativas registradas para caracterizar por tipo."
    conteo = df["tipo_accion"].value_counts()
    conteo = conteo[conteo.index != ""]
    if conteo.empty:
        return "No hay tipos de accion afirmativa clasificados en el periodo seleccionado."
    principal = conteo.index[0]
    participacion = conteo.iloc[0] / conteo.sum() * 100
    return (
        f"El tipo de accion afirmativa predominante es '{principal}', representando el {participacion:.1f}% "
        f"del total de intervenciones registradas, seguido de {', '.join(conteo.index[1:3].tolist())}."
    )


def analizar_beneficios(df: pd.DataFrame) -> str:
    if df.empty:
        return "No hay beneficios entregados para analizar en el periodo seleccionado."
    conteo = df["beneficio"].value_counts()
    conteo = conteo[conteo.index != ""]
    if conteo.empty:
        return "No se registran beneficios clasificados en el periodo seleccionado."
    principal = conteo.index[0]
    return (
        f"El beneficio mas entregado a la poblacion recicladora corresponde a '{principal}' "
        f"({conteo.iloc[0]} entregas), lo que refleja la principal linea de apoyo activa durante el periodo."
    )


# --------------------------------------------------------------------------------
# Motor de recomendaciones
# --------------------------------------------------------------------------------
def generar_recomendaciones(df: pd.DataFrame, kpis: dict) -> list:
    """
    Genera una lista de recomendaciones accionables a partir de los KPIs y del
    comportamiento de los datos filtrados. Las recomendaciones cambian de forma
    automatica segun la informacion visualizada.
    """
    recomendaciones = []

    if df.empty:
        return ["Cargue informacion o amplie los filtros seleccionados para generar recomendaciones."]

    # Cobertura territorial
    conteo_loc = df.groupby("localidad")["documento"].nunique()
    conteo_loc = conteo_loc[conteo_loc.index != ""]
    if not conteo_loc.empty and len(conteo_loc) > 1:
        promedio = conteo_loc.mean()
        rezagadas = conteo_loc[conteo_loc < promedio * 0.6].index.tolist()
        if rezagadas:
            recomendaciones.append(
                f"Fortalecer las acciones afirmativas en las localidades con baja cobertura relativa: "
                f"{', '.join(rezagadas[:3])}."
            )

    # Participacion de organizaciones
    conteo_org = df["organizacion"].value_counts()
    conteo_org = conteo_org[conteo_org.index != ""]
    if not conteo_org.empty and len(conteo_org) > 1:
        rezagadas_org = conteo_org[conteo_org <= conteo_org.quantile(0.25)].index.tolist()
        if rezagadas_org:
            recomendaciones.append(
                f"Priorizar a las organizaciones con menor participacion en el periodo: "
                f"{', '.join(rezagadas_org[:3])}."
            )

    # Ejecucion presupuestal
    if kpis.get("pct_ejecucion_presupuestal", 0) < 60:
        recomendaciones.append(
            "Optimizar la distribucion y ejecucion del presupuesto asignado, actualmente por debajo del 60%."
        )

    # Programas de mayor impacto
    conteo_prog = df[df["estado"] == "Ejecutada"]["programa"].value_counts()
    if not conteo_prog.empty:
        recomendaciones.append(
            f"Reforzar el programa '{conteo_prog.index[0]}', que concentra el mayor numero de acciones "
            f"ejecutadas exitosamente."
        )

    # Informacion incompleta
    campos_clave = ["documento", "organizacion", "localidad", "responsable"]
    incompletos = df[campos_clave].apply(lambda col: (col == "").sum()).sum()
    if incompletos > 0:
        recomendaciones.append(
            f"Actualizar la informacion incompleta detectada en {int(incompletos)} registros de campos clave."
        )

    # Acciones pendientes
    if kpis.get("acciones_pendientes", 0) > 0:
        recomendaciones.append(
            f"Realizar seguimiento prioritario a las {kpis['acciones_pendientes']} acciones afirmativas "
            f"pendientes de ejecucion."
        )

    if not recomendaciones:
        recomendaciones.append(
            "La gestion de las acciones afirmativas presenta un comportamiento adecuado; se recomienda "
            "mantener el ritmo de ejecucion y monitoreo actual."
        )

    return recomendaciones
