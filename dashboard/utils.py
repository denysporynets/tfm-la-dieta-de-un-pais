"""
utils.py — Data loader y constantes compartidas
Aguacate Team · TFM La Dieta de un País · 2026
"""

from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import streamlit as st

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
    return float(model.predict(X)[0])


def dominant_macro(row: pd.Series) -> str:
    vals = {m: row[m] for m in MACROS}
    key = max(vals, key=vals.get)
    return MACRO_LABELS[key]
