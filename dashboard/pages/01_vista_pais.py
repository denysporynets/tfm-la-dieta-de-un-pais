"""
01_vista_pais.py — Series temporales de composición dietaria y CO₂ por país
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    load_clusters, load_css, render_nav,
    MACROS, MACRO_LABELS, MACRO_COLORS,
    CLUSTER_NAMES, CLUSTER_COLORS,
    dominant_macro,
)

st.set_page_config(page_title="Vista País · La Dieta de un País", page_icon="🌍", layout="wide")
load_css()
render_nav("vista")

# ── DATOS MACRO POR CLÚSTER (Marina Aguinacio, World Bank/OMS/FAO/PNUD/OCDE) ─
MACRO_CLUSTER = {
    0: {
        "nombre": "Proteica Diversificada",
        "n_paises": 17,
        "pib_per_capita": "10 000 – 65 000 USD",
        "gasto_comida_pct": "6 – 15 %",
        "emisiones_alim_pct": "9 – 13 %",
        "obesidad_pct": "20 – 36 %",
        "esperanza_vida": "74 – 83 años",
        "objetivo_inflacion": "~2 % (objetivo FMI/Banco Mundial)",
        "nota": (
            "Economías desarrolladas y emergentes avanzadas. Mayor diversidad dietaria "
            "(lácteos, huevos, carnes). La Ley de Engel explica el bajo gasto relativo "
            "en alimentación: a mayor renta, menor % del presupuesto destinado a comida."
        ),
    },
    1: {
        "nombre": "Tuberosa Subsahariana",
        "n_paises": 1,
        "pib_per_capita": "2 000 – 5 000 USD",
        "gasto_comida_pct": "50 – 65 %",
        "emisiones_alim_pct": "25 – 35 %",
        "obesidad_pct": "8 – 22 %",
        "esperanza_vida": "55 – 65 años",
        "objetivo_inflacion": "Sin objetivo formal estable",
        "nota": (
            "Patrón dominado por tubérculos (ñame, yuca). Nigeria: mayor productor de "
            "petróleo de África pero manufactura ~8 % PIB y sector terciario poco "
            "desarrollado, lo que explica la persistencia de un patrón de subsistencia."
        ),
    },
    2: {
        "nombre": "Cereal-Dependiente",
        "n_paises": 11,
        "pib_per_capita": "1 500 – 12 000 USD",
        "gasto_comida_pct": "35 – 50 %",
        "emisiones_alim_pct": "13 – 16 %",
        "obesidad_pct": "5 – 28 %",
        "esperanza_vida": "65 – 77 años",
        "objetivo_inflacion": "Variable (4 – 8 % en la mayoría)",
        "nota": (
            "Los países C2 priorizan cereales por bajos ingresos, tradición, clima, "
            "geografía y subvenciones. El cereal es saciante y barato: lógica de "
            "subsistencia antes que elección. Alta volatilidad del CPI, sensible a "
            "shocks globales de precios agrícolas."
        ),
    },
}

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
    fig2.update_yaxes(title_text="t CO₂eq / cápita", rangemode="tozero", secondary_y=False)
    fig2.update_yaxes(title_text="Food CPI (2015=100)", rangemode="tozero", secondary_y=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(
        "El CO₂eq incluye emisiones del sistema agroalimentario (AFOLU) per cápita. "
        "El Food CPI es el índice de precios al consumidor de alimentos (base 2015=100)."
    )

    # ── PENDIENTE 3: Volatilidad CPI contextualizada por clúster ──
    cpi_series = sub["Food_CPI"].dropna()
    if len(cpi_series) > 1:
        cpi_cv   = cpi_series.std() / cpi_series.mean() * 100
        cpi_max  = cpi_series.max()
        cpi_min  = cpi_series.min()

        mc = MACRO_CLUSTER[cluster_id]
        objetivo = mc["objetivo_inflacion"]

        if cluster_id == 0:
            volatilidad_txt = (
                f"**{pais}** pertenece al clúster de economías **{mc['nombre']}** (C0), "
                f"cuyo objetivo de inflación alimentaria es {objetivo}. "
                f"La volatilidad observada del Food CPI en el periodo es del **{cpi_cv:.1f} %** "
                f"(rango: {cpi_min:.0f} – {cpi_max:.0f}). "
                f"Picos por encima del objetivo suelen coincidir con shocks externos "
                f"(ej. crisis 2008, guerra de Ucrania 2022)."
            )
            color_box = "#e8f0fe"
            border_color = "#1a73e8"
        elif cluster_id == 2:
            volatilidad_txt = (
                f"**{pais}** pertenece al clúster **{mc['nombre']}** (C2), "
                f"con mayor sensibilidad a shocks globales de precios agrícolas. "
                f"Volatilidad Food CPI observada: **{cpi_cv:.1f} %** "
                f"(rango: {cpi_min:.0f} – {cpi_max:.0f}). "
                f"Las economías C2 no tienen un objetivo formal estable; la inflación "
                f"alimentaria afecta directamente al poder adquisitivo dado que el gasto "
                f"en comida representa el {mc['gasto_comida_pct']} del presupuesto familiar."
            )
            color_box = "#fff3e0"
            border_color = "#e67e22"
        else:
            volatilidad_txt = (
                f"**{pais}** pertenece al clúster **{mc['nombre']}** (C1). "
                f"Volatilidad Food CPI observada: **{cpi_cv:.1f} %** "
                f"(rango: {cpi_min:.0f} – {cpi_max:.0f}). "
                f"El gasto en alimentación supone el {mc['gasto_comida_pct']} del "
                f"presupuesto familiar, lo que hace muy sensible cualquier subida del CPI."
            )
            color_box = "#e8f5e9"
            border_color = "#27ae60"

        st.markdown(
            f"<div style='background:{color_box}; border-left:4px solid {border_color}; "
            f"padding:12px 16px; border-radius:0 6px 6px 0; margin-top:12px; font-size:0.9em;'>"
            f"{volatilidad_txt}</div>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Fuente contexto inflación: FMI / Banco Mundial. "
            "Datos CPI: FAOSTAT 2010–2022. "
            "Volatilidad medida como coeficiente de variación (CV = σ/μ)."
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

# ── PENDIENTE 4: Contexto macroeconómico del clúster (Marina Aguinacio) ──
st.markdown("---")
st.subheader("🏦 Contexto macroeconómico del clúster")
st.caption(
    "Datos aproximados elaborados por Marina Aguinacio a partir de World Bank, OMS, FAO, PNUD y OCDE. "
    "Adecuados para contexto narrativo; no citar como cifras exactas."
)

mc = MACRO_CLUSTER[cluster_id]
color_c = CLUSTER_COLORS[cluster_id]

col_info, col_tabla = st.columns([1, 2])

with col_info:
    st.markdown(
        f"<div style='background:{color_c}18; border:1px solid {color_c}44; "
        f"border-radius:8px; padding:16px 18px;'>"
        f"<div style='font-size:0.78em; color:#666; margin-bottom:4px;'>Clúster {cluster_id}</div>"
        f"<div style='font-size:1.1em; font-weight:700; color:{color_c};'>{mc['nombre']}</div>"
        f"<div style='font-size:0.82em; color:#555; margin-top:8px; line-height:1.6;'>{mc['nota']}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

with col_tabla:
    macro_rows = [
        ("Países en el clúster",        str(mc["n_paises"])),
        ("PIB per cápita (rango aprox.)", mc["pib_per_capita"]),
        ("Gasto en alimentación",        mc["gasto_comida_pct"]),
        ("Emisiones agroalimentarias",   mc["emisiones_alim_pct"]),
        ("Tasa de obesidad",             mc["obesidad_pct"]),
        ("Esperanza de vida",            mc["esperanza_vida"]),
        ("Objetivo inflación",           mc["objetivo_inflacion"]),
    ]
    df_macro = pd.DataFrame(macro_rows, columns=["Indicador", "Valor (aprox.)"])
    st.dataframe(df_macro.set_index("Indicador"), use_container_width=True)

# Comparativa de los tres clústeres
with st.expander("📊 Comparativa macro entre los 3 clústeres", expanded=True):
    _CL_COLORS = {0: "#0d9488", 1: "#d97706", 2: "#7c3aed"}
    _HEADERS = ["Clúster", "PIB per cápita", "Gasto alim.", "Emisiones", "Obesidad", "Esp. vida", "Inflación obj."]
    _WIDTHS  = ["22%", "16%", "11%", "11%", "9%", "12%", "19%"]

    th_style = "padding:8px 10px;font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#57534e;background:#f5f4f2;border-bottom:2px solid #e7e5e4;white-space:nowrap"
    td_style = "padding:9px 10px;font-size:.83rem;color:#1c1917;border-bottom:1px solid #f0eeec;overflow:hidden;white-space:nowrap;text-overflow:ellipsis"

    cols_html = "".join(f'<col style="width:{w}">' for w in _WIDTHS)
    head_html = "".join(f'<th style="{th_style}">{h}</th>' for h in _HEADERS)

    rows_html = ""
    for cid, datos in MACRO_CLUSTER.items():
        c = _CL_COLORS[cid]
        name_cell = (
            f'<td style="{td_style};border-left:3px solid {c};padding-left:8px">'
            f'<span style="color:{c};font-weight:700">C{cid}</span>'
            f' — {datos["nombre"]}</td>'
        )
        vals = [
            datos["pib_per_capita"],
            datos["gasto_comida_pct"],
            datos["emisiones_alim_pct"],
            datos["obesidad_pct"],
            datos["esperanza_vida"],
            datos["objetivo_inflacion"],
        ]
        val_cells = "".join(f'<td style="{td_style}">{v}</td>' for v in vals)
        bg = "background:#fafaf9" if cid % 2 == 0 else ""
        rows_html += f'<tr style="{bg}">{name_cell}{val_cells}</tr>'

    st.markdown(
        f'<div style="overflow:hidden;border-radius:10px;border:1px solid #e7e5e4;margin-bottom:12px">'
        f'<table style="width:100%;border-collapse:collapse;table-layout:fixed">'
        f'<colgroup>{cols_html}</colgroup>'
        f'<thead><tr>{head_html}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "La Ley de Engel explica el gradiente de gasto en alimentación: "
        "C0 (6–15 %) → C2 (35–50 %) → C1 (50–65 %). "
        "A mayor renta, menor proporción del presupuesto destinada a comida."
    )
