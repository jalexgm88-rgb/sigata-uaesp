"""
pages/3_Registro.py
--------------------------------------------------------------------------------
Pagina de registro directo desde formularios. Permite crear, consultar,
actualizar y eliminar informacion de las ocho entidades del sistema:
acciones afirmativas, recicladores, organizaciones de recicladores de oficio
(ORO), programas, proyectos, responsables, incentivos y lineas de accion.

Toda la logica de interfaz es generica (ver modules/forms.py); esta pagina
unicamente declara la configuracion de campos de cada entidad.
--------------------------------------------------------------------------------
"""

import streamlit as st

from config.settings import (
    ESTADOS_ACCION, GRUPOS_POBLACIONALES, LOCALIDADES_BOGOTA, PROGRAMAS,
    PROYECTOS, SEXOS, TIPOS_ACCION_AFIRMATIVA,
)
from modules import ui
from modules.database import fetch_df, init_db
from modules.forms import render_entity_crud

init_db()
st.set_page_config(page_title="SIGATA | Registro", page_icon="📝", layout="wide")
ui.inject_global_css()
ui.render_header("Registro de informacion")

localidades = list(LOCALIDADES_BOGOTA.keys())


def _organizaciones_disponibles():
    df = fetch_df("organizaciones")
    return df["nombre"].tolist() if not df.empty else ["Sin organizaciones registradas"]


entidad = st.selectbox(
    "Seleccione la entidad a gestionar",
    [
        "Acciones afirmativas", "Recicladores", "Organizaciones (ORO)", "Programas",
        "Proyectos", "Responsables", "Incentivos", "Lineas de accion",
    ],
)

if entidad == "Acciones afirmativas":
    campos = [
        {"key": "documento", "label": "Documento del reciclador", "tipo": "texto"},
        {"key": "nombre", "label": "Nombre del reciclador", "tipo": "texto"},
        {"key": "organizacion", "label": "Organizacion", "tipo": "select", "opciones": _organizaciones_disponibles()},
        {"key": "localidad", "label": "Localidad", "tipo": "select", "opciones": localidades},
        {"key": "tipo_accion", "label": "Tipo de accion afirmativa", "tipo": "select", "opciones": TIPOS_ACCION_AFIRMATIVA},
        {"key": "programa", "label": "Programa", "tipo": "select", "opciones": PROGRAMAS},
        {"key": "proyecto", "label": "Proyecto", "tipo": "select", "opciones": PROYECTOS},
        {"key": "fecha", "label": "Fecha", "tipo": "fecha"},
        {"key": "responsable", "label": "Responsable", "tipo": "texto"},
        {"key": "estado", "label": "Estado", "tipo": "select", "opciones": ESTADOS_ACCION},
        {"key": "presupuesto", "label": "Presupuesto asignado", "tipo": "numero", "paso": 100000.0},
        {"key": "presupuesto_ejecutado", "label": "Presupuesto ejecutado", "tipo": "numero", "paso": 100000.0},
        {"key": "beneficio", "label": "Beneficio entregado", "tipo": "texto"},
        {"key": "sexo", "label": "Sexo", "tipo": "select", "opciones": SEXOS},
        {"key": "edad", "label": "Edad", "tipo": "entero"},
        {"key": "grupo_poblacional", "label": "Grupo poblacional", "tipo": "select", "opciones": GRUPOS_POBLACIONALES},
        {"key": "observaciones", "label": "Observaciones", "tipo": "area"},
    ]
    render_entity_crud(
        "acciones_afirmativas", "Acciones afirmativas", campos,
        columnas_tabla=["id", "documento", "nombre", "organizacion", "localidad",
                         "tipo_accion", "fecha", "estado", "presupuesto"],
    )

elif entidad == "Recicladores":
    campos = [
        {"key": "documento", "label": "Documento de identidad", "tipo": "texto"},
        {"key": "nombre", "label": "Nombre completo", "tipo": "texto"},
        {"key": "sexo", "label": "Sexo", "tipo": "select", "opciones": SEXOS},
        {"key": "edad", "label": "Edad", "tipo": "entero"},
        {"key": "telefono", "label": "Telefono", "tipo": "texto"},
        {"key": "localidad", "label": "Localidad", "tipo": "select", "opciones": localidades},
        {"key": "organizacion", "label": "Organizacion", "tipo": "select", "opciones": _organizaciones_disponibles()},
        {"key": "fecha_ingreso", "label": "Fecha de ingreso", "tipo": "fecha"},
        {"key": "grupo_poblacional", "label": "Grupo poblacional", "tipo": "select", "opciones": GRUPOS_POBLACIONALES},
        {"key": "observaciones", "label": "Observaciones", "tipo": "area"},
    ]
    render_entity_crud(
        "recicladores", "Recicladores de oficio", campos,
        columnas_tabla=["id", "documento", "nombre", "sexo", "edad", "localidad", "organizacion"],
    )

elif entidad == "Organizaciones (ORO)":
    campos = [
        {"key": "nombre", "label": "Nombre de la organizacion", "tipo": "texto"},
        {"key": "nit", "label": "NIT", "tipo": "texto"},
        {"key": "localidad", "label": "Localidad", "tipo": "select", "opciones": localidades},
        {"key": "fecha_constitucion", "label": "Fecha de constitucion", "tipo": "fecha"},
        {"key": "representante", "label": "Representante legal", "tipo": "texto"},
        {"key": "num_afiliados", "label": "Numero de afiliados", "tipo": "entero"},
        {"key": "estado", "label": "Estado", "tipo": "select", "opciones": ["Activa", "En seguimiento", "Inactiva"]},
        {"key": "telefono", "label": "Telefono", "tipo": "texto"},
        {"key": "observaciones", "label": "Observaciones", "tipo": "area"},
    ]
    render_entity_crud(
        "organizaciones", "Organizaciones de Recicladores de Oficio", campos,
        columnas_tabla=["id", "nombre", "localidad", "num_afiliados", "estado"],
    )

elif entidad == "Programas":
    campos = [
        {"key": "nombre", "label": "Nombre del programa", "tipo": "texto"},
        {"key": "descripcion", "label": "Descripcion", "tipo": "area"},
        {"key": "meta_ods12", "label": "Meta ODS 12 asociada", "tipo": "texto"},
        {"key": "responsable", "label": "Responsable", "tipo": "texto"},
    ]
    render_entity_crud("programas", "Programas", campos)

elif entidad == "Proyectos":
    campos = [
        {"key": "nombre", "label": "Nombre del proyecto", "tipo": "texto"},
        {"key": "programa", "label": "Programa asociado", "tipo": "select", "opciones": PROGRAMAS},
        {"key": "descripcion", "label": "Descripcion", "tipo": "area"},
        {"key": "presupuesto_asignado", "label": "Presupuesto asignado", "tipo": "numero", "paso": 1000000.0},
        {"key": "fecha_inicio", "label": "Fecha de inicio", "tipo": "fecha"},
        {"key": "fecha_fin", "label": "Fecha de finalizacion", "tipo": "fecha"},
    ]
    render_entity_crud("proyectos", "Proyectos", campos)

elif entidad == "Responsables":
    campos = [
        {"key": "nombre", "label": "Nombre", "tipo": "texto"},
        {"key": "cargo", "label": "Cargo", "tipo": "texto"},
        {"key": "area", "label": "Area / dependencia", "tipo": "texto"},
        {"key": "correo", "label": "Correo electronico", "tipo": "texto"},
        {"key": "telefono", "label": "Telefono", "tipo": "texto"},
    ]
    render_entity_crud("responsables", "Responsables", campos)

elif entidad == "Incentivos":
    campos = [
        {"key": "nombre", "label": "Nombre del incentivo", "tipo": "texto"},
        {"key": "tipo", "label": "Tipo", "tipo": "select", "opciones": ["Monetario", "Especie", "Formacion"]},
        {"key": "valor", "label": "Valor estimado", "tipo": "numero", "paso": 10000.0},
        {"key": "descripcion", "label": "Descripcion", "tipo": "area"},
    ]
    render_entity_crud("incentivos", "Incentivos", campos)

elif entidad == "Lineas de accion":
    campos = [
        {"key": "nombre", "label": "Nombre de la linea de accion", "tipo": "texto"},
        {"key": "descripcion", "label": "Descripcion", "tipo": "area"},
    ]
    render_entity_crud("lineas_accion", "Lineas de accion", campos)


ui.render_footer()
