"use client";

import { useState } from "react";

// ============================================================
// DONNÉES
// ============================================================
const REGIONS_DATA: Record<string, { villes: Record<string, string[]> }> = {
  "Casablanca-Settat": {
    villes: {
      "Casablanca": ["Pharmacie Casablanca 1", "Pharmacie Casablanca 2", "Pharmacie Casablanca 3", "Pharmacie Casablanca 4"],
      "Mohammedia": ["Pharmacie Mohammedia 1"],
      "Settat": ["Pharmacie Settat 1"],
    }
  },
  "Rabat-Salé-Kénitra": {
    villes: {
      "Rabat": ["Pharmacie Rabat 1", "Pharmacie Rabat 2"],
      "Salé": ["Pharmacie Salé 1", "Pharmacie Salé 2"],
    }
  },
};

const SAISONS_MOIS: Record<string, { mois: number; label: string }[]> = {
  "hiver": [{ mois: 12, label: "Décembre" }, { mois: 1, label: "Janvier" }, { mois: 2, label: "Février" }],
  "printemps": [{ mois: 3, label: "Mars" }, { mois: 4, label: "Avril" }, { mois: 5, label: "Mai" }],
  "ete": [{ mois: 6, label: "Juin" }, { mois: 7, label: "Juillet" }, { mois: 8, label: "Août" }],
  "automne": [{ mois: 9, label: "Septembre" }, { mois: 10, label: "Octobre" }, { mois: 11, label: "Novembre" }],
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

// Gradient b l-khdar l-gham9 w l-fatih
const GRAD = "linear-gradient(90deg, #064e3b, #059669)";

const labelStyle: React.CSSProperties = { color: "#475569", fontSize: "13px", fontWeight: 600, display: "block", marginBottom: "6px" };
const inputStyle: React.CSSProperties = {
  width: "100%", padding: "10px 14px", background: "#ffffff",
  border: "1px solid #cbd5e1", borderRadius: "10px", color: "#0f172a",
  fontSize: "14px", outline: "none", boxSizing: "border-box",
};

function Field({ label, value, onChange, options }: {
  label: string; value: string | number;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  options: { value: string | number; label: string }[];
}) {
  return (
    <div style={{ marginBottom: "16px" }}>
      <label style={labelStyle}>{label}</label>
      <select value={value} onChange={onChange} style={inputStyle}>
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
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
      <label style={labelStyle}>{label}</label>
      <input type="number" value={value} onChange={onChange} style={inputStyle} />
    </div>
  );
}

export default function Home() {
  const [page, setPage] = useState<"accueil" | "login" | "predict">("accueil");
  const [authMode, setAuthMode] = useState<"connexion" | "inscription">("connexion");

  const [nom, setNom] = useState("");
  const [email, setEmail] = useState("");
  const [mdp, setMdp] = useState("");

  const regions = Object.keys(REGIONS_DATA);
  const [region, setRegion] = useState(regions[0]);
  const [ville, setVille] = useState(Object.keys(REGIONS_DATA[regions[0]].villes)[0]);
  const [pharmacie, setPharmacyE] = useState(Object.values(REGIONS_DATA[regions[0]].villes)[0][0]);
  const [saison, setSaison] = useState("hiver");
  const [mois, setMois] = useState(12);
  const [categorie, setCategorie] = useState("T1");
  const [model, setModel] = useState("random_forest");
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
    const sv = e.target.value;
    setSaison(sv);
    setMois(SAISONS_MOIS[sv][0].mois);
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
          pharmacie,
          categorie,
          ville,
          mois,
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

  const Nav = ({ showCta = true }: { showCta?: boolean }) => (
    <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 48px", background: "white", borderBottom: "1px solid #eef0f2" }}>
      <div onClick={() => setPage("accueil")} style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}>
        <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: GRAD, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px", color: "white", fontWeight: "bold" }}>✚</div>
        <span style={{ fontWeight: 700, fontSize: "16px", color: "#0f172a" }}>PharmaPredict</span>
      </div>
      {showCta && (
        <button onClick={() => setPage(page === "accueil" ? "login" : "accueil")} style={{ padding: "8px 18px", background: "transparent", border: "1px solid #cbd5e1", borderRadius: "8px", color: "#334155", fontSize: "13px", fontWeight: 600, cursor: "pointer" }}>
          {page === "accueil" ? "Se connecter" : "Accueil"}
        </button>
      )}
    </nav>
  );

  if (page === "accueil") {
    return (
      <main style={{ minHeight: "100vh", background: "#ffffff", fontFamily: "'Segoe UI', system-ui, sans-serif", display: "flex", flexDirection: "column" }}>
        <Nav />
        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", padding: "50px 24px" }}>
          <h1 style={{ fontSize: "clamp(32px, 5vw, 52px)", fontWeight: 800, color: "#0f172a", margin: "0 0 20px", lineHeight: 1.1, maxWidth: "800px" }}>
            Prévision intelligente de la<br />
            <span style={{ background: GRAD, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>demande de médicaments</span>
          </h1>
          <p style={{ fontSize: "18px", color: "#64748b", maxWidth: "600px", margin: "0 0 36px", lineHeight: 1.6 }}>
            Optimisez la gestion des stocks de votre pharmacie grâce au Machine Learning. Anticipez la demande, évitez les ruptures et le surstock.
          </p>
          <button onClick={() => setPage("login")} style={{ padding: "15px 40px", background: GRAD, border: "none", borderRadius: "10px", color: "white", fontSize: "16px", fontWeight: 700, cursor: "pointer" }}>
            Commencer
          </button>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px", marginTop: "70px", maxWidth: "850px", width: "100%" }}>
            {[
              ["Précision 78.6%", "Random Forest · R² = 0.786 · MAE = 3.91 boîtes"],
              ["Données réelles", "Calibré sur les statistiques marocaines"],
              ["Temps réel", "Prédiction instantanée par pharmacie"],
            ].map(([titre, desc], i) => (
              <div key={i} style={{ padding: "24px", background: "#fafbfc", border: "1px solid #eef0f2", borderRadius: "14px", textAlign: "left" }}>
                <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#0f172a", margin: "0 0 6px" }}>{titre}</h3>
                <p style={{ fontSize: "14px", color: "#64748b", margin: 0, lineHeight: 1.5 }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    );
  }

  if (page === "login") {
    return (
      <main style={{ minHeight: "100vh", background: "#f8fafc", fontFamily: "'Segoe UI', system-ui, sans-serif", display: "flex", flexDirection: "column" }}>
        <Nav showCta={false} />
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "40px 24px" }}>
          <div style={{ width: "100%", maxWidth: "420px", background: "white", border: "1px solid #eef0f2", borderRadius: "20px", padding: "36px", boxShadow: "0 4px 20px rgba(0,0,0,0.05)" }}>
            <div style={{ textAlign: "center", marginBottom: "26px" }}>
              <div style={{ width: "48px", height: "48px", borderRadius: "12px", background: GRAD, display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: "24px", color: "white", fontWeight: "bold", marginBottom: "14px" }}>✚</div>
              <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#0f172a", margin: "0 0 6px" }}>
                {authMode === "connexion" ? "Bienvenue" : "Créer un compte"}
              </h1>
              <p style={{ color: "#64748b", fontSize: "14px", margin: 0 }}>
                {authMode === "connexion" ? "Connectez-vous pour continuer" : "Inscrivez-vous pour commencer"}
              </p>
            </div>

            <div style={{ display: "flex", background: "#f1f5f9", borderRadius: "10px", padding: "4px", marginBottom: "24px" }}>
              {(["connexion", "inscription"] as const).map(m => (
                <button key={m} onClick={() => setAuthMode(m)} style={{
                  flex: 1, padding: "9px", borderRadius: "8px", border: "none", cursor: "pointer",
                  fontSize: "14px", fontWeight: 600,
                  background: authMode === m ? "white" : "transparent",
                  color: authMode === m ? "#0f172a" : "#64748b",
                  boxShadow: authMode === m ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
                }}>
                  {m === "connexion" ? "Connexion" : "Inscription"}
                </button>
              ))}
            </div>

            {authMode === "inscription" && (
              <div style={{ marginBottom: "16px" }}>
                <label style={labelStyle}>Nom complet</label>
                <input type="text" value={nom} onChange={e => setNom(e.target.value)} placeholder="Votre nom" style={inputStyle} />
              </div>
            )}
            <div style={{ marginBottom: "16px" }}>
              <label style={labelStyle}>Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="exemple@pharmacie.ma" style={inputStyle} />
            </div>
            <div style={{ marginBottom: "22px" }}>
              <label style={labelStyle}>Mot de passe</label>
              <input type="password" value={mdp} onChange={e => setMdp(e.target.value)} placeholder="••••••••" style={inputStyle} />
            </div>

            <button onClick={() => setPage("predict")} style={{
              width: "100%", padding: "13px", background: GRAD, border: "none",
              borderRadius: "10px", color: "white", fontSize: "15px", fontWeight: 700, cursor: "pointer",
            }}>
              {authMode === "connexion" ? "Se connecter" : "S'inscrire"}
            </button>

            <p style={{ textAlign: "center", color: "#64748b", fontSize: "13px", marginTop: "18px", marginBottom: 0 }}>
              {authMode === "connexion" ? "Pas encore de compte ? " : "Déjà un compte ? "}
              <span onClick={() => setAuthMode(authMode === "connexion" ? "inscription" : "connexion")} style={{ color: "#059669", fontWeight: 600, cursor: "pointer" }}>
                {authMode === "connexion" ? "S'inscrire" : "Se connecter"}
              </span>
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main style={{ minHeight: "100vh", background: "#f8fafc", fontFamily: "'Segoe UI', system-ui, sans-serif" }}>
      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 48px", background: "white", borderBottom: "1px solid #eef0f2" }}>
        <div onClick={() => setPage("accueil")} style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}>
          <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: GRAD, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px", color: "white", fontWeight: "bold" }}>✚</div>
          <span style={{ fontWeight: 700, fontSize: "16px", color: "#0f172a" }}>PharmaPredict</span>
        </div>
        <button onClick={() => setPage("login")} style={{ padding: "8px 18px", background: "transparent", border: "1px solid #cbd5e1", borderRadius: "8px", color: "#334155", fontSize: "13px", fontWeight: 600, cursor: "pointer" }}>Déconnexion</button>
      </nav>

      <div style={{ padding: "40px 24px" }}>
        <div style={{ textAlign: "center", marginBottom: "36px" }}>
          <h1 style={{ fontSize: "clamp(24px, 4vw, 34px)", fontWeight: 800, color: "#0f172a", margin: "0 0 8px" }}>Prévision de la demande</h1>
          <p style={{ color: "#64748b", fontSize: "16px", margin: 0 }}>Saisissez les paramètres pour obtenir une prédiction</p>
        </div>

        <div style={{ maxWidth: "920px", margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
          <div style={{ background: "white", border: "1px solid #eef0f2", borderRadius: "18px", padding: "30px", boxShadow: "0 1px 3px rgba(0,0,0,0.04)" }}>
            <h2 style={{ color: "#0f172a", fontSize: "17px", fontWeight: 700, marginTop: 0, marginBottom: "22px" }}>Paramètres de prédiction</h2>
            <Field label="Région" value={region} onChange={handleRegion} options={regions.map(r => ({ value: r, label: r }))} />
            <Field label="Ville" value={ville} onChange={handleVille} options={villesDisponibles.map(v => ({ value: v, label: v }))} />
            <Field label="Pharmacie" value={pharmacie} onChange={e => setPharmacyE(e.target.value)} options={pharmaciesDisponibles.map(p => ({ value: p, label: p }))} />
            <Field label="Catégorie" value={categorie} onChange={e => setCategorie(e.target.value)} options={CATEGORIES.map(c => ({ value: c, label: c }))} />
            <Field label="Saison" value={saison} onChange={handleSaison} options={Object.keys(SAISONS_MOIS).map(sv => ({ value: sv, label: sv }))} />
            <Field label="Mois" value={mois} onChange={e => setMois(parseInt(e.target.value))} options={moisDisponibles.map(m => ({ value: m.mois, label: m.label }))} />
            <NumInput label="Stock moyen (boîtes)" value={stockMoyen} onChange={e => setStockMoyen(parseFloat(e.target.value))} />
            <NumInput label="Marge moyenne (%)" value={margeMoyenne} onChange={e => setMargeMoyenne(parseFloat(e.target.value))} />
            <NumInput label="PFHT moyen (DH)" value={pfhtMoyen} onChange={e => setPfhtMoyen(parseFloat(e.target.value))} />
            <Field label="Modèle ML" value={model} onChange={e => setModel(e.target.value)} options={MODELES} />
            <button onClick={handleSubmit} disabled={loading} style={{
              width: "100%", padding: "14px",
              background: loading ? "#cbd5e1" : GRAD,
              border: "none", borderRadius: "12px", color: "white", fontSize: "16px", fontWeight: 700,
              cursor: loading ? "not-allowed" : "pointer",
            }}>
              {loading ? "Prédiction en cours..." : "Prédire la demande"}
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {error && (
              <div style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "16px", padding: "20px", color: "#dc2626", fontSize: "14px" }}>{error}</div>
            )}
            {!result && !error && (
              <div style={{ background: "white", border: "1px dashed #cbd5e1", borderRadius: "18px", padding: "60px 20px", textAlign: "center", color: "#94a3b8" }}>
                <p>Remplissez les paramètres et lancez la prédiction</p>
              </div>
            )}
            {result && (
              <>
                <div style={{ background: "linear-gradient(135deg, #f0fdf4, #e6f4ea)", border: "1px solid #bbf7d0", borderRadius: "18px", padding: "28px", textAlign: "center" }}>
                  <p style={{ color: "#64748b", fontSize: "13px", margin: "0 0 8px", textTransform: "uppercase", letterSpacing: "1px" }}>Quantité prévue</p>
                  <div style={{ fontSize: "64px", fontWeight: 800, background: GRAD, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", lineHeight: 1 }}>
                    {result.quantite_prevue}
                  </div>
                  <p style={{ color: "#64748b", fontSize: "14px", margin: "8px 0 0" }}>boîtes / mois • Modèle : {result.model_used}</p>
                </div>
                <div style={{ background: "white", border: "1px solid #eef0f2", borderRadius: "16px", padding: "20px 24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <p style={{ color: "#64748b", fontSize: "13px", margin: "0 0 4px" }}>Stock de sécurité</p>
                    <p style={{ color: "#059669", fontSize: "24px", fontWeight: 700, margin: 0 }}>{result.stock_securite} boîtes</p>
                  </div>
                </div>
                <div style={{ background: "white", border: "1px solid #eef0f2", borderRadius: "16px", padding: "20px 24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <p style={{ color: "#64748b", fontSize: "13px", margin: "0 0 4px" }}>Point de réapprovisionnement</p>
                    <p style={{ color: "#064e3b", fontSize: "24px", fontWeight: 700, margin: 0 }}>{result.point_reapprovisionnement} boîtes</p>
                  </div>
                </div>
                <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "16px", padding: "16px 20px", color: "#15803d", fontSize: "13px", lineHeight: 1.6 }}>
                  <strong>Recommandation :</strong> Commandez dès que votre stock descend sous <strong>{result.point_reapprovisionnement} boîtes</strong>. Maintenez un stock de sécurité de <strong>{result.stock_securite} boîtes</strong>.
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}