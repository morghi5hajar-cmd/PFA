# =========================================
#  PRÉDICTION DEMANDE PHARMACIES
# =========================================

import pandas as pd
import numpy as np
import sqlite3

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb

# =========================================
# 1. CHARGEMENT DONNÉES
# =========================================

conn = sqlite3.connect("dataset/pharmacieee.db")

df = pd.read_sql_query("""
SELECT 
    v.date_vente,
    v.quantite,
    v.prix_vente,
    v.id_pharmacie,
    p.nom AS pharmacie,
    vi.nom_ville AS ville,
    m.categorie,
    m.pfht
FROM ventes v
JOIN pharmacies p ON v.id_pharmacie = p.id_pharmacie
JOIN villes vi ON p.id_ville = vi.id_ville
JOIN medicaments m ON v.id_medicament = m.id_medicament
""", conn)

df["date_vente"] = pd.to_datetime(df["date_vente"])

# =========================================
# 2. FEATURE ENGINEERING
# =========================================

df["ca"] = df["prix_vente"]
df["cout"] = df["pfht"] * df["quantite"]
df["profit"] = df["ca"] - df["cout"]

df["mois"] = df["date_vente"].dt.month
df["jour"] = df["date_vente"].dt.day
df["jour_semaine"] = df["date_vente"].dt.dayofweek

# =========================================
# 3. PREPARATION ML
# =========================================

features = ["quantite", "pfht", "mois", "jour_semaine"]
target = "quantite"

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

# =========================================
# 4. MODELES
# =========================================

# Linear Regression
lr = LinearRegression()
lr.fit(X_train, y_train)
pred_lr = lr.predict(X_test)

# Random Forest
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
pred_rf = rf.predict(X_test)

# XGBoost
xgb_model = xgb.XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6
)

xgb_model.fit(X_train, y_train)
pred_xgb = xgb_model.predict(X_test)

# =========================================
# 5. EVALUATION
# =========================================

def evaluate(name, y_true, y_pred):
    print("\n", name)
    print("MAE :", mean_absolute_error(y_true, y_pred))
    print("RMSE:", np.sqrt(mean_squared_error(y_true, y_pred)))
    print("R2  :", r2_score(y_true, y_pred))

evaluate("Linear Regression", y_test, pred_lr)
evaluate("Random Forest", y_test, pred_rf)
evaluate("XGBoost", y_test, pred_xgb)

# =========================================
# 6. COMPARAISON MODELES
# =========================================

results = pd.DataFrame({
    "Model": ["Linear Regression", "Random Forest", "XGBoost"],
    "MAE": [
        mean_absolute_error(y_test, pred_lr),
        mean_absolute_error(y_test, pred_rf),
        mean_absolute_error(y_test, pred_xgb)
    ],
    "RMSE": [
        np.sqrt(mean_squared_error(y_test, pred_lr)),
        np.sqrt(mean_squared_error(y_test, pred_rf)),
        np.sqrt(mean_squared_error(y_test, pred_xgb))
    ]
})

print("\n COMPARAISON MODELES")
print(results.sort_values("MAE"))

# =========================================
# 7. VISUALISATION SIMPLE
# =========================================

import matplotlib.pyplot as plt

plt.figure(figsize=(10,5))
plt.plot(y_test[:100].values, label="Réel")
plt.plot(pred_xgb[:100], label="XGBoost")
plt.legend()
plt.title("Prédiction vs Réel")
plt.show()

# =========================================
# 8. CONCLUSION
# =========================================

print("""
 CONCLUSION :
- Le modèle XGBoost est généralement le plus performant
- Le système permet de prédire la demande des médicaments
- Objectif : réduire rupture de stock et surstock
""")