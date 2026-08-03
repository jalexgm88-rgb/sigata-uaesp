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
from pathlib import Path

import streamlit as st

from config.settings import (
    APP_ENTITY, APP_FULL_NAME, APP_NAME, APP_VERSION, COLOR_ACCENT_BLUE,
    COLOR_GRAY_DARK, COLOR_GRAY_LIGHT, COLOR_PRIMARY_GREEN, COLOR_PRIMARY_GREEN_DARK,
    COLOR_PRIMARY_GREEN_LIGHT,
)

_LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo_uaesp.png"


@st.cache_data(show_spinner=False)
def _logo_base64() -> str:
    """Lee el logo institucional de UAESP y lo retorna codificado en base64.
    Si el archivo no existe, retorna cadena vacia (el encabezado se muestra
    igual, simplemente sin logo)."""
    try:
        return base64.b64encode(_LOGO_PATH.read_bytes()).decode("utf-8")
    except FileNotFoundError:
        return ""


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
            background: #FFFFFF;
            border: 1px solid #E7EAEC;
            border-radius: 12px;
            padding: 10px 20px;
            margin-bottom: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .sigata-logo-bar img {{
            height: 34px;
            width: auto;
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
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            height: 108px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .kpi-card.blue {{ border-left-color: {COLOR_ACCENT_BLUE}; }}
        .kpi-card.warning {{ border-left-color: #E0A100; }}
        .kpi-card.danger {{ border-left-color: #C0392B; }}
        .kpi-label {{
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
            margin-top: 22px;
            margin-bottom: 8px;
            border-bottom: 2px solid {COLOR_PRIMARY_GREEN_LIGHT};
            padding-bottom: 6px;
        }}
        div[data-testid="stMetricValue"] {{
            color: {COLOR_PRIMARY_GREEN_DARK};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(subtitulo: str = ""):
    logo_b64 = _logo_base64()
    if logo_b64:
        st.markdown(
            f"""
            <div class="sigata-logo-bar">
                <img src="data:image/png;base64,{logo_b64}" alt="UAESP" />
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


def render_kpi_card(label: str, value: str, sub: str = "", variant: str = ""):
    clase = f"kpi-card {variant}".strip()
    st.markdown(
        f"""
        <div class="{clase}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
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
