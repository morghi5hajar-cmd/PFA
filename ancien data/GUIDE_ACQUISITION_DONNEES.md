# Guide d'Acquisition de Données Réelles
## Projet PFA - AI-Based Drug Demand Forecasting

---

##  EMAIL TYPE - DEMANDE DONNÉES CNOPS

**À:** contact@cnops.org.ma  
**Objet:** Demande de données statistiques dans le cadre d'un projet académique

Madame, Monsieur,

Je suis étudiant en [Votre Formation] à [Votre Université] et je réalise actuellement mon projet de fin d'année sur la prévision de la demande en médicaments dans les pharmacies marocaines à l'aide de l'intelligence artificielle.

Dans le cadre de ce projet académique encadré par [Nom Professeur], je souhaiterais accéder aux données statistiques suivantes, si elles sont disponibles en open data :

1. **Répartition des prescriptions par catégorie thérapeutique** (classification ATC)
   - Antibiotiques, Analgésiques, Antidiabétiques, etc.
   - Sur la période 2021-2023 si possible

2. **Distribution géographique des bénéficiaires** par région administrative

3. **Évolution mensuelle ou trimestrielle** du nombre de prescriptions remboursées

Je précise que ces données seront utilisées uniquement à des fins pédagogiques et de recherche, dans le respect des règles de confidentialité et de protection des données personnelles.

Je reste à votre disposition pour tout complément d'information.

Cordialement,  
[Votre Nom]  
[Votre Email]  
[Votre Téléphone]

---

## 📧 EMAIL TYPE - DEMANDE DONNÉES MÉTÉO MAROC

**À:** contact@marocmeteo.ma  
**Objet:** Demande de données climatiques historiques - Projet académique

Madame, Monsieur,

Dans le cadre de mon projet de fin d'études portant sur la prévision de la demande pharmaceutique au Maroc, j'aurais besoin de données de températures historiques pour les villes suivantes :

- **Villes** : Rabat, Casablanca, Marrakech, Fès, Tanger, Agadir
- **Période** : 2021-2023 (données quotidiennes si possible)
- **Variables** : Température moyenne journalière (min/max si disponibles)

Ces données seront utilisées comme variables explicatives dans nos modèles de machine learning pour corréler la demande en médicaments avec les conditions climatiques.

Pourriez-vous m'indiquer la procédure pour obtenir ces données historiques ?

Je vous remercie par avance.

Cordialement,  
[Votre Nom]

---

## ✅ CHECKLIST D'ACQUISITION - À FAIRE CETTE SEMAINE

### Priorité 1 - Données Accessibles en Ligne (0-2 jours)

- [ ] **Télécharger rapport annuel CNOPS le plus récent**
  - URL : https://www.cnops.org.ma/fr/publications
  - Chercher section "Statistiques remboursement médicaments"
  - Extraire tableau proportions par catégorie thérapeutique
  - Prendre screenshot + noter page et tableau

- [ ] **Consulter statistiques CNSS en ligne**
  - URL : https://www.cnss.ma/fr/statistiques
  - Section "Prestations maladie"
  - Noter distribution régionale bénéficiaires
  - Télécharger bulletins trimestriels si disponibles

- [ ] **Explorer Open Data Santé**
  - URL : https://www.sante.gov.ma
  - Bulletins épidémiologiques (grippe, gastro-entérites)
  - Identifier pics saisonniers pathologies

### Priorité 2 - Demandes Officielles (3-5 jours délai réponse)

- [ ] **Email CNOPS** (utiliser template ci-dessus)
  - Demander accès données détaillées si non public

- [ ] **Email Météo Maroc** (utiliser template ci-dessus)
  - Demander températures historiques 2021-2023

- [ ] **Contact ANAM** (si temps disponible)
  - Nomenclature médicaments + prix de référence
  - Classification ATC détaillée

### Priorité 3 - Sources Alternatives (si blocage)

- [ ] **Haut Commissariat au Plan (HCP)**
  - URL : https://www.hcp.ma
  - Annuaires statistiques du Maroc
  - Démographie régionale

- [ ] **WHO Morocco**
  - URL : https://www.emro.who.int/countries/mor/
  - Données santé publique Maroc

- [ ] **Thèses et mémoires disponibles en ligne**
  - Google Scholar : "pharmacie Maroc statistiques"
  - TOUBKAL (dépôt thèses marocaines)

---

## 📊 DONNÉES MINIMALES NÉCESSAIRES (Seuil de Réussite)

Pour que ton dataset soit crédible avec des données réelles, il te faut **AU MINIMUM** :

### ✅ Données Critiques (OBLIGATOIRES)
1. **Proportions par catégorie** (même approximatives)
   - Source : Rapport CNOPS ou article scientifique
   - Exemple : "Les antibiotiques représentent ~18% des prescriptions"

2. **Distribution régionale** (même en %)
   - Source : CNSS ou HCP
   - Exemple : "Casablanca = 32% de la population"

### ✅ Données Importantes (RECOMMANDÉES)
3. **Températures réelles** 2021-2023
   - Source : Météo Maroc ou World Weather Online
   - Utiliser API gratuite si email sans réponse

4. **Un pic saisonnier documenté**
   - Source : Bulletin épidémiologique grippe
   - Exemple : "Pic infections respiratoires en janvier-février"

### ⚠️ Données Bonus (OPTIONNELLES)
5. Volumes totaux annuels
6. Prix moyens médicaments
7. Nombre pharmacies par région

---

## 🔄 PLAN B - SI AUCUNE RÉPONSE OFFICIELLE

### Option 1 : Utiliser Publications Scientifiques
- Rechercher articles sur PubMed / Google Scholar
- Mots-clés : "Morocco pharmaceutical consumption statistics"
- Citer les articles comme sources

### Option 2 : Extrapoler depuis Données Françaises/OMS
- Adapter proportions pays similaires
- Documenter méthodologie d'adaptation
- Mentionner limitation dans rapport

### Option 3 : Dataset 100% Synthétique Validé
- Garder ton dataset actuel (très bien construit)
- Faire valider les proportions par ton encadrant
- Justifier choix dans section "Limites et perspectives"

---

## 📝 DOCUMENTATION POUR LE RAPPORT

Pour chaque donnée réelle utilisée, documenter :

```
Source : [Nom exact du document]
Auteur/Organisation : [CNOPS / CNSS / Ministère Santé]
Date de publication : [Année]
Page/Tableau : [Page 47, Tableau 4.2]
Date de consultation : [DD/MM/YYYY]
URL : [Lien direct si disponible]

Données extraites :
- [Valeur 1] : [Description]
- [Valeur 2] : [Description]

Traitement appliqué :
- [Ex: Normalisation des pourcentages]
- [Ex: Interpolation pour données manquantes]
```

---

## 🎯 OBJECTIF FINAL

**Dataset Hybride Optimal :**
- **70% données réelles** (proportions, saisonnalité, températures)
- **30% synthèse** (volumes quotidiens détaillés)
- **100% traçabilité** (chaque valeur sourcée ou justifiée)

**Temps estimé :** 5-7 jours
- Jours 1-2 : Extraction rapports en ligne
- Jours 3-5 : Attente réponses emails
- Jours 6-7 : Intégration et validation

---

## ⏰ DEADLINE RECOMMANDÉE

**Cette semaine (avant vendredi)** : Envoyer tous les emails de demande
**Semaine prochaine** : Exploiter les données reçues + Plan B si silence
**Dans 2 semaines** : Dataset final validé par encadrant

---

**Note importante :** Même si tu n'obtiens que 20-30% de données réelles, c'est déjà un excellent point pour la crédibilité du projet. L'important est de **documenter ta démarche** de recherche de données réelles.
