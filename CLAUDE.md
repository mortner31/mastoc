# Guide de Contribution pour l'IA (Claude)

Ce document définit les règles à suivre pour maintenir la structure et l'organisation de la documentation de ce projet.

---

## 🗂️ Structure des Dossiers

### Dossiers Principaux

- **`/docs`** : Documentation de référence (stratégie, protocoles) du projet global
- **`/mastoc`** : Code et documentation spécifiques à l'application mastoc
- **`/tools`** : Scripts d'analyse et de validation (si nécessaire)
- **`/docs/reports`** : Rapports générés par les outils et sessions de travail
- **`/docs/TODOS`** : Fiches de tâches **actives uniquement**
- **`/archive`** : Documents et tâches **terminés ou obsolètes**

### Documents à la Racine

**Règle** : Garder la racine minimaliste avec uniquement les documents de navigation

**Documents autorisés à la racine** :
- ✅ `README.md` - Description générale du projet
- ✅ `START_HERE.md` - Point d'entrée pour démarrage rapide
- ✅ `CLAUDE.md` - Ce guide (pour Claude)
- ✅ `GEMINI.md` - Guide pour Gemini
- ❌ Autres documents → doivent aller dans `/TODOS`, `/reports` ou `/archive`

---

## 🔄 Cycle de Vie d'une Tâche

### 1. Planification
**Où** : Feuille de route (`/docs/TODOS/XX_MYTASK.md`)
**Action** : Identifier la tâche à faire

### 2. Exécution
**Où** : Créer une fiche dans `/docs/TODOS/XX_nom_tache.md`
**Format** :
- Numéro séquentiel (01, 02, 03...)
- Nom descriptif
- Exemple : `03_create_interface.md`

**Contenu minimum** :
- Objectif clair
- Liste simple des tâches (checklist)
- Références aux documents existants si nécessaire

### 3. Suivi de Progression
**Où** : Créer un fichier STATUS associé `/docs/TODOS/XX_nom_tache_STATUS.md`
**Contenu (simplicité maximale)** :
- Liste de tâches avec coches
- Progression globale en pourcentage uniquement
- **PAS d'indicateurs temporels** (durée, timeline, etc.)

### 4. Analyse et Résultats
**Où** : `/docs/reports/`
**Type de documents** :
- Rapports de session : `SESSION_YYYY-MM-DD_description.md`
- Rapports d'analyse : `nom_analyse_report.md`
- Datasets : `/tools/datasets/nom_dataset.json`

**Contenu (simplicité maximale)** :
- Liste des objectifs atteints
- Résultats concrets
- **PAS d'indicateurs temporels**

### 5. Archivage
**Quand** : Tâche complétée OU devenue obsolète

**Action** :
```bash
# Déplacer le TODO et son STATUS
mv /docs/TODOS/XX_nom_tache.md /archive/TODOS/
mv /docs/TODOS/XX_nom_tache_STATUS.md /archive/TODOS/

# Mettre à jour la timeline
echo "YYYY-MM-DD | TODO XX archivé (complété/obsolète)" >> /docs/TIMELINE.md
```

**Important** : Les rapports de session restent dans `/docs/reports/` (historique du projet)

### 6. Synthèse
**Où** : Documentation principale (`/docs`)
**Action** : Intégrer le savoir acquis dans la documentation permanente

**Fichiers à maintenir** :
- `/docs/INDEX.md` - Index de la documentation
- `/docs/TIMELINE.md` - Historique chronologique des TODOs (une ligne par TODO avec date)

---

## ⚠️ RÈGLE CRITIQUE : Tests et Code de Production

**IMPÉRATIF** : Les tests doivent **TOUJOURS** utiliser le code de production, jamais des copies ou des mocks du code métier.

### Vérifications obligatoires :
- [ ] Les tests importent depuis les modules de production (`/mastoc/src/`)
- [ ] Aucune duplication de logique métier dans les tests
- [ ] Les fixtures utilisent les vraies classes/fonctions de production
- [ ] Les tests échouent si le code de production change

**Exemple CORRECT** :
```python
from mastoc.module import fonction  # Import depuis production
```

**Exemple INCORRECT** :
```python
def fonction(...):  # Copie dans le fichier de test ❌
    # logique dupliquée
```

---

## 📋 Workflow de Démarrage de Session

### Pour Claude (au début de chaque session)

1. **Lire le point d'entrée** :
   ```bash
   cat /START_HERE.md
   ```

2. **Identifier la tâche active** :
   ```bash
   ls /docs/TODOS/*.md
   # Chercher les fichiers SANS "_STATUS" → ce sont les plans de tâches
   ```

3. **Lire le STATUS de la tâche** :
   ```bash
   cat /docs/TODOS/XX_nom_tache_STATUS.md
   # Voir la progression, ce qui reste à faire
   ```

4. **Consulter les références** selon la tâche

---

## 🧹 Règles d'Organisation

### Ce qui va dans `/TODOS/`

✅ **Autorisé** :
- Fiches de tâches actives (`XX_nom.md`)
- Fichiers de statut (`XX_nom_STATUS.md`)
- Guides pour la prochaine phase (`XX_nom_suite.md`)

❌ **Interdit** :
- Rapports de session (→ `/reports/`)
- Documentation permanente (→ `/docs` ou `/mastoc/docs`)
- Documents obsolètes (→ `/archive/`)

### Ce qui va dans `/reports/`

✅ **Autorisé** :
- Rapports de session (`SESSION_*.md`)
- Rapports d'analyse générés par les outils
- Synthèses de travail
- Validation et statistiques

❌ **Interdit** :
- Plans de tâches (→ `/TODOS/`)
- Documentation technique (→ `/docs`)

### Ce qui va dans `/archive/`

✅ **Autorisé** :
- TODOs complétés (→ `/archive/TODOS/`)
- Documents obsolètes (→ `/archive/sessions/` ou autre)
- Anciennes versions de documents

**Important** : Toujours inclure un `README.md` dans les dossiers d'archive expliquant pourquoi les documents ont été archivés.

### Ce qui reste à la racine

**Strict minimum** :
- `README.md` - Description du projet
- `START_HERE.md` - Point d'entrée rapide
- `CLAUDE.md` - Ce guide
- `GEMINI.md` - Guide pour Gemini

**Tout le reste doit être organisé dans les dossiers appropriés.**

---

## 📛 Convention de Nommage

### Documentation dans `/docs/`

**RÈGLE IMPÉRATIVE** : Tous les fichiers de documentation dans `/docs/` doivent être préfixés par un indice numérique.

**Format** : `XX_nom_descriptif.md`

**Exemples** :
- ✅ `01_architecture.md`
- ✅ `02_api_design.md`
- ✅ `10_security.md`
- ❌ `architecture.md` (pas d'indice)
- ❌ `doc.md` (pas d'indice)

**Exceptions** : Seuls `INDEX.md` et `TIMELINE.md` ne suivent pas cette règle car ils sont des fichiers système.

### TODOs dans `/docs/TODOS/`

**Format** : `XX_nom_tache.md` + `XX_nom_tache_STATUS.md`

**Exemples** :
- `01_setup_project.md` + `01_setup_project_STATUS.md`
- `02_implement_crypto.md` + `02_implement_crypto_STATUS.md`

### Rapports dans `/docs/reports/`

**Format** : `SESSION_YYYY-MM-DD_description.md`

**Exemple** :
- `SESSION_2025-11-05_init_android.md`

---

## 📝 Templates de Documents

### Template : Fichier TODO
```markdown
# TODO XX - Titre de la Tâche

## 🎯 Objectif
[Description claire et concise]

## 📋 Tâches
- [ ] Tâche 1
- [ ] Tâche 2
- [ ] Tâche 3

## 📚 Références
- `/docs/xxx.md` si nécessaire
```

### Template : Fichier STATUS
```markdown
# STATUS - TODO XX : Titre

**Progression** : XX%

## ✅ Complété
- [x] Tâche complétée

## ⏳ En cours / À faire
- [ ] Tâche en cours
- [ ] Tâche à faire
```

### Template : Rapport de Session
```markdown
# Rapport de Session - Description

**Date** : YYYY-MM-DD

## 🎯 Objectifs Atteints
- ✅ Objectif 1
- ✅ Objectif 2

## 📊 Résultats
[Résultats concrets, statistiques si pertinent]

## 🚀 Prochaines Étapes
[Ce qui reste à faire]
```

---

## ✅ Checklist Avant de Terminer une Session

- [ ] Fichier STATUS mis à jour avec progression actuelle
- [ ] `/docs/TIMELINE.md` mis à jour avec nouvelle entrée si TODO créé/archivé
- [ ] Rapport de session créé dans `/docs/reports/` si pertinent
- [ ] Fichiers obsolètes archivés dans `/archive/`
- [ ] `START_HERE.md` mis à jour si changements majeurs
- [ ] Racine du projet propre (pas de fichiers temporaires)

---

## 🚨 Erreurs Courantes à Éviter

### ❌ Ne PAS faire

1. **Créer des documents à la racine** (sauf les 4 autorisés)
   - ❌ `NEXT_SESSION.md` à la racine
   - ✅ `/TODOS/04_prochaine_phase.md`

2. **Mélanger rapports et TODOs**
   - ❌ Rapport de session dans `/docs/TODOS/`
   - ✅ Rapport dans `/docs/reports/`, TODO dans `/docs/TODOS/`

3. **Oublier d'archiver les TODOs complétés**
   - ❌ Garder `03_implementation_crypto.md` dans `/docs/TODOS/` une fois terminé
   - ✅ Déplacer vers `/archive/TODOS/03_implementation_crypto.md`

4. **Créer plusieurs fichiers STATUS**
   - ❌ `03_xxx_STATUS.md` + `03_xxx_PROGRESS.md`
   - ✅ Un seul fichier `03_xxx_STATUS.md` qui centralise tout

5. **Ajouter des indicateurs temporels dans TODO/STATUS/rapports**
   - ❌ Durée estimée, timeline, dates dans les tâches
   - ✅ Uniquement pourcentage de progression et liste de tâches
   - ℹ️ L'historique temporel est dans `/docs/TIMELINE.md`

6. **Tests qui n'utilisent pas le code de production**
   - ❌ Copier/dupliquer la logique métier dans les tests
   - ✅ Toujours importer depuis les modules de production

### ✅ Bonnes Pratiques

1. **Toujours partir de `START_HERE.md`** en début de session
2. **Un TODO = Un fichier + Un STATUS** (paire indissociable)
3. **Les rapports restent dans `/docs/reports/`** (historique permanent)
4. **Archiver dès que complété ou obsolète**
5. **Mettre à jour `/docs/TIMELINE.md`** pour chaque TODO créé/archivé
6. **Simplicité maximale** : liste de tâches + pourcentage (pas de durées)
7. **Tests = code de production** : jamais de duplication de logique

---

## 📞 Aide Rapide

| Situation | Action |
|-----------|--------|
| Je commence une session | Lire `START_HERE.md` |
| Je veux créer une nouvelle tâche | Créer `/docs/TODOS/XX_nom.md` + `/docs/TODOS/XX_nom_STATUS.md` + ligne dans `/docs/TIMELINE.md` |
| Je veux documenter ma session | Créer `/docs/reports/SESSION_YYYY-MM-DD_xxx.md` |
| J'ai terminé un TODO | Déplacer vers `/archive/TODOS/` + mettre à jour `/docs/TIMELINE.md` |
| Un document devient obsolète | Déplacer vers `/archive/` |
| Je veux voir l'historique | Consulter `/docs/TIMELINE.md` |

---

**Respectez impérativement ce cycle pour toute modification.**

**Version** : 3.1 (adaptée pour mastoc)
**Dernière mise à jour** : 2025-11-10
