# 🚀 Start Here - mastock

**Point d'entrée rapide pour comprendre le projet et commencer à travailler.**

## 📌 Qu'est-ce que mastock ?

mastock est un projet visant à créer une application personnelle pour visualiser et gérer des blocs d'escalade. Le projet part de l'analyse d'une application existante (Stōkt) qui présente des problèmes en mode hors ligne, avec pour objectif de créer une version simplifiée et optimisée pour un usage offline-first, spécialisée sur la salle **Montoboard** (Caraman, France).

## 🎯 Objectif Actuel

**TODO 04** : Test Extraction Données Montoboard

**Statut** : En cours (25%)

**Contexte** : L'analyse Hermes (TODO 03 à 95%) a révélé les endpoints, mais les tests montrent que plusieurs endpoints retournent 404. Il faut analyser plus en profondeur la construction des requêtes.

**Problème identifié** : Les endpoints comme `api/gyms/{id}/climbs` retournent 404 malgré un token valide. Piste : analyser `fetchMySentClimbs` pour comprendre la construction exacte des URLs.

**Fichiers clés** :
- `/docs/TODOS/04_test_extraction_montoboard_STATUS.md` - Progression
- `/docs/TODOS/03_analyse_hermes_agents_STATUS.md` - Analyse Hermes (95%)
- `/docs/reverse_engineering/INDEX.md` - Base documentaire RE
- Code : `/extracted/stockt_decompiled/decompiled/stokt_decompiled.js`

## 📋 TODOs

| TODO | Description | Statut |
|------|-------------|--------|
| 01 | Analyse de l'app Stōkt | 80% - Bloqué sur extraction données |
| 02 | Conception schéma SQLite | 0% - En attente |
| 03 | Analyse Hermes via agents | 95% - Endpoints documentés |
| 04 | Test extraction Montoboard | 25% - **Prioritaire** - Analyser requêtes |

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

**Priorité : Analyser construction des requêtes**

1. **Analyser `fetchMySentClimbs`** (ligne 442389 dans stokt_decompiled.js)
   - Comprendre comment l'URL `/my-sent-climbs` est construite
   - Vérifier s'il y a des headers additionnels
2. Comparer la construction des requêtes avec ce qu'on envoie
3. Tester avec les corrections trouvées
4. Si échec → intercepter le trafic réel de l'app

**Fonctions clés à analyser** :
- `fetchMySentClimbs` (ligne 442389)
- `fetchGymRecentClimbs` (ligne 458971)

**Documentation de référence** : `/docs/reverse_engineering/03_ENDPOINTS.md`

---

**Dernière mise à jour** : 2025-12-20
**Statut du projet** : Phase d'analyse approfondie
