"""
modules/alertas.py
--------------------------------------------------------------------------------
Motor de alertas inteligentes. Analiza la tabla de hechos (acciones
afirmativas), las organizaciones y los documentos asociados para detectar de
forma automatica situaciones que requieren atencion de gestion:

  - acciones afirmativas vencidas
  - beneficiarios duplicados
  - documentos faltantes
  - informacion incompleta
  - organizaciones sin seguimiento reciente
  - presupuestos agotados
  - acciones pendientes de ejecucion

Cada alerta se retorna como un diccionario homogeneo para ser renderizado por
cualquier pagina de la aplicacion.
--------------------------------------------------------------------------------
"""

from datetime import datetime, timedelta

import pandas as pd

from config.settings import DIAS_ALERTA_SEGUIMIENTO_ORGANIZACION, PORC_ALERTA_PRESUPUESTO_AGOTADO


def generar_alertas(df: pd.DataFrame, df_documentos: pd.DataFrame = None) -> list:
    """Retorna una lista de alertas: [{tipo, severidad, mensaje, cantidad}]."""
    alertas = []
    hoy = pd.Timestamp(datetime.now().date())

    if df.empty:
        return alertas

    # 1. Acciones vencidas
    vencidas = df[(df["estado"].isin(["Vencida"])) | ((df["fecha"] < hoy) & (df["estado"] == "Planeada"))]
    if len(vencidas) > 0:
        alertas.append({
            "tipo": "Acciones vencidas",
            "severidad": "alta",
            "mensaje": f"{len(vencidas)} acciones afirmativas se encuentran vencidas o no iniciaron a tiempo.",
            "cantidad": len(vencidas),
        })

    # 2. Beneficiarios duplicados (mismo documento con mas de un nombre distinto)
    doc_nombres = df.groupby("documento")["nombre"].nunique()
    duplicados = doc_nombres[doc_nombres > 1]
    if len(duplicados) > 0:
        alertas.append({
            "tipo": "Beneficiarios duplicados",
            "severidad": "media",
            "mensaje": f"{len(duplicados)} documentos de identidad presentan mas de un nombre asociado.",
            "cantidad": len(duplicados),
        })

    # 3. Documentos faltantes
    if df_documentos is not None:
        ids_con_doc = set(df_documentos["accion_id"].unique()) if not df_documentos.empty else set()
        acciones_ejecutadas = df[df["estado"] == "Ejecutada"]
        sin_soporte = acciones_ejecutadas[~acciones_ejecutadas["id"].isin(ids_con_doc)]
        if len(sin_soporte) > 0:
            alertas.append({
                "tipo": "Documentos faltantes",
                "severidad": "media",
                "mensaje": f"{len(sin_soporte)} acciones ejecutadas no cuentan con soportes documentales cargados.",
                "cantidad": len(sin_soporte),
            })

    # 4. Informacion incompleta
    campos_clave = ["organizacion", "localidad", "responsable"]
    incompletos = df[df[campos_clave].apply(lambda col: col == "").any(axis=1)]
    if len(incompletos) > 0:
        alertas.append({
            "tipo": "Informacion incompleta",
            "severidad": "baja",
            "mensaje": f"{len(incompletos)} registros presentan campos clave sin diligenciar.",
            "cantidad": len(incompletos),
        })

    # 5. Organizaciones sin seguimiento reciente
    ultima_por_org = df[df["organizacion"] != ""].groupby("organizacion")["fecha"].max()
    limite = hoy - timedelta(days=DIAS_ALERTA_SEGUIMIENTO_ORGANIZACION)
    sin_seguimiento = ultima_por_org[ultima_por_org < limite]
    if len(sin_seguimiento) > 0:
        alertas.append({
            "tipo": "Organizaciones sin seguimiento",
            "severidad": "media",
            "mensaje": f"{len(sin_seguimiento)} organizaciones no registran acciones en mas de "
                       f"{DIAS_ALERTA_SEGUIMIENTO_ORGANIZACION} dias.",
            "cantidad": len(sin_seguimiento),
        })

    # 6. Presupuestos agotados
    agotado = df[df["presupuesto"] > 0]
    agotado = agotado[
        (agotado["presupuesto_ejecutado"] / agotado["presupuesto"]) >= PORC_ALERTA_PRESUPUESTO_AGOTADO
    ]
    if len(agotado) > 0:
        alertas.append({
            "tipo": "Presupuestos agotados",
            "severidad": "alta",
            "mensaje": f"{len(agotado)} acciones han ejecutado mas del "
                       f"{int(PORC_ALERTA_PRESUPUESTO_AGOTADO*100)}% de su presupuesto asignado.",
            "cantidad": len(agotado),
        })

    # 7. Acciones pendientes
    pendientes = df[df["estado"].isin(["Planeada", "En ejecucion"])]
    if len(pendientes) > 0:
        alertas.append({
            "tipo": "Acciones pendientes",
            "severidad": "baja",
            "mensaje": f"{len(pendientes)} acciones afirmativas se encuentran planeadas o en ejecucion.",
            "cantidad": len(pendientes),
        })

    orden_severidad = {"alta": 0, "media": 1, "baja": 2}
    alertas.sort(key=lambda a: orden_severidad.get(a["severidad"], 3))
    return alertas
