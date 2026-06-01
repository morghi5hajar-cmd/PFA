"""
EDA COMPLET + EXPORT DES RÉSULTATS
Projet Pharmacie Maroc
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import os
import warnings

warnings.filterwarnings("ignore")

# ==============================
# CONFIGURATION
# ==============================

plt.style.use("seaborn-v0_8")
sns.set_palette("Set2")
plt.rcParams["figure.figsize"] = (12, 6)

os.makedirs("resultats", exist_ok=True)


# ==============================
# CLASSE EDA
# ==============================

class EDA_Pharmacie:

    def __init__(self, db_path="dataset/pharmacieee.db"):

        self.conn = sqlite3.connect(db_path)

        self.df = pd.read_sql_query("""
            SELECT
                v.id_vente,
                r.nom_region AS region,
                vi.nom_ville AS ville,
                p.nom AS pharmacie,
                pa.nom AS patient,
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
            JOIN villes vi      ON p.id_ville       = vi.id_ville
            JOIN regions r      ON vi.id_region     = r.id_region
            JOIN medicaments m  ON v.id_medicament  = m.id_medicament
        """, self.conn)

        print(" Données chargées")
        print(f" Nombre de ventes : {len(self.df)}")

        with open("resultats/rapport_eda.txt", "w", encoding="utf-8") as f:
            f.write("RAPPORT EDA PHARMACIE MAROC\n")
            f.write("=" * 60 + "\n\n")

    # ==============================
    # SAUVEGARDE TEXTE
    # ==============================

    def save_text(self, text):
        with open("resultats/rapport_eda.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")

    # ==============================
    # OVERVIEW
    # ==============================

    def overview(self):
        titre = "\n OVERVIEW DATASET\n"
        print(titre)
        self.save_text(titre)

        infos = f"""
Dimensions : {self.df.shape}

Colonnes :
{self.df.dtypes}

Valeurs manquantes :
{self.df.isnull().sum()}

Statistiques :
{self.df.describe()}
"""
        print(infos)
        self.save_text(infos)

    # ==============================
    # DISTRIBUTIONS
    # ==============================

    def distributions(self):

        plt.hist(self.df["quantite"], bins=10)
        plt.title("Distribution Quantité")
        plt.savefig("resultats/distribution_quantite.png")
        plt.close()

        plt.hist(self.df["prix_vente"], bins=30)
        plt.title("Distribution Prix Vente")
        plt.savefig("resultats/distribution_prix.png")
        plt.close()

        print(" Graphiques distributions sauvegardés")

    # ==============================
    # CORRÉLATION
    # ==============================

    def correlation(self):

        cols = ["quantite", "prix_vente", "pfht", "stock", "marge"]
        corr = self.df[cols].corr()

        print("\n MATRICE CORRÉLATION")
        print(corr)
        self.save_text("\nMATRICE DE CORRELATION\n")
        self.save_text(str(corr))

        plt.figure(figsize=(10, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm")
        plt.title("Matrice de Corrélation")
        plt.savefig("resultats/correlation.png")
        plt.close()

        print(" Corrélation sauvegardée")

    # ==============================
    # ANALYSE DES VENTES
    # ==============================

    def analyse_ventes(self):

        # CA par région
        ca_region = self.df.groupby("region")["prix_vente"].sum()
        print("\n CA PAR REGION")
        print(ca_region)
        self.save_text("\nCA PAR REGION\n")
        self.save_text(str(ca_region))

        ca_region.plot(kind="bar")
        plt.title("CA par Région")
        plt.ylabel("CA")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig("resultats/ca_region.png")
        plt.close()

        # CA par ville  ← NOUVEAU
        ca_ville = self.df.groupby("ville")["prix_vente"].sum().sort_values(ascending=False)
        print("\n CA PAR VILLE")
        print(ca_ville)
        self.save_text("\nCA PAR VILLE\n")
        self.save_text(str(ca_ville))

        ca_ville.plot(kind="bar", color=sns.color_palette("Set2"))
        plt.title("CA par Ville")
        plt.ylabel("CA (MAD)")
        plt.xlabel("Ville")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig("resultats/ca_ville.png")
        plt.close()

        print(" CA par ville sauvegardé")

        # Catégories
        ventes_cat = self.df["categorie"].value_counts()
        ventes_cat.plot(kind="pie", autopct="%1.1f%%")
        plt.title("Répartition Catégories")
        plt.ylabel("")
        plt.savefig("resultats/categories.png")
        plt.close()

        print(" Analyse ventes sauvegardée")

    # ==============================
    # ANALYSE TEMPORELLE
    # ==============================

    def analyse_temporelle(self):

        self.df["date_vente"] = pd.to_datetime(self.df["date_vente"])
        self.df["mois"] = self.df["date_vente"].dt.month

        # CA par mois
        ventes_mois = self.df.groupby("mois")["prix_vente"].sum()
        print("\n CA PAR MOIS")
        print(ventes_mois)
        self.save_text("\nCA PAR MOIS\n")
        self.save_text(str(ventes_mois))

        ventes_mois.plot(marker="o")
        plt.title("Evolution CA")
        plt.xlabel("Mois")
        plt.ylabel("CA")
        plt.grid(True)
        plt.savefig("resultats/ca_mois.png")
        plt.close()

        # Ventes par saison  ← NOUVEAU
        ca_saison = self.df.groupby("saison")["prix_vente"].sum().sort_values(ascending=False)
        nb_saison = self.df.groupby("saison")["id_vente"].count().sort_values(ascending=False)

        print("\n VENTES PAR SAISON")
        print(ca_saison)
        self.save_text("\nVENTES PAR SAISON\n")
        self.save_text(str(ca_saison))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        colors = sns.color_palette("Set2", len(ca_saison))

        ax1.bar(ca_saison.index, ca_saison.values, color=colors)
        ax1.set_title("CA par Saison (MAD)")
        ax1.set_xlabel("Saison")
        ax1.set_ylabel("Chiffre d'Affaires (MAD)")
        ax1.tick_params(axis="x", rotation=15)

        ax2.bar(nb_saison.index, nb_saison.values, color=colors)
        ax2.set_title("Nombre de Ventes par Saison")
        ax2.set_xlabel("Saison")
        ax2.set_ylabel("Nombre de ventes")
        ax2.tick_params(axis="x", rotation=15)

        plt.suptitle("Analyse Saisonnalité", fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.savefig("resultats/ventes_saison.png")
        plt.close()

        print(" Analyse saisonnalité sauvegardée")
        print(" Analyse temporelle sauvegardée")

    # ==============================
    # TOP MÉDICAMENTS
    # ==============================

    def top_medicaments(self):

        top_med = self.df.groupby("medicament")["prix_vente"] \
                         .sum() \
                         .sort_values(ascending=False) \
                         .head(10)

        print("\n TOP MEDICAMENTS")
        print(top_med)
        self.save_text("\nTOP MEDICAMENTS\n")
        self.save_text(str(top_med))

        top_med.plot(kind="barh")
        plt.title("Top Médicaments")
        plt.xlabel("CA")
        plt.tight_layout()
        plt.savefig("resultats/top_medicaments.png")
        plt.close()

        print(" Top médicaments sauvegardés")

    # ==============================
    # OUTLIERS
    # ==============================

    def outliers(self):

        sns.boxplot(data=self.df[["prix_vente", "pfht", "stock"]])
        plt.title("Détection Outliers")
        plt.savefig("resultats/outliers.png")
        plt.close()

        print(" Outliers sauvegardés")

    # ==============================
    # INSIGHTS
    # ==============================

    def insights(self):

        panier     = self.df["prix_vente"].mean()
        med_top    = self.df["medicament"].value_counts().idxmax()
        region_top = self.df.groupby("region")["prix_vente"].sum().idxmax()
        ville_top  = self.df.groupby("ville")["prix_vente"].sum().idxmax()
        saison_top = self.df.groupby("saison")["prix_vente"].sum().idxmax()

        texte = f"""

INSIGHTS PRINCIPAUX

Panier moyen : {panier:.2f} DH

Médicament le plus vendu : {med_top}

Région la plus rentable : {region_top}

Ville la plus rentable : {ville_top}

Saison la plus active : {saison_top}

"""
        print(texte)
        self.save_text(texte)

    # ==============================
    # EXPORT EXCEL
    # ==============================

    def export_excel(self):
        self.df.to_excel("resultats/dataset_analyse.xlsx", index=False)
        print(" Excel exporté")

    # ==============================
    # RAPPORT COMPLET
    # ==============================

    def rapport_complet(self):

        self.overview()
        self.distributions()
        self.correlation()
        self.analyse_ventes()
        self.analyse_temporelle()
        self.top_medicaments()
        self.outliers()
        self.insights()
        self.export_excel()

        print("\n EDA TERMINÉ")
        print("\n FICHIERS GÉNÉRÉS :")
        print("""
resultats/
│
├── rapport_eda.txt
├── dataset_analyse.xlsx
├── correlation.png
├── ca_region.png
├── ca_ville.png          ← NOUVEAU
├── ca_mois.png
├── ventes_saison.png     ← NOUVEAU
├── categories.png
├── top_medicaments.png
├── outliers.png
├── distribution_quantite.png
└── distribution_prix.png
""")


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    eda = EDA_Pharmacie(db_path=r"C:\Users\aitta\Downloads\PFA.rar\PFA\PFA\dataset\pharmacieee.db")

    eda.rapport_complet()

    eda.conn.close()