"""
modules/ui.py
--------------------------------------------------------------------------------
Componentes visuales compartidos: estilos globales (CSS institucional inspirado
en Power BI / Fabric / Tableau), tarjetas KPI, encabezados de pagina y bloques
de analisis/recomendaciones. Se centralizan aqui para mantener una identidad
visual consistente en toda la aplicacion.
--------------------------------------------------------------------------------
"""

import base64
from datetime import datetime

import streamlit as st

from config.settings import (
    APP_ENTITY, APP_FULL_NAME, APP_NAME, APP_VERSION, COLOR_ACCENT_BLUE,
    COLOR_ACCENT_BLUE_LIGHT, COLOR_DANGER, COLOR_GRAY_DARK, COLOR_GRAY_LIGHT,
    COLOR_PRIMARY_GREEN, COLOR_PRIMARY_GREEN_DARK, COLOR_PRIMARY_GREEN_LIGHT,
    COLOR_SUCCESS, LOGO_PATH, MESES_ES, PROYECTO_INVERSION, USUARIO_CONECTADO,
)

_LOGO_PATH = LOGO_PATH


@st.cache_data(show_spinner=False)
def _logo_base64() -> str:
    """Lee el logo institucional de UAESP y lo retorna codificado en base64.
    Si el archivo no existe, retorna cadena vacia (el encabezado se muestra
    igual, simplemente sin logo)."""
    try:
        return base64.b64encode(_LOGO_PATH.read_bytes()).decode("utf-8")
    except FileNotFoundError:
        return ""


def fecha_larga_es(fecha: datetime = None) -> str:
    """Formatea una fecha en formato largo en espanol (ej. '06 de agosto de 2026')
    sin depender del locale del sistema operativo/servidor."""
    fecha = fecha or datetime.now()
    return f"{fecha.day:02d} de {MESES_ES[fecha.month - 1]} de {fecha.year}"


def inject_global_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #FFFFFF;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {COLOR_GRAY_LIGHT};
            border-right: 1px solid #E4E7E9;
        }}
        h1, h2, h3, h4 {{
            color: {COLOR_GRAY_DARK};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        p, span, div, label {{
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        .sigata-logo-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 14px;
            background: #FFFFFF;
            border: 1px solid #E7EAEC;
            border-radius: 12px;
            padding: 14px 24px;
            margin-bottom: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }}
        .sigata-logo-bar img {{
            height: 64px;
            width: auto;
        }}
        /* -------------------- Barra superior: usuario y ultima actualizacion -------------------- */
        .sigata-topbar-right {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .sigata-update-badge {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: {COLOR_GRAY_LIGHT};
            border: 1px solid #E4E7E9;
            border-radius: 10px;
            padding: 6px 14px;
        }}
        .sigata-update-badge .icono {{
            font-size: 16px;
        }}
        .sigata-update-badge .texto .label {{
            font-size: 10.5px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            color: #8A9096;
            font-weight: 600;
        }}
        .sigata-update-badge .texto .valor {{
            font-size: 12.5px;
            color: {COLOR_GRAY_DARK};
            font-weight: 600;
        }}
        .sigata-user-card {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: {COLOR_PRIMARY_GREEN_LIGHT};
            border: 1px solid #D3E9DF;
            border-radius: 10px;
            padding: 6px 14px 6px 8px;
        }}
        .sigata-user-avatar {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 34px;
            height: 34px;
            border-radius: 50%;
            background: linear-gradient(135deg, {COLOR_PRIMARY_GREEN} 0%, {COLOR_PRIMARY_GREEN_DARK} 100%);
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 700;
            flex-shrink: 0;
        }}
        .sigata-user-info .nombre {{
            font-size: 12.5px;
            font-weight: 700;
            color: {COLOR_GRAY_DARK};
            line-height: 1.3;
        }}
        .sigata-user-info .detalle {{
            font-size: 10.5px;
            color: #6B7278;
            line-height: 1.3;
        }}
        /* -------------------- Tarjeta Proyecto de Inversion -------------------- */
        .sigata-proyecto-card {{
            display: flex;
            align-items: center;
            gap: 16px;
            background: linear-gradient(90deg, {COLOR_ACCENT_BLUE_LIGHT} 0%, #FFFFFF 100%);
            border: 1px solid #D2E1F5;
            border-left: 5px solid {COLOR_ACCENT_BLUE};
            border-radius: 10px;
            padding: 14px 20px;
            margin-bottom: 18px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }}
        .sigata-proyecto-card .icono {{
            font-size: 30px;
        }}
        .sigata-proyecto-card .codigo {{
            font-size: 22px;
            font-weight: 800;
            color: {COLOR_ACCENT_BLUE};
            line-height: 1;
        }}
        .sigata-proyecto-card .etiqueta {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #6B7278;
            font-weight: 700;
            margin-bottom: 2px;
        }}
        .sigata-proyecto-card .nombre {{
            font-size: 13.5px;
            color: {COLOR_GRAY_DARK};
            margin-top: 2px;
        }}
        .sigata-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 18px 24px;
            background: linear-gradient(90deg, {COLOR_PRIMARY_GREEN_DARK} 0%, {COLOR_PRIMARY_GREEN} 100%);
            border-radius: 12px;
            color: white;
            margin-bottom: 18px;
        }}
        .sigata-header h1 {{
            color: white;
            margin: 0;
            font-size: 26px;
            font-weight: 700;
        }}
        .sigata-header p {{
            color: #DDEFE6;
            margin: 2px 0 0 0;
            font-size: 13px;
        }}
        .sigata-badge {{
            background: rgba(255,255,255,0.15);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            color: white;
            border: 1px solid rgba(255,255,255,0.35);
        }}
        .kpi-card {{
            background: #FFFFFF;
            border: 1px solid #E7EAEC;
            border-left: 5px solid {COLOR_PRIMARY_GREEN};
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            transition: box-shadow 0.15s ease;
            height: 108px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-bottom: 6px;
        }}
        .kpi-card.blue {{ border-left-color: {COLOR_ACCENT_BLUE}; }}
        .kpi-card.warning {{ border-left-color: #E0A100; }}
        .kpi-card.danger {{ border-left-color: #C0392B; }}
        .kpi-label {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 12.5px;
            color: #6B7278;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 4px;
        }}
        .kpi-value {{
            font-size: 26px;
            font-weight: 700;
            color: {COLOR_GRAY_DARK};
            line-height: 1.1;
        }}
        .kpi-sub {{
            font-size: 11.5px;
            color: #8A9096;
            margin-top: 2px;
        }}
        .kpi-tendencia {{
            font-size: 11px;
            font-weight: 700;
            margin-top: 2px;
        }}
        .kpi-tendencia.up {{ color: {COLOR_SUCCESS}; }}
        .kpi-tendencia.down {{ color: {COLOR_DANGER}; }}
        .kpi-tendencia.flat {{ color: #8A9096; }}
        /* -------------------- Tarjeta Valor Publico Generado -------------------- */
        .sigata-vp-card {{
            display: flex;
            align-items: center;
            gap: 26px;
            background: #FFFFFF;
            border: 1px solid #E7EAEC;
            border-radius: 12px;
            padding: 20px 26px;
            margin-top: 6px;
            margin-bottom: 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .sigata-vp-semaforo {{
            font-size: 40px;
            line-height: 1;
        }}
        .sigata-vp-valor {{
            font-size: 40px;
            font-weight: 800;
            color: {COLOR_GRAY_DARK};
            line-height: 1;
        }}
        .sigata-vp-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #6B7278;
            font-weight: 700;
        }}
        .sigata-vp-interpretacion {{
            font-size: 14.5px;
            font-weight: 700;
            color: {COLOR_PRIMARY_GREEN_DARK};
            margin-top: 2px;
        }}
        .sigata-vp-tendencia {{
            font-size: 12px;
            color: #6B7278;
            margin-top: 2px;
        }}
        .sigata-vp-nota {{
            font-size: 11px;
            color: #8A9096;
            margin-top: 8px;
            line-height: 1.5;
            border-top: 1px dashed #E4E7E9;
            padding-top: 8px;
        }}
        .analysis-box {{
            background: {COLOR_PRIMARY_GREEN_LIGHT};
            border: 1px solid #D3E9DF;
            border-radius: 10px;
            padding: 14px 18px;
            font-size: 14px;
            color: {COLOR_GRAY_DARK};
            margin-top: 6px;
            margin-bottom: 18px;
            line-height: 1.5;
        }}
        .analysis-box b {{ color: {COLOR_PRIMARY_GREEN_DARK}; }}
        .reco-box {{
            background: #EAF1FB;
            border: 1px solid #D2E1F5;
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 13.5px;
            color: {COLOR_GRAY_DARK};
            margin-bottom: 8px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: {COLOR_GRAY_DARK};
            margin-top: 28px;
            margin-bottom: 12px;
            border-bottom: 2px solid {COLOR_PRIMARY_GREEN_LIGHT};
            padding-bottom: 7px;
        }}
        div[data-testid="stMetricValue"] {{
            color: {COLOR_PRIMARY_GREEN_DARK};
        }}
        .sigata-footer {{
            margin-top: 36px;
            padding-top: 16px;
            border-top: 1px solid #E7EAEC;
            font-size: 12px;
            color: #8A9096;
            line-height: 1.6;
            text-align: center;
        }}
        .sigata-footer b {{ color: {COLOR_GRAY_DARK}; }}
        .sigata-disclaimer {{
            background: #FBF7E9;
            border: 1px solid #EFE2B0;
            border-radius: 10px;
            padding: 12px 18px;
            font-size: 11.5px;
            color: #6B5D2A;
            line-height: 1.6;
            text-align: center;
            margin-bottom: 14px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(subtitulo: str = ""):
    """
    Renderiza el encabezado institucional de SIGATA, presente en todas las
    paginas del sistema. Incluye tres bloques:
      1. Barra superior blanca con el logo institucional, la fecha de ultima
         actualizacion (calculada automaticamente en cada ejecucion) y la
         tarjeta del usuario conectado, en un estilo inspirado en las barras
         de encabezado de Microsoft Fabric / Power BI Service.
      2. Banner verde con el nombre e identidad del sistema.
    """
    logo_b64 = _logo_base64()
    usuario = USUARIO_CONECTADO

    topbar_derecha = f"""
        <div class="sigata-topbar-right">
            <div class="sigata-update-badge">
                <span class="icono">🕒</span>
                <div class="texto">
                    <div class="label">Ultima actualizacion</div>
                    <div class="valor">{fecha_larga_es()}</div>
                </div>
            </div>
            <div class="sigata-user-card">
                <div class="sigata-user-avatar">{usuario['iniciales']}</div>
                <div class="sigata-user-info">
                    <div class="nombre">{usuario['nombre']}</div>
                    <div class="detalle">{usuario['cargo']} · {usuario['area']}</div>
                </div>
            </div>
        </div>
    """

    logo_img = f'<img src="data:image/png;base64,{logo_b64}" alt="UAESP" />' if logo_b64 else "<div></div>"
    st.markdown(
        f"""
        <div class="sigata-logo-bar">
            {logo_img}
            {topbar_derecha}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="sigata-header">
            <div>
                <h1>♻ {APP_NAME}</h1>
                <p>{APP_FULL_NAME}</p>
                <p>{subtitulo if subtitulo else APP_ENTITY}</p>
            </div>
            <div class="sigata-badge">v{APP_VERSION}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_proyecto_inversion():
    """Tarjeta de contexto institucional: proyecto de inversion asociado a la
    estrategia de aprovechamiento. Se muestra en el Dashboard Ejecutivo."""
    p = PROYECTO_INVERSION
    st.markdown(
        f"""
        <div class="sigata-proyecto-card">
            <div class="icono">🏛️</div>
            <div>
                <div class="etiqueta">Proyecto de Inversion</div>
                <div class="codigo">{p['codigo']}</div>
                <div class="nombre">{p['nombre']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, sub: str = "", variant: str = "", icono: str = "", tendencia: str = ""):
    """
    Renderiza una tarjeta KPI estandar.

    Parametros opcionales (compatibles hacia atras, no rompen llamadas
    existentes que no los usan):
      icono     : emoji/simbolo institucional mostrado junto a la etiqueta.
      tendencia : texto de tendencia ya formateado, p. ej. "▲ 6.4% vs. periodo
                  anterior". Se colorea automaticamente segun el simbolo
                  (▲ verde, ▼ rojo, ▬ gris neutro).
    """
    clase = f"kpi-card {variant}".strip()
    etiqueta_html = f"{icono} {label}" if icono else label

    tendencia_html = ""
    if tendencia:
        if tendencia.startswith("▲"):
            clase_tend = "up"
        elif tendencia.startswith("▼"):
            clase_tend = "down"
        else:
            clase_tend = "flat"
        tendencia_html = f'<div class="kpi-tendencia {clase_tend}">{tendencia}</div>'

    st.markdown(
        f"""
        <div class="{clase}">
            <div class="kpi-label">{etiqueta_html}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
            {tendencia_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_valor_publico_card(vp: dict):
    """
    Renderiza la tarjeta ejecutiva del indicador sintetico 'Valor Publico
    Generado'. Recibe el diccionario retornado por
    `modules.analisis.calcular_valor_publico`.
    """
    st.markdown(
        f"""
        <div class="sigata-vp-card">
            <div class="sigata-vp-semaforo">{vp['semaforo']}</div>
            <div>
                <div class="sigata-vp-label">Valor Publico Generado</div>
                <div class="sigata-vp-valor">{vp['valor_pct']:.0f}%</div>
                <div class="sigata-vp-interpretacion">{vp['interpretacion']}</div>
                <div class="sigata-vp-tendencia">{vp['tendencia_texto']}</div>
                <div class="sigata-vp-nota">
                    Indicador sintetico construido a partir de cobertura de beneficiarios, trazabilidad
                    de las acciones, completitud de los registros, evidencia documental y oportunidad del
                    seguimiento. Se calcula automaticamente sobre los datos filtrados y apoya la evaluacion
                    del valor publico generado por la estrategia; no corresponde a una cifra financiera.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis(texto: str, titulo: str = "Analisis ejecutivo"):
    st.markdown(
        f"""<div class="analysis-box"><b>{titulo}:</b> {texto}</div>""",
        unsafe_allow_html=True,
    )


def render_recomendaciones(lista: list):
    st.markdown('<div class="section-title">Recomendaciones automaticas</div>', unsafe_allow_html=True)
    for r in lista:
        st.markdown(f'<div class="reco-box">💡 {r}</div>', unsafe_allow_html=True)


def section_title(texto: str):
    st.markdown(f'<div class="section-title">{texto}</div>', unsafe_allow_html=True)


def render_footer():
    """Aviso legal/academico y creditos del equipo que diseno y prototipo SIGATA."""
    st.markdown(
        """
        <div class="sigata-disclaimer">
            <b>Aviso:</b> El contenido de esta aplicacion corresponde exclusivamente a fines
            academicos y de investigacion. No tiene caracter comercial, ni implica tratamiento
            real de datos personales fuera del ambito educativo. Los datos, ejemplos y
            visualizaciones son simulados o anonimizados, conforme a los principios de la
            Ley 1581 de 2012 sobre proteccion de datos personales en Colombia. Cualquier uso
            distinto al academico debera contar con autorizacion expresa de sus autores.
        </div>
        <div class="sigata-footer">
            Diseñado y prototipado por el equipo: <b>Danyi Paola Villa Cadena</b> ·
            <b>Natalia Isabel Rivera Rueda</b> · <b>Nilson Gabriel Quiñonez Males</b> ·
            <b>José Alexander Gómez Mantilla</b><br>
            En el marco de la asignatura <b>Pensamiento Disruptivo</b> de la Maestría en
            Administración de Empresas, con la guía del docente <b>Alexis González Marcelo</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )
