"""
01_vista_pais.py — Series temporales de composición dietaria y CO₂ por país
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    load_clusters,
    MACROS, MACRO_LABELS, MACRO_COLORS,
    CLUSTER_NAMES, CLUSTER_COLORS,
    dominant_macro,
)

st.set_page_config(page_title="Vista País · La Dieta de un País", page_icon="🌍", layout="wide")

st.title("🌍 Vista País")
st.caption("Evolución histórica de la composición dietaria y huella de CO₂ (2010–2022)")

df = load_clusters()
paises = sorted(df["Area"].unique())

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controles")
    pais = st.selectbox("País", paises, index=paises.index("Spain") if "Spain" in paises else 0)
    sub  = df[df["Area"] == pais].sort_values("Year")
    cluster_id  = int(sub["cluster_id"].iloc[-1])
    cluster_nom = CLUSTER_NAMES[cluster_id]
    color_c     = CLUSTER_COLORS[cluster_id]

    st.markdown(
        f"<div style='background:{color_c}22; border-left:4px solid {color_c}; "
        f"padding:8px 12px; border-radius:0 6px 6px 0; margin-top:8px;'>"
        f"<strong style='color:{color_c};'>C{cluster_id} — {cluster_nom}</strong></div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("Fuente: FAOSTAT Food Balance Sheets 2010–2022")

# ── KPIs ─────────────────────────────────────────────────────────
row_2022 = sub[sub["Year"] == 2022].iloc[0] if 2022 in sub["Year"].values else sub.iloc[-1]
co2_2022 = row_2022["CO2eq_t_per_capita"]
kcal_2022 = row_2022["Total_DES_Kcal"]
macro_dom = dominant_macro(row_2022)
cpi_2022  = row_2022["Food_CPI"]

k1, k2, k3, k4 = st.columns(4)
k1.metric("CO₂ per cápita (2022)", f"{co2_2022:.2f} t")
k2.metric("Macro dominante (2022)", macro_dom)
k3.metric("DES total (2022)", f"{kcal_2022:,.0f} kcal/día")
k4.metric("Food CPI (2022)", f"{cpi_2022:.2f}", help="Índice de precios de alimentos, base 2015=100")

# ── TABS ─────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🥗 Composición dietaria", "🌡️ Evolución CO₂"])

with tab1:
    fig = go.Figure()

    for macro in MACROS:
        label = MACRO_LABELS[macro]
        color = MACRO_COLORS[macro]
        fig.add_trace(go.Scatter(
            x=sub["Year"],
            y=sub[macro],
            name=label,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=6),
            hovertemplate=f"<b>{label}</b><br>Año: %{{x}}<br>Proporción: %{{y:.1%}}<extra></extra>",
        ))

    fig.update_layout(
        title=f"{pais} — Composición calórica por macrocategoría",
        xaxis_title="Año",
        yaxis_title="Proporción calórica",
        yaxis=dict(tickformat=".0%"),
        hovermode="x unified",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.35),
        margin=dict(b=120),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Cada línea representa la proporción calórica de una macrocategoría sobre el total "
        "de energía disponible (DES). La suma de las 7 líneas es 1.0 en cada año."
    )

with tab2:
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    fig2.add_trace(
        go.Scatter(
            x=sub["Year"],
            y=sub["CO2eq_t_per_capita"],
            name="CO₂ real (t/cápita)",
            mode="lines+markers",
            line=dict(color="#3498db", width=2.5),
            marker=dict(size=7),
            hovertemplate="CO₂: %{y:.2f} t/cáp<extra></extra>",
        ),
        secondary_y=False,
    )

    fig2.add_trace(
        go.Bar(
            x=sub["Year"],
            y=sub["Food_CPI"],
            name="Food CPI",
            marker_color="rgba(240,165,0,0.3)",
            hovertemplate="Food CPI: %{y:.2f}<extra></extra>",
        ),
        secondary_y=True,
    )

    fig2.update_layout(
        title=f"{pais} — CO₂eq per cápita y Food CPI",
        hovermode="x unified",
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25),
    )
    fig2.update_yaxes(title_text="t CO₂eq / cápita", secondary_y=False)
    fig2.update_yaxes(title_text="Food CPI (2015=100)", secondary_y=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(
        "El CO₂eq incluye emisiones del sistema agroalimentario (AFOLU) per cápita. "
        "El Food CPI es el índice de precios al consumidor de alimentos (base 2015=100)."
    )

# ── TABLA RESUMEN ─────────────────────────────────────────────────
with st.expander("📋 Datos históricos completos"):
    cols_show = ["Year"] + MACROS + ["Total_DES_Kcal", "CO2eq_t_per_capita", "Food_CPI"]
    fmt = {m: "{:.1%}" for m in MACROS}
    fmt["Total_DES_Kcal"] = "{:,.0f}"
    fmt["CO2eq_t_per_capita"] = "{:.3f}"
    fmt["Food_CPI"] = "{:.2f}"
    st.dataframe(
        sub[cols_show].rename(columns=MACRO_LABELS).set_index("Year").style.format(fmt),
        use_container_width=True,
    )
