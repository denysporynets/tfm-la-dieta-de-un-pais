# 🥑 La Dieta de un País

> Triangulación nutrición × coste × clima para descubrir tipologías dietarias globales y cuantificar su huella de carbono.

**TFM · Máster en Data Science & AI · Nuclio Digital School · Madrid 2026**
**Aguacate Team:** Rafael Montero · Marina Aguinacio · Ignacio Garrido · Denys Porynets
**Tutor:** Pedro Costa del Amo

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.0-success)](https://lightgbm.readthedocs.io)

---

## 🎯 Objetivo

Descubrir tipologías de dieta no evidentes a nivel país y cuantificar su impacto monetario y ambiental, sin pre-etiquetar — dejando que el algoritmo encuentre la estructura latente.

## 📊 Datos

- **Fuente:** FAOSTAT — Food Balance Sheets (2010–2022) · Emissions AFOLU · Food CPI
- **Cobertura:** 30 países seleccionados por máxima varianza geográfica, PIB y climática
- **Compresión:** 87 ítems FAO → 7 macro-categorías (Cereales · Tubérculos · Azúcares · Aceites/Grasas · Carnes · Lácteos/Huevos · Frutas/Verduras)

## ⚙️ Los 3 motores analíticos

| Motor | Técnica | Output | Métrica clave |
|---|---|---|---|
| **A — Clustering** | K-Means K=3 | 3 tipologías dietarias | Silhouette = 0.40 · Estabilidad temporal 98.7% |
| **B — Predictor CO₂** | LightGBM + SHAP | 9 drivers explicativos | R² = **0.864** (5-fold CV) · vs baseline LinReg 0.29 |
| **C — Forecast 2023–2030** | LightGBM Global | Proyección dietaria + CO₂ | R² walk-forward = **0.9943** · MAE = 0.0064 |

## 🔍 Hallazgo principal

El modelo reproduce la jerarquía de impacto climático de **Poore & Nemecek (2018)** sin ningún conocimiento previo: los top-3 drivers SHAP (Cereales · Azúcares · Carnes) coinciden con la jerarquía IPCC. El vector dietario contiene la señal completa — el `cluster_id` aporta solo 0.04 |SHAP|.

## 🗂️ Las 3 tipologías descubiertas

- **C0 — Proteica Diversificada** (18 países · Europa, Américas, Oceanía) — Lácteos 20%, Carnes 12%, Cereales 31%
- **C1 — Tuberosa Subsahariana** (Nigeria singleton) — Tubérculos 28%, Cereales 45%
- **C2 — Cereal-Dependiente** (12 países · Asia/África en desarrollo) — Cereales 60%

**Caso especial:** Pakistan — único país con transición documentada (C2→C0 desde 2016, correlacionado con crecimiento PIB).

---

## 🚀 Dashboard interactivo

5 vistas Streamlit con datos en vivo desde los parquets:

1. **Vista País** — Series temporales 7 macros + CO₂ + CPI (2010–2022)
2. **Comparador** — Radar chart hasta 4 países
3. **Mapa Clústeres** — Choropleth mundial con slider temporal
4. **Simulador What-If** — 7 sliders → predicción CO₂ en tiempo real con `lgb_final.pkl`
5. **Forecast 2023–2030** — Motor C LightGBM Global

### Ejecución local

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

### Deploy

Desplegado en **Streamlit Community Cloud** — entry point: `dashboard/app.py`.

---

## 📁 Estructura

```
TFM_Dieta_Pais/
├── dashboard/              # App Streamlit (5 páginas)
│   ├── app.py              # Home + KPIs + tabla clústeres
│   ├── utils.py            # Loaders cacheados + constantes + predict_co2()
│   ├── pages/              # 01–05 vistas
│   └── requirements.txt
├── notebooks/              # Pipeline completo (00–05c)
│   ├── 01_EDA_exploracion_inicial.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_clustering.ipynb
│   ├── 04_motor_b_lightgbm.ipynb
│   ├── 05b_forecast_lightgbm.ipynb   ← ganador Motor C
│   └── html_s/             # Notebooks renderizados
├── processed/              # Parquets + modelo serializado
│   ├── 03_clusters.parquet
│   ├── 04_model_results.parquet
│   ├── 05b_forecast_lgbm.parquet
│   └── lgb_final.pkl
├── requirements.txt
├── packages.txt            # libgomp1 (lightgbm en Linux)
└── .streamlit/config.toml
```

---

## 🛠️ Stack técnico

`Python 3.11` · `pandas` · `numpy` · `scikit-learn` (K-Means) · `lightgbm` · `shap` · `prophet` · `statsmodels` (SARIMAX) · `streamlit` · `plotly` · `joblib` · `pyarrow`

## 📚 Referencias clave

- Poore, J. & Nemecek, T. (2018). *Reducing food's environmental impacts through producers and consumers*. **Science**, 360(6392).
- Ke, G. et al. (2017). *LightGBM: A Highly Efficient Gradient Boosting Decision Tree*. **NeurIPS**.
- Lundberg, S. & Lee, S.-I. (2017). *A Unified Approach to Interpreting Model Predictions*. **NeurIPS**.
- FAOSTAT (2023). *Food Balance Sheets*. Food and Agriculture Organization of the United Nations.

---

<div align="center">

[← Portfolio](https://denysporynets.github.io)

</div>
