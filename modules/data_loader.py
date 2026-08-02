"""
modules/data_loader.py
--------------------------------------------------------------------------------
Encargado de la carga de archivos Excel externos. Detecta automaticamente:

  - las hojas disponibles en el libro,
  - los nombres de columnas de cada hoja,
  - el tipo de dato inferido de cada columna,
  - la cantidad de registros por hoja.

No asume ninguna estructura fija: el resultado de este modulo alimenta al
modulo de mapeo (column_mapper.py), que es quien traduce las columnas reales
del archivo del usuario hacia los campos canonicos de SIGATA.
--------------------------------------------------------------------------------
"""

import pandas as pd


def load_excel_file(uploaded_file) -> dict:
    """
    Lee todas las hojas de un archivo Excel cargado desde Streamlit.

    Retorna:
        dict {nombre_hoja: DataFrame}
    """
    excel = pd.ExcelFile(uploaded_file)
    hojas = {}
    for sheet_name in excel.sheet_names:
        df = excel.parse(sheet_name)
        # Limpieza basica: quitar columnas totalmente vacias y espacios en encabezados
        df = df.dropna(axis=1, how="all")
        df.columns = [str(c).strip() for c in df.columns]
        hojas[sheet_name] = df
    return hojas


def get_sheet_summary(hojas: dict) -> pd.DataFrame:
    """Retorna un resumen (hoja, columnas, registros) por cada hoja detectada."""
    filas = []
    for nombre, df in hojas.items():
        filas.append({
            "Hoja": nombre,
            "Columnas": df.shape[1],
            "Registros": df.shape[0],
        })
    return pd.DataFrame(filas)


def get_column_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un perfil de columnas de un DataFrame: nombre, tipo inferido,
    cantidad de valores no nulos y un valor de ejemplo.
    """
    filas = []
    for col in df.columns:
        serie = df[col]
        ejemplo = serie.dropna().iloc[0] if serie.dropna().shape[0] > 0 else ""
        filas.append({
            "Columna": col,
            "Tipo detectado": str(serie.dtype),
            "No nulos": int(serie.notna().sum()),
            "Nulos": int(serie.isna().sum()),
            "Ejemplo": str(ejemplo)[:60],
        })
    return pd.DataFrame(filas)


def sugerir_mapeo_automatico(columnas: list, campos_canonicos: dict) -> dict:
    """
    Intenta preasignar automaticamente columnas a campos canonicos comparando
    nombres normalizados (sin tildes, minusculas). El usuario siempre puede
    corregir la sugerencia en la interfaz de mapeo.
    """
    import unicodedata

    def normalizar(texto):
        texto = str(texto).strip().lower()
        texto = "".join(
            c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
        )
        return texto.replace(" ", "").replace("_", "")

    columnas_norm = {normalizar(c): c for c in columnas}
    sinonimos = {
        "documento": ["documento", "cedula", "cc", "identificacion", "numerodocumento", "documentoidentidad"],
        "nombre": ["nombre", "nombres", "nombrecompleto", "reciclador"],
        "organizacion": ["organizacion", "organizacionrecicladores", "arb", "cooperativa"],
        "localidad": ["localidad", "zona", "sector"],
        "tipo_accion": ["tipoaccion", "tipodeaccion", "tipoaccionafirmativa", "accion"],
        "programa": ["programa"],
        "proyecto": ["proyecto"],
        "fecha": ["fecha", "fechaejecucion", "fechaaccion", "fecharegistro"],
        "responsable": ["responsable", "encargado", "gestor"],
        "estado": ["estado", "estatus"],
        "presupuesto": ["presupuesto", "valor", "monto", "costo"],
        "beneficio": ["beneficio", "tipobeneficio", "incentivo"],
        "sexo": ["sexo", "genero"],
        "edad": ["edad"],
        "grupo_poblacional": ["grupopoblacional", "poblacion", "grupoetnico"],
    }
    mapeo = {}
    for campo in campos_canonicos:
        candidatos = sinonimos.get(campo, [campo])
        encontrado = ""
        for cand in candidatos:
            if cand in columnas_norm:
                encontrado = columnas_norm[cand]
                break
        mapeo[campo] = encontrado
    return mapeo
