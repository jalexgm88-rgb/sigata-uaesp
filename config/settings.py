"""
config/settings.py
--------------------------------------------------------------------------------
Configuracion global de SIGATA - Sistema Integral para la Gestion y Trazabilidad
de las Acciones Afirmativas.

Centraliza constantes, paleta de colores institucional, listas de referencia
(localidades de Bogota con coordenadas), catalogo de campos canonicos para el
mapeo automatico de columnas y rutas de archivos usadas por toda la aplicacion.
--------------------------------------------------------------------------------
"""

from pathlib import Path

# --------------------------------------------------------------------------------
# Rutas base del proyecto
# --------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
DATABASE_PATH = DATA_DIR / "sigata.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------------
# Identidad del sistema
# --------------------------------------------------------------------------------
APP_NAME = "SIGATA"
APP_FULL_NAME = "Sistema Integral para la Gestion y Trazabilidad de las Acciones Afirmativas"
APP_ENTITY = "Subdireccion de Aprovechamiento - UAESP"
APP_PROJECT = (
      "Diseno de una propuesta de estrategia de innovacion para fortalecer la gestion "
      "de las acciones afirmativas dirigidas a la poblacion recicladora de oficio, "
      "en el marco del ODS 12: Produccion y Consumo Responsables."
)
APP_VERSION = "1.0.0 (MVP)"

# --------------------------------------------------------------------------------
# Paleta institucional (inspirada en Power BI / Fabric / Tableau)
# --------------------------------------------------------------------------------
COLOR_PRIMARY_GREEN = "#0E6E4F"
COLOR_PRIMARY_GREEN_DARK = "#094A35"
COLOR_PRIMARY_GREEN_LIGHT = "#E5F2ED"
COLOR_ACCENT_BLUE = "#2464B4"
COLOR_ACCENT_BLUE_LIGHT = "#EAF1FB"
COLOR_GRAY_LIGHT = "#F4F6F7"
COLOR_GRAY_MEDIUM = "#D9DEE2"
COLOR_GRAY_DARK = "#3B4148"
COLOR_WHITE = "#FFFFFF"
COLOR_WARNING = "#E0A100"
COLOR_DANGER = "#C0392B"
COLOR_SUCCESS = "#1E8E5A"

CHART_COLOR_SEQUENCE = [
      COLOR_PRIMARY_GREEN, COLOR_ACCENT_BLUE, "#5FAE8C", "#7FA8D9",
      COLOR_WARNING, "#8CC7AE", COLOR_GRAY_DARK, "#B7CBE8",
]

PLOTLY_TEMPLATE = "plotly_white"

# --------------------------------------------------------------------------------
# Localidades de Bogota relevantes para la poblacion recicladora
# --------------------------------------------------------------------------------
LOCALIDADES_BOGOTA = {
      "Usaquen":            (4.7030, -74.0300),
      "Chapinero":          (4.6488, -74.0648),
      "Santa Fe":           (4.6079, -74.0759),
      "San Cristobal":      (4.5709, -74.0817),
      "Usme":               (4.4826, -74.1264),
      "Tunjuelito":         (4.5723, -74.1499),
      "Bosa":               (4.6182, -74.1996),
      "Kennedy":            (4.6280, -74.1590),
      "Fontibon":           (4.6675, -74.1469),
      "Engativa":           (4.6900, -74.1180),
      "Suba":               (4.7411, -74.0930),
      "Barrios Unidos":     (4.6670, -74.0840),
      "Teusaquillo":        (4.6310, -74.0930),
      "Los Martires":       (4.6040, -74.0910),
      "Antonio Nariño":     (4.5880, -74.1000),
      "Puente Aranda":      (4.6160, -74.1160),
      "La Candelaria":      (4.5960, -74.0750),
      "Rafael Uribe Uribe": (4.5580, -74.1130),
      "Ciudad Bolivar":     (4.4940, -74.1430),
}

BOGOTA_CENTER = (4.6486, -74.1178)

# --------------------------------------------------------------------------------
# Catalogos de referencia para datos demo y formularios
# --------------------------------------------------------------------------------
TIPOS_ACCION_AFIRMATIVA = [
      "Formalizacion laboral", "Incentivo economico", "Capacitacion tecnica",
      "Dotacion de equipos", "Afiliacion a seguridad social", "Fortalecimiento asociativo",
      "Educacion ambiental", "Inclusion social", "Acompanamiento psicosocial",
      "Formalizacion organizacional",
]

PROGRAMAS = [
      "Programa de Aprovechamiento Integral",
      "Programa Basura Cero",
      "Programa de Inclusion del Reciclador de Oficio",
      "Programa de Fortalecimiento Organizacional ORO",
      "Programa de Cultura del Reciclaje",
]

PROYECTOS = [
      "Proyecto Rutas de Reciclaje Incluyentes",
      "Proyecto Estaciones de Clasificacion Comunitaria",
      "Proyecto Reciclador Digital",
      "Proyecto Escuela del Reciclador",
      "Proyecto Modernizacion de Bodegas",
]

ESTADOS_ACCION = ["Planeada", "En ejecucion", "Ejecutada", "Vencida", "Suspendida"]

GRUPOS_POBLACIONALES = [
      "Ninguno", "Victima del conflicto", "Discapacidad", "Adulto mayor",
      "Poblacion migrante", "Madre cabeza de hogar", "Jovenes en riesgo",
]

SEXOS = ["Femenino", "Masculino", "No binario", "No reporta"]

TIPOS_DOCUMENTO_SOPORTE = ["Acta", "Fotografia", "Soporte PDF", "Contrato", "Certificacion", "Otro"]

RESPONSABLES_DEMO = [
      "Subdireccion de Aprovechamiento", "Equipo Social UAESP", "Enlace ODS 12",
      "Coordinacion de Organizaciones", "Gestor Territorial", "Equipo de Formalizacion",
]

ODS_12_METAS = [
      "12.5 Reduccion de residuos", "12.8 Informacion y sensibilizacion",
      "12.2 Uso eficiente de recursos", "12.b Turismo sostenible / economia circular",
]

# --------------------------------------------------------------------------------
# Campos canonicos usados por el mapeo automatico de columnas
# --------------------------------------------------------------------------------
CAMPOS_CANONICOS = {
      "documento": "Documento de identidad",
      "nombre": "Nombre",
      "organizacion": "Organizacion",
      "localidad": "Localidad",
      "tipo_accion": "Tipo de accion afirmativa",
      "programa": "Programa",
      "proyecto": "Proyecto",
      "fecha": "Fecha",
      "responsable": "Responsable",
      "estado": "Estado",
      "presupuesto": "Presupuesto",
      "beneficio": "Beneficio",
      "sexo": "Sexo",
      "edad": "Edad",
      "grupo_poblacional": "Grupo poblacional",
}

DIAS_ALERTA_SEGUIMIENTO_ORGANIZACION = 180
PORC_ALERTA_PRESUPUESTO_AGOTADO = 0.95
