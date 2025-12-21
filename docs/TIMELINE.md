# Timeline du Projet mastock

Ce fichier trace l'historique chronologique des TODOs et jalons du projet.

## Format
`YYYY-MM-DD | TODO XX - Description | Statut`

---

## 2025-12-21

- **TODO 05 créé** - Structure Package Python mastock
  - Objectif : Restructurer le code en package installable (`pip install -e .`)
  - Stack : PyQtGraph + PyQt6 pour GUI, SQLite pour stockage local
  - Fonctionnalités : stockage BD, sync, filtres climbs, visualisation prises
  - Servira de prototype avant l'application mobile
  - Statut : À faire (0%)

- **TODO 04 complété à 100%** - Extraction données Montoboard
  - Endpoint `/api/faces/{faceId}/setup` découvert et testé
  - 776 prises avec polygones récupérées
  - Image haute résolution téléchargée (2263x3000)
  - Documentation mise à jour

## 2025-12-20 (nuit)

- **TODO 04 avancé à 25%** - Tests d'extraction
  - Authentification réussie (token valide)
  - Tests des endpoints : plusieurs retournent 404
  - Endpoints OK : `api/token-auth`, `api/users/me`, `api/version`, `api/my-notifications`
  - Endpoints 404 : `api/gyms/{id}/climbs`, `api/gyms/{id}/faces`, `api/users/{id}/sent-climbs`
  - **Découverte** : L'API a peut-être changé, ou il manque des headers
  - **Prochaine étape** : Analyser `fetchMySentClimbs` pour comprendre la construction des requêtes

- **TODO 03 avancé à 95%** - Endpoints supplémentaires découverts
  - Endpoint climbs récents : `api/gyms/{gymId}/climbs?max_age=60`
  - Endpoint sent-climbs : `api/users/{userId}/sent-climbs?limit=X`
  - Endpoint my-sent-climbs : `api/gyms/{gymId}/my-sent-climbs`
  - Paramètres filtrage complets documentés
  - HomeScreen analysé (flux de chargement)

## 2025-12-20 (soir)

- **TODO 04 créé** - Test extraction données Montoboard
  - Objectif : Tester les endpoints découverts
  - Récupérer gym, faces, climbs, images
  - Analyser le format holdsList
  - Exporter en JSON
  - Statut : À faire (0%)

- **TODO 03 avancé à 85%** - Analyse Hermes réussie
  - Installation de hermes-dec (décompileur Hermes v96)
  - Désassemblage complet du bundle (95 Mo)
  - Configuration app extraite (`baseURL`, `appVersion`, etc.)
  - Flux authentification documenté (`Token <value>`)
  - 40+ endpoints API identifiés et documentés
  - 100+ actions Redux cataloguées
  - Structures de données Climb/Face extraites
  - **Création base documentaire** : `/docs/reverse_engineering/`
  - Rapport : `/docs/reports/SESSION_2025-12-20_analyse_hermes.md`

## 2025-12-20 (après-midi)

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
