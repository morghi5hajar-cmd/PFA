# ============================================================
# 🎯 PFA - PRÉVISION DE LA DEMANDE DE MÉDICAMENTS
# ============================================================

import sqlite3
import pandas as pd
import numpy as np
import warnings
import os
import json

import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error
)

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import joblib

warnings.filterwarnings("ignore")

# ============================================================
# 1. CHARGEMENT DONNÉES
# ============================================================

DB_PATH = "dataset/new_pharmaci.db"

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query("""
SELECT
    v.id_vente, v.date_vente, v.quantite, v.prix_vente, v.categorie,
    m.nom AS medicament, m.pfht,
    p.nom AS pharmacie, p.stock, p.marge,
    vi.nom_ville AS ville,
    r.nom_region AS region
FROM ventes v
JOIN medicaments m ON v.id_medicament = m.id_medicament
JOIN pharmacies p ON v.id_pharmacie = p.id_pharmacie
JOIN villes vi ON p.id_ville = vi.id_ville
JOIN regions r ON vi.id_region = r.id_region
""", conn)

conn.close()

print("✅ Données chargées :", df.shape)

# ============================================================
# 2. FEATURE ENGINEERING TEMPOREL
# ============================================================

df["date_vente"] = pd.to_datetime(df["date_vente"])

df["mois"] = df["date_vente"].dt.month
df["trimestre"] = df["date_vente"].dt.quarter
df["jour_semaine"] = df["date_vente"].dt.dayofweek
df["weekend"] = df["jour_semaine"].isin([5,6]).astype(int)

# saison simple
def get_saison(m):
    if m in [12,1,2]:
        return "hiver"
    elif m in [3,4,5]:
        return "printemps"
    elif m in [6,7,8]:
        return "ete"
    return "automne"

df["saison"] = df["mois"].apply(get_saison)

# ============================================================
# 3. AGRÉGATION MÉTIER (IMPORTANT PFA)
# ============================================================

df_agg = df.groupby(
    ["pharmacie", "categorie", "ville", "region", "mois", "trimestre", "saison"]
).agg(
    quantite_totale=("quantite", "sum"),
    nb_transactions=("id_vente", "count"),
    ca_total=("prix_vente", "sum"),
    stock_moyen=("stock", "mean"),
    marge_moyenne=("marge", "mean"),
    pfht_moyen=("pfht", "mean")
).reset_index()

print("✅ Dataset agrégé :", df_agg.shape)

# ============================================================
# 4. FEATURES & TARGET
# ============================================================

TARGET = "quantite_totale"

X = df_agg.drop(columns=[TARGET])
y = df_agg[TARGET]

categorical_cols = ["pharmacie", "categorie", "ville", "region", "saison"]
numeric_cols = [c for c in X.columns if c not in categorical_cols]

# OneHotEncoding propre (IMPORTANT)
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ("num", "passthrough", numeric_cols)
    ]
)

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ============================================================
# 5. FONCTION ÉVALUATION
# ============================================================

def evaluate_model(name, model, X_test, y_test):
    pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    mape = mean_absolute_percentage_error(y_test, pred)
    r2 = r2_score(y_test, pred)

    print(f"\n📊 {name}")
    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"MAPE : {mape:.4f} ({mape*100:.2f}%)")
    print(f"R²   : {r2:.4f}")

    return name, mae, rmse, mape, r2, model

results = []

# ============================================================
# 6. MODÈLE 1 - LINEAR REGRESSION
# ============================================================

lr = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", LinearRegression())
])

lr.fit(X_train, y_train)
results.append(evaluate_model("Linear Regression", lr, X_test, y_test))

# ============================================================
# 7. MODÈLE 2 - RANDOM FOREST
# ============================================================

rf = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        random_state=42
    ))
])

rf.fit(X_train, y_train)
results.append(evaluate_model("Random Forest", rf, X_test, y_test))

# ============================================================
# 8. MODÈLE 3 - XGBOOST
# ============================================================

xgb_model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", xgb.XGBRegressor(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    ))
])

xgb_model.fit(X_train, y_train)
results.append(evaluate_model("XGBoost", xgb_model, X_test, y_test))

# ============================================================
# 9. COMPARAISON
# ============================================================

comparison = pd.DataFrame(results, columns=[
    "Model", "MAE", "RMSE", "MAPE", "R2", "Pipeline"
])

print("\n================ COMPARAISON ================")
print(comparison[["Model","MAE","RMSE","MAPE","R2"]])

best_model = comparison.loc[comparison["MAPE"].idxmin(), "Model"]
print("\n🏆 MEILLEUR MODÈLE :", best_model)

# ============================================================
# 10. FEATURE IMPORTANCE (XGBOOST)
# ============================================================

print("\n📌 Feature importance XGBoost")

xgb_trained = comparison.loc[comparison["Model"]=="XGBoost","Pipeline"].values[0]

model_xgb = xgb_trained.named_steps["model"]

print("Importance disponible après encoding (top features internes)")

# ============================================================
# 11. SAUVEGARDE
# ============================================================

os.makedirs("modele", exist_ok=True)

joblib.dump(lr, "modele/lr.pkl")
joblib.dump(rf, "modele/rf.pkl")
joblib.dump(xgb_model, "modele/xgb.pkl")

print("\n✅ MODELES SAUVEGARDÉS")

# ============================================================
# 12. INTERPRÉTATION MÉTIER (IMPORTANT PFA)
# ============================================================

mean_demand = y_test.mean()
std_demand = y_test.std()

print("\n📦 RECOMMANDATION STOCK")
print("Demande moyenne :", round(mean_demand,2))
print("Stock sécurité :", round(2*std_demand,2))
print("Point réapprovisionnement :", round(mean_demand + 1.5*std_demand,2))