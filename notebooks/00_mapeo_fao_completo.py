# -*- coding: utf-8 -*-
"""
mapeo_fao_completo.py
=====================
Diccionario de mapeo: 87 ítems hoja FBS → 7 macrocategorías.

SESIÓN 2 — 03/04/2026
Completado el mapeo completo de los 87 ítems leaf del FBS.
El prototipo de la Sesión 1 tenía ~15 ítems; este archivo cubre la totalidad.

USO:
    from mapeo_fao_completo import MAPEO_FAO, ITEMS_AGREGADOS, MACRO_COLS
    df['Macro_Grupo'] = df['Item'].map(MAPEO_FAO)

CATEGORÍAS:
    1. Cereales          — base energética de granos
    2. Tuberculos        — raíces y tubérculos
    3. Azucares          — azúcares y edulcorantes
    4. Aceites_Grasas    — aceites vegetales, grasas animales, semillas oleaginosas
    5. Carnes            — carnes, pescado, mariscos, despojos
    6. Lacteos_Huevos    — lácteos y huevos
    7. Frutas_Verduras   — frutas, verduras, legumbres, frutos secos, estimulantes
"""

# ─────────────────────────────────────────────────────────────
# 1. ÍTEMS AGREGADOS — EXCLUIR SIEMPRE (doble conteo)
# Estos 33 ítems son subtotales que ya incluyen los ítems hoja.
# Incluirlos produce doble conteo (Irlanda → 15.000 kcal/día).
# ─────────────────────────────────────────────────────────────
ITEMS_AGREGADOS = {
    'Grand Total',
    'Vegetal Products',
    'Animal Products',
    'Cereals - Excluding Beer',
    'Starchy Roots',
    'Sugar & Sweeteners',
    'Pulses',
    'Treenuts',
    'Oilcrops',
    'Vegetables',
    'Fruits - Excluding Wine',
    'Stimulants',
    'Spices',
    'Alcoholic Beverages',
    'Meat',
    # 'Offals',        # Fix Sesión 2: puede ser el único ítem de despojos en FBS
    'Animal fats',
    'Aquatic Products, Other',
    # 'Eggs',              # Fix Sesión 2: es el único ítem de huevos en FBS normalizado
    # 'Milk - Excluding Butter',  # Fix Sesión 2: es el único ítem de leche en FBS normalizado
    'Fish, Seafood',
    'Vegetable Oils',
    'Miscellaneous',
    'Oilcrops Oil, Other',
    'Vegetables, other',
    'Fruits, other',
    'Sweeteners, other',
    'Roots, other',
    'Cereals, other',
    'Meat, other',
    'Aquatic Animals, Others',
    'Fish, Body Oil',
    'Fish, Liver Oil',
}

# ─────────────────────────────────────────────────────────────
# 2. MAPEO 87 ÍTEMS HOJA → 7 MACROCATEGORÍAS
# ─────────────────────────────────────────────────────────────
MAPEO_FAO = {

    # ── CEREALES ─────────────────────────────────────────────
    # Base energética de granos. Primer grupo por volumen de kcal
    # en la mayoría de países del mundo.
    'Wheat and products':       'Cereales',
    'Rice and products':        'Cereales',
    'Barley and products':      'Cereales',
    'Maize and products':       'Cereales',
    'Rye and products':         'Cereales',
    'Oats':                     'Cereales',
    'Millet and products':      'Cereales',
    'Sorghum and products':     'Cereales',
    'Cereals, Other':           'Cereales',
    'Triticale':                'Cereales',
    'Buckwheat':                'Cereales',
    'Fonio':                    'Cereales',
    'Quinoa':                   'Cereales',
    'Beer':                     'Cereales',  # fermentado de cebada — kcal reales

    # ── TUBÉRCULOS ───────────────────────────────────────────
    # Raíces y tubérculos. Base calórica alternativa a cereales,
    # especialmente relevante en África subsahariana y Latinoamérica.
    'Potatoes and products':    'Tuberculos',
    'Sweet potatoes':           'Tuberculos',
    'Cassava and products':     'Tuberculos',
    'Yams':                     'Tuberculos',
    'Roots, Other':             'Tuberculos',
    'Plantains':                'Tuberculos',  # plátano macho, consumo como tubérculo

    # ── AZÚCARES ─────────────────────────────────────────────
    # Azúcares y edulcorantes. Marcador de dieta procesada/occidental.
    'Sugar cane':               'Azucares',
    'Sugar beet':               'Azucares',
    'Sugar (Raw Equivalent)':   'Azucares',
    'Sugar non-centrifugal':    'Azucares',
    'Sweeteners, Other':        'Azucares',
    'Honey':                    'Azucares',

    # ── ACEITES Y GRASAS ──────────────────────────────────────
    # Aceites vegetales, semillas oleaginosas y grasas animales.
    # Alta densidad calórica. Muy dependiente de precios de commodities globales.
    # Semillas oleaginosas:
    'Soyabeans':                'Aceites_Grasas',
    'Groundnuts (Shelled Eq)':  'Aceites_Grasas',
    'Sunflower seed':           'Aceites_Grasas',
    'Rape and Mustard seed':    'Aceites_Grasas',
    'Cottonseed':               'Aceites_Grasas',
    'Sesame seed':              'Aceites_Grasas',
    'Oilcrops, Other':          'Aceites_Grasas',
    'Palm kernels':             'Aceites_Grasas',
    'Coconuts - Incl Copra':    'Aceites_Grasas',
    'Olives (including preserved)': 'Aceites_Grasas',
    # Aceites refinados:
    'Soyabean Oil':             'Aceites_Grasas',
    'Groundnut Oil':            'Aceites_Grasas',
    'Sunflower seed Oil':       'Aceites_Grasas',  # nombre alternativo (algunos contextos FAO)
    'Sunflowerseed Oil':        'Aceites_Grasas',  # nombre real en FBS normalizado — Fix Sesión 2
    'Rape and Mustard Oil':     'Aceites_Grasas',
    'Cottonseed Oil':           'Aceites_Grasas',
    'Palm Oil':                 'Aceites_Grasas',
    'Sesame seed Oil':          'Aceites_Grasas',
    'Olive Oil':                'Aceites_Grasas',
    'Coconut Oil':              'Aceites_Grasas',
    'Palm kernel Oil':          'Aceites_Grasas',
    # Grasas animales:
    'Butter, Ghee':             'Aceites_Grasas',
    'Lard':                     'Aceites_Grasas',
    'Tallow':                   'Aceites_Grasas',

    # ── CARNES ───────────────────────────────────────────────
    # Carnes terrestres, pescado y mariscos, despojos.
    # Mayor huella de CO2 por kcal de todos los grupos.
    # Carnes terrestres:
    'Bovine Meat':              'Carnes',
    'Mutton & Goat Meat':       'Carnes',
    'Pigmeat':                  'Carnes',
    'Poultry Meat':             'Carnes',
    'Meat, Other':              'Carnes',
    'Horse Meat':               'Carnes',
    'Offals, Edible':           'Carnes',
    'Game meat':                'Carnes',
    # Pescado y mariscos (proteína animal, huella similar):
    'Freshwater Fish':          'Carnes',
    'Demersal Fish':            'Carnes',
    'Pelagic Fish':             'Carnes',
    'Marine Fish, Other':       'Carnes',
    'Crustaceans':              'Carnes',
    'Cephalopods':              'Carnes',
    'Molluscs, Other':          'Carnes',

    # ── LÁCTEOS Y HUEVOS ─────────────────────────────────────
    # Productos lácteos y huevos. Alta densidad nutricional.
    # Fix Sesión 2: 'Milk - Excluding Butter' y 'Eggs' eliminados de ITEMS_AGREGADOS
    # Son los únicos ítems con los que aparecen lácteos y huevos en el FBS normalizado.
    # Excluirlos dejaba pct_Lacteos_Huevos en 0.3% (debería ser ~10-15%).
    'Milk - Excluding Butter':  'Lacteos_Huevos',
    'Eggs':                     'Lacteos_Huevos',
    'Milk, Whole Fresh Cow':    'Lacteos_Huevos',
    'Milk, Whole Fresh Buffaloes': 'Lacteos_Huevos',
    'Milk, Whole Fresh Goats':  'Lacteos_Huevos',
    'Milk, Whole Fresh Sheep':  'Lacteos_Huevos',
    'Milk, Whole Dried':        'Lacteos_Huevos',
    'Milk, Skimmed Dried':      'Lacteos_Huevos',
    'Evaporated & Condensed Milk': 'Lacteos_Huevos',
    'Cheese':                   'Lacteos_Huevos',
    'Cream':                    'Lacteos_Huevos',
    'Whey':                     'Lacteos_Huevos',

    # ── FRUTAS Y VERDURAS ────────────────────────────────────
    # Frutas, verduras, legumbres, frutos secos, estimulantes.
    # Alta densidad nutricional, baja huella de CO2.
    # Verduras:
    'Tomatoes and products':    'Frutas_Verduras',
    'Onions':                   'Frutas_Verduras',
    'Vegetables, Other':        'Frutas_Verduras',
    # Frutas:
    'Oranges, Mandarines':      'Frutas_Verduras',
    'Lemons, Limes and products': 'Frutas_Verduras',
    'Grapefruit and products':  'Frutas_Verduras',
    'Citrus, Other':            'Frutas_Verduras',
    'Bananas':                  'Frutas_Verduras',
    'Apples and products':      'Frutas_Verduras',
    'Pineapples and products':  'Frutas_Verduras',
    'Dates':                    'Frutas_Verduras',
    'Grapes and products (excl wine)': 'Frutas_Verduras',
    'Fruits, Other':            'Frutas_Verduras',
    'Mangoes':                  'Frutas_Verduras',
    'Papayas':                  'Frutas_Verduras',
    'Wine':                     'Frutas_Verduras',  # fermentado de uva
    # Legumbres (proteína vegetal):
    'Beans':                    'Frutas_Verduras',
    'Peas':                     'Frutas_Verduras',
    'Pulses, Other':            'Frutas_Verduras',
    'Lentils':                  'Frutas_Verduras',
    'Chickpeas':                'Frutas_Verduras',
    'Groundnuts (in Shell Eq)': 'Frutas_Verduras',
    # Frutos secos:
    'Nuts and products':        'Frutas_Verduras',
    'Cashewnuts':               'Frutas_Verduras',
    'Almonds, with shell':      'Frutas_Verduras',
    # Estimulantes (kcal baja pero presentes):
    'Coffee and products':      'Frutas_Verduras',
    'Tea (including mate)':     'Frutas_Verduras',
    'Cocoa Beans and products': 'Frutas_Verduras',
    # Especias (kcal muy baja — quedará bajo umbral 50 kcal/día):
    'Spices, Other':            'Frutas_Verduras',
    'Pepper':                   'Frutas_Verduras',
    'Pimento':                  'Frutas_Verduras',
}

# ─────────────────────────────────────────────────────────────
# 3. COLUMNAS DE MACROCATEGORÍAS (orden estándar del proyecto)
# ─────────────────────────────────────────────────────────────
MACRO_COLS = [
    'Cereales',
    'Tuberculos',
    'Azucares',
    'Aceites_Grasas',
    'Carnes',
    'Lacteos_Huevos',
    'Frutas_Verduras',
]

# ─────────────────────────────────────────────────────────────
# 4. VALIDACIÓN DEL MAPEO (ejecutar al importar para detectar errores)
# ─────────────────────────────────────────────────────────────
_categorias_validas = set(MACRO_COLS)
_errores = [
    (item, cat) for item, cat in MAPEO_FAO.items()
    if cat not in _categorias_validas
]
if _errores:
    raise ValueError(f"[mapeo_fao_completo] Categorías inválidas detectadas: {_errores}")

print(f"[mapeo_fao_completo] ✅ {len(MAPEO_FAO)} ítems mapeados a {len(_categorias_validas)} categorías.")
print(f"[mapeo_fao_completo] Distribución:")
from collections import Counter
dist = Counter(MAPEO_FAO.values())
for cat in MACRO_COLS:
    print(f"  {cat:<20} {dist[cat]:>3} ítems")
