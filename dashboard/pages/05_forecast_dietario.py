import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Motor C: Forecast Dietario",
    page_icon="📈",
    layout="wide"
)

# ── RUTAS ────────────────────────────────────────────────────────
BASE      = Path(__file__).parent.parent.parent / "processed"
PATH_HIST = BASE / "03_clusters.parquet"
PATH_FC   = BASE / "05b_forecast_lgbm.parquet"

MACROS = [
    'pct_Cereales', 'pct_Tuberculos', 'pct_Azucares',
    'pct_Aceites_Grasas', 'pct_Carnes', 'pct_Lacteos_Huevos', 'pct_Frutas_Verduras'
]
MACRO_LABELS = {
    'pct_Cereales':       'Cereales',
    'pct_Tuberculos':     'Tubérculos',
    'pct_Azucares':       'Azúcares',
    'pct_Aceites_Grasas': 'Aceites y Grasas',
    'pct_Carnes':         'Carnes',
    'pct_Lacteos_Huevos': 'Lácteos y Huevos',
    'pct_Frutas_Verduras':'Frutas y Verduras'
}
MACRO_COLORS = [
    '#f0a500', '#8b4513', '#e84393',
    '#ffd700', '#c0392b', '#a0a0a0', '#2ecc71'
]
CLUSTER_LABELS = {0: 'C0 — Proteica Diversificada', 1: 'C1 — Tuberosa Subsahariana', 2: 'C2 — Cereal-Dependiente'}


@st.cache_data
def load_data():
    hist = pd.read_parquet(PATH_HIST)
    fc   = pd.read_parquet(PATH_FC)
    # 05b ya tiene columna Year como int64 — no requiere parseo de 'ds'
    fc['Year'] = fc['Year'].astype(int)
    return hist, fc


# ── LAYOUT ───────────────────────────────────────────────────────
st.title("📈 Motor C: Evolución Dietaria Proyectada 2023–2030")
st.caption(
    "LightGBM Global entrenado con ~2.100 muestras combinadas de 30 países (R²=0.9943 walk-forward). "
    "Escenario tendencial basado en inercia histórica con IC al 80% por quantile regression. "
    "No es una predicción exacta."
)

if not PATH_FC.exists():
    st.error(
        "⚠️ No se encuentra `processed/05b_forecast_lgbm.parquet`. "
        "Ejecuta primero el notebook `05b_forecast_lightgbm.ipynb`."
    )
    st.stop()

hist, fc = load_data()

# ── CONTROLES ────────────────────────────────────────────────────
col_ctrl, col_main = st.columns([1, 3])

with col_ctrl:
    pais = st.selectbox("🌍 País", sorted(hist['Area'].unique()), index=sorted(hist['Area'].unique()).index('Spain') if 'Spain' in hist['Area'].unique() else 0)
    horizonte = st.slider("📅 Año horizonte", min_value=2024, max_value=2030, value=2028)

    # Info del clúster del país
    cluster_pais = hist[hist['Area'] == pais]['cluster_id'].iloc[-1]
    st.info(f"**Tipología:** {CLUSTER_LABELS.get(int(cluster_pais), 'Desconocido')}")

    st.markdown("---")
    st.markdown("**¿Qué muestra este módulo?**")
    st.markdown(
        "Proyección de la composición dietaria según la tendencia histórica "
        "observada entre 2010 y 2022, y el impacto estimado en CO₂ per cápita "
        "derivado del modelo LightGBM."
    )

# ── DATOS DEL PAÍS ───────────────────────────────────────────────
h = hist[hist['Area'] == pais].sort_values('Year')
f_pais = fc[fc['Area'] == pais].sort_values('Year')
f_pais_horizon = f_pais[f_pais['Year'] <= horizonte]

# ── GRÁFICO 1: ÁREA APILADA DIETA (histórico + forecast) ────────
with col_main:
    tab1, tab2 = st.tabs(["🥗 Composición Dietaria", "🌡️ Proyección CO₂"])

    with tab1:
        fig_dieta = go.Figure()

        for macro, color, label in zip(MACROS, MACRO_COLORS, MACRO_LABELS.values()):
            fc_macro = f_pais_horizon[f_pais_horizon['variable'] == macro].sort_values('Year')
            hist_macro_years = fc_macro[fc_macro['Year'] <= 2022]['Year']
            hist_macro_vals  = fc_macro[fc_macro['Year'] <= 2022]['yhat']
            fc_years  = fc_macro[fc_macro['Year'] > 2022]['Year']
            fc_vals   = fc_macro[fc_macro['Year'] > 2022]['yhat']
            fc_lower  = fc_macro[fc_macro['Year'] > 2022]['yhat_lower']
            fc_upper  = fc_macro[fc_macro['Year'] > 2022]['yhat_upper']

            # Banda de confianza (sólo en zona forecast)
            if not fc_years.empty:
                fig_dieta.add_trace(go.Scatter(
                    x=list(fc_years) + list(fc_years[::-1]),
                    y=list(fc_upper) + list(fc_lower[::-1]),
                    fill='toself',
                    fillcolor=color + '30',
                    line=dict(color='rgba(0,0,0,0)'),
                    showlegend=False,
                    hoverinfo='skip'
                ))

            # Línea histórica
            fig_dieta.add_trace(go.Scatter(
                x=hist_macro_years, y=hist_macro_vals,
                mode='lines+markers',
                name=label,
                line=dict(color=color, width=2),
                marker=dict(size=5),
                legendgroup=label
            ))

            # Línea forecast (discontinua)
            if not fc_years.empty:
                fig_dieta.add_trace(go.Scatter(
                    x=fc_years, y=fc_vals,
                    mode='lines+markers',
                    name=f'{label} (forecast)',
                    line=dict(color=color, width=2, dash='dash'),
                    marker=dict(size=5, symbol='diamond'),
                    legendgroup=label,
                    showlegend=False
                ))

        fig_dieta.add_vline(x=2022, line_dash='dot', line_color='gray', annotation_text='2022 (último dato real)')
        fig_dieta.update_layout(
            title=f"{pais} — Composición dietaria 2010–{horizonte}",
            xaxis_title='Año',
            yaxis_title='Proporción calórica',
            yaxis=dict(range=[0, 0.7]),
            hovermode='x unified',
            height=480,
            legend=dict(orientation='h', yanchor='bottom', y=-0.3)
        )
        st.plotly_chart(fig_dieta, use_container_width=True)
        st.caption("Línea continua = datos históricos. Línea discontinua = forecast LightGBM Global. Banda semitransparente = IC 80% (quantile regression q=0.10/q=0.90).")

    with tab2:
        co2_hist = h[['Year', 'CO2eq_t_per_capita']].sort_values('Year')
        co2_fc_pais = (
            f_pais_horizon[['Year', 'CO2eq_forecast']]
            .drop_duplicates('Year')
            .sort_values('Year')
        )

        co2_2022 = float(h[h['Year'] == 2022]['CO2eq_t_per_capita'].values[0]) if 2022 in h['Year'].values else co2_hist['CO2eq_t_per_capita'].iloc[-1]
        co2_proj  = float(co2_fc_pais[co2_fc_pais['Year'] == horizonte]['CO2eq_forecast'].values[0]) if horizonte in co2_fc_pais['Year'].values else None
        delta_abs = (co2_proj - co2_2022) if co2_proj else None
        delta_pct = (delta_abs / co2_2022 * 100) if delta_abs else None

        # KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("CO₂ real 2022", f"{co2_2022:.2f} t/cáp")
        if co2_proj:
            kpi2.metric(f"CO₂ proyectado {horizonte}", f"{co2_proj:.2f} t/cáp",
                        delta=f"{delta_pct:+.1f}%",
                        delta_color='inverse')
            kpi3.metric("Variación absoluta", f"{delta_abs:+.2f} t/cáp")

        # Gráfico CO₂
        fig_co2 = go.Figure()
        fig_co2.add_trace(go.Scatter(
            x=co2_hist['Year'], y=co2_hist['CO2eq_t_per_capita'],
            mode='lines+markers',
            name='CO₂ real',
            line=dict(color='#3498db', width=2.5),
            marker=dict(size=6)
        ))
        fig_co2.add_trace(go.Scatter(
            x=co2_fc_pais[co2_fc_pais['Year'] > 2022]['Year'],
            y=co2_fc_pais[co2_fc_pais['Year'] > 2022]['CO2eq_forecast'],
            mode='lines+markers',
            name='CO₂ forecast (LightGBM Motor B + C)',
            line=dict(color='#e74c3c', width=2.5, dash='dash'),
            marker=dict(size=6, symbol='diamond')
        ))
        fig_co2.add_vline(x=2022, line_dash='dot', line_color='gray', annotation_text='2022')
        fig_co2.update_layout(
            title=f"{pais} — CO₂ per cápita 2010–{horizonte}",
            xaxis_title='Año',
            yaxis_title='t CO₂eq / cápita',
            height=420,
            hovermode='x unified'
        )
        st.plotly_chart(fig_co2, use_container_width=True)
        st.caption(
            "El CO₂ proyectado se obtiene aplicando el modelo LightGBM Motor B al vector dietario "
            "que el Motor C proyecta para cada año. El Food CPI se mantiene constante en el último valor "
            "conocido (2022) como simplificación."
        )

# ── NOTA METODOLÓGICA ────────────────────────────────────────────
with st.expander("ℹ️ Nota metodológica completa"):
    st.markdown("""
**Motor C — LightGBM Global (modelo elegido)**

- **Modelo:** 1 modelo global entrenado sobre ~2.100 muestras (30 países × 13 años × 7 macros).
  Features: lag1/lag2/lag3, año, macro codificada, país codificado, cluster_id, log(Food_CPI).
- **Métricas walk-forward (val 2020–2022):** R² = 0.9943 · MAE = 0.0064 (proporción calórica).
- **IC al 80%:** mediante quantile regression (q=0.10 / q=0.90), más conservadores que Prophet.
- **Forecast recursivo:** cada predicción anterior se usa como lag1 para el año siguiente.
  Los errores se acumulan — interpretar 2028–2030 como escenarios cualitativos.
- **Correlación, no causalidad:** las proyecciones reflejan la inercia histórica,
  no el efecto de políticas específicas.
- **Food CPI constante:** el coste de los alimentos se fija en el valor de 2022.
- **Cluster fijo:** se asume que el país permanece en su última tipología (2022).
  Sólo Pakistán mostró transición histórica (2016).

**Por qué no Prophet ni SARIMAX:** Prophet produjo caídas de CO₂ implausibles (Canadá −67.9%);
SARIMAX convergió en ARIMA(1,0,0) para el 95.7% de las series (random-walk) con crecimientos
explosivos en Asia y África (+204% Vietnam). LightGBM Global supera a ambos en R² y coherencia empírica.
""")
