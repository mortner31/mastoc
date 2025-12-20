# Base Documentaire Reverse Engineering - Stōkt API

**Index racine de la documentation de reverse engineering**

## Protocole de Documentation

### Structure Pyramidale

```
INDEX.md (ce fichier)
├── 01_CONFIGURATION.md    - Configuration et constantes de l'app
├── 02_AUTHENTIFICATION.md - Flux d'authentification
├── 03_ENDPOINTS.md        - Liste des endpoints API
├── 04_STRUCTURES.md       - Structures de données (objets)
├── 05_REDUX_ACTIONS.md    - Actions Redux par module
└── 06_SEQUENCES.md        - Diagrammes de séquence
```

### Règles de Mise à Jour

1. **Chaque découverte** doit être documentée dans le fichier approprié
2. **Références croisées** : utiliser `[voir FICHIER.md]` pour lier les docs
3. **Horodatage** : chaque modification majeure est datée
4. **Source** : indiquer la ligne/fonction d'origine dans le bundle

---

## Résumé des Découvertes (2025-12-20)

### Configuration Principale

| Élément | Valeur |
|---------|--------|
| Base URL | `https://www.sostokt.com/` |
| App Version | `6.1.13` |
| Content-Type | `application/x-www-form-urlencoded` |
| Timeout | `60000ms` |
| Bytecode | Hermes v96 |

### Authentification

- **Endpoint** : `POST api/token-auth`
- **Body** : `username=<email>&password=<password>`
- **Header** : `Authorization: Token <token>`

### Endpoints Principaux

| Endpoint | Description |
|----------|-------------|
| `api/token-auth` | Authentification |
| `api/gyms/` | Liste des gyms |
| `api/gyms/paginated` | Gyms avec pagination |
| `api/faces/` | Faces/murs d'un gym |
| `api/faces/{id}/climbs` | Climbs d'une face |
| `api/climbs/` | Climbs |
| `api/walls/` | Murs |
| `api/efforts/` | Tentatives/ascensions |
| `api/users/me` | Profil utilisateur |

### Paramètres de Pagination

| Paramètre | Description |
|-----------|-------------|
| `offset` | Position de départ |
| `page_size` | Taille de page (défaut: 30) |
| `ordering` | Tri (ex: `-date_updated`) |
| `limit` | Limite de résultats |

---

## Fichiers Source

| Fichier | Taille | Description |
|---------|--------|-------------|
| `stokt_disasm.hasm` | 95 Mo | Désassemblage complet |
| `stokt_decompiled.js` | 40 Mo | Décompilation partielle |
| `index.android.bundle` | 7.3 Mo | Bundle Hermes original |

---

**Dernière mise à jour** : 2025-12-20
**Statut** : En cours d'exploration
