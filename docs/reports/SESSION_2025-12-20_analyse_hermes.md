# Rapport de Session - Analyse Hermes Bundle Stōkt

**Date** : 2025-12-20

## 🎯 Objectifs Atteints

- ✅ Installation de hermes-dec (décompileur Hermes v96)
- ✅ Désassemblage complet du bundle (95 Mo de code)
- ✅ Extraction de la configuration de l'app
- ✅ Documentation complète du flux d'authentification
- ✅ Identification de 40+ endpoints API
- ✅ Extraction des structures de données (Climb, Face, etc.)
- ✅ Documentation de 100+ actions Redux
- ✅ Création de la base documentaire pyramidale

## 📊 Résultats

### Configuration Découverte

| Élément | Valeur |
|---------|--------|
| Base URL | `https://www.sostokt.com/` |
| App Version | `6.1.13` |
| Content-Type | `application/x-www-form-urlencoded` |
| Timeout | `60000ms` |
| Auth Header | `Authorization: Token <value>` |

### Endpoints Clés Identifiés

- `api/token-auth` - Authentification
- `api/gyms/` - Liste des gyms
- `api/faces/` - Faces/murs
- `api/faces/{id}/climbs` - Climbs d'une face
- `api/climbs/` - Tous les climbs
- `api/walls/` - Murs
- `api/efforts/` - Tentatives

### Structure Climb

```javascript
{
  'id': '',
  'name': '',
  'gymCreated': '',
  'crowdGrade': null,
  'climbSetters': null,
  'dateCreated': '',
  'holdsList': '',
  'attemptsToSend': 0,
  'bookmarkedByUser': false
}
```

### Paramètres Pagination

- `offset` - Position de départ
- `page_size` - Taille (défaut: 30)
- `ordering` - Tri (`-date_updated`)

## 📁 Fichiers Créés

```
/docs/reverse_engineering/
├── INDEX.md              - Index racine
├── 01_CONFIGURATION.md   - Configuration app
├── 02_AUTHENTIFICATION.md - Flux auth
├── 03_ENDPOINTS.md       - Liste endpoints
├── 04_STRUCTURES.md      - Structures données
└── 05_REDUX_ACTIONS.md   - Actions Redux
```

## 🔧 Outils Utilisés

- **hermes-dec** : Désassembleur/décompileur Hermes
- **grep/strings** : Extraction de patterns

## 🚀 Prochaines Étapes

1. Tester les endpoints avec le token déjà obtenu
2. Récupérer les données de Montoboard (gym_id connu)
3. Analyser le format exact des coordonnées de prises
4. Créer un script d'extraction automatisé

## ⚠️ Notes

- Le décompileur (hbc-decompiler) crash sur ce bundle
- Le désassembleur (hbc-disassembler) fonctionne parfaitement
- Les strings et objets sont bien extraits du bytecode
- Le code est minifié mais les actions Redux et endpoints sont lisibles

---

**Durée de session** : ~1h
**Statut TODO 03** : 85%
