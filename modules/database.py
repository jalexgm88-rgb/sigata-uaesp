"""
modules/database.py
--------------------------------------------------------------------------------
Capa de acceso a datos de SIGATA. Usa SQLite como motor embebido (sin
dependencias externas de servidor) para persistir:

  - acciones_afirmativas : tabla de hechos (fuente de datos para dashboard,
                            filtros, KPIs, mapa y reportes).
  - recicladores, organizaciones, programas, proyectos, responsables,
    incentivos, lineas_accion : tablas maestras usadas por los formularios
    de registro y por la Ficha 360.
  - documentos            : gestion documental asociada a una accion afirmativa.
  - config_mapeo          : mapeo de columnas configurado por el usuario.

Todas las funciones son independientes y reutilizables desde cualquier
modulo/pagina de la aplicacion.
--------------------------------------------------------------------------------
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

import pandas as pd

from config.settings import DATABASE_PATH

# --------------------------------------------------------------------------------
# Conexion
# --------------------------------------------------------------------------------
@contextmanager
def get_connection():
    """Context manager que entrega una conexion SQLite con foreign keys activas."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------------------------
# Definicion de esquema
# --------------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS acciones_afirmativas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento TEXT,
    nombre TEXT,
    organizacion TEXT,
    localidad TEXT,
    tipo_accion TEXT,
    programa TEXT,
    proyecto TEXT,
    fecha TEXT,
    responsable TEXT,
    estado TEXT,
    presupuesto REAL DEFAULT 0,
    presupuesto_ejecutado REAL DEFAULT 0,
    beneficio TEXT,
    sexo TEXT,
    edad INTEGER,
    grupo_poblacional TEXT,
    observaciones TEXT,
    fuente TEXT DEFAULT 'manual',
    fecha_registro TEXT
);

CREATE TABLE IF NOT EXISTS organizaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    nit TEXT,
    localidad TEXT,
    fecha_constitucion TEXT,
    representante TEXT,
    num_afiliados INTEGER DEFAULT 0,
    estado TEXT DEFAULT 'Activa',
    telefono TEXT,
    observaciones TEXT,
    fecha_registro TEXT
);

CREATE TABLE IF NOT EXISTS recicladores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento TEXT UNIQUE,
    nombre TEXT NOT NULL,
    sexo TEXT,
    edad INTEGER,
    telefono TEXT,
    localidad TEXT,
    organizacion TEXT,
    fecha_ingreso TEXT,
    grupo_poblacional TEXT,
    foto_path TEXT,
    observaciones TEXT,
    fecha_registro TEXT
);

CREATE TABLE IF NOT EXISTS programas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    meta_ods12 TEXT,
    responsable TEXT,
    fecha_registro TEXT
);

CREATE TABLE IF NOT EXISTS proyectos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    programa TEXT,
    descripcion TEXT,
    presupuesto_asignado REAL DEFAULT 0,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    fecha_registro TEXT
);

CREATE TABLE IF NOT EXISTS responsables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    cargo TEXT,
    area TEXT,
    correo TEXT,
    telefono TEXT,
    fecha_registro TEXT
);

CREATE TABLE IF NOT EXISTS incentivos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT,
    valor REAL DEFAULT 0,
    descripcion TEXT,
    fecha_registro TEXT
);

CREATE TABLE IF NOT EXISTS lineas_accion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    fecha_registro TEXT
);

CREATE TABLE IF NOT EXISTS documentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accion_id INTEGER,
    documento_reciclador TEXT,
    nombre_archivo TEXT,
    tipo_documento TEXT,
    ruta_archivo TEXT,
    fecha_carga TEXT,
    observaciones TEXT,
    FOREIGN KEY (accion_id) REFERENCES acciones_afirmativas (id)
);

CREATE TABLE IF NOT EXISTS config_mapeo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campo_canonico TEXT,
    columna_origen TEXT,
    hoja_origen TEXT,
    archivo_origen TEXT,
    fecha_configuracion TEXT
);

CREATE TABLE IF NOT EXISTS metadata_sistema (
    clave TEXT PRIMARY KEY,
    valor TEXT
);
"""


def init_db():
    """Crea el esquema de base de datos si no existe. Idempotente."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)


# --------------------------------------------------------------------------------
# Utilidades genericas
# --------------------------------------------------------------------------------
def fetch_df(table: str, order_by: str = "id DESC") -> pd.DataFrame:
    """Retorna una tabla completa como DataFrame de pandas."""
    with get_connection() as conn:
        try:
            return pd.read_sql_query(f"SELECT * FROM {table} ORDER BY {order_by}", conn)
        except Exception:
            return pd.read_sql_query(f"SELECT * FROM {table}", conn)


def run_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Ejecuta una consulta SQL de solo lectura y retorna un DataFrame."""
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def insert_row(table: str, data: dict) -> int:
    """Inserta un registro (dict columna->valor) y retorna el id generado."""
    data = dict(data)
    data.setdefault("fecha_registro", datetime.now().isoformat(timespec="seconds"))
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    with get_connection() as conn:
        cur = conn.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        return cur.lastrowid


def update_row(table: str, row_id: int, data: dict):
    """Actualiza un registro existente por id."""
    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
    with get_connection() as conn:
        conn.execute(
            f"UPDATE {table} SET {set_clause} WHERE id = ?",
            tuple(data.values()) + (row_id,),
        )


def delete_row(table: str, row_id: int):
    """Elimina un registro por id."""
    with get_connection() as conn:
        conn.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))


def count_rows(table: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
        return cur.fetchone()[0]


# --------------------------------------------------------------------------------
# Acciones afirmativas (tabla de hechos)
# --------------------------------------------------------------------------------
def insert_acciones_bulk(df: pd.DataFrame, fuente: str = "carga_excel"):
    """Inserta en bloque un DataFrame ya mapeado a los campos canonicos."""
    df = df.copy()
    df["fuente"] = fuente
    df["fecha_registro"] = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        df.to_sql("acciones_afirmativas", conn, if_exists="append", index=False)


def get_acciones_df() -> pd.DataFrame:
    """Retorna la tabla de hechos completa, con la fecha convertida a datetime."""
    df = fetch_df("acciones_afirmativas", order_by="fecha DESC")
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        for col in ("presupuesto", "presupuesto_ejecutado", "edad"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


# --------------------------------------------------------------------------------
# Configuracion de mapeo de columnas
# --------------------------------------------------------------------------------
def save_column_mapping(mapping: dict, hoja_origen: str = "", archivo_origen: str = ""):
    """Guarda (reemplazando la anterior) la configuracion de mapeo de columnas."""
    with get_connection() as conn:
        conn.execute("DELETE FROM config_mapeo")
        ts = datetime.now().isoformat(timespec="seconds")
        for campo, columna in mapping.items():
            conn.execute(
                "INSERT INTO config_mapeo (campo_canonico, columna_origen, hoja_origen, "
                "archivo_origen, fecha_configuracion) VALUES (?, ?, ?, ?, ?)",
                (campo, columna, hoja_origen, archivo_origen, ts),
            )


def load_column_mapping() -> dict:
    """Carga el ultimo mapeo de columnas guardado. Retorna {} si no existe."""
    df = fetch_df("config_mapeo", order_by="id ASC")
    if df.empty:
        return {}
    return dict(zip(df["campo_canonico"], df["columna_origen"]))


# --------------------------------------------------------------------------------
# Metadata del sistema (banderas de estado, p. ej. datos demo cargados)
# --------------------------------------------------------------------------------
def set_metadata(clave: str, valor: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO metadata_sistema (clave, valor) VALUES (?, ?) "
            "ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor",
            (clave, valor),
        )


def get_metadata(clave: str, default=None):
    with get_connection() as conn:
        cur = conn.execute("SELECT valor FROM metadata_sistema WHERE clave = ?", (clave,))
        row = cur.fetchone()
        return row[0] if row else default


# --------------------------------------------------------------------------------
# Documentos
# --------------------------------------------------------------------------------
def insert_documento(data: dict) -> int:
    data = dict(data)
    data.setdefault("fecha_carga", datetime.now().isoformat(timespec="seconds"))
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    with get_connection() as conn:
        cur = conn.execute(
            f"INSERT INTO documentos ({columns}) VALUES ({placeholders})",
            tuple(data.values()),
        )
        return cur.lastrowid


def get_documentos_df() -> pd.DataFrame:
    return fetch_df("documentos", order_by="id DESC")
