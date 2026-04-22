CARPETA: dashboard/
========================

Contiene la aplicación interactiva Streamlit del proyecto.

ARCHIVOS PREVISTOS:
- app.py                  Punto de entrada principal de la aplicación
- pages/                  Subcarpeta con las 5 vistas del dashboard:
    01_vista_pais.py          Series temporales DES / CPI / CO2eq por país
    02_comparador.py          Comparador vectorial entre dos países (radar chart)
    03_mapa_clusters.py       Mapa mundial coloreado por tipología de dieta
    04_simulador_whatif.py    Simulador What-If: sliders dieta → impacto CO2 y coste
    05_forecast_dietario.py   Motor C: forecast Prophet por país (2023–2030), CO₂ proyectado

ESTADO: pendiente (Semana 4 — 24 abr al 1 may)

CÓMO EJECUTAR (cuando esté listo):
    streamlit run app.py

DESPLIEGUE PREVISTO:
    Streamlit Community Cloud (URL pública + QR para la defensa oral)
    Los evaluadores podrán acceder desde sus teléfonos durante la presentación.

DEPENDENCIAS:
    streamlit, pandas, plotly, lightgbm, shap, pyarrow, prophet, joblib
