"""
modules/mapa.py
--------------------------------------------------------------------------------
Construccion del mapa geografico de Bogota con Folium. Muestra, sobre las
localidades de la ciudad:

  - concentracion de organizaciones de recicladores de oficio,
  - concentracion de recicladores (beneficiarios unicos),
  - cobertura de acciones afirmativas,
  - un mapa de calor de concentracion de beneficios entregados.

Como el sistema no captura coordenadas GPS exactas por persona u
organizacion, se ubica cada punto alrededor del centroide de su localidad
mediante una dispersion (jitter) deterministica basada en el identificador del
registro, de forma que los mapas sean visualmente representativos y estables
entre recargas.
--------------------------------------------------------------------------------
"""

import hashlib
import random

import folium
import pandas as pd
from folium.plugins import HeatMap, MarkerCluster

from config.settings import BOGOTA_CENTER, COLOR_ACCENT_BLUE, COLOR_PRIMARY_GREEN, LOCALIDADES_BOGOTA


def _jitter(lat: float, lon: float, seed_text: str, radius: float = 0.012):
    """Genera un desplazamiento pequeno y deterministico alrededor de un centroide."""
    rnd = random.Random(int(hashlib.md5(seed_text.encode()).hexdigest(), 16) % (10 ** 8))
    d_lat = (rnd.random() - 0.5) * 2 * radius
    d_lon = (rnd.random() - 0.5) * 2 * radius
    return lat + d_lat, lon + d_lon


def construir_mapa(df: pd.DataFrame, df_organizaciones: pd.DataFrame = None) -> folium.Map:
    mapa = folium.Map(location=BOGOTA_CENTER, zoom_start=11, tiles="CartoDB positron")

    if df.empty:
        return mapa

    # --------------------------------------------------------------------
    # Capa 1: cobertura por localidad (circulos proporcionales)
    # --------------------------------------------------------------------
    capa_localidades = folium.FeatureGroup(name="Cobertura por localidad", show=True)
    resumen_loc = df.groupby("localidad").agg(
        beneficiarios=("documento", "nunique"),
        acciones=("id", "count"),
        presupuesto=("presupuesto", "sum"),
    ).reset_index()

    max_benef = resumen_loc["beneficiarios"].max() if not resumen_loc.empty else 1
    for _, fila in resumen_loc.iterrows():
        coords = LOCALIDADES_BOGOTA.get(fila["localidad"])
        if not coords:
            continue
        radio = 8 + (fila["beneficiarios"] / max(max_benef, 1)) * 32
        folium.Circle(
            location=coords,
            radius=radio * 60,
            color=COLOR_PRIMARY_GREEN,
            fill=True,
            fill_color=COLOR_PRIMARY_GREEN,
            fill_opacity=0.35,
            weight=1.5,
            popup=folium.Popup(
                f"<b>{fila['localidad']}</b><br>"
                f"Beneficiarios unicos: {int(fila['beneficiarios'])}<br>"
                f"Acciones afirmativas: {int(fila['acciones'])}<br>"
                f"Presupuesto asociado: ${fila['presupuesto']:,.0f}",
                max_width=250,
            ),
        ).add_to(capa_localidades)
    capa_localidades.add_to(mapa)

    # --------------------------------------------------------------------
    # Capa 2: organizaciones de recicladores de oficio
    # --------------------------------------------------------------------
    if df_organizaciones is not None and not df_organizaciones.empty:
        capa_orgs = MarkerCluster(name="Organizaciones (ORO)")
        for _, org in df_organizaciones.iterrows():
            coords = LOCALIDADES_BOGOTA.get(org.get("localidad"))
            if not coords:
                continue
            lat, lon = _jitter(coords[0], coords[1], f"org-{org['id']}")
            folium.Marker(
                location=(lat, lon),
                icon=folium.Icon(color="blue", icon="home", prefix="fa"),
                popup=folium.Popup(
                    f"<b>{org['nombre']}</b><br>Localidad: {org['localidad']}<br>"
                    f"Afiliados: {org.get('num_afiliados', 0)}<br>Estado: {org.get('estado','')}",
                    max_width=250,
                ),
            ).add_to(capa_orgs)
        capa_orgs.add_to(mapa)

    # --------------------------------------------------------------------
    # Capa 3: recicladores (beneficiarios unicos dispersos por localidad)
    # --------------------------------------------------------------------
    capa_recicladores = MarkerCluster(name="Recicladores (beneficiarios)")
    beneficiarios_unicos = df.drop_duplicates("documento")
    for _, ben in beneficiarios_unicos.iterrows():
        coords = LOCALIDADES_BOGOTA.get(ben["localidad"])
        if not coords:
            continue
        lat, lon = _jitter(coords[0], coords[1], f"ben-{ben['documento']}")
        folium.CircleMarker(
            location=(lat, lon),
            radius=3.5,
            color=COLOR_ACCENT_BLUE,
            fill=True,
            fill_opacity=0.7,
            popup=f"{ben['nombre']} · {ben['organizacion']}",
        ).add_to(capa_recicladores)
    capa_recicladores.add_to(mapa)

    # --------------------------------------------------------------------
    # Capa 4: mapa de calor - concentracion de beneficios
    # --------------------------------------------------------------------
    puntos_calor = []
    for _, fila in df.iterrows():
        coords = LOCALIDADES_BOGOTA.get(fila["localidad"])
        if not coords:
            continue
        lat, lon = _jitter(coords[0], coords[1], f"heat-{fila['id']}")
        puntos_calor.append([lat, lon, 1])
    if puntos_calor:
        HeatMap(puntos_calor, name="Concentracion de beneficios", radius=18, blur=22, min_opacity=0.3).add_to(mapa)

    folium.LayerControl(collapsed=False).add_to(mapa)
    return mapa
