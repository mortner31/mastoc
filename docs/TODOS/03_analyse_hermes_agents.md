# TODO 03 - Analyse Approfondie du Bundle Hermes via Agents

## 🎯 Objectif

Analyser en profondeur le code source de l'application Stōkt pour comprendre exactement comment elle communique avec l'API, afin de pouvoir extraire les données de Montoboard sans risquer de bannissement.

## 🚫 Contraintes

- **Pas de requêtes exploratoires** sur l'API (risque de bannissement)
- **Analyse statique uniquement** dans un premier temps
- **Documenter avant d'agir** : comprendre le flux complet avant toute requête

## 📋 Tâches

### Phase 1 : Installation des outils

- [ ] Rechercher et installer un décompileur Hermes
  - Options : `hermes-dec`, `hbctool`, `hermes-parser`
  - Vérifier compatibilité avec bytecode v96
- [ ] Tester la décompilation sur le bundle
- [ ] Valider que le code est lisible

**Agent suggéré** : Agent Explore pour rechercher les outils

### Phase 2 : Analyse du flux d'authentification

- [ ] Identifier la fonction/module d'authentification
- [ ] Documenter le format exact de la requête token-auth
- [ ] Identifier comment le token est stocké (AsyncStorage?)
- [ ] Comprendre le refresh token si applicable

**Agent suggéré** : Agent Explore avec recherche ciblée

### Phase 3 : Analyse du flux "My Gym"

- [ ] Trouver le code qui gère `stokt-app/myGym/*`
- [ ] Identifier la séquence de requêtes au démarrage
- [ ] Documenter les endpoints appelés pour charger un gym
- [ ] Comprendre les paramètres (gym_id, pagination, filtres)

**Agent suggéré** : Agent Explore pour analyser le code Redux

### Phase 4 : Analyse du flux "Climbs"

- [ ] Trouver le code qui gère `stokt-app/problem/*`
- [ ] Identifier comment les climbs sont récupérés
- [ ] Comprendre la structure complète d'un climb (holds, coordinates)
- [ ] Documenter le format des réponses API

**Agent suggéré** : Agent Explore pour analyser les reducers

### Phase 5 : Analyse du flux "Faces/Walls"

- [ ] Trouver le code qui gère `stokt-app/faces/*`
- [ ] Identifier comment les murs sont récupérés
- [ ] Comprendre le lien entre face/wall/climb
- [ ] Documenter les images et leur système de coordonnées

**Agent suggéré** : Agent Explore

### Phase 6 : Synthèse et validation

- [ ] Créer un diagramme de séquence des requêtes
- [ ] Documenter les headers requis (User-Agent, etc.)
- [ ] Identifier l'ordre exact des appels au démarrage de l'app
- [ ] Préparer un script de test minimal et sûr

**Agent suggéré** : Agent Plan pour synthétiser

## 📚 Fichiers de référence

| Fichier | Description |
|---------|-------------|
| `/extracted/stockt_decompiled/assets/index.android.bundle` | Bundle Hermes à décompiler |
| `/docs/reports/ANALYSE_STRUCTURE_FIREBASE_API.md` | Actions Redux identifiées |
| `/docs/reports/SESSION_2025-12-20_api_extraction.md` | Résultats des tests API |

## 🎯 Résultats attendus

1. **Documentation complète** du flux de données de l'app
2. **Script sûr** pour récupérer les données Montoboard
3. **Aucun risque** de bannissement (requêtes identiques à l'app)
4. **Données exportables** pour l'app offline

## 💡 Stratégie d'agents

### Utilisation recommandée

```
1. Agent Explore (quick) → trouver les fichiers/fonctions clés
2. Agent Explore (medium) → analyser un flux spécifique
3. Agent Explore (very thorough) → analyse complète d'un module
4. Agent Plan → synthétiser et créer le plan d'extraction
```

### Prompts types pour les agents

**Recherche d'authentification** :
```
Analyse le bundle décompilé pour trouver :
- La fonction qui appelle /api/token-auth
- Le format de la requête (headers, body)
- Comment le token est stocké après login
```

**Recherche de flux gym** :
```
Analyse le code Redux pour comprendre :
- Quand et comment les données d'un gym sont chargées
- La séquence des actions dispatched
- Les endpoints appelés avec leurs paramètres
```

## ⚠️ Points d'attention

1. **Bundle volumineux** : le fichier fait plusieurs Mo, analyse par sections
2. **Code minifié** : les noms de variables sont courts, se baser sur les strings
3. **Actions Redux** : utiliser les noms d'actions comme points d'entrée
4. **Endpoints connus** : se concentrer sur ceux qui fonctionnent (`/api/gyms`)

## 📝 Notes

- Le bundle est en Hermes bytecode v96
- L'app utilise Redux avec des actions bien nommées (`stokt-app/*`)
- Les URLs sont probablement construites dynamiquement
- Chercher aussi les constantes de configuration
