"""
Extracteur de Données - Rapports CNOPS/CNSS/ANAM
Projet PFA - AI-Based Drug Demand Forecasting

Ce script facilite l'extraction de données depuis les rapports PDF officiels
"""

import re
import pandas as pd

# ============================================================================
# TEMPLATES D'EXTRACTION
# ============================================================================

def extract_cnops_categories(pdf_text):
    """
    Extrait les proportions par catégorie depuis rapport CNOPS
    
    Recherche des patterns type:
    "Antibiotiques: 18.5% des prescriptions"
    "Cardiovasculaires: 22.3%"
    """
    
    categories_map = {
        'antibiotique': 'Antibiotiques',
        'analgésique': 'Analgésiques',
        'antalgique': 'Analgésiques',
        'antihistaminique': 'Antihistaminiques',
        'antidiabétique': 'Antidiabétiques',
        'diabète': 'Antidiabétiques',
        'antiparasitaire': 'Antiparasitaires',
        'cardiovasculaire': 'Cardiovasculaires',
        'cardio': 'Cardiovasculaires',
    }
    
    results = {}
    
    # Pattern: "Catégorie: XX.X%"
    pattern = r'([a-zé-]+)\s*:?\s*(\d+[.,]\d+)\s*%'
    
    for match in re.finditer(pattern, pdf_text.lower()):
        category_raw = match.group(1)
        percentage = float(match.group(2).replace(',', '.'))
        
        # Normaliser le nom de catégorie
        for key, standard_name in categories_map.items():
            if key in category_raw:
                results[standard_name] = percentage / 100
                break
    
    return results


def extract_regional_distribution(pdf_text):
    """
    Extrait la distribution régionale depuis rapports CNSS
    
    Recherche patterns:
    "Casablanca-Settat: 32.1%"
    "Rabat-Salé-Kénitra: 18.4%"
    """
    
    regions_keywords = {
        'casablanca': 'Casablanca-Settat',
        'rabat': 'Rabat-Salé-Kénitra',
        'marrakech': 'Marrakech-Safi',
        'fès': 'Fès-Meknès',
        'fes': 'Fès-Meknès',
        'tanger': 'Tanger-Tétouan-Al Hoceïma',
        'agadir': 'Souss-Massa',
        'souss': 'Souss-Massa',
    }
    
    results = {}
    
    # Pattern similaire
    pattern = r'([a-zé-]+(?:-[a-zé-]+)?)\s*:?\s*(\d+[.,]\d+)\s*%'
    
    for match in re.finditer(pattern, pdf_text.lower()):
        region_raw = match.group(1)
        percentage = float(match.group(2).replace(',', '.'))
        
        for key, standard_name in regions_keywords.items():
            if key in region_raw:
                results[standard_name] = percentage / 100
                break
    
    return results


def extract_seasonal_trends(bulletin_text):
    """
    Extrait les tendances saisonnières depuis bulletins épidémiologiques
    
    Recherche patterns:
    "Pic infections respiratoires observé en décembre-février"
    "Augmentation allergies printanières mars-mai"
    """
    
    seasonal_indicators = {
        'Hiver': ['décembre', 'janvier', 'février', 'hiver'],
        'Printemps': ['mars', 'avril', 'mai', 'printemps'],
        'Été': ['juin', 'juillet', 'août', 'été'],
        'Automne': ['septembre', 'octobre', 'novembre', 'automne']
    }
    
    pathology_keywords = {
        'infections respiratoires': 'Antibiotiques',
        'grippe': 'Antibiotiques',
        'angine': 'Antibiotiques',
        'allergies': 'Antihistaminiques',
        'rhinite': 'Antihistaminiques',
        'parasitoses': 'Antiparasitaires',
        'diarrhée': 'Antiparasitaires',
    }
    
    findings = []
    
    text_lower = bulletin_text.lower()
    
    # Recherche co-occurrences pathologie + saison
    for pathology, category in pathology_keywords.items():
        if pathology in text_lower:
            for season, keywords in seasonal_indicators.items():
                if any(kw in text_lower for kw in keywords):
                    findings.append({
                        'category': category,
                        'season': season,
                        'pathology': pathology,
                        'evidence': 'mentioned in bulletin'
                    })
    
    return findings


# ============================================================================
# EXTRACTION MANUELLE GUIDÉE
# ============================================================================

def manual_extraction_template():
    """
    Template pour extraction manuelle depuis PDFs
    Copier-coller le texte du PDF et remplir ce dictionnaire
    """
    
    EXTRACTED_DATA = {
        
        # SOURCE 1: CNOPS Rapport Annuel 2023
        'cnops_categories': {
            'Antibiotiques': 0.18,       # Page X, Tableau Y
            'Analgésiques': 0.25,        # À remplir
            'Antidiabétiques': 0.15,
            'Cardiovasculaires': 0.22,
            'Antihistaminiques': 0.08,
            'Antiparasitaires': 0.05,
            'Autres': 0.07
        },
        
        # SOURCE 2: CNSS Statistiques Régionales T4 2023
        'cnss_regions': {
            'Casablanca-Settat': 0.32,
            'Rabat-Salé-Kénitra': 0.18,
            'Marrakech-Safi': 0.12,
            'Fès-Meknès': 0.11,
            'Tanger-Tétouan-Al Hoceïma': 0.09,
            'Souss-Massa': 0.08,
            'Autres': 0.10
        },
        
        # SOURCE 3: Bulletins Épidémiologiques 2023
        'seasonal_peaks': {
            'Antibiotiques': {
                'peak_season': 'Hiver',
                'evidence': 'Bulletin Grippe T1-2023: Pic infections respiratoires Déc-Fév',
                'multiplier': 1.45
            },
            'Antihistaminiques': {
                'peak_season': 'Printemps',
                'evidence': 'Rapport Allergologie: Pic pollinisation Mars-Mai',
                'multiplier': 1.70
            },
            'Antiparasitaires': {
                'peak_season': 'Été',
                'evidence': 'Bulletin Gastro-entérites: Augmentation estivale',
                'multiplier': 1.55
            }
        },
        
        # SOURCE 4: Volumes totaux (si disponibles)
        'volumes': {
            'total_annual_prescriptions': None,  # Si mentionné dans rapports
            'total_beneficiaries': None,
            'avg_prescriptions_per_capita': None
        }
    }
    
    return EXTRACTED_DATA


# ============================================================================
# VALIDATION DES DONNÉES EXTRAITES
# ============================================================================

def validate_extracted_data(data):
    """
    Vérifie la cohérence des données extraites
    """
    
    errors = []
    warnings = []
    
    # Vérifier que les proportions somment à ~1.0
    if 'cnops_categories' in data:
        total = sum(data['cnops_categories'].values())
        if abs(total - 1.0) > 0.05:
            errors.append(f"Proportions catégories somment à {total:.2f} (attendu ~1.0)")
    
    if 'cnss_regions' in data:
        total = sum(data['cnss_regions'].values())
        if abs(total - 1.0) > 0.05:
            warnings.append(f"Proportions régions somment à {total:.2f} (attendu ~1.0)")
    
    # Vérifier présence catégories principales
    required_categories = ['Antibiotiques', 'Analgésiques', 'Antidiabétiques']
    if 'cnops_categories' in data:
        for cat in required_categories:
            if cat not in data['cnops_categories']:
                errors.append(f"Catégorie manquante: {cat}")
    
    # Rapport de validation
    print("="*60)
    print("VALIDATION DES DONNÉES EXTRAITES")
    print("="*60)
    
    if errors:
        print("\n❌ ERREURS:")
        for err in errors:
            print(f"   • {err}")
    else:
        print("\n✅ Aucune erreur critique")
    
    if warnings:
        print("\n⚠️  AVERTISSEMENTS:")
        for warn in warnings:
            print(f"   • {warn}")
    
    print()
    return len(errors) == 0


# ============================================================================
# EXPORT POUR INTÉGRATION
# ============================================================================

def export_to_config(extracted_data, output_file='real_data_config.py'):
    """
    Exporte les données extraites dans un fichier de config Python
    utilisable par generate_dataset.py
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""\n')
        f.write('Configuration basée sur données réelles\n')
        f.write('Sources: CNOPS, CNSS, Ministère Santé\n')
        f.write('Date extraction: [À REMPLIR]\n')
        f.write('"""\n\n')
        
        f.write('# Proportions par catégorie (source: CNOPS)\n')
        f.write('REAL_CATEGORY_WEIGHTS = {\n')
        for cat, val in extracted_data.get('cnops_categories', {}).items():
            f.write(f"    '{cat}': {val},\n")
        f.write('}\n\n')
        
        f.write('# Distribution régionale (source: CNSS)\n')
        f.write('REAL_REGIONAL_WEIGHTS = {\n')
        for region, val in extracted_data.get('cnss_regions', {}).items():
            f.write(f"    '{region}': {val},\n")
        f.write('}\n\n')
        
        f.write('# Pics saisonniers (source: Bulletins épidémio)\n')
        f.write('REAL_SEASONAL_PEAKS = {\n')
        for cat, info in extracted_data.get('seasonal_peaks', {}).items():
            f.write(f"    '{cat}': {{\n")
            f.write(f"        'peak_season': '{info['peak_season']}',\n")
            f.write(f"        'multiplier': {info['multiplier']},\n")
            f.write(f"        'evidence': '{info['evidence']}'\n")
            f.write(f"    }},\n")
        f.write('}\n')
    
    print(f"✅ Configuration exportée: {output_file}")


# ============================================================================
# GUIDE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║  GUIDE D'EXTRACTION - DONNÉES RÉELLES CNOPS/CNSS                     ║
╚══════════════════════════════════════════════════════════════════════╝

ÉTAPE 1: TÉLÉCHARGER LES DOCUMENTS
   □ Rapport CNOPS: https://www.cnops.org.ma/fr/publications
   □ Stats CNSS: https://www.cnss.ma/fr/statistiques
   □ Bulletins Santé: https://www.sante.gov.ma/Publications

ÉTAPE 2: OUVRIR LES PDFs ET IDENTIFIER LES TABLEAUX
   Chercher:
   • Tableau remboursements par catégorie thérapeutique
   • Distribution géographique bénéficiaires
   • Courbes épidémiologiques saisonnières

ÉTAPE 3: EXTRACTION MANUELLE
   >>> data = manual_extraction_template()
   
   Remplir le dictionnaire avec les valeurs trouvées dans les PDFs

ÉTAPE 4: VALIDATION
   >>> validate_extracted_data(data)
   
   Vérifier cohérence (somme proportions ≈ 100%)

ÉTAPE 5: EXPORT
   >>> export_to_config(data)
   
   Génère real_data_config.py utilisable par ton dataset

ÉTAPE 6: DOCUMENTER LES SOURCES
   Dans ton rapport, citer:
   • Nom exact du document (ex: "CNOPS Rapport Annuel 2023")
   • Page et tableau (ex: "Page 47, Tableau 4.2")
   • Date de consultation

═══════════════════════════════════════════════════════════════════════

EXEMPLE CONCRET:

Si dans le rapport CNOPS page 47 tu vois:
   "Médicaments cardiovasculaires: 22.3% des prescriptions"

Tu remplis:
   data['cnops_categories']['Cardiovasculaires'] = 0.223

═══════════════════════════════════════════════════════════════════════
""")
    
    # Template pour démarrage rapide
    print("\n📋 Template d'extraction prêt à remplir:")
    data = manual_extraction_template()
    print("\ndata = {")
    for key, value in data.items():
        print(f"    '{key}': ...")
    print("}")
    
    print("\n💡 Conseil: Commence par extraire les proportions CNOPS,")
    print("   c'est la donnée la plus impactante pour ton modèle.\n")
