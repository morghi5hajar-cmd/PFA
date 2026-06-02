"""
API Flask — Prévision de la demande de médicaments
Projet PFA — ENSIAS 2024-2025
Hajar MORGHI — Doua AIT TALEB
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Autorise les requêtes depuis Next.js

# ============================================================
# CHARGEMENT DES MODÈLES
# ============================================================
MODELE_DIR = r"C:\Users\aitta\Downloads\PFA.rar\PFA\PFA\modele\version2"
models = {
    "random_forest": joblib.load(os.path.join(MODELE_DIR, "rf.pkl")),
    "xgboost":       joblib.load(os.path.join(MODELE_DIR, "xgb.pkl")),
    "linear":        joblib.load(os.path.join(MODELE_DIR, "lr.pkl")),
}

print("✅ Modèles chargés avec succès")

# ============================================================
# VALEURS ACCEPTÉES
# ============================================================

PHARMACIES = [
    "Pharmacie Casablanca 1", "Pharmacie Casablanca 2",
    "Pharmacie Casablanca 3", "Pharmacie Casablanca 4",
    "Pharmacie Rabat 1", "Pharmacie Rabat 2",
    "Pharmacie Salé 1", "Pharmacie Salé 2",
    "Pharmacie Mohammedia 1", "Pharmacie Settat 1"
]

CATEGORIES  = ["T1", "T2", "T3", "T4"]
VILLES      = ["Casablanca", "Rabat", "Salé", "Mohammedia", "Settat"]
REGIONS     = ["Casablanca-Settat", "Rabat-Salé-Kénitra"]
SAISONS     = ["hiver", "printemps", "ete", "automne"]

# ============================================================
# ROUTE — ACCUEIL
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "API Prévision Médicaments — ENSIAS PFA 2024-2025",
        "status": "running",
        "endpoints": {
            "/predict": "POST — Prédire la quantité vendue",
            "/models":  "GET  — Liste des modèles disponibles",
            "/health":  "GET  — Vérifier l'état de l'API"
        }
    })

# ============================================================
# ROUTE — HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "models_loaded": list(models.keys())
    })

# ============================================================
# ROUTE — LISTE DES MODÈLES
# ============================================================

@app.route("/models", methods=["GET"])
def get_models():
    return jsonify({
        "models": list(models.keys()),
        "default": "random_forest"
    })

# ============================================================
# ROUTE — PRÉDICTION
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # ── Validation des champs requis ──────────────────────
        required = ["pharmacie", "categorie", "ville", "region",
                    "mois", "trimestre", "saison",
                    "stock_moyen", "marge_moyenne", "pfht_moyen"]

        for field in required:
            if field not in data:
                return jsonify({"error": f"Champ manquant : {field}"}), 400

        # ── Choisir le modèle ─────────────────────────────────
        model_name = data.get("model", "random_forest")
        if model_name not in models:
            return jsonify({"error": f"Modèle inconnu : {model_name}"}), 400

        model = models[model_name]

        # ── Construire le DataFrame d'entrée ──────────────────
        input_df = pd.DataFrame([{
            "pharmacie":      data["pharmacie"],
            "categorie":      data["categorie"],
            "ville":          data["ville"],
            "region":         data["region"],
            "mois":           int(data["mois"]),
            "trimestre":      int(data["trimestre"]),
            "saison":         data["saison"],
            "nb_transactions": int(data.get("nb_transactions", 10)),
            "ca_total":       float(data.get("ca_total", 500)),
            "stock_moyen":    float(data["stock_moyen"]),
            "marge_moyenne":  float(data["marge_moyenne"]),
            "pfht_moyen":     float(data["pfht_moyen"]),
        }])

        # ── Prédiction ────────────────────────────────────────
        prediction = model.predict(input_df)[0]
        prediction = max(0, round(float(prediction), 2))

        # ── Recommandation stock ──────────────────────────────
        stock_securite     = round(prediction * 0.2, 2)
        point_reappro      = round(prediction + stock_securite, 2)

        return jsonify({
            "status":              "success",
            "model_used":          model_name,
            "quantite_prevue":     prediction,
            "stock_securite":      stock_securite,
            "point_reapprovision": point_reappro,
            "input":               data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# ROUTE — OPTIONS DISPONIBLES (pour le frontend)
# ============================================================

@app.route("/options", methods=["GET"])
def options():
    return jsonify({
        "pharmacies": PHARMACIES,
        "categories": CATEGORIES,
        "villes":     VILLES,
        "regions":    REGIONS,
        "saisons":    SAISONS,
        "mois":       list(range(1, 13)),
        "trimestres": [1, 2, 3, 4]
    })

# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)