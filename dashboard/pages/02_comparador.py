"""
02_comparador.py — Radar chart comparador de países
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    load_clusters,
    MACROS, MACRO_LABELS, MACRO_COLORS,
    CLUSTER_NAMES, CLUSTER_COLORS,
)

st.set_page_config(page_title="Comparador · La Dieta de un País", page_icon="📊", layout="wide")

st.title("📊 Comparador de Países")
st.caption("Compara la composición dietaria y huella de CO₂ de hasta 4 países en un radar chart")

df = load_clusters()
paises = sorted(df["Area"].unique())

COMPARADOR_COLORS = ["#2563eb", "#c0392b", "#16a34a", "#d97706"]

# ── CONTROLES ────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controles")
    default_sel = [p for p in ["Spain", "India", "Nigeria"] if p in paises]
    seleccion = st.multiselect(
        "Países a comparar (2–4)",
        paises,
        default=default_sel,
        max_selections=4,
    )
    anno = st.slider("Año", min_value=2010, max_value=2022, value=2022, step=1)

if len(seleccion) < 2:
    st.warning("Selecciona al menos 2 países para comparar.")
    st.stop()

sub = df[df["Year"] == anno]

# ── RADAR CHART ──────────────────────────────────────────────────
etiquetas = [MACRO_LABELS[m] for m in MACROS] + [MACRO_LABELS[MACROS[0]]]  # cerrar polígono

fig_radar = go.Figure()
for i, pais in enumerate(seleccion):
    fila = sub[sub["Area"] == pais]
    if fila.empty:
        continue
    valores = [float(fila[m].values[0]) for m in MACROS]
    valores_cierre = valores + [valores[0]]

    fig_radar.add_trace(go.Scatterpolar(
        r=valores_cierre,
        theta=etiquetas,
        fill="toself",
        fillcolor=COMPARADOR_COLORS[i] + "22",
        line=dict(color=COMPARADOR_COLORS[i], width=2.5),
        name=pais,
        hovertemplate="%{theta}: %{r:.1%}<extra>" + pais + "</extra>",
    ))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, max(
                float(sub[sub["Area"] == p][m].values[0])
                for p in seleccion if not sub[sub["Area"] == p].empty
                for m in MACROS
            ) * 1.1],
            tickformat=".0%",
        )
    ),
    showlegend=True,
    height=520,
    title=f"Composición dietaria comparada — {anno}",
)

col_radar, col_tabla = st.columns([1.5, 1])

with col_radar:
    st.plotly_chart(fig_radar, use_container_width=True)

with col_tabla:
    st.markdown(f"#### Resumen comparativo — {anno}")
    rows = []
    for pais in seleccion:
        fila = sub[sub["Area"] == pais]
        if fila.empty:
            continue
        cid = int(fila["cluster_id"].values[0])
        rows.append({
            "País": pais,
            "Tipología": f"C{cid} — {CLUSTER_NAMES[cid]}",
            "CO₂ (t/cáp)": round(float(fila["CO2eq_t_per_capita"].values[0]), 2),
            "DES (kcal)": int(fila["Total_DES_Kcal"].values[0]),
            "Food CPI": round(float(fila["Food_CPI"].values[0]), 2),
        })

    df_tabla = pd.DataFrame(rows).set_index("País")
    st.dataframe(df_tabla, use_container_width=True)

    # Diferencia CO₂ relativa respecto al primero
    if len(rows) >= 2:
        st.markdown("---")
        co2_ref = rows[0]["CO₂ (t/cáp)"]
        st.markdown(f"**Referencia CO₂:** {rows[0]['País']} = {co2_ref:.2f} t/cáp")
        for r in rows[1:]:
            delta = r["CO₂ (t/cáp)"] - co2_ref
            signo = "+" if delta >= 0 else ""
            st.markdown(
                f"- **{r['País']}**: {r['CO₂ (t/cáp)']:.2f} t/cáp "
                f"({signo}{delta:.2f} t · {signo}{delta/co2_ref*100:.1f}%)"
            )

# ── GRÁFICO DE BARRAS AGRUPADAS ───────────────────────────────────
st.markdown("---")
st.subheader(f"Desglose por macrocategoría — {anno}")

fig_bar = go.Figure()
for i, pais in enumerate(seleccion):
    fila = sub[sub["Area"] == pais]
    if fila.empty:
        continue
    valores = [float(fila[m].values[0]) for m in MACROS]
    fig_bar.add_trace(go.Bar(
        name=pais,
        x=[MACRO_LABELS[m] for m in MACROS],
        y=valores,
        marker_color=COMPARADOR_COLORS[i],
        hovertemplate="%{x}: %{y:.1%}<extra>" + pais + "</extra>",
    ))

fig_bar.update_layout(
    barmode="group",
    yaxis=dict(tickformat=".0%", title="Proporción calórica"),
    height=380,
    legend=dict(orientation="h", yanchor="bottom", y=-0.25),
    margin=dict(b=80),
)
st.plotly_chart(fig_bar, use_container_width=True)
