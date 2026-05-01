"""
utils.py — Data loader y constantes compartidas
Aguacate Team · TFM La Dieta de un País · 2026
"""

from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import streamlit as st
import streamlit.components.v1 as _components

_CSS_PATH = Path(__file__).parent / "style.css"

def load_css() -> None:
    css = _CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


_NAV_PAGES = [
    ("home",       "/",                  "🌌 Galaxia"),
    ("vista",      "/vista_pais",        "Vista País"),
    ("comparador", "/comparador",        "Comparador"),
    ("mapa",       "/mapa_clusters",     "Mapa"),
    ("simulador",  "/simulador_whatif",  "Simulador"),
    ("forecast",   "/forecast_dietario", "Forecast"),
]

def render_nav(active: str = "home", hide_sidebar: bool = False) -> None:
    links_html = "".join(
        '<a class="tdp-lnk{cls}" href="{href}">{label}</a>'.format(
            cls=" tdp-on" if k == active else "",
            href=href,
            label=label,
        )
        for k, href, label in _NAV_PAGES
    )
    nav_inner = (
        '<a class="logo" href="/">🥑 La Dieta de un País</a>'
        '<div class="lnks">' + links_html + "</div>"
    ).replace("'", "\\'")

    css = (
        "#_tdp_nav{position:fixed;top:0;left:0;right:0;z-index:9999999;height:54px;"
        "background:#1c1917;border-bottom:2px solid #0d9488;display:flex;"
        "align-items:center;padding:0 2rem;font-family:Inter,sans-serif;"
        "box-shadow:0 2px 16px rgba(0,0,0,.3)}"
        "#_tdp_nav a.logo{font-size:.92rem;font-weight:700;color:#fff;"
        "text-decoration:none;letter-spacing:-.01em;white-space:nowrap;"
        "margin-right:2.5rem;flex-shrink:0;transition:color .15s}"
        "#_tdp_nav a.logo:hover{color:#99f6e4}"
        "#_tdp_nav .lnks{display:flex;align-items:center;gap:2px;flex:1}"
        "#_tdp_nav a.tdp-lnk{font-size:.76rem;font-weight:500;color:#a8a29e;"
        "text-decoration:none;padding:6px 14px;border-radius:6px;"
        "text-transform:uppercase;letter-spacing:.07em;"
        "transition:color .15s,background .15s;white-space:nowrap}"
        "#_tdp_nav a.tdp-lnk:hover{color:#fff;background:rgba(255,255,255,.07)}"
        "#_tdp_nav a.tdp-on{color:#99f6e4!important;background:rgba(153,246,228,.12)}"
        "[data-testid=stHeader]{display:none!important}"
        ".block-container{padding-top:4rem!important}"
        + ("[data-testid=stSidebar]{display:none!important}" if hide_sidebar else "")
    )

    # Inject nav into the parent Streamlit page document via iframe JS bridge
    script = (
        "<script>(function(){"
        "var doc=window.parent.document;"
        "var s=doc.getElementById('_tdp_css');"
        "if(!s){s=doc.createElement('style');s.id='_tdp_css';doc.head.appendChild(s);}"
        "s.textContent='" + css + "';"
        "var old=doc.getElementById('_tdp_nav');if(old)old.remove();"
        "var n=doc.createElement('nav');n.id='_tdp_nav';"
        "n.innerHTML='" + nav_inner + "';"
        "doc.body.insertBefore(n,doc.body.firstChild);"
        "})();</script>"
    )
    _components.html(script, height=0)


def plotly_base_layout(**overrides) -> dict:
    """Plotly layout defaults matching DS-Nexus design system."""
    base = dict(
        font=dict(family="Inter, sans-serif", color="#1c1917", size=12),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(t=32, b=40, l=16, r=16),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="#e7e5e4",
            font=dict(family="Inter, sans-serif", size=12, color="#1c1917"),
        ),
        legend=dict(
            font=dict(size=11, family="Inter, sans-serif"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#e7e5e4",
            borderwidth=1,
        ),
        xaxis=dict(gridcolor="#f0eeec", linecolor="#e7e5e4", zerolinecolor="#e7e5e4"),
        yaxis=dict(gridcolor="#f0eeec", linecolor="#e7e5e4", zerolinecolor="#e7e5e4"),
    )
    base.update(overrides)
    return base

# ── RUTAS ────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent / "processed"

PATH_CLUSTERS      = BASE_DIR / "03_clusters.parquet"
PATH_MODEL_RESULTS = BASE_DIR / "04_model_results.parquet"
PATH_FORECAST      = BASE_DIR / "05b_forecast_lgbm.parquet"
PATH_LGB_MODEL     = BASE_DIR / "lgb_final.pkl"

# ── CONSTANTES ───────────────────────────────────────────────────
MACROS = [
    "pct_Cereales",
    "pct_Tuberculos",
    "pct_Azucares",
    "pct_Aceites_Grasas",
    "pct_Carnes",
    "pct_Lacteos_Huevos",
    "pct_Frutas_Verduras",
]

MACRO_LABELS = {
    "pct_Cereales":        "Cereales",
    "pct_Tuberculos":      "Tubérculos",
    "pct_Azucares":        "Azúcares",
    "pct_Aceites_Grasas":  "Aceites y Grasas",
    "pct_Carnes":          "Carnes",
    "pct_Lacteos_Huevos":  "Lácteos y Huevos",
    "pct_Frutas_Verduras": "Frutas y Verduras",
}

MACRO_COLORS = {
    "pct_Cereales":        "#f0a500",
    "pct_Tuberculos":      "#8b4513",
    "pct_Azucares":        "#e84393",
    "pct_Aceites_Grasas":  "#ffd700",
    "pct_Carnes":          "#c0392b",
    "pct_Lacteos_Huevos":  "#a0a0a0",
    "pct_Frutas_Verduras": "#2ecc71",
}

CLUSTER_NAMES = {
    0: "Proteica Diversificada",
    1: "Tuberosa Subsahariana",
    2: "Cereal-Dependiente",
}

CLUSTER_COLORS = {
    0: "#2563eb",
    1: "#16a34a",
    2: "#d97706",
}

FEATURES_LGB = MACROS + ["log_Food_CPI", "cluster_id"]

# ── ISO-3 MAPPING (para choropleth Plotly) ───────────────────────
COUNTRY_ISO3 = {
    "Argentina":                                          "ARG",
    "Australia":                                          "AUS",
    "Bangladesh":                                         "BGD",
    "Brazil":                                             "BRA",
    "Canada":                                             "CAN",
    "China, mainland":                                    "CHN",
    "Colombia":                                           "COL",
    "Egypt":                                              "EGY",
    "Ethiopia":                                           "ETH",
    "France":                                             "FRA",
    "Germany":                                            "DEU",
    "India":                                              "IND",
    "Indonesia":                                          "IDN",
    "Italy":                                              "ITA",
    "Kazakhstan":                                         "KAZ",
    "Kenya":                                              "KEN",
    "Mexico":                                             "MEX",
    "Morocco":                                            "MAR",
    "Nigeria":                                            "NGA",
    "Pakistan":                                           "PAK",
    "Poland":                                             "POL",
    "Republic of Korea":                                  "KOR",
    "Romania":                                            "ROU",
    "Saudi Arabia":                                       "SAU",
    "Senegal":                                            "SEN",
    "Spain":                                              "ESP",
    "Thailand":                                           "THA",
    "United Kingdom of Great Britain and Northern Ireland": "GBR",
    "United States of America":                           "USA",
    "Viet Nam":                                           "VNM",
}

# ── DATA LOADERS ─────────────────────────────────────────────────
@st.cache_data
def load_clusters() -> pd.DataFrame:
    df = pd.read_parquet(PATH_CLUSTERS)
    df["cluster_nombre"] = df["cluster_id"].map(CLUSTER_NAMES)
    return df


@st.cache_data
def load_model_results() -> pd.DataFrame:
    return pd.read_parquet(PATH_MODEL_RESULTS)


@st.cache_data
def load_forecast() -> pd.DataFrame:
    return pd.read_parquet(PATH_FORECAST)


@st.cache_resource
def load_lgb_model():
    return joblib.load(PATH_LGB_MODEL)


# ── HELPERS ──────────────────────────────────────────────────────
def predict_co2(pct_values: list[float], food_cpi: float, cluster_id: int) -> float:
    """Predice CO₂ t/cápita con lgb_final.pkl.
    pct_values: lista de 7 floats (proporciones, se normalizan internamente).
    food_cpi: CPI en unidades brutas del parquet (rango ~45–1076, base 2015=100).
    El modelo fue entrenado con log(Food_CPI) sin dividir por 100.
    """
    model = load_lgb_model()
    pcts = np.array(pct_values, dtype=float)
    pcts = pcts / pcts.sum()
    log_cpi = np.log(food_cpi)
    X = np.array([[*pcts, log_cpi, cluster_id]])
    return float(model.booster_.predict(X)[0])


def dominant_macro(row: pd.Series) -> str:
    vals = {m: row[m] for m in MACROS}
    key = max(vals, key=vals.get)
    return MACRO_LABELS[key]
