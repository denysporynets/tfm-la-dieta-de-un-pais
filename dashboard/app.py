"""
app.py — Home page del dashboard
La Dieta de un País · Aguacate Team · Nuclio DS&AI 2026
"""

import streamlit as st
import pandas as pd
from utils import (
    load_clusters,
    CLUSTER_NAMES,
    CLUSTER_COLORS,
    MACROS,
    MACRO_LABELS,
    dominant_macro,
)

st.set_page_config(
    page_title="La Dieta de un País",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── HEADER ───────────────────────────────────────────────────────
st.markdown(
    """
    <div style="border-bottom: 3px solid #1a1a2e; padding-bottom: 16px; margin-bottom: 24px;">
      <span style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.12em; color:#888;">
        Nuclio Digital School · Máster en Data Science &amp; AI · Madrid 2026
      </span>
      <h1 style="font-size:2.2rem; font-weight:800; color:#1a1a2e; margin:4px 0;">
        🥑 La Dieta de un País
      </h1>
      <p style="color:#555; font-size:0.95rem; margin:0;">
        Tipologías dietarias globales, huella de carbono y simulación de escenarios · 30 países · 2010–2030
      </p>
      <p style="color:#888; font-size:0.8rem; margin-top:6px;">
        Rafael Montero · Marina Aguinacio · Ignacio Garrido · Denys Porynets · Tutor: Pedro Costa del Amo
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPIs ─────────────────────────────────────────────────────────
df = load_clusters()
co2_medio = df[df["Year"] == 2022]["CO2eq_t_per_capita"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🌍 Países", "30", help="30 países seleccionados por máxima varianza geográfica, PIB y climática")
k2.metric("🍽️ Tipologías", "3", help="K-Means K=3 · Silhouette=0.40 · Estabilidad temporal 98.7%")
k3.metric("🤖 R² Motor B", "0.864", help="LightGBM CO₂ predictor · 5-fold CV · vs baseline LinReg 0.29")
k4.metric("📅 Serie temporal", "13 años", help="FAOSTAT Food Balance Sheets 2010–2022")
k5.metric("🌡️ CO₂ medio 2022", f"{co2_medio:.2f} t/cáp", help="CO₂eq t/cápita media de los 30 países en 2022")

st.markdown("---")

# ── DESCRIPCIÓN DEL PROYECTO ─────────────────────────────────────
col_desc, col_motores = st.columns([1.4, 1])

with col_desc:
    st.subheader("¿Qué es este proyecto?")
    st.markdown(
        """
        Triangulamos **nutrición**, **coste** y **clima** para descubrir las tipologías dietarias
        no evidentes de 30 países y cuantificar su impacto en CO₂.

        Los datos provienen de FAOSTAT (Food Balance Sheets, Emisiones AFOLU, Food CPI)
        y cubren el período 2010–2022. Las 87 categorías de alimentos se comprimieron en
        **7 Macro-Categorías** para el análisis.

        **Hallazgo clave:** el modelo reproduce la jerarquía de impacto de Poore & Nemecek (2018)
        sin ningún conocimiento previo — el top-3 SHAP coincide con el top-3 IPCC.
        """
    )

with col_motores:
    st.subheader("Los 3 motores analíticos")
    st.markdown(
        """
        | Motor | Técnica | Output |
        |---|---|---|
        | **A — Clustering** | K-Means K=3 | 3 tipologías dietarias |
        | **B — LightGBM+SHAP** | Gradient Boosting | R²=0.864 · 9 drivers CO₂ |
        | **C — Forecast** | LightGBM Global | Proyección 2023–2030 |
        """
    )

st.markdown("---")

# ── TABLA DE CLÚSTERES ───────────────────────────────────────────
st.subheader("Las 3 tipologías dietarias descubiertas")

for cid, cname in CLUSTER_NAMES.items():
    color = CLUSTER_COLORS[cid]
    sub = df[(df["cluster_id"] == cid) & (df["Year"] == 2022)]
    paises = sorted(sub["Area"].unique())
    co2_c  = sub["CO2eq_t_per_capita"].mean()
    n_paises = len(paises)

    # macrocategoría dominante del centroide
    centroide = df[df["cluster_id"] == cid][MACROS].mean()
    top3 = centroide.nlargest(3)
    top3_str = " · ".join(f"{MACRO_LABELS[m]} {v*100:.0f}%" for m, v in top3.items())

    with st.container():
        st.markdown(
            f"""
            <div style="border-left: 5px solid {color}; padding: 12px 16px; margin-bottom: 12px;
                        background:#fafafa; border-radius: 0 8px 8px 0;">
              <strong style="color:{color}; font-size:1rem;">C{cid} — {cname}</strong>
              &nbsp;&nbsp;
              <span style="font-size:0.8rem; color:#555;">
                {n_paises} {'país' if n_paises == 1 else 'países'} · CO₂ medio {co2_c:.2f} t/cáp
              </span>
              <br/>
              <span style="font-size:0.82rem; color:#333;">
                <strong>Centroide top-3:</strong> {top3_str}
              </span>
              <br/>
              <span style="font-size:0.78rem; color:#666;">
                {' · '.join(paises)}
              </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── NAVEGACIÓN ───────────────────────────────────────────────────
st.subheader("Módulos del dashboard")
st.markdown(
    """
    Usa el menú lateral para navegar entre las 5 vistas:

    | Módulo | Descripción |
    |---|---|
    | **01 · Vista País** | Series temporales de composición dietaria y CO₂ por país (2010–2022) |
    | **02 · Comparador** | Radar chart comparativo entre 2–4 países |
    | **03 · Mapa Clústeres** | Mapa mundial coroplético coloreado por tipología dietaria |
    | **04 · Simulador What-If** | Ajusta la dieta con sliders → predicción CO₂ en tiempo real |
    | **05 · Motor C Forecast** | Proyección dietaria 2023–2030 con LightGBM Global |
    """
)

# ── FOOTER ───────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; font-size:0.75rem; color:#aaa; margin-top:40px;
                padding-top:16px; border-top:1px solid #eee;">
      Aguacate Team · TFM "La Dieta de un País" · Nuclio Digital School · Madrid 2026<br>
      Datos: FAOSTAT (FAO, 2023) · Modelo: LightGBM (Ke et al., 2017) · SHAP (Lundberg & Lee, 2017)
    </div>
    """,
    unsafe_allow_html=True,
)
