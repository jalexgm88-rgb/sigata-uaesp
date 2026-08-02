"""
modules/documentos.py
--------------------------------------------------------------------------------
Gestion documental. Permite cargar PDFs, imagenes, fotografias, actas y otros
soportes, asociandolos siempre a una accion afirmativa especifica. Los
archivos se guardan fisicamente en `data/documents/<accion_id>/` y su
metadata se persiste en la tabla `documentos` de la base de datos.
--------------------------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path

from config.settings import DOCUMENTS_DIR
from modules.database import delete_row, get_documentos_df, insert_documento


def guardar_documento(accion_id: int, documento_reciclador: str, archivo, tipo_documento: str, observaciones: str = "") -> int:
    """Guarda en disco el archivo cargado y registra su metadata en la base de datos."""
    carpeta = DOCUMENTS_DIR / str(accion_id)
    carpeta.mkdir(parents=True, exist_ok=True)

    nombre_archivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.name}"
    ruta_destino = carpeta / nombre_archivo
    with open(ruta_destino, "wb") as f:
        f.write(archivo.getbuffer())

    return insert_documento({
        "accion_id": accion_id,
        "documento_reciclador": documento_reciclador,
        "nombre_archivo": archivo.name,
        "tipo_documento": tipo_documento,
        "ruta_archivo": str(ruta_destino),
        "observaciones": observaciones,
    })


def listar_documentos_por_accion(accion_id: int):
    df = get_documentos_df()
    if df.empty:
        return df
    return df[df["accion_id"] == accion_id]


def listar_documentos_por_reciclador(documento: str):
    df = get_documentos_df()
    if df.empty:
        return df
    return df[df["documento_reciclador"] == documento]


def eliminar_documento(doc_id: int, ruta_archivo: str = None):
    delete_row("documentos", doc_id)
    if ruta_archivo:
        try:
            Path(ruta_archivo).unlink(missing_ok=True)
        except Exception:
            pass
