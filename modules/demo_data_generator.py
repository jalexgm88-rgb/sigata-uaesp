"""
modules/demo_data_generator.py
--------------------------------------------------------------------------------
Genera un conjunto de datos ficticios pero realistas (sin Lorem Ipsum) para que
SIGATA sea completamente explorable la primera vez que se ejecuta, antes de
que el usuario cargue su propio archivo Excel.

Los datos simulan tres anos de operacion (permitiendo ver evolucion historica,
mensual y anual) de la Subdireccion de Aprovechamiento de la UAESP con
organizaciones de recicladores de oficio, recicladores individuales y acciones
afirmativas asociadas a programas y proyectos reales del sector.
--------------------------------------------------------------------------------
"""

import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

from config.settings import (
    ESTADOS_ACCION, GRUPOS_POBLACIONALES, LOCALIDADES_BOGOTA, PROGRAMAS,
    PROYECTOS, RESPONSABLES_DEMO, SEXOS, TIPOS_ACCION_AFIRMATIVA, ODS_12_METAS,
)
from modules.database import get_connection, insert_row, set_metadata

fake = Faker("es_CO")
random.seed(2026)
Faker.seed(2026)

# NOTA DE PRIVACIDAD: los nombres de organizacion listados a continuacion son
# enteramente ficticios (supuestos), construidos solo para efectos de la
# demostracion academica. Cualquier coincidencia con organizaciones reales de
# recicladores de oficio es involuntaria. No representan entidades existentes.
NOMBRES_ORGANIZACIONES = [
    "Asociacion Renacer Verde", "Cooperativa Horizonte Reciclador",
    "ARB Nueva Vida Sostenible", "Asociacion Manos Unidas por el Ambiente",
    "Cooperativa Raices del Reciclaje", "Organizacion Comunitaria Sendero Verde",
    "ARB Amanecer Sostenible", "Asociacion Progreso Circular",
    "Cooperativa Tierra Fertil", "ARB Vision Ecologica",
    "Asociacion Union Recicladora", "Cooperativa Nuevo Horizonte Ambiental",
    "Organizacion Semillas del Futuro", "ARB Esperanza Circular",
    "Asociacion Manos Verdes de Bogota",
]


def _random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, max(delta.days, 1)))


def _generar_organizaciones(n=15):
    localidades = list(LOCALIDADES_BOGOTA.keys())
    registros = []
    for i in range(n):
        nombre = NOMBRES_ORGANIZACIONES[i % len(NOMBRES_ORGANIZACIONES)]
        if i >= len(NOMBRES_ORGANIZACIONES):
            nombre = f"{nombre} {i}"
        loc = random.choice(localidades)
        fecha_const = _random_date(datetime(2015, 1, 1), datetime(2022, 12, 31))
        row = {
            "nombre": nombre,
            "nit": f"90{random.randint(1000000, 9999999)}-{random.randint(0,9)}",
            "localidad": loc,
            "fecha_constitucion": fecha_const.strftime("%Y-%m-%d"),
            "representante": fake.name(),
            "num_afiliados": random.randint(15, 180),
            "estado": random.choices(["Activa", "En seguimiento", "Inactiva"], weights=[0.75, 0.18, 0.07])[0],
            "telefono": fake.phone_number(),
            "observaciones": "Organizacion registrada en el censo de la Subdireccion de Aprovechamiento.",
        }
        registros.append(row)
        insert_row("organizaciones", row)
    return registros


def _generar_recicladores(organizaciones, n=220):
    localidades = list(LOCALIDADES_BOGOTA.keys())
    registros = []
    documentos_usados = set()
    for _ in range(n):
        doc = str(random.randint(1_200_000_000, 1_299_999_999))
        while doc in documentos_usados:
            doc = str(random.randint(1_200_000_000, 1_299_999_999))
        documentos_usados.add(doc)
        sexo = random.choices(SEXOS, weights=[0.52, 0.44, 0.02, 0.02])[0]
        nombre = fake.name_female() if sexo == "Femenino" else fake.name_male() if sexo == "Masculino" else fake.name()
        org = random.choice(organizaciones)
        row = {
            "documento": doc,
            "nombre": nombre,
            "sexo": sexo,
            "edad": random.randint(18, 72),
            "telefono": fake.phone_number(),
            "localidad": org["localidad"],
            "organizacion": org["nombre"],
            "fecha_ingreso": _random_date(datetime(2018, 1, 1), datetime(2026, 6, 30)).strftime("%Y-%m-%d"),
            "grupo_poblacional": random.choices(
                GRUPOS_POBLACIONALES, weights=[0.45, 0.14, 0.10, 0.14, 0.07, 0.08, 0.02]
            )[0],
            "foto_path": "",
            "observaciones": "Reciclador de oficio activo en proceso de formalizacion.",
        }
        registros.append(row)
        insert_row("recicladores", row)
    return registros


def _generar_catalogos_apoyo():
    for p in PROGRAMAS:
        insert_row("programas", {
            "nombre": p,
            "descripcion": f"Programa institucional orientado al fortalecimiento de la poblacion recicladora ({p}).",
            "meta_ods12": random.choice(ODS_12_METAS),
            "responsable": random.choice(RESPONSABLES_DEMO),
        })
    for pr in PROYECTOS:
        insert_row("proyectos", {
            "nombre": pr,
            "programa": random.choice(PROGRAMAS),
            "descripcion": f"Proyecto operativo asociado a la estrategia de aprovechamiento ({pr}).",
            "presupuesto_asignado": random.randint(80_000_000, 450_000_000),
            "fecha_inicio": "2024-01-15",
            "fecha_fin": "2026-12-31",
        })
    for r in RESPONSABLES_DEMO:
        insert_row("responsables", {
            "nombre": fake.name(),
            "cargo": r,
            "area": "Subdireccion de Aprovechamiento",
            "correo": fake.email(),
            "telefono": fake.phone_number(),
        })
    incentivos = [
        ("Incentivo economico mensual", "Monetario", 150000),
        ("Bono de dotacion", "Especie", 220000),
        ("Auxilio de transporte", "Monetario", 90000),
        ("Kit de bioseguridad", "Especie", 60000),
        ("Capacitacion certificada SENA", "Formacion", 0),
    ]
    for nombre, tipo, valor in incentivos:
        insert_row("incentivos", {
            "nombre": nombre, "tipo": tipo, "valor": valor,
            "descripcion": f"Incentivo entregado en el marco de las acciones afirmativas ({nombre}).",
        })
    lineas = [
        "Formalizacion e inclusion socioeconomica",
        "Fortalecimiento organizacional y asociativo",
        "Educacion ambiental y cultura ciudadana",
        "Bienestar social y acompanamiento psicosocial",
        "Infraestructura y dotacion para el aprovechamiento",
    ]
    for linea in lineas:
        insert_row("lineas_accion", {
            "nombre": linea,
            "descripcion": f"Linea de accion estrategica: {linea}.",
        })


def _generar_acciones_afirmativas(organizaciones, recicladores, n=950):
    hoy = datetime(2026, 8, 2)
    inicio = datetime(2023, 1, 1)
    registros = []
    for _ in range(n):
        reciclador = random.choice(recicladores)
        fecha = _random_date(inicio, hoy + timedelta(days=60))
        presupuesto = random.randint(300_000, 6_000_000)
        if fecha > hoy:
            estado = random.choices(["Planeada", "En ejecucion"], weights=[0.6, 0.4])[0]
        elif (hoy - fecha).days > 400:
            estado = random.choices(ESTADOS_ACCION, weights=[0.02, 0.05, 0.75, 0.13, 0.05])[0]
        else:
            estado = random.choices(ESTADOS_ACCION, weights=[0.05, 0.20, 0.55, 0.15, 0.05])[0]
        ejecutado = 0
        if estado == "Ejecutada":
            ejecutado = presupuesto
        elif estado == "En ejecucion":
            ejecutado = round(presupuesto * random.uniform(0.3, 0.85))
        elif estado == "Vencida":
            ejecutado = round(presupuesto * random.uniform(0.0, 0.4))
        row = {
            "documento": reciclador["documento"],
            "nombre": reciclador["nombre"],
            "organizacion": reciclador["organizacion"],
            "localidad": reciclador["localidad"],
            "tipo_accion": random.choice(TIPOS_ACCION_AFIRMATIVA),
            "programa": random.choice(PROGRAMAS),
            "proyecto": random.choice(PROYECTOS),
            "fecha": fecha.strftime("%Y-%m-%d"),
            "responsable": random.choice(RESPONSABLES_DEMO),
            "estado": estado,
            "presupuesto": presupuesto,
            "presupuesto_ejecutado": ejecutado,
            "beneficio": random.choice([
                "Incentivo economico", "Dotacion de equipos", "Capacitacion",
                "Afiliacion EPS/ARL", "Auxilio de transporte", "Kit de bioseguridad",
            ]),
            "sexo": reciclador["sexo"],
            "edad": reciclador["edad"],
            "grupo_poblacional": reciclador["grupo_poblacional"],
            "observaciones": "",
        }
        registros.append(row)

    df = pd.DataFrame(registros)
    df["fuente"] = "datos_demo"
    df["fecha_registro"] = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        df.to_sql("acciones_afirmativas", conn, if_exists="append", index=False)


def generar_datos_demo():
    """Punto de entrada: genera todo el conjunto de datos demo si aun no existe."""
    organizaciones = _generar_organizaciones()
    recicladores = _generar_recicladores(organizaciones)
    _generar_catalogos_apoyo()
    _generar_acciones_afirmativas(organizaciones, recicladores)
    set_metadata("datos_demo_generados", "true")
    set_metadata("fecha_generacion_demo", datetime.now().isoformat(timespec="seconds"))
