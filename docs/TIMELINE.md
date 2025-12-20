# Timeline du Projet mastock

Ce fichier trace l'historique chronologique des TODOs et jalons du projet.

## Format
`YYYY-MM-DD | TODO XX - Description | Statut`

---

## 2025-12-20

- **Test d'extraction API directe**
  - Authentification réussie sur `sostokt.com` (pas getstokt.com)
  - Token DRF obtenu via `/api/token-auth`
  - Salle Montoboard identifiée (ID: `be149ef2-317d-4c73-8d7d-50074577d2fa`)
  - Endpoints `/api/faces`, `/api/climbs` : erreurs/timeout
  - **Décision** : Analyse statique approfondie avant nouvelles requêtes
  - Rapport : `/docs/reports/SESSION_2025-12-20_api_extraction.md`

- **TODO 03 créé** - Analyse approfondie du bundle Hermes via agents
  - Objectif : Comprendre exactement les flux API de l'app
  - Stratégie : Décompilation Hermes + analyse Redux
  - Contrainte : Pas de requêtes exploratoires (risque bannissement)
  - Statut : À faire (0%)

- **TODO 01 mis à jour** - Analyse complète refaite depuis zéro
  - Re-analyse de l'APK et du bundle JavaScript
  - 40+ endpoints API identifiés
  - Architecture Redux documentée (150+ actions)
  - Système de prises (holds) analysé
  - Problème offline confirmé (pas de persistance locale)
  - Statut : En cours (70%)
  - Rapport : `/docs/reports/SESSION_2025-12-20_analyse_complete_stokt.md`

- **Tentative de patch APK pour interception HTTPS**
  - Utilisation de apk-mitm pour patcher le certificate pinning
  - Split APKs re-signés avec clé commune
  - **Échec** : Bug `@null` dans le manifest empêche l'installation
  - Guide créé : `/docs/02_guide_interception_https.md`
  - Rapport : `/docs/reports/SESSION_2025-12-20_patch_apk_mitm.md`
  - Statut : Bloqué - alternatives à explorer

- **TODO 02 créé** - Conception du schéma SQLite pour mastock
  - Basé sur l'analyse statique de Stōkt
  - Architecture offline-first
  - Statut : À faire (0%)

## 2025-11-10

- **TODO 01 créé** - Analyse et décompilation de l'application d'escalade
  - Objectif : Comprendre le fonctionnement de l'app existante
  - Focus : Système d'images interactives et problèmes offline
  - Statut : En cours (0%)
