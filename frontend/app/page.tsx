"use client";

import { useState } from "react";

const REGIONS_DATA: Record<string, {
  villes: Record<string, string[]>;
}> = {
  "Casablanca-Settat": {
    villes: {
      "Casablanca": [
        "Pharmacie Casablanca 1", "Pharmacie Casablanca 2",
        "Pharmacie Casablanca 3", "Pharmacie Casablanca 4"
      ],
      "Mohammedia": ["Pharmacie Mohammedia 1"],
      "Settat":     ["Pharmacie Settat 1"],
    }
  },
  "Rabat-Salé-Kénitra": {
    villes: {
      "Rabat": ["Pharmacie Rabat 1", "Pharmacie Rabat 2"],
      "Salé":  ["Pharmacie Salé 1", "Pharmacie Salé 2"],
    }
  },
};

const SAISONS_MOIS: Record<string, { mois: number; label: string }[]> = {
  "hiver":     [{ mois: 12, label: "Décembre" }, { mois: 1, label: "Janvier" }, { mois: 2, label: "Février" }],
  "printemps": [{ mois: 3, label: "Mars" }, { mois: 4, label: "Avril" }, { mois: 5, label: "Mai" }],
  "ete":       [{ mois: 6, label: "Juin" }, { mois: 7, label: "Juillet" }, { mois: 8, label: "Août" }],
  "automne":   [{ mois: 9, label: "Septembre" }, { mois: 10, label: "Octobre" }, { mois: 11, label: "Novembre" }],
};

const CATEGORIES = ["T1", "T2", "T3", "T4"];
const MODELES = [
  { value: "xgboost", label: "XGBoost" },
  { value: "random_forest", label: "Random Forest" },
  { value: "linear", label: "Régression Linéaire" },
];

function getTrimestre(mois: number) {
  if (mois <= 3) return 1;
  if (mois <= 6) return 2;
  if (mois <= 9) return 3;
  return 4;
}

interface Result {
  quantite_prevue: number;
  stock_securite: number;
  point_reapprovisionnement: number;
  model_used: string;
}

function Field({ label, value, onChange, options }: {
  label: string;
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  options: { value: string | number; label: string }[];
}) {
  return (
    <div style={{ marginBottom: "16px" }}>
      <label style={{ color: "#94a3b8", fontSize: "13px", display: "block", marginBottom: "6px" }}>{label}</label>
      <select value={value} onChange={onChange} style={{
        width: "100%", padding: "10px 14px",
        background: "rgba(255,255,255,0.08)",
        border: "1px solid rgba(255,255,255,0.15)",
        borderRadius: "10px", color: "white", fontSize: "14px", outline: "none",
      }}>
        {options.map(o => <option key={o.value} value={o.value} style={{ background: "#1e293b" }}>{o.label}</option>)}
      </select>
    </div>
  );
}

function NumInput({ label, value, onChange }: {
  label: string; value: number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <div style={{ marginBottom: "16px" }}>
      <label style={{ color: "#94a3b8", fontSize: "13px", display: "block", marginBottom: "6px" }}>{label}</label>
      <input type="number" value={value} onChange={onChange} style={{
        width: "100%", padding: "10px 14px",
        background: "rgba(255,255,255,0.08)",
        border: "1px solid rgba(255,255,255,0.15)",
        borderRadius: "10px", color: "white", fontSize: "14px",
        outline: "none", boxSizing: "border-box",
      }} />
    </div>
  );
}

export default function Home() {
  const regions = Object.keys(REGIONS_DATA);
  const [region, setRegion] = useState(regions[0]);
  const [ville, setVille] = useState(Object.keys(REGIONS_DATA[regions[0]].villes)[0]);
  const [pharmacie, setPharmacyE] = useState(Object.values(REGIONS_DATA[regions[0]].villes)[0][0]);
  const [saison, setSaison] = useState("hiver");
  const [mois, setMois] = useState(12);
  const [categorie, setCategorie] = useState("T1");
  const [model, setModel] = useState("xgboost");
  const [stockMoyen, setStockMoyen] = useState(1000);
  const [margeMoyenne, setMargeMoyenne] = useState(27);
  const [pfhtMoyen, setPfhtMoyen] = useState(50);
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const villesDisponibles = Object.keys(REGIONS_DATA[region].villes);
  const pharmaciesDisponibles = REGIONS_DATA[region].villes[ville] || [];
  const moisDisponibles = SAISONS_MOIS[saison];

  const handleRegion = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const r = e.target.value;
    const premVille = Object.keys(REGIONS_DATA[r].villes)[0];
    setRegion(r);
    setVille(premVille);
    setPharmacyE(REGIONS_DATA[r].villes[premVille][0]);
  };

  const handleVille = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const v = e.target.value;
    setVille(v);
    setPharmacyE(REGIONS_DATA[region].villes[v][0]);
  };

  const handleSaison = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const s = e.target.value;
    setSaison(s);
    setMois(SAISONS_MOIS[s][0].mois);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pharmacie, categorie, ville, region, mois,
          trimestre: getTrimestre(mois), saison,
          stock_moyen: stockMoyen,
          marge_moyenne: margeMoyenne,
          pfht_moyen: pfhtMoyen,
          model,
        }),
      });
      const data = await res.json();
      if (data.error) setError(data.error);
      else setResult(data);
    } catch {
      setError("Impossible de contacter l'API. Vérifiez que Flask tourne sur le port 5000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)",
      fontFamily: "'Segoe UI', sans-serif",
      padding: "40px 20px",
    }}>
      <div style={{ textAlign: "center", marginBottom: "40px" }}>
        <div style={{
          display: "inline-block",
          background: "linear-gradient(90deg, #38bdf8, #818cf8)",
          borderRadius: "50px", padding: "6px 20px",
          fontSize: "12px", color: "white", fontWeight: 600,
          letterSpacing: "2px", textTransform: "uppercase", marginBottom: "16px",
        }}>ENSIAS PFA 2024-2025</div>
        <h1 style={{ fontSize: "clamp(24px, 4vw, 40px)", fontWeight: 800, color: "white", margin: "0 0 8px" }}>
          Prévision de la Demande
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "16px", margin: 0 }}>
          Pharmacies Marocaines — Système intelligent de prédiction ML
        </p>
      </div>

      <div style={{ maxWidth: "900px", margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
        <div style={{
          background: "rgba(255,255,255,0.05)",
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: "20px", padding: "32px",
        }}>
          <h2 style={{ color: "white", fontSize: "18px", fontWeight: 700, marginBottom: "24px" }}>
            Paramètres de prédiction
          </h2>

          <Field label="Région" value={region} onChange={handleRegion}
            options={regions.map(r => ({ value: r, label: r }))} />
          <Field label="Ville" value={ville} onChange={handleVille}
            options={villesDisponibles.map(v => ({ value: v, label: v }))} />
          <Field label="Pharmacie" value={pharmacie} onChange={e => setPharmacyE(e.target.value)}
            options={pharmaciesDisponibles.map(p => ({ value: p, label: p }))} />
          <Field label="Catégorie" value={categorie} onChange={e => setCategorie(e.target.value)}
            options={CATEGORIES.map(c => ({ value: c, label: c }))} />
          <Field label="Saison" value={saison} onChange={handleSaison}
            options={Object.keys(SAISONS_MOIS).map(s => ({ value: s, label: s }))} />
          <Field label="Mois" value={mois} onChange={e => setMois(parseInt(e.target.value))}
            options={moisDisponibles.map(m => ({ value: m.mois, label: m.label }))} />

          <NumInput label="Stock moyen (boîtes)" value={stockMoyen} onChange={e => setStockMoyen(parseFloat(e.target.value))} />
          <NumInput label="Marge moyenne (%)" value={margeMoyenne} onChange={e => setMargeMoyenne(parseFloat(e.target.value))} />
          <NumInput label="PFHT moyen (DH)" value={pfhtMoyen} onChange={e => setPfhtMoyen(parseFloat(e.target.value))} />

          <Field label="Modèle ML" value={model} onChange={e => setModel(e.target.value)} options={MODELES} />

          <button onClick={handleSubmit} disabled={loading} style={{
            width: "100%", padding: "14px",
            background: loading ? "rgba(56,189,248,0.3)" : "linear-gradient(90deg, #38bdf8, #818cf8)",
            border: "none", borderRadius: "12px", color: "white",
            fontSize: "16px", fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
          }}>
            {loading ? "Prédiction en cours..." : "Prédire la demande"}
          </button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {error && (
            <div style={{
              background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.3)",
              borderRadius: "16px", padding: "20px", color: "#fca5a5", fontSize: "14px",
            }}>⚠️ {error}</div>
          )}

          {!result && !error && (
            <div style={{
              background: "rgba(255,255,255,0.03)", border: "1px dashed rgba(255,255,255,0.1)",
              borderRadius: "20px", padding: "60px 20px", textAlign: "center", color: "#475569",
            }}>
              <div style={{ fontSize: "48px", marginBottom: "16px" }}>💊</div>
              <p>Remplissez les paramètres et lancez la prédiction</p>
            </div>
          )}

          {result && (
            <>
              <div style={{
                background: "linear-gradient(135deg, rgba(56,189,248,0.15), rgba(129,140,248,0.15))",
                border: "1px solid rgba(56,189,248,0.3)",
                borderRadius: "20px", padding: "28px", textAlign: "center",
              }}>
                <p style={{ color: "#94a3b8", fontSize: "13px", margin: "0 0 8px", textTransform: "uppercase", letterSpacing: "1px" }}>
                  Quantité prévue
                </p>
                <div style={{
                  fontSize: "64px", fontWeight: 800,
                  background: "linear-gradient(90deg, #38bdf8, #818cf8)",
                  WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", lineHeight: 1,
                }}>
                  {result.quantite_prevue}
                </div>
                <p style={{ color: "#64748b", fontSize: "14px", margin: "8px 0 0" }}>
                  boîtes / mois • Modèle : {result.model_used}
                </p>
              </div>

              <div style={{
                background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "16px", padding: "20px 24px",
                display: "flex", justifyContent: "space-between", alignItems: "center",
              }}>
                <div>
                  <p style={{ color: "#94a3b8", fontSize: "13px", margin: "0 0 4px" }}>Stock de sécurité</p>
                  <p style={{ color: "#fbbf24", fontSize: "24px", fontWeight: 700, margin: 0 }}>
                    {result.stock_securite} boîtes
                  </p>
                </div>
                <div style={{ fontSize: "32px" }}>🛡️</div>
              </div>

              <div style={{
                background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "16px", padding: "20px 24px",
                display: "flex", justifyContent: "space-between", alignItems: "center",
              }}>
                <div>
                  <p style={{ color: "#94a3b8", fontSize: "13px", margin: "0 0 4px" }}>Point de réapprovisionnement</p>
                  <p style={{ color: "#34d399", fontSize: "24px", fontWeight: 700, margin: 0 }}>
                    {result.point_reapprovisionnement} boîtes
                  </p>
                </div>
                <div style={{ fontSize: "32px" }}>📦</div>
              </div>

              <div style={{
                background: "rgba(52,211,153,0.08)", border: "1px solid rgba(52,211,153,0.2)",
                borderRadius: "16px", padding: "16px 20px", color: "#6ee7b7", fontSize: "13px", lineHeight: 1.6,
              }}>
                <strong>💡 Recommandation :</strong> Commandez dès que votre stock
                descend sous <strong>{result.point_reapprovisionnement} boîtes</strong>.
                Maintenez un stock de sécurité de <strong>{result.stock_securite} boîtes</strong>.
              </div>
            </>
          )}
        </div>
      </div>

      <p style={{ textAlign: "center", color: "#334155", fontSize: "12px", marginTop: "40px" }}>
        Hajar Morghi & Douae Ait Taleb — ENSIAS 2SCL 2024-2025
      </p>
    </main>
  );
}