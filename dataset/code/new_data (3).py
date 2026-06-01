import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "pharmaci.db"

BOITES_PAR_PERSONNE = 12.26
DEPENSE_PAR_PERSONNE = 500
ANNEE = 2024

# Villes : (id_region, id_grossiste, nb_pharmacies, nb_patients)
# Grossistes :
#   1 COOPHARMA    (Rabat + Salé)
#   2 PHARMA 5     (Casablanca)
#   3 MAGHREB PHARMA (Mohammedia + Settat)
VILLES_CONFIG = {
    "Rabat":       (1, 1,  2,  20),
    "Salé":        (1, 1,  2,  40),
    "Casablanca":  (2, 2,  4, 120),
    "Mohammedia":  (2, 3,  1,  20),
    "Settat":      (2, 3,  1,  25),
}

# 1000 médicaments simulés 
# T1 (PFHT <= 165 DH)        : 80% du volume
# T2 (166-588 DH)            : 15% du volume
# T3 (589-1756 DH)           :  4% du volume
# T4 (> 1756 DH)             :  1% du volume
NB_MEDS = {"T1": 800, "T2": 150, "T3": 40, "T4": 10}

# Noms de base vrais pour générer les 1000 médicaments
NOMS_T1 = [
    "Paracétamol", "Amoxicilline", "Ibuprofène", "Doliprane", "Metformine",
    "Oméprazole", "Cétirizine", "Vitamine C", "Loratadine", "Azithromycine",
    "Fluconazole", "Metronidazole", "Antalgique", "Aspirine", "Doliprane",
    "Spasfon", "Smecta", "Toplexil", "Voltarène", "Zyrtec"
]
NOMS_T2 = [
    "Ventoline", "Insuline", "Atorvastatine", "Losartan", "Amlodipine",
    "Metoprolol", "Furosémide", "Lisinopril", "Simvastatine", "Ramipril"
]
NOMS_T3 = [
    "Rituximab", "Trastuzumab", "Bevacizumab", "Cetuximab", "Imatinib"
]
NOMS_T4 = [
    "Sutent", "Glivec", "Votrient", "Tykerb", "Novoseven"
]

DOSAGES = ["100mg", "200mg", "250mg", "500mg", "1g", "5mg", "10mg", "20mg", "40mg", "50mg"]
FORMES  = ["cp", "gél", "sol", "inj", "susp", "crème", "patch", "spray"]


def gen_medicaments():
    meds = []
    compteurs = {}
    for cat, nb in NB_MEDS.items():
        if cat == "T1":
            noms_base = NOMS_T1
            pmin, pmax = 8, 165
        elif cat == "T2":
            noms_base = NOMS_T2
            pmin, pmax = 166, 588
        elif cat == "T3":
            noms_base = NOMS_T3
            pmin, pmax = 589, 1756
        else:
            noms_base = NOMS_T4
            pmin, pmax = 1757, 4000

        for i in range(nb):
            base = random.choice(noms_base)
            if base not in compteurs:
                compteurs[base] = 0
            compteurs[base] += 1
            dosage = random.choice(DOSAGES)
            forme  = random.choice(FORMES)
            nom    = f"{base} {dosage} {forme} ({compteurs[base]})"
            pfht   = round(random.uniform(pmin, pmax), 2)
            meds.append((nom, cat, pfht))
    return meds


def consommation():
    """12.26 boites/an en moyenne — Ministère de la Santé Maroc"""
    return max(1, int(random.gauss(BOITES_PAR_PERSONNE, 3)))


def calcul_marge(prix, cat):
    """
    Marges réglementées — Source : Cour des comptes Maroc
    T1 : +33.93% | T2 : +29.74% | T3 : +300 DH | T4 : +400 DH
    """
    if cat == "T1":
        return prix * 0.3393
    elif cat == "T2":
        return prix * 0.2974
    elif cat == "T3":
        return 300
    else:
        return 400


def get_saison(mois):
    if mois in [12, 1, 2]:
        return "hiver"
    elif mois in [6, 7, 8]:
        return "été"
    else:
        return "printemps/automne"


conn = None
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    #  SUPPRESSION 
    cursor.execute("DROP VIEW IF EXISTS vue_globale")
    for t in ["approvisionnement", "ventes", "patients", "pharmacies",
              "medicaments", "grossistes", "villes", "regions"]:
        cursor.execute(f"DROP TABLE IF EXISTS {t}")

    # CRÉATION DES TABLES 
    cursor.execute("""
        CREATE TABLE regions (
            id_region  INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_region TEXT NOT NULL
        )""")

    cursor.execute("""
        CREATE TABLE villes (
            id_ville  INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_ville TEXT NOT NULL,
            id_region INTEGER,
            FOREIGN KEY (id_region) REFERENCES regions(id_region)
        )""")

    cursor.execute("""
        CREATE TABLE grossistes (
            id_grossiste       INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_grossiste      TEXT NOT NULL,
            id_region          INTEGER,
            capacite_livraison INTEGER,
            FOREIGN KEY (id_region) REFERENCES regions(id_region)
        )""")

    cursor.execute("""
        CREATE TABLE medicaments (
            id_medicament INTEGER PRIMARY KEY AUTOINCREMENT,
            nom           TEXT NOT NULL,
            categorie     TEXT,
            pfht          REAL
        )""")

    cursor.execute("""
        CREATE TABLE pharmacies (
            id_pharmacie INTEGER PRIMARY KEY AUTOINCREMENT,
            nom          TEXT NOT NULL,
            id_ville     INTEGER,
            id_grossiste INTEGER,
            stock        INTEGER,
            marge        REAL,
            FOREIGN KEY (id_ville)     REFERENCES villes(id_ville),
            FOREIGN KEY (id_grossiste) REFERENCES grossistes(id_grossiste)
        )""")

    cursor.execute("""
        CREATE TABLE patients (
            id_patient                   INTEGER PRIMARY KEY AUTOINCREMENT,
            nom                          TEXT NOT NULL,
            id_ville                     INTEGER,
            id_pharmacie                 INTEGER,
            consommation_annuelle_boites INTEGER,
            depense_annuelle             REAL,
            FOREIGN KEY (id_ville)     REFERENCES villes(id_ville),
            FOREIGN KEY (id_pharmacie) REFERENCES pharmacies(id_pharmacie)
        )""")

    cursor.execute("""
        CREATE TABLE ventes (
            id_vente      INTEGER PRIMARY KEY AUTOINCREMENT,
            id_patient    INTEGER,
            id_pharmacie  INTEGER,
            id_medicament INTEGER,
            quantite      INTEGER,
            prix_vente    REAL,
            categorie     TEXT,
            date_vente    DATE,
            saison        TEXT,
            FOREIGN KEY (id_patient)    REFERENCES patients(id_patient),
            FOREIGN KEY (id_pharmacie)  REFERENCES pharmacies(id_pharmacie),
            FOREIGN KEY (id_medicament) REFERENCES medicaments(id_medicament)
        )""")

    cursor.execute("""
        CREATE TABLE approvisionnement (
            id_appro        INTEGER PRIMARY KEY AUTOINCREMENT,
            id_grossiste    INTEGER NOT NULL,
            id_pharmacie    INTEGER NOT NULL,
            id_medicament   INTEGER NOT NULL,
            quantite_livree INTEGER NOT NULL,
            date_livraison  DATE    NOT NULL,
            statut          TEXT    DEFAULT 'livré',
            FOREIGN KEY (id_grossiste)  REFERENCES grossistes(id_grossiste),
            FOREIGN KEY (id_pharmacie)  REFERENCES pharmacies(id_pharmacie),
            FOREIGN KEY (id_medicament) REFERENCES medicaments(id_medicament)
        )""")

    # RÉGIONS 
    cursor.executemany("INSERT INTO regions (nom_region) VALUES (?)", [
        ("Rabat-Salé-Kénitra",),
        ("Casablanca-Settat",)
    ])
    print(" 2 régions insérées")

    # GROSSISTES 
    # 1 grossiste par zone géographique
    cursor.executemany(
        "INSERT INTO grossistes (nom_grossiste, id_region, capacite_livraison) VALUES (?,?,?)",
        [
            ("COOPHARMA Rabat",        1, 50000),   # Rabat + Salé
            ("PHARMA 5 Casablanca",    2, 80000),   # Casablanca
            ("MAGHREB PHARMA",         2, 40000),   # Mohammedia + Settat
        ]
    )
    print(" 3 grossistes insérés (COOPHARMA, PHARMA 5, MAGHREB PHARMA)")

    # VILLES 
    for nom, (id_region, *_) in VILLES_CONFIG.items():
        cursor.execute("INSERT INTO villes (nom_ville, id_region) VALUES (?,?)",
                       (nom, id_region))
    print(" 5 villes insérées (Rabat, Salé, Casablanca, Mohammedia, Settat)")


    # MÉDICAMENTS 
    meds_list = gen_medicaments()
    cursor.executemany(
        "INSERT INTO medicaments (nom, categorie, pfht) VALUES (?,?,?)",
        meds_list
    )
    cursor.execute("SELECT id_medicament, nom, categorie, pfht FROM medicaments")
    meds_inseres = cursor.fetchall()
    print(f" {len(meds_inseres)} médicaments insérés (T1:800, T2:150, T3:40, T4:10)")

    #  PHARMACIES 
    cursor.execute("SELECT id_ville, nom_ville FROM villes")
    villes_data = cursor.fetchall()

    nb_pharmacies_total = 0
    pharmacies_par_ville = {}

    for id_ville, nom_ville in villes_data:
        _, id_grossiste, nb_pharma, _ = VILLES_CONFIG[nom_ville]
        ids_pharma = []
        for i in range(nb_pharma):
            cursor.execute(
                "INSERT INTO pharmacies (nom, id_ville, id_grossiste, stock, marge) VALUES (?,?,?,?,?)",
                (f"Pharmacie {nom_ville} {i+1}", id_ville, id_grossiste,
                 random.randint(500, 2000), round(random.uniform(20, 34), 2))
            )
            ids_pharma.append(cursor.lastrowid)
            nb_pharmacies_total += 1
        pharmacies_par_ville[id_ville] = ids_pharma

    print(f" {nb_pharmacies_total} pharmacies insérées")
    print("   Casa:4 | Rabat:2 | Salé:2 | Mohammedia:1 | Settat:1")

    # PATIENTS
    patients_data = []
    for id_ville, nom_ville in villes_data:
        _, _, _, nb_patients = VILLES_CONFIG[nom_ville]
        for i in range(nb_patients):
            patients_data.append((
                f"Patient_{nom_ville}_{i+1}",
                id_ville,
                random.choice(pharmacies_par_ville[id_ville]),
                consommation(),
                DEPENSE_PAR_PERSONNE
            ))

    cursor.executemany("""
        INSERT INTO patients
        (nom, id_ville, id_pharmacie, consommation_annuelle_boites, depense_annuelle)
        VALUES (?,?,?,?,?)
    """, patients_data)
    print(f" {len(patients_data)} patients insérés")
    print("   Casa:120 | Salé:40 | Rabat:20 | Mohammedia:20 | Settat:25")

    # VENTES 
    cursor.execute("""
        SELECT id_patient, id_ville, id_pharmacie, consommation_annuelle_boites
        FROM patients
    """)
    patients_list = cursor.fetchall()

    date_debut = datetime(ANNEE, 1, 1)
    ventes_data = []

    for id_patient, id_ville, id_pharmacie, nb_achats in patients_list:
        for _ in range(int(nb_achats)):
            id_med, nom, cat, prix = random.choice(meds_inseres)
            quantite = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
            prix_vente = round((prix + calcul_marge(prix, cat)) * quantite, 2)
            date_vente = date_debut + timedelta(days=random.randint(0, 364))
            ventes_data.append((
                id_patient, id_pharmacie, id_med,
                quantite, prix_vente, cat,
                date_vente.strftime("%Y-%m-%d"),
                get_saison(date_vente.month)
            ))

    for i in range(0, len(ventes_data), 500):
        cursor.executemany("""
            INSERT INTO ventes
            (id_patient, id_pharmacie, id_medicament, quantite, prix_vente,
             categorie, date_vente, saison)
            VALUES (?,?,?,?,?,?,?,?)
        """, ventes_data[i:i+500])
    print(f" {len(ventes_data)} ventes insérées")

    #  APPROVISIONNEMENT 
    # 1 livraison par mois par pharmacie
    cursor.execute("SELECT id_pharmacie, id_grossiste FROM pharmacies")
    appro_data = []
    for id_pharmacie, id_grossiste in cursor.fetchall():
        for mois in range(1, 13):
            date_liv = datetime(ANNEE, mois, random.randint(1, 28)).strftime("%Y-%m-%d")
            appro_data.append((
                id_grossiste,
                id_pharmacie,
                random.choice(meds_inseres)[0],
                random.randint(50, 300),
                date_liv,
                "livré"
            ))

    cursor.executemany("""
        INSERT INTO approvisionnement
        (id_grossiste, id_pharmacie, id_medicament, quantite_livree, date_livraison, statut)
        VALUES (?,?,?,?,?,?)
    """, appro_data)
    print(f" {len(appro_data)} approvisionnements insérés")

    #  VUE GLOBALE 
    cursor.execute("""
        CREATE VIEW vue_globale AS
        SELECT
            v.id_vente,
            v.date_vente,
            v.saison,
            v.quantite,
            v.prix_vente,
            v.categorie,
            m.nom        AS medicament,
            m.pfht,
            p.nom        AS pharmacie,
            p.stock,
            p.marge,
            vi.nom_ville AS ville,
            r.nom_region AS region,
            pat.nom      AS patient
        FROM ventes v
        JOIN medicaments  m   ON v.id_medicament = m.id_medicament
        JOIN pharmacies   p   ON v.id_pharmacie  = p.id_pharmacie
        JOIN villes       vi  ON p.id_ville      = vi.id_ville
        JOIN regions      r   ON vi.id_region    = r.id_region
        JOIN patients     pat ON v.id_patient    = pat.id_patient
    """)
    print(" Vue globale créée")

    
    conn.commit()
    print("\n Base de données créée avec succès")
    print(f"   Régions     : 2")
    print(f"   Villes      : 5")
    print(f"   Grossistes  : 3")
    print(f"   Médicaments : {len(meds_inseres)}")
    print(f"   Pharmacies  : {nb_pharmacies_total}")
    print(f"   Patients    : {len(patients_data)}")
    print(f"   Ventes      : {len(ventes_data)}")
    print(f"   Appros      : {len(appro_data)}")

except sqlite3.Error as e:
    print(f" Erreur SQLite : {e}")
    if conn:
        conn.rollback()

except Exception as e:
    print(f" Erreur générale : {e}")
    if conn:
        conn.rollback()

finally:
    if conn:
        conn.close()
        print("Connexion fermée")
