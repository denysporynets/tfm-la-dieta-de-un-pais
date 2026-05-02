"""
04_simulador_whatif.py — Simulador What-If: ajusta la dieta → predicción CO₂ en tiempo real
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    load_clusters, load_css, render_nav,
    load_lgb_model,
    MACROS, MACRO_LABELS, MACRO_COLORS,
    CLUSTER_NAMES, CLUSTER_COLORS,
    predict_co2,
)

st.set_page_config(
    page_title="Simulador What-If · La Dieta de un País",
    page_icon="🎛️",
    layout="wide",
)
load_css()
render_nav("simulador", hide_sidebar=True)

st.title("🎛️ Simulador What-If")
st.caption(
    "Ajusta la composición dietaria con los sliders y obtén la predicción de CO₂ en tiempo real. "
    "Modelo: LightGBM (R²=0.864 · 5-fold CV)"
)

df = load_clusters()
paises = sorted(df["Area"].unique())

# ── SHAP narrativo (top-5 drivers, texto fijo basado en ranking global) ──
SHAP_NARRATIVA = [
    ("Cereales", "Principal discriminador entre tipologías. Alto % de cereales → alta varianza CO₂."),
    ("Azúcares", "Señal de dieta procesada/transición nutricional. A mayor % azúcares, mayor CO₂ asociado."),
    ("Carnes", "Coherente con IPCC: ganadería intensiva = alta huella. Efecto amplificado en C0."),
    ("Tubérculos", "Marcador clave de la tipología C1 (Nigeria). Tubérculos → baja huella por kcal."),
    ("Aceites y Grasas", "Señal de dietas de renta media-alta. Moderado impacto en CO₂."),
]

# ── LAYOUT ───────────────────────────────────────────────────────
col_ctrl, col_res = st.columns([1, 1.4])

with col_ctrl:
    st.subheader("Configura la dieta")

    pais_ref = st.selectbox(
        "Partir de un país (2022)",
        ["— personalizado —"] + paises,
        index=paises.index("Spain") + 1 if "Spain" in paises else 1,
    )

    # Valores iniciales
    if pais_ref != "— personalizado —":
        fila_ref = df[(df["Area"] == pais_ref) & (df["Year"] == 2022)]
        if fila_ref.empty:
            fila_ref = df[df["Area"] == pais_ref].sort_values("Year").iloc[[-1]]
        vals_init   = {m: float(fila_ref[m].values[0]) * 100 for m in MACROS}
        cpi_init    = float(fila_ref["Food_CPI"].values[0])   # unidades brutas (base 2015=100)
        cluster_init = int(fila_ref["cluster_id"].values[0])
        co2_ref_val  = float(fila_ref["CO2eq_t_per_capita"].values[0])
    else:
        vals_init = {m: 100 / 7 for m in MACROS}
        cpi_init  = 110.0
        cluster_init = 0
        co2_ref_val  = None

    st.markdown("**Proporciones calóricas (% de cada macrocategoría)**")
    sliders = {}
    for macro in MACROS:
        sliders[macro] = st.slider(
            MACRO_LABELS[macro],
            min_value=0,
            max_value=100,
            value=max(1, int(round(vals_init[macro]))),
            step=1,
            key=f"sl_{macro}",
        )

    total_raw = sum(sliders.values())
    if total_raw == 0:
        st.error("Al menos una macrocategoría debe ser > 0.")
        st.stop()

    pct_norm = {m: sliders[m] / total_raw for m in MACROS}
    st.info(f"Suma bruta de sliders: **{total_raw}** → normalizado automáticamente a 100%")

    st.markdown("---")
    cpi_slider = st.slider(
        "Food CPI (2015 = 100)",
        min_value=50,
        max_value=500,
        value=max(50, min(500, int(round(cpi_init)))),
        step=5,
        help="Índice de precios de alimentos (unidades brutas, base 2015=100). Rango real: ~45–1076.",
    )

    cluster_radio = st.radio(
        "Tipología dietaria del escenario",
        options=list(CLUSTER_NAMES.keys()),
        format_func=lambda c: f"C{c} — {CLUSTER_NAMES[c]}",
        index=cluster_init,
        horizontal=False,
    )

# ── PREDICCIÓN ───────────────────────────────────────────────────
pct_list  = [pct_norm[m] for m in MACROS]
co2_pred  = predict_co2(pct_list, cpi_slider, cluster_radio)
color_gauge = "#27ae60" if co2_pred < 2 else "#f0a500" if co2_pred < 4 else "#c0392b"

with col_res:
    st.subheader("Resultado de la simulación")

    # KPIs
    k1, k2 = st.columns(2)
    k1.metric(
        "CO₂ predicho",
        f"{co2_pred:.2f} t/cáp",
        delta=f"{co2_pred - co2_ref_val:+.2f} t vs {pais_ref}" if co2_ref_val else None,
        delta_color="inverse",
    )
    k2.metric(
        "Tipología del escenario",
        f"C{cluster_radio} — {CLUSTER_NAMES[cluster_radio]}",
    )

    # Gauge CO₂
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=co2_pred,
        number={"suffix": " t CO₂/cáp", "font": {"size": 28}},
        gauge={
            "axis": {"range": [0, 12], "ticksuffix": " t"},
            "bar": {"color": color_gauge},
            "steps": [
                {"range": [0, 2],   "color": "#d4edda"},
                {"range": [2, 4],   "color": "#fff3cd"},
                {"range": [4, 12],  "color": "#f8d7da"},
            ],
            "threshold": {
                "line": {"color": "#c0392b", "width": 3},
                "thickness": 0.8,
                "value": 4,
            },
        },
        title={"text": "CO₂eq per cápita proyectado"},
    ))
    fig_gauge.update_layout(height=300, margin=dict(t=40, b=10, l=30, r=30))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Barras horizontales agrupadas: escenario vs referencia
    st.markdown("**Composición dietaria del escenario**")
    labels_bar  = [MACRO_LABELS[m] for m in MACROS]
    vals_esc    = [pct_norm[m] * 100 for m in MACROS]
    colors_esc  = [MACRO_COLORS[m] for m in MACROS]
    x_max       = 80

    fig_bars = go.Figure()

    if co2_ref_val is not None:
        vals_ref = [
            float(df[(df["Area"] == pais_ref) & (df["Year"] == 2022)][m].values[0]) * 100
            for m in MACROS
        ]
        x_max = max(x_max, max(vals_ref) * 1.25, max(vals_esc) * 1.25)
        fig_bars.add_trace(go.Bar(
            x=vals_ref,
            y=labels_bar,
            orientation="h",
            name=f"{pais_ref} 2022",
            marker=dict(color=colors_esc, opacity=0.30,
                        line=dict(color=colors_esc, width=1.5)),
            text=[f"{v:.1f}%" for v in vals_ref],
            textposition="outside",
            textfont=dict(size=11, color="#555"),
        ))
    else:
        x_max = max(x_max, max(vals_esc) * 1.25)

    fig_bars.add_trace(go.Bar(
        x=vals_esc,
        y=labels_bar,
        orientation="h",
        name="Escenario simulado",
        marker=dict(color=colors_esc, opacity=0.90),
        text=[f"{v:.1f}%" for v in vals_esc],
        textposition="outside",
        textfont=dict(size=11, color="#1a1a2e"),
    ))

    fig_bars.update_layout(
        barmode="group",
        height=340,
        xaxis=dict(
            title="% calórico",
            range=[0, x_max],
            ticksuffix="%",
            gridcolor="#ececec",
        ),
        yaxis=dict(title="", autorange="reversed"),
        plot_bgcolor="#ffffff",
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, x=0),
        margin=dict(t=10, b=70, l=10, r=90),
    )
    st.plotly_chart(fig_bars, use_container_width=True)

# ── DRIVERS SHAP ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("📌 Top-5 drivers de CO₂ (SHAP global)")
cols_shap = st.columns(5)
for i, (macro_name, narrativa) in enumerate(SHAP_NARRATIVA):
    with cols_shap[i]:
        st.markdown(
            f"<div style='background:#f8f9fa; border-radius:8px; padding:10px; height:100%;'>"
            f"<strong style='font-size:0.85rem;'>#{i+1} {macro_name}</strong><br>"
            f"<span style='font-size:0.78rem; color:#555;'>{narrativa}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.caption(
    "Ranking basado en |SHAP| medio global del Motor B (LightGBM, 5-fold CV, 390 obs). "
    "Los signos SHAP se interpretan con el beeswarm — en datos composicionales (suma=1.0) "
    "el SHAP medio con signo ≈ 0 es comportamiento esperado."
)

# ── SECCIÓN LITERATURA Y VISIÓN DE NEGOCIO ───────────────────────
st.markdown("---")
components.html(
    """
    <div style="background:#f5f5f7; border-radius:12px; padding:28px 32px; margin-top:8px; font-family:Inter,-apple-system,sans-serif;">

      <h3 style="color:#1a1a2e; font-size:1.15rem; font-weight:700; margin-bottom:18px;">
        📖 Acerca del Global Dietary Simulator
      </h3>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px;">

        <div>
          <h4 style="color:#1a1a2e; font-size:0.9rem; font-weight:700; margin-bottom:8px;">
            ¿Cómo se usa?
          </h4>
          <ol style="color:#444; font-size:0.83rem; line-height:1.75; padding-left:18px; margin:0;">
            <li><strong>Selecciona un país</strong> como punto de partida — los sliders se cargan con su dieta real de 2022.</li>
            <li><strong>Ajusta los sliders</strong> de cada macrocategoría calórica. La suma se normaliza automáticamente a 100 %.</li>
            <li><strong>Elige la tipología</strong> dietaria del escenario (C0 Proteica · C1 Tuberosa · C2 Cereal-Dependiente).</li>
            <li><strong>Lee el resultado</strong>: el gauge muestra la huella de CO₂eq predicha; las barras comparan tu escenario con el país de referencia.</li>
          </ol>
        </div>

        <div>
          <h4 style="color:#1a1a2e; font-size:0.9rem; font-weight:700; margin-bottom:8px;">
            ¿Para qué sirve?
          </h4>
          <ul style="color:#444; font-size:0.83rem; line-height:1.75; padding-left:18px; margin:0;">
            <li><strong>Políticas públicas:</strong> cuantifica el impacto de cambios dietarios antes de legislar incentivos o subsidios alimentarios.</li>
            <li><strong>Industria agroalimentaria:</strong> evalúa la huella de reformulaciones de producto o cambios en la cesta de compra.</li>
            <li><strong>Investigación nutricional:</strong> contrasta hipótesis dietarias con un modelo entrenado en datos reales FAOSTAT (2010–2022).</li>
            <li><strong>Educación:</strong> ilustra en tiempo real la relación entre patrón alimentario y emisiones de CO₂eq.</li>
          </ul>
        </div>

      </div>

      <div style="margin-top:22px; padding-top:18px; border-top:1px solid #ddd;">
        <h4 style="color:#1a1a2e; font-size:0.9rem; font-weight:700; margin-bottom:10px;">
          Base científica
        </h4>
        <p style="color:#444; font-size:0.83rem; line-height:1.7; margin:0;">
          El modelo predictivo reproduce la jerarquía de emisiones documentada por
          <strong>Poore &amp; Nemecek (2018, <em>Science</em>)</strong> — sin haber sido entrenado con esa información —,
          lo que valida su coherencia con el consenso IPCC sobre impacto agroalimentario.
          Los datos de composición dietaria provienen de las <strong>Food Balance Sheets de FAOSTAT</strong>
          (30 países · 2010–2022), y el índice de precios alimentarios de la
          <strong>FAO Food Price Index</strong> (base 2015 = 100).
          La huella de carbono objetivo integra emisiones de producción, procesado y distribución
          expresadas en <strong>CO₂ equivalente per cápita</strong> (t CO₂eq/año).
        </p>
        <p style="color:#777; font-size:0.78rem; margin-top:10px; margin-bottom:0;">
          Poore, J. &amp; Nemecek, T. (2018). Reducing food's environmental impacts through producers and consumers.
          <em>Science</em>, 360(6392), 987–992. · FAO (2024). FAOSTAT Food Balance Sheets. · IPCC (2022). AR6 WGIII Ch.12.
        </p>
      </div>

    </div>
    """,
    height=380,
    scrolling=False,
)
