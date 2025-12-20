# TODO 01 - Analyse et Décompilation de l'Application d'Escalade

## 🎯 Objectif

Analyser et décompiler l'application mobile d'escalade existante pour comprendre son fonctionnement, notamment :
- Le système de visualisation des blocs via images interactives
- Les mécanismes de stockage et d'accès aux données
- Pourquoi l'application ne fonctionne pas correctement hors ligne
- Identifier les données pertinentes à extraire pour une version simplifiée

## 📋 Tâches

### Phase 1 : Extraction et Décompilation
- [ ] Extraire l'APK depuis le téléphone
- [ ] Identifier le nom du package et les informations de base
- [ ] Décompiler l'application (APKTool, jadx, etc.)
- [ ] Analyser la structure du projet décompilé

### Phase 2 : Analyse Fonctionnelle
- [ ] Identifier le système de gestion des images interactives
- [ ] Analyser le mécanisme de données (API, base locale, etc.)
- [ ] Comprendre le système de cache/offline
- [ ] Identifier les limitations du mode hors ligne
- [ ] Cartographier les endpoints API (si applicable)

### Phase 3 : Extraction des Données
- [ ] Identifier les formats de données utilisés
- [ ] Extraire les données pertinentes (blocs, salles, etc.)
- [ ] Documenter la structure des données
- [ ] Créer des exemples de données de référence

### Phase 4 : Documentation
- [ ] Documenter l'architecture de l'application
- [ ] Créer un diagramme de flux de données
- [ ] Lister les fonctionnalités critiques à reproduire
- [ ] Proposer une architecture simplifiée pour la nouvelle version

## 📚 Références

- Documentation à créer dans `/docs/`
- Rapports d'analyse dans `/docs/reports/`
- Datasets extraits dans `/tools/datasets/` (si nécessaire)

## 🎯 Résultat Attendu

Une base documentaire complète permettant de :
1. Comprendre le fonctionnement de l'application originale
2. Identifier les données et fonctionnalités essentielles
3. Proposer une architecture pour une version simplifiée et offline-first
4. Avoir tous les éléments pour reprendre le travail ultérieurement
