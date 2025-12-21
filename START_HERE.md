# 🚀 Start Here - mastock

**Point d'entrée rapide pour comprendre le projet et commencer à travailler.**

## 📌 Qu'est-ce que mastock ?

mastock est un projet visant à créer une application personnelle pour visualiser et gérer des blocs d'escalade. Le projet part de l'analyse d'une application existante (Stōkt) qui présente des problèmes en mode hors ligne, avec pour objectif de créer une version simplifiée et optimisée pour un usage offline-first, spécialisée sur la salle **Montoboard** (Caraman, France).

## 🎯 Objectif Actuel

**TODO 05** : Structure Package Python mastock

**Statut** : A faire (0%)

**Contexte** : L'extraction des données Montoboard est complète (TODO 04 terminé). On passe maintenant au développement du prototype Python.

**Objectif** : Créer un package Python installable (`pip install -e .`) avec interface PyQtGraph pour :
- Visualiser les climbs et prises sur le mur
- Tester les concepts d'interaction avec la BD
- Servir de base pour l'application mobile

**Fichiers clés** :
- `/docs/TODOS/05_python_package_structure.md` - Plan détaillé
- `/docs/TODOS/05_python_package_structure_STATUS.md` - Progression
- `/mastock/src/stokt_api.py` - API client existant
- `/extracted/data/montoboard_setup.json` - 776 prises avec polygones

## 📋 TODOs

| TODO | Description | Statut |
|------|-------------|--------|
| 01 | Analyse de l'app Stōkt | 80% - Terminé (objectif atteint) |
| 02 | Conception schéma SQLite | 0% - Fusionné dans TODO 05 |
| 03 | Analyse Hermes via agents | 95% - Terminé |
| 04 | Test extraction Montoboard | 100% - Terminé |
| 05 | Structure Package Python | 0% - **Prioritaire** |

## 🔑 Données clés

| Information | Valeur |
|-------------|--------|
| Backend API | `https://www.sostokt.com/api/` |
| Endpoint auth | `POST /api/token-auth` (username + password) |
| Salle cible | Montoboard |
| Gym ID | `be149ef2-317d-4c73-8d7d-50074577d2fa` |
| Bundle | Hermes bytecode v96 (à décompiler) |

## 🔄 Workflow de Session

### Pour Claude (début de session)

```bash
# 1. Lire ce fichier (START_HERE.md)
# 2. Consulter le TODO actif
cat /media/veracrypt1/Repositories/mastock/docs/TODOS/03_analyse_hermes_agents_STATUS.md

# 3. Vérifier la timeline
cat /media/veracrypt1/Repositories/mastock/docs/TIMELINE.md
```

## 📊 Résumé des sessions

### Session 2025-12-21
- TODO 04 complété (100%)
- Endpoint `/api/faces/{faceId}/setup` testé et documenté
- 776 prises avec polygones récupérées
- Image haute résolution (2263x3000) téléchargée
- TODO 05 créé : Structure Package Python mastock
- Objectif : prototype Python avec PyQtGraph + SQLite

### Session 2025-12-20 (soir)
- ✅ Installation hermes-dec (décompileur Hermes v96)
- ✅ Désassemblage complet du bundle (95 Mo)
- ✅ Configuration app extraite
- ✅ 40+ endpoints API documentés
- ✅ 100+ actions Redux cataloguées
- ✅ Structures Climb/Face extraites
- ✅ Base documentaire créée : `/docs/reverse_engineering/`
- 📝 TODO 03 avancé à 85%

### Session 2025-12-20 (après-midi)
- ✅ Authentification API réussie (`sostokt.com`, pas `getstokt.com`)
- ✅ Token DRF obtenu
- ✅ Montoboard identifié (ID récupéré)
- ❌ Endpoints faces/climbs : erreurs 500 ou timeout
- ⚠️ Risque de bannissement si requêtes exploratoires
- 📝 TODO 03 créé pour analyse approfondie

### Session 2025-12-20 (matin)
- ✅ Re-analyse complète de l'APK Stōkt
- ✅ 40+ endpoints API documentés
- ✅ 150+ actions Redux identifiées
- ✅ Système de prises analysé (coordonnées X/Y)
- ❌ Patch APK pour mitmproxy échoué (bug manifest)
- 📝 TODO 02 créé pour conception SQLite

### Session 2025-11-10
- ✅ Application Stōkt identifiée et extraite
- ✅ Architecture React Native + Expo + Firebase
- ✅ Cause du problème offline identifiée

## 📁 Rapports disponibles

- `/docs/reports/SESSION_2025-12-20_analyse_hermes.md` - **Analyse Hermes (nouveau)**
- `/docs/reports/SESSION_2025-12-20_api_extraction.md` - Test extraction API
- `/docs/reports/SESSION_2025-12-20_analyse_complete_stokt.md` - Analyse complète
- `/docs/reports/SESSION_2025-12-20_patch_apk_mitm.md` - Tentative patch APK
- `/docs/reports/SESSION_2025-11-10_extraction_stockt.md` - Extraction initiale
- `/docs/reports/ANALYSE_STRUCTURE_FIREBASE_API.md` - Structure API/Firebase

## 📚 Documentation Reverse Engineering

- `/docs/reverse_engineering/INDEX.md` - **Index racine**
- `/docs/reverse_engineering/01_CONFIGURATION.md` - Configuration app
- `/docs/reverse_engineering/02_AUTHENTIFICATION.md` - Flux auth
- `/docs/reverse_engineering/03_ENDPOINTS.md` - Liste endpoints
- `/docs/reverse_engineering/04_STRUCTURES.md` - Structures données
- `/docs/reverse_engineering/05_REDUX_ACTIONS.md` - Actions Redux

## 🗂️ Structure du Projet

```
/mastock/
├── README.md              # Description générale
├── START_HERE.md          # Ce fichier
├── CLAUDE.md              # Guide de contribution
├── /data/                 # Données extraites (à venir)
│   └── /montoboard/       # Données Montoboard
├── /docs/
│   ├── TIMELINE.md        # Historique du projet
│   ├── 02_guide_interception_https.md
│   ├── /TODOS/            # Tâches actives (01, 02, 03)
│   └── /reports/          # Rapports de sessions
├── /extracted/            # APKs et fichiers décompilés (git ignored)
│   ├── stockt_apk/        # APKs originaux
│   ├── stockt_decompiled/ # APK décompilé + bundle Hermes
│   └── stockt_patched/    # APKs patchés (non fonctionnels)
├── /tools/                # Scripts d'analyse
└── /archive/              # Documents archivés
```

## 🎯 Prochaine session

**Priorité : Créer la structure du package Python**

1. **Créer `pyproject.toml`** avec dépendances (PyQtGraph, PyQt6, requests)
2. **Réorganiser le code** en `src/mastock/` avec modules api/, db/, gui/, core/
3. **Créer le schéma SQLite** pour stocker climbs, prises, metadata sync
4. **Prototype GUI** : afficher l'image du mur avec les polygones des prises

**Stack technique** :
- PyQtGraph + PyQt6 pour l'interface interactive
- SQLite pour le stockage local
- pytest pour les tests

**Documentation de référence** : `/docs/TODOS/05_python_package_structure.md`

---

**Dernière mise à jour** : 2025-12-21
**Statut du projet** : Phase de développement prototype Python
