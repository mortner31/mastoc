# 🚀 Start Here - mastock

**Point d'entrée rapide pour comprendre le projet et commencer à travailler.**

## 📌 Qu'est-ce que mastock ?

mastock est un projet visant à créer une application personnelle pour visualiser et gérer des blocs d'escalade. Le projet part de l'analyse d'une application existante (Stōkt) qui présente des problèmes en mode hors ligne, avec pour objectif de créer une version simplifiée et optimisée pour un usage offline-first, spécialisée sur la salle **Montoboard** (Caraman, France).

## 🎯 Objectif Actuel

**TODO 03** : Analyse approfondie du bundle Hermes via agents

**Statut** : À faire (0%)

**Contexte** : L'extraction directe via API a partiellement fonctionné (auth OK, liste gyms OK) mais les endpoints détaillés (faces, climbs) donnent des erreurs. Avant de faire d'autres requêtes, il faut analyser le code pour comprendre exactement comment l'app fonctionne.

**Fichiers clés** :
- `/docs/TODOS/03_analyse_hermes_agents.md` - Plan de travail
- `/docs/TODOS/03_analyse_hermes_agents_STATUS.md` - Progression

## 📋 TODOs

| TODO | Description | Statut |
|------|-------------|--------|
| 01 | Analyse de l'app Stōkt | 80% - Bloqué sur extraction données |
| 02 | Conception schéma SQLite | 0% - En attente |
| 03 | Analyse Hermes via agents | 0% - **Prioritaire** |

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

- `/docs/reports/SESSION_2025-12-20_api_extraction.md` - Test extraction API
- `/docs/reports/SESSION_2025-12-20_analyse_complete_stokt.md` - Analyse complète
- `/docs/reports/SESSION_2025-12-20_patch_apk_mitm.md` - Tentative patch APK
- `/docs/reports/SESSION_2025-11-10_extraction_stockt.md` - Extraction initiale
- `/docs/reports/ANALYSE_STRUCTURE_FIREBASE_API.md` - Structure API/Firebase

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

**Priorité : TODO 03 - Analyse Hermes**

1. Installer un décompileur Hermes (`hermes-dec` ou équivalent)
2. Décompiler le bundle `index.android.bundle`
3. Analyser le flux Redux pour comprendre les requêtes API
4. Documenter les endpoints exacts avec leurs paramètres
5. Préparer un script d'extraction sûr

**Stratégie** : Utiliser des agents Explore pour analyser le code sans faire de requêtes API risquées.

---

**Dernière mise à jour** : 2025-12-20
**Statut du projet** : Phase d'analyse approfondie
