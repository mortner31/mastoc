# STATUS - TODO 01 : Analyse et Décompilation de l'Application d'Escalade

**Progression** : 80%

## ✅ Complété

### Phase 1 : Extraction et Décompilation
- [x] Extraire l'APK depuis le téléphone
- [x] Identifier le nom du package et les informations de base
- [x] Décompiler l'application (APKTool)
- [x] Analyser la structure du projet décompilé

**Résultats** : Application identifiée (com.getstokt.stokt v6.1.13), APK extrait et décompilé avec succès.

### Phase 2 : Analyse Fonctionnelle
- [x] Analyser le mécanisme de données (Firebase structure)
- [x] Analyser le bundle JavaScript (format Hermes bytecode)
- [x] Identifier la structure de l'API REST (40+ endpoints)
- [x] Documenter le schéma de données
- [x] Identifier le système de gestion des images interactives
- [x] Comprendre le système de cache/offline
- [x] Identifier les limitations du mode hors ligne
- [x] Cartographier les endpoints API

**Résultats** :
- Architecture : React Native + Expo SDK 53 + Redux
- **Backend réel** : `https://www.sostokt.com/api/` (pas getstokt.com)
- 150+ actions Redux identifiées
- Système de prises : coordonnées X/Y sur images, max 1500 prises/mur
- **Cause du problème offline confirmée** : Aucune persistance locale

### Phase 2.5 : Test d'Extraction API Directe (2025-12-20)
- [x] Authentification sur l'API (`/api/token-auth`)
- [x] Identification de la salle Montoboard
- [x] Test des endpoints disponibles

**Résultats** :
- ✅ Authentification réussie (format `username` + `password`)
- ✅ Token obtenu (format DRF)
- ✅ Endpoint `/api/gyms` fonctionne → liste complète des salles
- ✅ **Montoboard** : ID `be149ef2-317d-4c73-8d7d-50074577d2fa`
- ❌ Endpoints `/api/faces`, `/api/climbs` : erreurs 500 ou timeout
- ❌ Endpoints détaillés (`/api/gyms/{id}`) : 404

**Rapports** :
- `/docs/reports/SESSION_2025-11-10_extraction_stockt.md`
- `/docs/reports/ANALYSE_STRUCTURE_FIREBASE_API.md`
- `/docs/reports/SESSION_2025-12-20_analyse_complete_stokt.md`
- `/docs/reports/SESSION_2025-12-20_patch_apk_mitm.md`
- `/docs/reports/SESSION_2025-12-20_api_extraction.md`

## ⏳ Bloqué

### Extraction des données réelles
- Patch APK échoué (bug manifest `@null`)
- API directe : endpoints non accessibles ou différents de l'app
- Risque de bannissement si trop de requêtes exploratoires

**→ Nécessite analyse approfondie du code avant nouvelles tentatives**

## 📋 À faire

### Phase 3 : Analyse Approfondie du Code (NOUVEAU)
- [ ] Installer un décompileur Hermes (`hermes-dec`)
- [ ] Décompiler le bundle `index.android.bundle`
- [ ] Analyser le flux de données Redux complet
- [ ] Identifier les requêtes exactes pour récupérer les climbs d'un gym
- [ ] Mapper les paramètres requis pour chaque endpoint

**→ Voir TODO 03 pour le plan détaillé**

### Phase 4 : Documentation et Conception
- [ ] Créer un diagramme de flux de données
- [ ] Lister les fonctionnalités critiques à reproduire
- [ ] Concevoir le schéma SQLite pour mastoc
- [ ] Proposer une architecture offline-first

## 📝 Notes

- **Nom de l'application** : Stōkt
- **Package** : com.getstokt.stokt
- **Version analysée** : 6.1.13
- **Framework** : React Native + Expo SDK 53
- **Backend** : `https://www.sostokt.com` (PythonAnywhere)
- **Bundle** : Hermes bytecode v96 (nécessite décompilation)
- **Salle cible** : Montoboard (Caraman, France)
