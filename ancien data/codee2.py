import sqlite3
import random
import pandas as pd
from datetime import datetime, timedelta

# =========================
# CONFIGURATION
# =========================
DB_PATH = "dataset/pharmacieee.db"
EXCEL_PATH = "dataset/fichier/ref-des-medicaments-cnops-2014.xlsx"

BOITES_PAR_PERSONNE = 12.26
DEPENSE_PAR_PERSONNE = 500
NOMBRE_PATIENTS = 500
ANNEE = 2024


# =========================
# FONCTIONS
# =========================

def consommation():
    """Génère une consommation annuelle réaliste"""
    return max(1, int(random.gauss(BOITES_PAR_PERSONNE, 3)))


def calcul_marge(prix, cat):
    """Calcule la marge selon la catégorie"""
    
    if cat == "T1":
        return prix * 0.3393
    
    elif cat == "T2":
        return prix * 0.2974
    
    elif cat == "T3":
        return 300
    
    else:
        return 400


def get_saison(mois):
    """Retourne la saison"""

    if mois in [12, 1, 2]:
        return "hiver"

    elif mois in [6, 7, 8]:
        return "été"

    else:
        return "printemps/automne"


def categoriser_medicament(prix):
    """
    Catégorisation selon le prix
    """

    if prix <= 165:
        return "T1"

    elif prix <= 588:
        return "T2"

    elif prix <= 1756:
        return "T3"

    else:
        return "T4"


# =========================
# CONNEXION SQLITE
# =========================

try:

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # =========================
    # SUPPRESSION DES TABLES
    # =========================

    cursor.execute("DROP TABLE IF EXISTS ventes")
    cursor.execute("DROP TABLE IF EXISTS patients")
    cursor.execute("DROP TABLE IF EXISTS pharmacies")
    cursor.execute("DROP TABLE IF EXISTS medicaments")
    cursor.execute("DROP TABLE IF EXISTS grossistes")
    cursor.execute("DROP TABLE IF EXISTS villes")
    cursor.execute("DROP TABLE IF EXISTS regions")

    # =========================
    # CREATION DES TABLES
    # =========================

    # REGIONS
    cursor.execute("""
        CREATE TABLE regions (
            id_region INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_region TEXT NOT NULL
        )
    """)

    # VILLES
    cursor.execute("""
        CREATE TABLE villes (
            id_ville INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_ville TEXT NOT NULL,
            id_region INTEGER,
            FOREIGN KEY (id_region) REFERENCES regions(id_region)
        )
    """)

    # GROSSISTES
    cursor.execute("""
        CREATE TABLE grossistes (
            id_grossiste INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_grossiste TEXT NOT NULL,
            id_region INTEGER,
            capacite_livraison INTEGER,
            FOREIGN KEY (id_region) REFERENCES regions(id_region)
        )
    """)

    # MEDICAMENTS
    cursor.execute("""
        CREATE TABLE medicaments (
            id_medicament INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            nom TEXT NOT NULL,
            dci TEXT,
            forme TEXT,
            presentation TEXT,
            categorie TEXT,
            pfht REAL
        )
    """)

    # PHARMACIES
    cursor.execute("""
        CREATE TABLE pharmacies (
            id_pharmacie INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            id_ville INTEGER,
            id_region INTEGER,
            id_grossiste INTEGER,
            stock INTEGER,
            marge REAL,
            FOREIGN KEY (id_ville) REFERENCES villes(id_ville),
            FOREIGN KEY (id_region) REFERENCES regions(id_region),
            FOREIGN KEY (id_grossiste) REFERENCES grossistes(id_grossiste)
        )
    """)

    # PATIENTS
    cursor.execute("""
        CREATE TABLE patients (
            id_patient INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            id_ville INTEGER,
            id_pharmacie INTEGER,
            consommation_annuelle_boites INTEGER,
            depense_annuelle REAL,
            FOREIGN KEY (id_ville) REFERENCES villes(id_ville),
            FOREIGN KEY (id_pharmacie) REFERENCES pharmacies(id_pharmacie)
        )
    """)

    # VENTES
    cursor.execute("""
        CREATE TABLE ventes (
            id_vente INTEGER PRIMARY KEY AUTOINCREMENT,
            id_patient INTEGER,
            id_pharmacie INTEGER,
            id_medicament INTEGER,
            quantite INTEGER,
            prix_vente REAL,
            categorie TEXT,
            date_vente DATE,
            saison TEXT,
            FOREIGN KEY (id_patient) REFERENCES patients(id_patient),
            FOREIGN KEY (id_pharmacie) REFERENCES pharmacies(id_pharmacie),
            FOREIGN KEY (id_medicament) REFERENCES medicaments(id_medicament)
        )
    """)

    # =========================
    # INSERTION REGIONS
    # =========================

    regions = [
        "Rabat-Salé-Kénitra",
        "Casablanca-Settat"
    ]

    cursor.executemany(
        "INSERT INTO regions (nom_region) VALUES (?)",
        [(r,) for r in regions]
    )

    # =========================
    # INSERTION VILLES
    # =========================

    villes = [
        ("Rabat", 1),
        ("Kénitra", 1),
        ("Salé", 1),
        ("Témara", 1),
        ("Casablanca", 2),
        ("Mohammedia", 2),
        ("El Jadida", 2),
        ("Settat", 2)
    ]

    cursor.executemany(
        "INSERT INTO villes (nom_ville, id_region) VALUES (?,?)",
        villes
    )

    # =========================
    # INSERTION GROSSISTES
    # =========================

    grossistes = [
        ("Grossiste Rabat", 1, 5000),
        ("Grossiste Casa", 2, 4500)
    ]

    cursor.executemany(
        """
        INSERT INTO grossistes
        (nom_grossiste, id_region, capacite_livraison)
        VALUES (?,?,?)
        """,
        grossistes
    )

    # =========================
    # IMPORT FICHIER EXCEL
    # =========================

    print("Chargement du fichier Excel...")

    df = pd.read_excel(EXCEL_PATH)

    # Supprimer lignes sans nom
    df = df.dropna(subset=["NOM"])

    # Garder colonnes utiles
    df = df[
        [
            "CODE",
            "NOM",
            "DCI1",
            "FORME",
            "PRESENTATION",
            "PPV"
        ]
    ]

    # Supprimer doublons
    df = df.drop_duplicates(subset=["NOM"])

    medicaments_data = []

    for _, row in df.iterrows():

        try:

            prix = float(row["PPV"])

            categorie = categoriser_medicament(prix)

            medicaments_data.append(
                (
                    str(row["CODE"]),
                    str(row["NOM"]),
                    str(row["DCI1"]),
                    str(row["FORME"]),
                    str(row["PRESENTATION"]),
                    categorie,
                    prix
                )
            )

        except:
            continue

    # Insertion médicaments
    cursor.executemany(
        """
        INSERT INTO medicaments
        (code, nom, dci, forme, presentation, categorie, pfht)
        VALUES (?,?,?,?,?,?,?)
        """,
        medicaments_data
    )

    print(f"{len(medicaments_data)} médicaments réels ajoutés")

    # =========================
    # PHARMACIES
    # =========================

    cursor.execute(
        "SELECT id_ville, nom_ville, id_region FROM villes"
    )

    villes_data = cursor.fetchall()

    pharmacies_data = []

    for id_ville, nom_ville, id_region in villes_data:

        stock = random.randint(800, 1200)

        marge = random.uniform(20, 30)

        pharmacies_data.append(
            (
                f"Pharmacie {nom_ville}",
                id_ville,
                id_region,
                id_region,
                stock,
                round(marge, 2)
            )
        )

    cursor.executemany(
        """
        INSERT INTO pharmacies
        (nom, id_ville, id_region, id_grossiste, stock, marge)
        VALUES (?,?,?,?,?,?)
        """,
        pharmacies_data
    )

    # =========================
    # PATIENTS
    # =========================

    patients_data = []

    for i in range(NOMBRE_PATIENTS):

        cursor.execute("SELECT id_ville FROM villes")
        villes_list = cursor.fetchall()

        id_ville = random.choice(villes_list)[0]

        cursor.execute("""
            SELECT id_pharmacie
            FROM pharmacies
            WHERE id_ville = ?
        """, (id_ville,))

        pharmacies_list = cursor.fetchall()

        id_pharmacie = random.choice(pharmacies_list)[0]

        patients_data.append(
            (
                f"Patient_{i+1}",
                id_ville,
                id_pharmacie,
                consommation(),
                DEPENSE_PAR_PERSONNE
            )
        )

    cursor.executemany(
        """
        INSERT INTO patients
        (
            nom,
            id_ville,
            id_pharmacie,
            consommation_annuelle_boites,
            depense_annuelle
        )
        VALUES (?,?,?,?,?)
        """,
        patients_data
    )

    # =========================
    # VENTES
    # =========================

    cursor.execute("""
        SELECT
            id_patient,
            id_ville,
            id_pharmacie,
            consommation_annuelle_boites
        FROM patients
    """)

    patients_list = cursor.fetchall()

    cursor.execute("""
        SELECT
            id_medicament,
            nom,
            categorie,
            pfht
        FROM medicaments
    """)

    meds = cursor.fetchall()

    ventes_data = []

    date_debut = datetime(ANNEE, 1, 1)

    for id_patient, id_ville, id_pharmacie, nb_achats in patients_list:

        for _ in range(int(nb_achats)):

            id_med, nom, cat, prix = random.choice(meds)

            quantite = random.choices(
                [1, 2, 3],
                weights=[70, 25, 5]
            )[0]

            marge = calcul_marge(prix, cat)

            prix_vente = (prix + marge) * quantite

            date_vente = date_debut + timedelta(
                days=random.randint(0, 365)
            )

            saison = get_saison(date_vente.month)

            ventes_data.append(
                (
                    id_patient,
                    id_pharmacie,
                    id_med,
                    quantite,
                    round(prix_vente, 2),
                    cat,
                    date_vente.strftime("%Y-%m-%d"),
                    saison
                )
            )

    # INSERTION PAR BATCH
    batch_size = 500

    for i in range(0, len(ventes_data), batch_size):

        batch = ventes_data[i:i + batch_size]

        cursor.executemany(
            """
            INSERT INTO ventes
            (
                id_patient,
                id_pharmacie,
                id_medicament,
                quantite,
                prix_vente,
                categorie,
                date_vente,
                saison
            )
            VALUES (?,?,?,?,?,?,?,?)
            """,
            batch
        )

    # =========================
    # COMMIT
    # =========================

    conn.commit()

    print("Base de données créée avec succès")

except sqlite3.Error as e:

    print(f"Erreur SQLite : {e}")

    if conn:
        conn.rollback()

except Exception as e:

    print(f"Erreur générale : {e}")

    if conn:
        conn.rollback()

finally:

    if conn:
        conn.close()

    print("Connexion fermée")