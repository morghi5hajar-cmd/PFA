"""
API Flask - Prévision de la demande de médicaments
PFA ENSIAS
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os

app = Flask(__name__)
CORS(app)

# ============================================================
# CHARGEMENT MODELE
# ============================================================

MODEL_PATH = r"C:\Users\aitta\Downloads\PFA.rar\PFA\PFA\modele\version2\xgb.pkl"

model = joblib.load(MODEL_PATH)

print("✅ Modèle XGBoost chargé")

# ============================================================
# DONNÉES POUR LE FRONTEND
# ============================================================

PHARMACIES = [
    "Pharmacie Casablanca 1",
    "Pharmacie Casablanca 2",
    "Pharmacie Casablanca 3",
    "Pharmacie Casablanca 4",
    "Pharmacie Rabat 1",
    "Pharmacie Rabat 2",
    "Pharmacie Salé 1",
    "Pharmacie Salé 2",
    "Pharmacie Mohammedia 1",
    "Pharmacie Settat 1"
]

CATEGORIES = ["T1", "T2", "T3", "T4"]

VILLES = [
    "Casablanca",
    "Rabat",
    "Salé",
    "Mohammedia",
    "Settat"
]

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
    return jsonify({
        "message": "API Prévision Médicaments",
        "status": "running"
    })


# ============================================================
# HEALTH
# ============================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": "XGBoost"
    })


# ============================================================
# OPTIONS
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
# PREDICT
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()

        required_fields = [
            "pharmacie",
            "categorie",
            "ville",
            "mois",
            "stock_moyen",
            "marge_moyenne",
            "pfht_moyen"
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Champ manquant : {field}"
                }), 400

        mois = int(data["mois"])

        trimestre = (mois - 1) // 3 + 1
        saison = get_saison(mois)
        region = get_region(data["ville"])

        input_df = pd.DataFrame([{
            "pharmacie": data["pharmacie"],
            "categorie": data["categorie"],
            "ville": data["ville"],
            "region": region,
            "mois": mois,
            "trimestre": trimestre,
            "saison": saison,

            # valeurs par défaut
            "nb_transactions": 10,
            "ca_total": 500,

            "stock_moyen": float(data["stock_moyen"]),
            "marge_moyenne": float(data["marge_moyenne"]),
            "pfht_moyen": float(data["pfht_moyen"])
        }])

        prediction = float(model.predict(input_df)[0])

        prediction = max(0, round(prediction, 2))

        stock_securite = round(prediction * 0.20, 2)

        point_reapprovisionnement = round(
            prediction + stock_securite,
            2
        )

        return jsonify({

            "status": "success",

            "quantite_prevue": prediction,

            "stock_securite": stock_securite,

            "point_reapprovisionnement":
                point_reapprovisionnement,

            "details": {
                "saison": saison,
                "trimestre": trimestre,
                "region": region
            }

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )