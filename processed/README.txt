CARPETA: processed/
========================

Contiene los datos intermedios y finales generados por el pipeline de análisis.
Todos los archivos están en formato Parquet (más rápido y compacto que CSV).

ARCHIVOS PREVISTOS:
- 02_dataset_final.parquet      Dataset maestro listo para modelizar.
                                 30 países × 13 años (2010–2022).
                                 Columnas: Area, Year, 7 macrocategorías (%),
                                 Total_DES_Kcal, Ratio_Proteina_Animal_Vegetal,
                                 CO2eq_t_per_capita, Food_CPI.
                                 Generado por: notebooks/02_feature_engineering.ipynb

- 03_clusters.parquet           Resultado del clustering K-Means.
                                 Añade columna Cluster_ID y Cluster_Nombre
                                 al dataset final.
                                 Generado por: notebooks/03_clustering.ipynb

- 04_model_shap.parquet         Predicciones del modelo LightGBM y
                                 valores SHAP por observación.
                                 Generado por: notebooks/04_modelo_supervisado.ipynb

NOTA IMPORTANTE:
Los archivos Parquet NO se suben a GitHub (están en .gitignore) por su tamaño.
Cada miembro del equipo debe regenerarlos ejecutando el pipeline desde notebooks/.
Los datos originales en raw/ tampoco se suben a GitHub por el mismo motivo.

PARA LEER UN PARQUET EN PYTHON:
    import pandas as pd
    df = pd.read_parquet('processed/02_dataset_final.parquet')
