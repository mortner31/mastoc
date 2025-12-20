# Rapport de Session - Découverte API Stokt

**Date** : 2025-12-20

## Objectifs Atteints

- Analyse approfondie du code décompilé React Native (Hermes bytecode)
- Découverte des endpoints API fonctionnels
- Création d'un client Python complet
- Extraction de 1017 climbs du gym Montoboard

## Contexte

Le TODO 04 était bloqué car les endpoints testés retournaient des erreurs 404/403. L'analyse du code décompilé a révélé que les URLs utilisées étaient incorrectes.

## Méthodologie

### 1. Analyse du code décompilé

Fichier analysé : `/extracted/stockt_decompiled/decompiled/stokt_decompiled.js`

Fonctions clés identifiées :
- `fetchMySentClimbs` (ligne 442389)
- `fetchGymRecentClimbs` (ligne 458971)
- `getWalls` (ligne 440447)
- `fetchGymSummary` (ligne 440848)
- `setToken` (ligne 432060)

### 2. Découverte du pattern de construction d'URL

```javascript
// Pattern découvert dans le code décompilé
r4 = 'api/gyms/';
r1 = '/my-sent-climbs';
r1 = HermesInternal.concat(r4, gymId, r1);
// Résultat: 'api/gyms/{gymId}/my-sent-climbs'
```

### 3. Comparaison URLs testées vs correctes

| Ce qu'on testait (FAUX) | Ce qui marche (CORRECT) |
|-------------------------|-------------------------|
| `api/users/{id}/sent-climbs` | `api/gyms/{gymId}/my-sent-climbs` |
| `api/gyms/{id}/climbs` (sans params) | `api/gyms/{gymId}/climbs?max_age={days}` |
| `api/gyms/{id}/faces` | `api/gyms/{gymId}/walls` (inclut les faces) |
| `api/gyms/{id}/` | `api/gyms/{gymId}/summary` |

## Endpoints Découverts

### Fonctionnels

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/token-auth` | POST | Auth (form: username, password) |
| `api/users/me` | GET | Profil utilisateur |
| `api/version` | GET | Version API (1.3.0) |
| `api/my-notifications` | GET | Notifications |
| `api/gyms/{id}/summary` | GET | Résumé gym |
| `api/gyms/{id}/walls` | GET | Murs + faces |
| `api/gyms/{id}/climbs?max_age={days}` | GET | Climbs (paginé) |
| `api/gyms/{id}/my-sent-climbs` | GET | Mes climbs validés |

### Non fonctionnels

| Endpoint | Erreur | Note |
|----------|--------|------|
| `api/faces/{faceId}` | 403 | Permission refusée |
| `api/faces/{faceId}/latest-climbs/paginated` | 404 | Endpoint protégé/différent |
| `api/efforts` | 403 | Permission refusée |

## Format holdsList Décodé

```
S829279 S829528 O828906 O828964 T829009
│       │       │       │       └── T = Top (prise finale)
│       │       │       └── O = Other (prise normale)
│       │       └── O = Other
│       └── S = Start (départ, 2ème main)
└── S = Start (départ, 1ère main)
```

Types découverts :
- **S** = Start (prise de départ)
- **O** = Other (prise normale)
- **F** = Feet (pied obligatoire, pour "pieds des mains")
- **T** = Top (prise finale)

Le nombre après la lettre = ID unique de la prise sur la face.

## Résultats d'Extraction

### Données récupérées

| Métrique | Valeur |
|----------|--------|
| Gym | Montoboard |
| Location | Caraman, France |
| Total climbs (summary) | 1174 |
| Climbs sur la face | 1017 |
| Climbs extraits | **1017** (100%) |

### Répartition par grade

```
4: 14    |  6B: 115   |  7A+: 72
4+: 42   |  6B+: 104  |  7B: 43
5: 37    |  6C: 130   |  7B+: 8
5+: 40   |  6C+: 79   |  7C: 2
6A: 78   |  7A: 127   |  8A: 2
6A+: 93  |            |  ?: 31
```

### Différence 1174 vs 1017

La différence de 157 climbs s'explique par :
- Climbs privés (`isPrivate: true`)
- Climbs sur d'autres faces (le gym n'a qu'une face active)
- Climbs archivés/supprimés

## Livrables

### Scripts Python créés

1. **`mastock/src/stokt_api.py`**
   - Client API complet
   - Méthodes : `login()`, `get_gym_summary()`, `get_gym_walls()`, `get_gym_climbs()`, `get_all_gym_climbs()`, `get_my_sent_climbs()`
   - Helper : `parse_holds_list()`

2. **`mastock/src/extract_all_climbs.py`**
   - Script d'extraction complète
   - Pagination automatique
   - Export JSON

### Données exportées

- `extracted/data/montoboard_ALL_climbs.json` - 1017 climbs
- `extracted/images/face_small.jpg` - Image de la face

## Découvertes Techniques

### Mécanisme d'authentification

```python
# Le token est ajouté aux headers par défaut d'axios
axios.defaults.headers.common['Authorization'] = 'Token ' + token
```

### Configuration axios dans l'app

```javascript
{
  baseURL: 'https://www.sostokt.com/',
  timeout: 60000,
  headers: {
    post: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }
}
```

### Pagination

L'API utilise une pagination standard Django REST Framework :
```json
{
  "count": 1017,
  "next": "https://www.sostokt.com/api/gyms/.../climbs?max_age=9999&page=2",
  "previous": null,
  "results": [...]
}
```

## Prochaines Étapes

1. **Mapper les IDs de prises aux coordonnées sur l'image**
   - Analyser comment l'app affiche les prises sur l'image
   - Chercher un endpoint qui retourne les positions

2. **Explorer d'autres gyms**
   - Tester l'extraction sur d'autres gyms Stokt
   - Valider la généricité du client

3. **Analyser la structure complète d'un climb**
   - Comprendre tous les champs (attemptsToSend, lastEffortDate, etc.)
   - Documenter le système de notation (ircra, hueco, font, dankyu)
