# 🚀 Start Here - mastock

**Point d'entrée rapide pour comprendre le projet et commencer à travailler.**

## 📌 Qu'est-ce que mastock ?

mastock est un projet visant à créer une application personnelle pour visualiser et gérer des blocs d'escalade. Le projet part de l'analyse d'une application existante qui présente des problèmes en mode hors ligne, avec pour objectif de créer une version simplifiée et optimisée pour un usage offline-first.

## 🎯 Objectif Actuel

**TODO 02** : Conception du schéma SQLite pour mastock

**Statut** : À faire (0%)

**Fichiers clés** :
- `/docs/TODOS/02_conception_schema_sqlite.md` - Plan de travail
- `/docs/TODOS/02_conception_schema_sqlite_STATUS.md` - Progression

## 📋 TODOs

| TODO | Description | Statut |
|------|-------------|--------|
| 01 | Analyse de l'app Stōkt | 70% - Analyse statique complète |
| 02 | Conception schéma SQLite | 0% - À faire |

## 🔄 Workflow de Session

### Pour Claude (début de session)

```bash
# 1. Lire ce fichier (START_HERE.md)
# 2. Consulter le TODO actif
cat /media/veracrypt1/Repositories/mastock/docs/TODOS/02_conception_schema_sqlite_STATUS.md

# 3. Vérifier la timeline
cat /media/veracrypt1/Repositories/mastock/docs/TIMELINE.md
```

## 📊 Résumé des sessions

### Session 2025-12-20
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
├── /docs/
│   ├── TIMELINE.md        # Historique du projet
│   ├── 02_guide_interception_https.md
│   ├── /TODOS/            # Tâches actives
│   └── /reports/          # Rapports de sessions
├── /extracted/            # APKs et fichiers décompilés
│   ├── stockt_apk/        # APKs originaux
│   ├── stockt_decompiled/ # APK décompilé
│   └── stockt_patched/    # APKs patchés (non fonctionnels)
├── /mastock/              # Code source (à venir)
├── /tools/                # Scripts d'analyse
└── /archive/              # Documents archivés
```

## 🎯 Prochaine session

Conception du schéma SQLite :
1. Identifier les entités (gyms, walls, climbs, holds, etc.)
2. Définir les relations
3. Créer les tables SQL
4. Préparer des données mock

---

**Dernière mise à jour** : 2025-12-20
**Statut du projet** : Phase de conception
