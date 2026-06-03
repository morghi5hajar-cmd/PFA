"""
MACHINE LEARNING — Régression : Prévision de la demande de médicaments
Projet PFA — ENSIAS 2024-2025
Hajar MORGHI — Doua AIT TALEB

Variable cible : quantite vendue par médicament/pharmacie/mois
Modèles        : Régression Linéaire, Random Forest, XGBoost
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib
import os

warnings.filterwarnings("ignore")

# ============================================================
# CHEMINS
# ============================================================
DB_PATH       = r"C:\Users\aitta\Downloads\PFA.rar\PFA\PFA\dataset\pharmacieee.db"
RESULTATS_DIR = r"C:\Users\aitta\Downloads\PFA.rar\PFA\PFA\resultats\ml"
MODELE_DIR    = r"C:\Users\aitta\Downloads\PFA.rar\PFA\PFA\modele"

os.makedirs(RESULTATS_DIR, exist_ok=True)
os.makedirs(MODELE_DIR, exist_ok=True)

# ============================================================
# 1. CHARGEMENT DES DONNÉES
# ============================================================
print("=" * 60)
print(" CHARGEMENT DES DONNÉES")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("""
    SELECT
        v.id_vente, v.date_vente, v.saison, v.quantite, v.prix_vente, v.categorie,
        m.nom AS medicament, m.pfht,
        p.nom AS pharmacie, p.stock, p.marge,
        vi.nom_ville AS ville,
        r.nom_region AS region
    FROM ventes v
    JOIN medicaments  m   ON v.id_medicament = m.id_medicament
    JOIN pharmacies   p   ON v.id_pharmacie  = p.id_pharmacie
    JOIN villes       vi  ON p.id_ville      = vi.id_ville
    JOIN regions      r   ON vi.id_region    = r.id_region
""", conn)
conn.close()
print(f"✓ Dataset chargé : {df.shape[0]} ventes, {df.shape[1]} colonnes")

# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================
print("\n" + "=" * 60)
print(" FEATURE ENGINEERING")
print("=" * 60)

df["date_vente"]   = pd.to_datetime(df["date_vente"])
df["mois"]         = df["date_vente"].dt.month
df["trimestre"]    = df["date_vente"].dt.quarter
df["jour_semaine"] = df["date_vente"].dt.dayofweek

le = LabelEncoder()
df["saison_enc"]     = le.fit_transform(df["saison"])
df["categorie_enc"]  = le.fit_transform(df["categorie"])
df["ville_enc"]      = le.fit_transform(df["ville"])
df["region_enc"]     = le.fit_transform(df["region"])
df["pharmacie_enc"]  = le.fit_transform(df["pharmacie"])
df["medicament_enc"] = le.fit_transform(df["medicament"])

print("✓ Features temporelles extraites")
print("✓ Variables catégorielles encodées")

df_agg = df.groupby(
    ["medicament_enc", "pharmacie_enc", "mois", "trimestre",
     "saison_enc", "categorie_enc", "ville_enc", "region_enc",
     "pfht", "stock", "marge"]
).agg(
    quantite_totale=("quantite", "sum"),
    nb_transactions=("id_vente", "count"),
    ca_total=("prix_vente", "sum")
).reset_index()

print(f"✓ Agrégation : {len(df_agg)} lignes médicament/pharmacie/mois")

# ============================================================
# 3. PRÉPARATION X / y
# ============================================================
print("\n" + "=" * 60)
print(" PRÉPARATION X / y")
print("=" * 60)

FEATURES = [
    "medicament_enc", "pharmacie_enc", "mois", "trimestre",
    "saison_enc", "categorie_enc", "ville_enc", "region_enc",
    "pfht", "stock", "marge", "nb_transactions"
]
TARGET = "quantite_totale"

X = df_agg[FEATURES]
y = df_agg[TARGET]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"✓ Train : {X_train.shape[0]} lignes | Test : {X_test.shape[0]} lignes")

# ============================================================
# 4. MODÈLE 1 — RÉGRESSION LINÉAIRE
# ============================================================
print("\n" + "=" * 60)
print(" MODÈLE 1 — RÉGRESSION LINÉAIRE")
print("=" * 60)
lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
print("✓ Régression Linéaire entraînée")

# ============================================================
# 5. MODÈLE 2 — RANDOM FOREST
# ============================================================
print("\n" + "=" * 60)
print(" MODÈLE 2 — RANDOM FOREST")
print("=" * 60)
rf = RandomForestRegressor(n_estimators=100, max_depth=10,
                            min_samples_split=5, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
print("✓ Random Forest entraîné")

# ============================================================
# 6. MODÈLE 3 — XGBOOST
# ============================================================
print("\n" + "=" * 60)
print(" MODÈLE 3 — XGBOOST")
print("=" * 60)
xgb_model = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1,
                               subsample=0.8, colsample_bytree=0.8,
                               random_state=42, verbosity=0)
xgb_model.fit(X_train, y_train)
y_pred_xgb = xgb_model.predict(X_test)
print("✓ XGBoost entraîné")

# ============================================================
# 7. GRAPHIQUES
# ============================================================
print("\n" + "=" * 60)
print(" GÉNÉRATION DES GRAPHIQUES")
print("=" * 60)

# Réel vs Prédit — Random Forest
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred_rf, alpha=0.5, color="#3498DB", label="Random Forest")
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--", lw=2, label="Prédiction parfaite")
plt.xlabel("Quantité réelle")
plt.ylabel("Quantité prédite")
plt.title("Random Forest — Réel vs Prédit")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTATS_DIR, "rf_reel_vs_predit.png"), dpi=150)
plt.close()
print("✓ rf_reel_vs_predit.png")

# Réel vs Prédit — XGBoost
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred_xgb, alpha=0.5, color="#E74C3C", label="XGBoost")
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "b--", lw=2, label="Prédiction parfaite")
plt.xlabel("Quantité réelle")
plt.ylabel("Quantité prédite")
plt.title("XGBoost — Réel vs Prédit")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTATS_DIR, "xgb_reel_vs_predit.png"), dpi=150)
plt.close()
print("✓ xgb_reel_vs_predit.png")

# Importance des features — Random Forest
feat_imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=True)
plt.figure(figsize=(10, 6))
feat_imp.plot(kind="barh", color="#2ECC71")
plt.title("Importance des features — Random Forest")
plt.xlabel("Importance")
plt.tight_layout()
plt.savefig(os.path.join(RESULTATS_DIR, "feature_importance_rf.png"), dpi=150)
plt.close()
print("✓ feature_importance_rf.png")

# Importance des features — XGBoost
feat_imp_xgb = pd.Series(xgb_model.feature_importances_, index=FEATURES).sort_values(ascending=True)
plt.figure(figsize=(10, 6))
feat_imp_xgb.plot(kind="barh", color="#E74C3C")
plt.title("Importance des features — XGBoost")
plt.xlabel("Importance")
plt.tight_layout()
plt.savefig(os.path.join(RESULTATS_DIR, "feature_importance_xgb.png"), dpi=150)
plt.close()
print("✓ feature_importance_xgb.png")

# ============================================================
# 8. SAUVEGARDE DES MODÈLES
# ============================================================
print("\n" + "=" * 60)
print(" SAUVEGARDE DES MODÈLES")
print("=" * 60)
joblib.dump(rf,        os.path.join(MODELE_DIR, "random_forest.pkl"))
joblib.dump(xgb_model, os.path.join(MODELE_DIR, "xgboost.pkl"))
joblib.dump(lr,        os.path.join(MODELE_DIR, "regression_lineaire.pkl"))
print("✓ random_forest.pkl")
print("✓ xgboost.pkl")
print("✓ regression_lineaire.pkl")

print("\n✅ ML RÉGRESSION TERMINÉ !")
print(f"\n📁 Graphiques : {RESULTATS_DIR}")
print(f"📁 Modèles    : {MODELE_DIR}")