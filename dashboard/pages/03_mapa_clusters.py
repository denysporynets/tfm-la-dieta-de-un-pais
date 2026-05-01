"""
03_mapa_clusters.py — Mapa coroplético mundial coloreado por tipología dietaria
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    load_clusters, load_css, render_nav,
    MACROS, MACRO_LABELS,
    CLUSTER_NAMES, CLUSTER_COLORS,
    COUNTRY_ISO3,
    dominant_macro,
)

st.set_page_config(page_title="Mapa Clústeres · La Dieta de un País", page_icon="🗺️", layout="wide")
load_css()
render_nav("mapa")

st.title("🗺️ Mapa de Tipologías Dietarias")
st.caption("Distribución geográfica de las 3 tipologías detectadas por K-Means (K=3)")

df = load_clusters()

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controles")
    anno = st.slider("Año", min_value=2010, max_value=2022, value=2022, step=1)
    st.markdown("---")
    st.markdown("**Leyenda de tipologías:**")
    for cid, cname in CLUSTER_NAMES.items():
        color = CLUSTER_COLORS[cid]
        st.markdown(
            f"<div style='display:flex; align-items:center; gap:8px; margin:4px 0;'>"
            f"<div style='width:14px; height:14px; background:{color}; border-radius:3px;'></div>"
            f"<span style='font-size:0.85rem;'><b>C{cid}</b> — {cname}</span></div>",
            unsafe_allow_html=True,
        )

# ── DATOS ────────────────────────────────────────────────────────
sub = df[df["Year"] == anno].copy()
sub["iso3"]        = sub["Area"].map(COUNTRY_ISO3)
sub["macro_dom"]   = sub.apply(dominant_macro, axis=1)
sub["cluster_label"] = sub["cluster_id"].map(lambda c: f"C{c} — {CLUSTER_NAMES[c]}")
sub["co2_fmt"]     = sub["CO2eq_t_per_capita"].round(2)

# Ordenar categorías para colores discretos consistentes
cat_order = [f"C{cid} — {CLUSTER_NAMES[cid]}" for cid in sorted(CLUSTER_NAMES.keys())]
color_map  = {f"C{cid} — {CLUSTER_NAMES[cid]}": CLUSTER_COLORS[cid] for cid in CLUSTER_NAMES}

# ── MAPA ─────────────────────────────────────────────────────────
fig_map = px.choropleth(
    sub.dropna(subset=["iso3"]),
    locations="iso3",
    color="cluster_label",
    category_orders={"cluster_label": cat_order},
    color_discrete_map=color_map,
    hover_name="Area",
    hover_data={
        "iso3": False,
        "cluster_label": True,
        "co2_fmt": True,
        "macro_dom": True,
    },
    labels={
        "cluster_label": "Tipología",
        "co2_fmt": "CO₂ (t/cáp)",
        "macro_dom": "Macro dominante",
    },
    title=f"Tipología dietaria por país — {anno}",
)
fig_map.update_layout(
    height=520,
    geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
    legend=dict(orientation="h", yanchor="bottom", y=-0.12, title_text=""),
    margin=dict(l=0, r=0, t=40, b=0),
)
st.plotly_chart(fig_map, use_container_width=True)
st.caption(
    "Los 30 países de la muestra están coloreados según su tipología K-Means (K=3). "
    "Los países en gris claro no forman parte de la muestra."
)

# ── RESUMEN POR CLÚSTER ───────────────────────────────────────────
st.markdown("---")
st.subheader(f"Resumen de clústeres — {anno}")

cols = st.columns(3)
for i, (cid, cname) in enumerate(CLUSTER_NAMES.items()):
    color = CLUSTER_COLORS[cid]
    subc  = sub[sub["cluster_id"] == cid]
    paises_c = sorted(subc["Area"].tolist())
    co2_m  = subc["CO2eq_t_per_capita"].mean()
    kcal_m = subc["Total_DES_Kcal"].mean()

    centroide = df[df["cluster_id"] == cid][MACROS].mean()
    top2 = centroide.nlargest(2)
    top2_str = " · ".join(f"{MACRO_LABELS[m]} {v*100:.0f}%" for m, v in top2.items())

    with cols[i]:
        st.markdown(
            f"<div style='border-left:5px solid {color}; padding:12px 14px; "
            f"background:#fafafa; border-radius:0 8px 8px 0; height:100%;'>"
            f"<strong style='color:{color}; font-size:0.95rem;'>C{cid} — {cname}</strong><br>"
            f"<span style='font-size:0.8rem; color:#555;'>"
            f"{len(paises_c)} {'país' if len(paises_c)==1 else 'países'} · "
            f"CO₂ medio {co2_m:.2f} t/cáp · {kcal_m:,.0f} kcal/día</span><br>"
            f"<span style='font-size:0.78rem; color:#333;'><b>Top-2 macros:</b> {top2_str}</span><br>"
            f"<span style='font-size:0.75rem; color:#888; margin-top:4px; display:block;'>"
            f"{' · '.join(paises_c)}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

# ── TABLA CO₂ POR PAÍS ────────────────────────────────────────────
st.markdown("---")
with st.expander(f"📋 Tabla completa de países — {anno}"):
    tabla = sub[["Area", "cluster_label", "CO2eq_t_per_capita", "Total_DES_Kcal", "macro_dom"]].copy()
    tabla.columns = ["País", "Tipología", "CO₂ (t/cáp)", "DES (kcal/día)", "Macro dominante"]
    tabla = tabla.sort_values("CO₂ (t/cáp)", ascending=False).set_index("País")
    st.dataframe(tabla.style.format({"CO₂ (t/cáp)": "{:.2f}", "DES (kcal/día)": "{:,.0f}"}), use_container_width=True)
