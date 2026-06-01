# %%
# 1. INTRODUCTION
#Analyse des ventes pharmaceutiques pour comprendre la performance des pharmacies,
#la consommation des patients et la chaîne logistique.

# %%
# 2. IMPORTS & DATA LOADING

# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import os
import os
os.makedirs("resultats", exist_ok=True)
import warnings

warnings.filterwarnings("ignore")

plt.style.use("seaborn-v0_8")
sns.set_palette("Set2")
plt.rcParams["figure.figsize"] = (12, 6)

os.makedirs("resultats", exist_ok=True)

# %%
conn = sqlite3.connect("new_pharmaci.db")

df = pd.read_sql_query("""
SELECT
    v.id_vente,
    r.nom_region AS region,
    vi.nom_ville AS ville,
    pa.nom AS patient,
    p.nom AS pharmacie,
    p.id_grossiste,   
    m.nom AS medicament,
    m.categorie,
    v.quantite,
    v.prix_vente,
    v.date_vente,
    v.saison,
    m.pfht,
    p.stock,
    p.marge
FROM ventes v
JOIN patients pa    ON v.id_patient    = pa.id_patient
JOIN pharmacies p   ON v.id_pharmacie  = p.id_pharmacie
JOIN villes vi      ON p.id_ville      = vi.id_ville
JOIN regions r      ON vi.id_region    = r.id_region
JOIN medicaments m  ON v.id_medicament = m.id_medicament
""", conn)

df.head()

# %%
# =========================
# 3. FEATURE ENGINEERING
# =========================

# %%
df["ca"] = df["prix_vente"]

df["cout"] = df["pfht"] * df["quantite"]

df["profit"] = df["ca"] - df["cout"]

df["prix_unitaire"] = df["ca"] / df["quantite"]

df["marge_unitaire"] = df["prix_unitaire"] - df["pfht"]

df["taux_marge"] = (df["marge_unitaire"] / df["pfht"]) * 100

# %%
print("CA total :", df["ca"].sum())
print("Profit total :", df["profit"].sum())
print("Nombre ventes :", df["id_vente"].count())
print("Panier moyen :", df["ca"].mean())

# %%
# =========================
# 4. EDA (EXPLORATION)
# =========================

# %%
print("SHAPE :", df.shape)
print("\nMissing values :\n", df.isnull().sum())
print("\nDescription :\n", df.describe())

# %%
#distributions
plt.hist(df["quantite"], bins=15)
plt.title("Distribution Quantité")
plt.savefig("resultats/distribution_quantite.png", dpi=300, bbox_inches="tight")
plt.show()

plt.hist(df["ca"], bins=30)
plt.title("Distribution CA")
plt.savefig("resultats/distribution_ca.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
#  CORRELATION
cols = ["quantite", "prix_vente", "pfht", "ca", "profit"]
sns.heatmap(df[cols].corr(), annot=True, cmap="coolwarm")
plt.title("Corrélation")
plt.savefig("resultats/correlation.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
# =========================
# 5. BUSINESS ANALYSIS
# =========================

# %%
#Ventes géographiques
#CA par région
df.groupby("region")["ca"].sum().sort_values().plot(kind="bar")
plt.title("CA par région")
plt.xticks(rotation=45)
plt.savefig("resultats/ca_region.png", dpi=300, bbox_inches="tight")
plt.show()


# %%
#CA par ville
df.groupby("ville")["ca"].sum().sort_values(ascending=False).head(10).plot(kind="bar")
plt.title("Top villes")
plt.xticks(rotation=45)
plt.savefig("resultats/top_villes.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
pivot = df.pivot_table(
    index="ville",
    columns="categorie",
    values="ca",
    aggfunc="sum",
    fill_value=0
)

sns.heatmap(pivot, cmap="YlOrRd")
plt.title("CA Ville × Catégorie")
plt.savefig("resultats/heatmap_ville_categorie.png", dpi=300, bbox_inches="tight")

plt.show()

# %%
#Produits

# %%
df.groupby("medicament")["ca"].sum().sort_values(ascending=False).head(10).plot(kind="barh")
plt.title("Top médicaments")
plt.savefig("resultats/top_medicaments.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
sns.boxplot(data=df, x="categorie", y="prix_unitaire")
plt.yscale("log")
plt.title("Prix par catégorie")
plt.savefig("resultats/prix_categorie.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
pareto = df.groupby("medicament")["ca"].sum().sort_values(ascending=False)
pareto_cumsum = pareto.cumsum() / pareto.sum()

pareto_cumsum.plot()
plt.title("Courbe de Pareto (80/20)")
plt.grid()
plt.savefig("resultats/pareto.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
df.groupby("categorie")["profit"].sum().sort_values().plot(kind="bar")
plt.title("Profit par catégorie")
plt.xticks(rotation=45)
plt.savefig("resultats/profit_categorie.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
#Temps
#CA par mois
df["date_vente"] = pd.to_datetime(df["date_vente"])
df["mois"] = df["date_vente"].dt.month

df.groupby("mois")["ca"].sum().plot(marker="o")
plt.title("CA par mois")
plt.grid()
plt.savefig("resultats/ca_mois.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
df.groupby(["saison", "categorie"])["ca"].sum().unstack().plot(kind="bar")
plt.title("CA par saison et catégorie")
plt.xticks(rotation=30)
plt.savefig("resultats/ca_saison_categorie.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
#Clients
#Top patients
df.groupby("patient")["ca"].sum().sort_values(ascending=False).head(10).plot(kind="bar")
plt.title("Top patients VIP")
plt.xticks(rotation=45)
plt.savefig("resultats/top_patients.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
fidelite = df.groupby("patient").agg(
    nb_achats=("id_vente", "count"),
    ca=("ca", "sum"),
    debut=("date_vente", "min"),
    fin=("date_vente", "max")
)

fidelite["jours_activite"] = (
    pd.to_datetime(fidelite["fin"]) - pd.to_datetime(fidelite["debut"])
).dt.days

fidelite["frequence_jours"] = fidelite["jours_activite"] / fidelite["nb_achats"]

fidelite.head()


# %%
fidelite["segment"] = pd.cut(
    fidelite["ca"],
    bins=[0, 2000, 5000, float("inf")],
    labels=["Bronze", "Silver", "Gold"]
)

fidelite["segment"].value_counts().plot(kind="bar")
plt.title("Segments clients")
plt.savefig("resultats/segments_clients.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
import numpy as np
def gini(array):
    array = np.sort(array)
    n = len(array)
    index = np.arange(1, n+1)
    return (np.sum((2 * index - n - 1) * array)) / (n * np.sum(array))

gini_value = gini(df.groupby("patient")["ca"].sum().values)

print("Indice de Gini :", gini_value)

# %%
# =========================
# 6. SUPPLY CHAIN ANALYSIS
# =========================

# %%
#Pharmacies

# %%
df_pharma = df.copy()

perf_pharma = df_pharma.groupby("pharmacie").agg(
    ca=("ca", "sum"),
    profit=("profit", "sum"),
    nb_ventes=("id_vente", "count"),
    quantite_totale=("quantite", "sum"),
    stock_moyen=("stock", "mean")
)

perf_pharma["ca_moyen_vente"] = perf_pharma["ca"] / perf_pharma["nb_ventes"]

perf_pharma.sort_values("ca", ascending=False).head(10)

perf_pharma["ca"].sort_values().plot(kind="bar")
plt.title("Performance des pharmacies (CA)")
plt.xticks(rotation=45)
plt.savefig("resultats/performance_pharmacies.png", dpi=300, bbox_inches="tight")
plt.show()

# %%

kpi_pharma = df.groupby("pharmacie").agg(
    ca=("ca", "sum"),
    profit=("profit", "sum"),
    nb_ventes=("id_vente", "count"),
    stock_moyen=("stock", "mean")
)

kpi_pharma["marge_moyenne"] = (kpi_pharma["profit"] / kpi_pharma["ca"]) * 100

kpi_pharma.sort_values("marge_moyenne", ascending=False).head(10)

kpi_pharma["marge_moyenne"].sort_values().plot(kind="bar")
plt.title("Marge moyenne par pharmacie (%)")
plt.xticks(rotation=45)
plt.savefig("resultats/marge_moyenne_pharmacies.png", dpi=300, bbox_inches="tight")
plt.show()

#On mesure la rentabilité réelle des pharmacies via la marge moyenne, 
# qui indique la part du profit dans le chiffre d’affaires.

# %%
kpi_ville = df.groupby("ville").agg(
    ca=("ca", "sum"),
    profit=("profit", "sum"),
    nb_ventes=("id_vente", "count")
)

kpi_ville["rentabilite"] = (kpi_ville["profit"] / kpi_ville["ca"]) * 100

kpi_ville.sort_values("rentabilite", ascending=False)

kpi_ville["rentabilite"].sort_values().plot(kind="bar")
plt.title("Rentabilité par ville (%)")
plt.xticks(rotation=45)
plt.savefig("resultats/rentabilite_ville.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
#grossistes

# %%
query_grossistes = """
SELECT 
    g.nom_grossiste,
    COUNT(DISTINCT p.id_pharmacie) as nb_pharmacies,
    SUM(a.quantite_livree) as total_livre,
    g.capacite_livraison,
    (SUM(a.quantite_livree)*100.0/g.capacite_livraison) as taux_utilisation
FROM grossistes g
JOIN approvisionnement a ON g.id_grossiste = a.id_grossiste
JOIN pharmacies p ON a.id_pharmacie = p.id_pharmacie
GROUP BY g.id_grossiste
"""

df_grossistes = pd.read_sql_query(query_grossistes, conn)

df_grossistes["livre_par_pharmacie"] = (
    df_grossistes["total_livre"] / df_grossistes["nb_pharmacies"]
)
df_grossistes.set_index("nom_grossiste")["taux_utilisation"].plot(kind="bar")
plt.title("Taux d'utilisation des grossistes") 
plt.savefig("resultats/taux_utilisation_grossistes.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
#COMPARAISON GROSSISTES vs PHARMACIES pour voir si la chaîne logistique influence la performance.

df["ca"] = df["prix_vente"]
df["cout"] = df["pfht"] * df["quantite"]
df["profit"] = df["ca"] - df["cout"]

df_gross_pharma = df.groupby(["id_grossiste", "pharmacie"]).agg(
    ca=("ca", "sum"),
    profit=("profit", "sum"),
    nb_ventes=("id_vente", "count")
).reset_index()

gross_perf = df.groupby("id_grossiste").agg(
    ca=("ca", "sum"),
    profit=("profit", "sum"),
    nb_ventes=("id_vente", "count")
)

gross_perf["rentabilite"] = (gross_perf["profit"] / gross_perf["ca"]) * 100

gross_perf["rentabilite"].plot(kind="bar")
plt.title("Rentabilité par grossiste")
plt.xticks(rotation=0) 
plt.savefig("resultats/rentabilite_grossistes.png", dpi=300, bbox_inches="tight")
plt.show()



# %%
#risque rupture

# %%
seuil_stock = df["stock"].quantile(0.25)

ruptures = df[df["stock"] < seuil_stock]

ruptures.groupby("pharmacie")["stock"].min().sort_values()

ruptures["pharmacie"].value_counts().plot(kind="bar")
plt.title("Pharmacies à risque de rupture")
plt.xticks(rotation=45) 
plt.savefig("resultats/rupture_pharmacies.png", dpi=300, bbox_inches="tight")
plt.show()

# %%
# =========================
# 7. INSIGHTS BUSINESS
# =========================

# %%
print("CA total :", df["ca"].sum())
print("Profit total :", df["profit"].sum())

print("Ville top :", df.groupby("ville")["ca"].sum().idxmax())
print("Région top :", df.groupby("region")["ca"].sum().idxmax())
print("Produit top :", df.groupby("medicament")["ca"].sum().idxmax())
print("Client VIP :", df.groupby("patient")["ca"].sum().idxmax())

# %%





