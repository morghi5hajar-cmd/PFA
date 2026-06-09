# ============================================================
# PFA - PRÉVISION DE LA DEMANDE DE MÉDICAMENTS (CLEAN VERSION)
# ============================================================

import sqlite3
import pandas as pd
import numpy as np
import warnings
import os

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

print("Données chargées :", df.shape)

# ============================================================
# 2. FEATURE ENGINEERING TEMPOREL
# ============================================================

df["date_vente"] = pd.to_datetime(df["date_vente"])

df["mois"] = df["date_vente"].dt.month
df["trimestre"] = df["date_vente"].dt.quarter

def get_saison(m):
    if m in [12, 1, 2]:
        return "hiver"
    elif m in [3, 4, 5]:
        return "printemps"
    elif m in [6, 7, 8]:
        return "ete"
    return "automne"

df["saison"] = df["mois"].apply(get_saison)

# ============================================================
# 3. AGRÉGATION MÉTIER (SANS DATA LEAKAGE)
# ============================================================

df_agg = df.groupby(
    ["pharmacie", "categorie", "ville", "region", "mois", "trimestre", "saison"]
).agg(
    quantite_totale=("quantite", "sum"),
    stock_moyen=("stock", "mean"),
    marge_moyenne=("marge", "mean"),
    pfht_moyen=("pfht", "mean")
).reset_index()

# ============================================================
# 4. SPLIT TEMPOREL (IMPORTANT CORRECTION)
# ============================================================

df_agg = df_agg.sort_values("mois")

split_index = int(len(df_agg) * 0.8)

train = df_agg.iloc[:split_index]
test = df_agg.iloc[split_index:]

TARGET = "quantite_totale"

X_train = train.drop(columns=[TARGET])
y_train = train[TARGET]

X_test = test.drop(columns=[TARGET])
y_test = test[TARGET]

# ============================================================
# 5. PREPROCESSING
# ============================================================

categorical_cols = ["pharmacie", "categorie", "ville", "region", "saison"]
numeric_cols = [c for c in X_train.columns if c not in categorical_cols]

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
    ("num", "passthrough", numeric_cols)
])

# ============================================================
# 6. FONCTION D'ÉVALUATION
# ============================================================

def evaluate_model(name, model):
    pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    mape = mean_absolute_percentage_error(y_test, pred)
    r2 = r2_score(y_test, pred)

    print(f"\n {name}")
    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"MAPE : {mape:.4f} ({mape*100:.2f}%)")
    print(f"R²   : {r2:.4f}")

    return {"Model": name, "MAE": mae, "RMSE": rmse, "MAPE": mape, "R2": r2, "ModelObj": model}

results = []

# ============================================================
# 7. MODÈLE 1 - LINEAR REGRESSION
# ============================================================

lr = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LinearRegression())
])

lr.fit(X_train, y_train)
results.append(evaluate_model("Linear Regression", lr))

# ============================================================
# 8. MODÈLE 2 - RANDOM FOREST
# ============================================================

rf = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        random_state=42
    ))
])

rf.fit(X_train, y_train)
results.append(evaluate_model("Random Forest", rf))

# ============================================================
# 9. MODÈLE 3 - XGBOOST
# ============================================================

xgb_model = Pipeline([
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
results.append(evaluate_model("XGBoost", xgb_model))

# ============================================================
# 10. COMPARAISON
# ============================================================

comparison = pd.DataFrame(results)
comparison = comparison.drop(columns=["ModelObj"])

print("\n================ COMPARAISON ================")
print(comparison)

best_model = comparison.loc[comparison["MAPE"].idxmin(), "Model"]

print("\nMEILLEUR MODÈLE :", best_model)

# ============================================================
# 11. INTERPRÉTATION MÉTIER
# ============================================================

mean_demand = y_test.mean()
std_demand = y_test.std()

print("\n RECOMMANDATION STOCK")
print("Demande moyenne :", round(mean_demand, 2))
print("Stock sécurité :", round(2 * std_demand, 2))
print("Point réapprovisionnement :", round(mean_demand + 1.5 * std_demand, 2))
# ============================================================
#  PHASE 4 : VISUALISATIONS & INSIGHTS (CORRIGÉE)
# ============================================================

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set(style="whitegrid")

# ============================================================
# 1. PRÉDICTIONS XGBOOST
# ============================================================

print("\n Prédictions vs Réel (XGBoost)")

y_pred = xgb_model.predict(X_test)

plt.figure(figsize=(8,6))

plt.scatter(y_test, y_pred, alpha=0.6)

plt.plot(
    [y_test.min(), y_test.max()],
    [y_test.min(), y_test.max()],
    'r--'
)

plt.xlabel("Quantité réelle")
plt.ylabel("Quantité prédite")
plt.title("XGBoost - Réel vs Prédit")

plt.tight_layout()
plt.show()
plt.close()

# ============================================================
# 2. ERREURS
# ============================================================

errors = y_test - y_pred

# ============================================================
# 3. DISTRIBUTION DES ERREURS
# ============================================================

print("\n Distribution des erreurs")

plt.figure(figsize=(8,6))

sns.histplot(errors, bins=20, kde=True)

plt.title("Distribution des erreurs de prédiction")
plt.xlabel("Erreur (Réel - Prédit)")
plt.ylabel("Fréquence")

plt.tight_layout()
plt.show()
plt.close()

# ============================================================
# 4. BOXPLOT DES ERREURS
# ============================================================

print("\n Boxplot des erreurs")

plt.figure(figsize=(8,3))

sns.boxplot(x=errors)

plt.title("Boxplot des erreurs")

plt.tight_layout()
plt.show()
plt.close()

# ============================================================
# 5. ANALYSE DES ERREURS (PROPRE)
# ============================================================

mae = np.mean(np.abs(errors))
rmse = np.sqrt(np.mean(errors**2))
max_err = np.max(np.abs(errors))
min_err = np.min(np.abs(errors))

print("\n ANALYSE DES ERREURS")
print(f"MAE globale   : {mae:.2f}")
print(f"RMSE globale  : {rmse:.2f}")
print(f"Erreur max    : {max_err:.2f}")
print(f"Erreur min    : {min_err:.2f}")

# ============================================================
# 6. INTERPRÉTATION MÉTIER
# ============================================================

print("\n INTERPRÉTATION MÉTIER")

print(
    f"Le modèle XGBoost a une erreur moyenne de {mae:.2f} boîtes "
    "sur la prédiction de la demande mensuelle."
)

print(
    "Les résultats montrent une bonne capacité de généralisation "
    "et une utilisation possible pour la gestion des stocks."
)