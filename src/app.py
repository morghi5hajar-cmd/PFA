"""
API Flask - Prévision de la demande de médicaments
Version alignée avec ML clean (sans data leakage)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib

app = Flask(__name__)
CORS(app)

import json

with open("modele/version2/stats.json")as f:
    stats = json.load(f)

STD_DEMANDE  = stats["std_demand"]
MEAN_DEMANDE = stats["mean_demand"]

print(f"Stats chargées — mean: {MEAN_DEMANDE}, std: {STD_DEMANDE}")

# ============================================================
# CHARGEMENT MODELE
# ============================================================

models = {
    "xgboost": joblib.load("modele/version2/xgb2.pkl"),
    "random_forest": joblib.load("modele/version2/rf2.pkl"),
    "linear": joblib.load("modele/version2/lr2.pkl"),
}

print("Modèles chargés")

# ============================================================
# LISTES FRONTEND
# ============================================================

PHARMACIES = [
    "Pharmacie Casablanca 1", "Pharmacie Casablanca 2",
    "Pharmacie Casablanca 3", "Pharmacie Casablanca 4",
    "Pharmacie Rabat 1",      "Pharmacie Rabat 2",
    "Pharmacie Salé 1",       "Pharmacie Salé 2",
    "Pharmacie Mohammedia 1",
    "Pharmacie Settat 1",
]

CATEGORIES = ["T1", "T2", "T3", "T4"]

VILLES = ["Casablanca", "Rabat", "Salé"]

# ============================================================
# FONCTIONS
# ============================================================

def get_saison(mois):
    if mois in [12, 1, 2]:
        return "hiver"
    elif mois in [3, 4, 5]:
        return "printemps"
    elif mois in [6, 7, 8]:
        return "ete"
    return "automne"


def get_region(ville):
    if ville in ["Rabat", "Salé"]:
        return "Rabat-Salé-Kénitra"
    return "Casablanca-Settat"

# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API OK", "status": "running"})

# ============================================================
# OPTIONS FRONTEND
# ============================================================

@app.route("/options", methods=["GET"])
def options():
    return jsonify({
        "pharmacies": PHARMACIES,
        "categories": CATEGORIES,
        "villes": VILLES,
        "mois": list(range(1, 13))
    })

# ============================================================
# PREDICT (CORRIGÉ)
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json()

        # champs obligatoires
        required = [
            "pharmacie",
            "categorie",
            "ville",
            "mois",
            "stock_moyen",
            "marge_moyenne",
            "pfht_moyen"
        ]

        for r in required:
            if r not in data:
                return jsonify({"error": f"Missing {r}"}), 400

        mois = int(data["mois"])
        trimestre = (mois - 1) // 3 + 1
        saison = get_saison(mois)
        region = get_region(data["ville"])

        # ====================================================
        #  FEATURES EXACTEMENT COMME TRAINING
        # ====================================================
        input_df = pd.DataFrame([{
            "pharmacie": data["pharmacie"],
            "categorie": data["categorie"],
            "ville": data["ville"],
            "region": region,
            "mois": mois,
            "trimestre": trimestre,
            "saison": saison,
            "stock_moyen": float(data["stock_moyen"]),
            "marge_moyenne": float(data["marge_moyenne"]),
            "pfht_moyen": float(data["pfht_moyen"])
        }])

        model_name = data.get("model", "xgboost")
        model = models[model_name]

        prediction = float(model.predict(input_df)[0])
        prediction = max(0, round(prediction, 2))


        stock_securite = round(2 * STD_DEMANDE, 2)          # = 25.48
        reappro        = round(prediction + 1.5 * STD_DEMANDE, 2)

        return jsonify({
            "status": "success",
            "quantite_prevue": prediction,
            "stock_securite": stock_securite,
            "point_reapprovisionnement": reappro,
            "model_used": model_name,
            "details": {
                "mois": mois,
                "trimestre": trimestre,
                "saison": saison,
                "region": region}
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)