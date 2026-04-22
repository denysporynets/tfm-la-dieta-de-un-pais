CARPETA: notebooks/
========================

Contiene todo el código del análisis, ordenado por fases del pipeline.
Cada notebook es autocontenido y ejecutable de forma independiente.

ARCHIVOS ACTUALES:
- 00_descarga_faostat.py                Script de descarga automática de los
                                         3 datasets FAOSTAT. Idempotente: si los
                                         archivos ya existen en raw/, los omite.
                                         Ejecutar: python 00_descarga_faostat.py

- 01_EDA_exploracion_inicial.ipynb      Análisis exploratorio de datos. COMPLETADO.
                                         Incluye correcciones de los 4 problemas
                                         críticos detectados (doble conteo, encoding,
                                         proyecciones, Japón → Viet Nam).

- cálculo_de_dieta_por_país_            Prototipo inicial del pipeline de
  normalización.py                       normalización. Referencia para el notebook 02.

ARCHIVOS PREVISTOS:
- 02_feature_engineering.ipynb          Mapeo 87→7 macrocategorías, vectorización
                                         porcentual, join 3 datasets, guardado
                                         de processed/02_dataset_final.parquet

- 03_clustering.ipynb                   K-Means (K=3 a 6), Silhouette Score,
                                         Davies-Bouldin Index, naming de clusters,
                                         guardado de processed/03_clusters.parquet

- 04_modelo_supervisado.ipynb           LightGBM, SHAP values, R² ajustado ≥ 0.4,
                                         análisis de errores por región,
                                         guardado de processed/04_model_shap.parquet

ORDEN DE EJECUCIÓN:
    00 → 01 → 02 → 03 → 04

DEPENDENCIAS:
    pandas, numpy, scikit-learn, lightgbm, shap, matplotlib, seaborn, pyarrow
