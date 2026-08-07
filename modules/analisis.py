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
# Metadatos de priorizacion para cada tipo de recomendacion. Se usan
# unicamente en las vistas enriquecidas (matriz visual del Informe
# Ejecutivo); no alteran el texto ni la logica original de cada
# recomendacion, solo la clasifican para su presentacion.
_META_RECOMENDACIONES = {
    "cobertura_territorial": {
        "icono": "pin", "impacto": "Equidad territorial",
        "prioridad": "Alta", "responsable": "Gestor Territorial",
        "horizonte": "Corto plazo (0-3 meses)",
    },
    "participacion_organizaciones": {
        "icono": "objetivo", "impacto": "Fortalecimiento asociativo",
        "prioridad": "Media", "responsable": "Coordinacion de Organizaciones",
        "horizonte": "Mediano plazo (3-6 meses)",
    },
    "ejecucion_presupuestal": {
        "icono": "dinero", "impacto": "Optimizacion financiera",
        "prioridad": "Alta", "responsable": "Subdireccion de Aprovechamiento",
        "horizonte": "Corto plazo (0-3 meses)",
    },
    "programa_destacado": {
        "icono": "bombilla", "impacto": "Escalamiento de buenas practicas",
        "prioridad": "Media", "responsable": "Enlace ODS 12",
        "horizonte": "Mediano plazo (3-6 meses)",
    },
    "informacion_incompleta": {
        "icono": "documento", "impacto": "Calidad e integridad de datos",
        "prioridad": "Media", "responsable": "Equipo Social UAESP",
        "horizonte": "Corto plazo (0-3 meses)",
    },
    "acciones_pendientes": {
        "icono": "reloj", "impacto": "Cumplimiento de metas",
        "prioridad": "Alta", "responsable": "Subdireccion de Aprovechamiento",
        "horizonte": "Corto plazo (0-3 meses)",
    },
    "gestion_adecuada": {
        "icono": "check", "impacto": "Sostenibilidad de resultados",
        "prioridad": "Baja", "responsable": "Subdireccion de Aprovechamiento",
        "horizonte": "Largo plazo (6-12 meses)",
    },
    "sin_datos": {
        "icono": "documento", "impacto": "Disponibilidad de informacion",
        "prioridad": "Alta", "responsable": "Subdireccion de Aprovechamiento",
        "horizonte": "Corto plazo (0-3 meses)",
    },
}


def _generar_recomendaciones_detalladas(df: pd.DataFrame, kpis: dict) -> list:
    """
    Motor unico de recomendaciones: evalua las mismas reglas deterministicas
    sobre los datos filtrados y retorna cada recomendacion como diccionario
    ({categoria, texto, icono, impacto, prioridad, responsable, horizonte}).
    `generar_recomendaciones()` y `generar_recomendaciones_matriz()` son dos
    proyecciones distintas de este mismo resultado (texto plano vs. matriz
    enriquecida), por lo que ambas permanecen siempre sincronizadas.
    """
    detalladas = []

    def _agregar(categoria, texto):
        meta = _META_RECOMENDACIONES[categoria]
        detalladas.append({"categoria": categoria, "texto": texto, **meta})

    if df.empty:
        _agregar("sin_datos", "Cargue informacion o amplie los filtros seleccionados para generar recomendaciones.")
        return detalladas

    # Cobertura territorial
    conteo_loc = df.groupby("localidad")["documento"].nunique()
    conteo_loc = conteo_loc[conteo_loc.index != ""]
    if not conteo_loc.empty and len(conteo_loc) > 1:
        promedio = conteo_loc.mean()
        rezagadas = conteo_loc[conteo_loc < promedio * 0.6].index.tolist()
        if rezagadas:
            _agregar(
                "cobertura_territorial",
                f"Fortalecer las acciones afirmativas en las localidades con baja cobertura relativa: "
                f"{', '.join(rezagadas[:3])}.",
            )

    # Participacion de organizaciones
    conteo_org = df["organizacion"].value_counts()
    conteo_org = conteo_org[conteo_org.index != ""]
    if not conteo_org.empty and len(conteo_org) > 1:
        rezagadas_org = conteo_org[conteo_org <= conteo_org.quantile(0.25)].index.tolist()
        if rezagadas_org:
            _agregar(
                "participacion_organizaciones",
                f"Priorizar a las organizaciones con menor participacion en el periodo: "
                f"{', '.join(rezagadas_org[:3])}.",
            )

    # Ejecucion presupuestal
    if kpis.get("pct_ejecucion_presupuestal", 0) < 60:
        _agregar(
            "ejecucion_presupuestal",
            "Optimizar la distribucion y ejecucion del presupuesto asignado, actualmente por debajo del 60%.",
        )

    # Programas de mayor impacto
    conteo_prog = df[df["estado"] == "Ejecutada"]["programa"].value_counts()
    if not conteo_prog.empty:
        _agregar(
            "programa_destacado",
            f"Reforzar el programa '{conteo_prog.index[0]}', que concentra el mayor numero de acciones "
            f"ejecutadas exitosamente.",
        )

    # Informacion incompleta
    campos_clave = ["documento", "organizacion", "localidad", "responsable"]
    incompletos = df[campos_clave].apply(lambda col: (col == "").sum()).sum()
    if incompletos > 0:
        _agregar(
            "informacion_incompleta",
            f"Actualizar la informacion incompleta detectada en {int(incompletos)} registros de campos clave.",
        )

    # Acciones pendientes
    if kpis.get("acciones_pendientes", 0) > 0:
        _agregar(
            "acciones_pendientes",
            f"Realizar seguimiento prioritario a las {kpis['acciones_pendientes']} acciones afirmativas "
            f"pendientes de ejecucion.",
        )

    if not detalladas:
        _agregar(
            "gestion_adecuada",
            "La gestion de las acciones afirmativas presenta un comportamiento adecuado; se recomienda "
            "mantener el ritmo de ejecucion y monitoreo actual.",
        )

    return detalladas


def generar_recomendaciones(df: pd.DataFrame, kpis: dict) -> list:
    """
    Genera una lista de recomendaciones accionables (solo texto) a partir de
    los KPIs y del comportamiento de los datos filtrados. Mantiene el mismo
    comportamiento y firma que siempre ha tenido esta funcion; internamente
    delega en `_generar_recomendaciones_detalladas()`.
    """
    return [d["texto"] for d in _generar_recomendaciones_detalladas(df, kpis)]


def generar_recomendaciones_matriz(df: pd.DataFrame, kpis: dict) -> list:
    """
    Version enriquecida de `generar_recomendaciones()`: retorna las mismas
    recomendaciones (mismo texto, mismas reglas) pero acompanadas de
    metadatos de priorizacion (impacto esperado, prioridad, responsable
    sugerido y horizonte de implementacion). Pensada para la matriz visual
    de recomendaciones del Informe Ejecutivo.
    """
    return _generar_recomendaciones_detalladas(df, kpis)


# --------------------------------------------------------------------------------
# Indicador de tendencia generico (usado en tarjetas KPI del Dashboard y en
# los elementos visuales del Informe Ejecutivo)
# --------------------------------------------------------------------------------
def variacion_periodo(df: pd.DataFrame) -> dict:
    """
    Compara el numero de registros del ultimo trimestre disponible frente al
    trimestre inmediatamente anterior dentro del DataFrame recibido (ya
    filtrado). Retorna un valor numerico puro (sin simbolos ni texto), listo
    para alimentar tanto texto como elementos graficos (flechas, chips de
    tendencia):
        {"delta_pct": float | None, "direccion": "up" | "down" | "flat" | "sin_datos"}
    """
    if df.empty or "fecha" not in df.columns or df["fecha"].isna().all():
        return {"delta_pct": None, "direccion": "sin_datos"}
    d = df.dropna(subset=["fecha"]).copy()
    d["periodo"] = d["fecha"].apply(lambda f: (f.year, _trimestre(f)))
    periodos = sorted(d["periodo"].unique())
    if len(periodos) < 2:
        return {"delta_pct": None, "direccion": "sin_datos"}
    actual = len(d[d["periodo"] == periodos[-1]])
    anterior = len(d[d["periodo"] == periodos[-2]])
    if anterior == 0:
        return {"delta_pct": None, "direccion": "sin_datos"}
    delta_pct = (actual - anterior) / anterior * 100
    direccion = "up" if delta_pct > 0.5 else ("down" if delta_pct < -0.5 else "flat")
    return {"delta_pct": round(delta_pct, 1), "direccion": direccion}


def tendencia_conteo(df: pd.DataFrame) -> str:
    """
    Version en texto de `variacion_periodo()`, lista para mostrar en una
    tarjeta KPI, p. ej. '▲ 12.4% vs. periodo anterior'. Retorna cadena vacia
    si no hay suficiente informacion para comparar.
    """
    variacion = variacion_periodo(df)
    if variacion["direccion"] == "sin_datos":
        return ""
    if variacion["direccion"] == "up":
        return f"▲ {variacion['delta_pct']:.1f}% vs. periodo anterior"
    if variacion["direccion"] == "down":
        return f"▼ {abs(variacion['delta_pct']):.1f}% vs. periodo anterior"
    return "▬ estable vs. periodo anterior"


# --------------------------------------------------------------------------------
# Valor Publico Generado: indicador sintetico de impacto institucional
# --------------------------------------------------------------------------------
_CAMPOS_CLAVE_COMPLETITUD = [
    "documento", "nombre", "organizacion", "localidad", "tipo_accion",
    "programa", "proyecto", "responsable", "estado", "beneficio",
]

_PESOS_VALOR_PUBLICO = {
    "cobertura": 0.25,
    "trazabilidad": 0.20,
    "completitud_registros": 0.20,
    "evidencia_documental": 0.20,
    "seguimiento_oportuno": 0.15,
}


def _componentes_valor_publico(df: pd.DataFrame, df_documentos: pd.DataFrame,
                                total_recicladores_maestro: int) -> dict:
    """Calcula, sobre un DataFrame ya filtrado, los cinco componentes (0-100)
    que integran el indicador sintetico 'Valor Publico Generado'."""
    if df.empty:
        return {k: 0.0 for k in _PESOS_VALOR_PUBLICO}

    # 1. Cobertura de beneficiarios sobre la poblacion registrada.
    beneficiarios_unicos = df["documento"].nunique()
    cobertura = (
        beneficiarios_unicos / total_recicladores_maestro * 100
        if total_recicladores_maestro else 0.0
    )
    cobertura = min(cobertura, 100.0)

    # 2. Completitud de registros: proporcion de acciones con todos los
    #    campos clave diligenciados (sin vacios).
    campos = [c for c in _CAMPOS_CLAVE_COMPLETITUD if c in df.columns]
    completos = df[campos].apply(lambda fila: all(str(v).strip() != "" for v in fila), axis=1)
    completitud_registros = completos.mean() * 100 if len(df) else 0.0

    # 3. Trazabilidad completa: acciones con fecha, estado y responsable
    #    asignados y con una ejecucion presupuestal coherente (no mayor a lo
    #    presupuestado), como proxy de un ciclo de gestion bien documentado.
    trazable = (
        df["fecha"].notna()
        & (df["estado"].astype(str).str.strip() != "")
        & (df["responsable"].astype(str).str.strip() != "")
        & (df["presupuesto_ejecutado"] <= df["presupuesto"] + 1)
    )
    trazabilidad = trazable.mean() * 100 if len(df) else 0.0

    # 4. Evidencia documental: de las acciones ya ejecutadas, cuantas cuentan
    #    con al menos un soporte cargado en Gestion Documental.
    ejecutadas = df[df["estado"] == "Ejecutada"]
    if len(ejecutadas) == 0:
        evidencia_documental = 100.0  # no aplica: no se penaliza el indicador
    elif df_documentos is not None and not df_documentos.empty:
        ids_con_doc = set(df_documentos["accion_id"].unique())
        evidencia_documental = ejecutadas["id"].isin(ids_con_doc).mean() * 100
    else:
        evidencia_documental = 0.0

    # 5. Seguimiento oportuno: complemento de las acciones vencidas o que no
    #    iniciaron a tiempo, sobre el total de acciones del periodo.
    hoy = pd.Timestamp(datetime.now().date())
    vencidas = (
        (df["estado"] == "Vencida") | ((df["fecha"] < hoy) & (df["estado"] == "Planeada"))
    ).sum()
    seguimiento_oportuno = max(0.0, 100 - (vencidas / len(df) * 100)) if len(df) else 100.0

    return {
        "cobertura": round(cobertura, 1),
        "trazabilidad": round(trazabilidad, 1),
        "completitud_registros": round(completitud_registros, 1),
        "evidencia_documental": round(evidencia_documental, 1),
        "seguimiento_oportuno": round(seguimiento_oportuno, 1),
    }


def calcular_valor_publico(df: pd.DataFrame, df_documentos: pd.DataFrame, kpi: dict) -> dict:
    """
    Calcula el indicador compuesto 'Valor Publico Generado': una medida
    sintetica (0-100%) del impacto institucional de la estrategia, construida
    como el promedio ponderado de cinco componentes (ver
    `_PESOS_VALOR_PUBLICO`). No representa una cifra financiera.

    Retorna un diccionario con:
      valor_pct        : porcentaje final (float).
      componentes       : detalle de cada componente (dict).
      interpretacion     : texto ejecutivo segun el rango alcanzado.
      semaforo          : emoji de semaforo (🟢/🟡/🔴).
      tendencia_texto    : variacion frente al trimestre anterior, si aplica (texto).
      tendencia_valor    : la misma variacion, como numero (float) o None.
      tendencia_direccion: "up" | "down" | "flat" | "sin_datos".
    """
    total_maestro = kpi.get("total_recicladores", 0)
    componentes = _componentes_valor_publico(df, df_documentos, total_maestro)
    valor_pct = sum(componentes[k] * peso for k, peso in _PESOS_VALOR_PUBLICO.items())

    if valor_pct >= 85:
        interpretacion, semaforo = "Alto impacto institucional", "🟢"
    elif valor_pct >= 65:
        interpretacion, semaforo = "Impacto institucional moderado", "🟡"
    else:
        interpretacion, semaforo = "Impacto institucional en desarrollo", "🔴"

    # Tendencia: compara el valor del ultimo trimestre disponible frente al
    # trimestre anterior, reutilizando la misma metodologia de componentes.
    tendencia_texto = "Sin periodos suficientes para calcular tendencia."
    tendencia_valor = None
    tendencia_direccion = "sin_datos"
    if not df.empty and df["fecha"].notna().any():
        d = df.dropna(subset=["fecha"]).copy()
        d["periodo"] = d["fecha"].apply(lambda f: (f.year, _trimestre(f)))
        periodos = sorted(d["periodo"].unique())
        if len(periodos) >= 2:
            actual = d[d["periodo"] == periodos[-1]]
            anterior = d[d["periodo"] == periodos[-2]]
            comp_actual = _componentes_valor_publico(actual, df_documentos, total_maestro)
            comp_anterior = _componentes_valor_publico(anterior, df_documentos, total_maestro)
            vp_actual = sum(comp_actual[k] * p for k, p in _PESOS_VALOR_PUBLICO.items())
            vp_anterior = sum(comp_anterior[k] * p for k, p in _PESOS_VALOR_PUBLICO.items())
            delta = vp_actual - vp_anterior
            tendencia_valor = round(delta, 1)
            tendencia_direccion = "up" if delta > 0.5 else ("down" if delta < -0.5 else "flat")
            flecha = "▲" if tendencia_direccion == "up" else ("▼" if tendencia_direccion == "down" else "▬")
            tendencia_texto = f"{flecha} {delta:+.1f} pts frente al trimestre anterior"

    return {
        "valor_pct": round(valor_pct, 1),
        "componentes": componentes,
        "interpretacion": interpretacion,
        "semaforo": semaforo,
        "tendencia_texto": tendencia_texto,
        "tendencia_valor": tendencia_valor,
        "tendencia_direccion": tendencia_direccion,
    }


# --------------------------------------------------------------------------------
# Sintesis narrativa ejecutiva (usada en el Resumen Ejecutivo visual del
# Informe Ejecutivo en PDF). No calcula ni inventa informacion nueva: solo
# selecciona y resume los resultados que el resto del sistema ya produjo
# (KPIs, Valor Publico Generado, alertas y recomendaciones).
# --------------------------------------------------------------------------------
def sintetizar_hallazgos_ejecutivos(kpi: dict, valor_publico: dict, alertas: list,
                                     recomendaciones_matriz: list) -> dict:
    """
    Organiza los resultados ya calculados en cinco bloques narrativos breves
    (maximo 2 lineas cada uno): hallazgos, logros, oportunidades, riesgos y
    acciones prioritarias. Pensado para el Resumen Ejecutivo tipo
    storytelling del Informe Ejecutivo (una idea por bloque, sin parrafos).
    """
    hallazgos = [
        f"{kpi.get('total_acciones', 0):,} acciones afirmativas registradas, con "
        f"{kpi.get('cobertura_pct', 0):.0f}% de cobertura sobre la poblacion.",
        f"{kpi.get('total_organizaciones', 0):,} organizaciones activas agrupan a "
        f"{kpi.get('beneficiarios_unicos', 0):,} beneficiarios unicos.",
    ]

    logros = [
        f"{kpi.get('acciones_ejecutadas_anio', 0):,} acciones ejecutadas durante el ano en curso.",
        f"Valor Publico Generado de {valor_publico.get('valor_pct', 0):.0f}% "
        f"({valor_publico.get('interpretacion', '')}).",
    ]

    prioridad_alta = [d["texto"] for d in recomendaciones_matriz if d.get("prioridad") == "Alta"]
    prioridad_media = [d["texto"] for d in recomendaciones_matriz if d.get("prioridad") == "Media"]
    textos_generales = [d["texto"] for d in recomendaciones_matriz]

    oportunidades = (prioridad_media or textos_generales)[:2]
    acciones_prioritarias = (prioridad_alta or textos_generales)[:2]

    alertas_altas = [a for a in alertas if a.get("severidad") == "alta"]
    fuente_riesgos = alertas_altas or alertas
    if fuente_riesgos:
        riesgos = [f"{a['tipo']}: {a['mensaje']}" for a in fuente_riesgos[:2]]
    else:
        riesgos = ["No se identifican riesgos criticos para el periodo y filtros seleccionados."]

    return {
        "hallazgos": hallazgos[:2],
        "logros": logros[:2],
        "oportunidades": oportunidades[:2] or ["Sin oportunidades adicionales identificadas en el periodo."],
        "riesgos": riesgos[:2],
        "acciones_prioritarias": acciones_prioritarias[:2] or ["Mantener el ritmo de ejecucion y monitoreo actual."],
    }
