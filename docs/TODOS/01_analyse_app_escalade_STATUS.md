# STATUS - TODO 01 : Analyse et Décompilation de l'Application d'Escalade

**Progression** : 70%

## ✅ Complété

### Phase 1 : Extraction et Décompilation
- [x] Extraire l'APK depuis le téléphone
- [x] Identifier le nom du package et les informations de base
- [x] Décompiler l'application (APKTool)
- [x] Analyser la structure du projet décompilé

**Résultats** : Application identifiée (com.getstokt.stokt v6.1.13), APK extrait et décompilé avec succès.

### Phase 2 : Analyse Fonctionnelle
- [x] Analyser le mécanisme de données (Firebase structure)
- [x] Analyser le bundle JavaScript (format Hermes)
- [x] Identifier la structure de l'API REST (40+ endpoints)
- [x] Documenter le schéma de données
- [x] Identifier le système de gestion des images interactives
- [x] Comprendre le système de cache/offline
- [x] Identifier les limitations du mode hors ligne
- [x] Cartographier les endpoints API

**Résultats** :
- Architecture : React Native + Expo SDK 53 + Redux
- Backend : https://www.getstokt.com/api/
- 150+ actions Redux identifiées
- Système de prises : coordonnées X/Y sur images, max 1500 prises/mur
- **Cause du problème offline confirmée** : Aucune persistance locale (pas de SQLite/AsyncStorage)

**Rapports** :
- `/docs/reports/SESSION_2025-11-10_extraction_stockt.md`
- `/docs/reports/ANALYSE_STRUCTURE_FIREBASE_API.md`
- `/docs/reports/SESSION_2025-12-20_analyse_complete_stokt.md`

## ⏳ En cours

Aucune tâche en cours.

## 📋 À faire

### Phase 3 : Extraction des Données Réelles
- [ ] Capture réseau avec mitmproxy
- [ ] Extraire les données JSON réelles (blocs, murs, prises)
- [ ] Documenter la structure exacte des réponses API
- [ ] Créer des exemples de données de référence

### Phase 4 : Documentation et Conception
- [ ] Créer un diagramme de flux de données
- [ ] Lister les fonctionnalités critiques à reproduire
- [ ] Concevoir le schéma SQLite pour mastock
- [ ] Proposer une architecture offline-first

## 📝 Notes

- **Nom de l'application** : Stōkt
- **Package** : com.getstokt.stokt
- **Version analysée** : 6.1.13
- **Framework** : React Native + Expo SDK 53
- **Problème identifié** : Pas de persistance locale → échec offline
- **Objectif** : Créer une version simplifiée et offline-first
