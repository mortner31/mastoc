# TODO 05 - Structure Package Python mastoc

## Objectif

Restructurer le code Python existant en un package installable (`pip install -e .`) pour :
- Servir de **prototype** avant l'application mobile finale
- Permettre de **tester les concepts** d'interaction avec la BD de climbs et prises
- Fournir une **base de code** réutilisable et testée

## Stack technique

| Composant | Choix | Justification |
|-----------|-------|---------------|
| GUI | PyQtGraph + PyQt6 | Visualisation interactive rapide, affichage des polygones de prises |
| BD locale | SQLite | Stockage offline, léger, portable |
| HTTP | requests | API client existant déjà fonctionnel |
| Config | python-dotenv | Gestion sécurisée des credentials |
| Tests | pytest | Tests unitaires et d'intégration |

## Architecture cible

```
mastoc/
├── pyproject.toml          # Configuration package (pip install -e .)
├── src/
│   └── mastoc/
│       ├── __init__.py
│       ├── api/            # Client API Stokt
│       │   ├── __init__.py
│       │   ├── client.py   # StoktAPI (refactoré)
│       │   └── models.py   # Dataclasses Climb, Hold, Face, etc.
│       ├── db/             # Stockage local SQLite
│       │   ├── __init__.py
│       │   ├── database.py # Gestion connexion, migrations
│       │   └── models.py   # Tables SQLite (climbs, holds, sync_state)
│       ├── gui/            # Interface PyQtGraph
│       │   ├── __init__.py
│       │   ├── app.py      # Application principale
│       │   ├── widgets/    # Composants réutilisables
│       │   │   ├── board_view.py   # Vue du mur avec prises
│       │   │   ├── climb_list.py   # Liste des climbs avec filtres
│       │   │   └── climb_viewer.py # Visualisation d'un climb
│       │   └── dialogs/    # Dialogs (login, settings)
│       └── core/           # Logique métier
│           ├── __init__.py
│           ├── sync.py     # Synchronisation API ↔ BD locale
│           └── filters.py  # Filtres (niveau, auteur, prises)
├── tests/
│   ├── test_api.py
│   ├── test_db.py
│   └── test_filters.py
└── data/                   # Données locales (gitignored)
    ├── mastoc.db          # Base SQLite
    └── images/             # Images téléchargées
```

## Fonctionnalités

### a) Stockage de la BD
- [x] Télécharger les climbs via API (code existant)
- [ ] Schéma SQLite : tables climbs, holds, faces, sync_metadata
- [ ] Stocker la **date du dernier téléchargement** dans sync_metadata
- [ ] Sauvegarder l'image du mur localement

### b) Bouton de mise à jour de la BD
- [ ] Vérifier les nouveaux climbs depuis la dernière sync
- [ ] Télécharger uniquement les différences (delta sync)
- [ ] Afficher la progression dans l'interface

### c) Bouton de régénération du token
- [ ] Détecter expiration token (erreur 401)
- [ ] Dialog de re-login si token invalide
- [ ] Stocker token de manière sécurisée (keyring ou .env)

### d) Interface de balayage des climbs
- [ ] Liste scrollable des climbs
- [ ] Filtre par **niveau** (dropdown multi-select : 4, 5, 6A, 6B...)
- [ ] Filtre par **auteur** (dropdown avec setters)
- [ ] Affichage preview : nom, grade, nb prises
- [ ] Click → affiche le climb sur le mur

### e) Interface de balayage par prises

**→ Voir TODO 06** : Cette fonctionnalité est détaillée dans le TODO 06 (Interface de Filtrage et Sélection de Blocs).

### f) Interface de création de climb (optionnel)
- [ ] Mode "création" : click sur prises pour les ajouter
- [ ] Définir type de prise (S/O/F/T)
- [ ] Définir feetRule
- [ ] Sauvegarder localement (isPrivate=true par défaut)
- [ ] Push vers API (futur)

## Références

- API client existant : `/mastoc/src/stokt_api.py`
- Structure de données : `/docs/reverse_engineering/04_STRUCTURES.md`
- Endpoints : `/docs/reverse_engineering/03_ENDPOINTS.md`
- Données extraites : `/extracted/data/montoboard_ALL_climbs.json`
- Setup prises : `/extracted/data/montoboard_setup.json`
- **TODO 06** : `/docs/TODOS/06_interface_filtrage_blocs.md` (interface de sélection par prises)

## Notes techniques

### Format holdsList
```
S829279 O828906 F829104 T829220
│       │       │       │
│       │       │       └── Top (prise finale)
│       │       └── Feet (pied obligatoire)
│       └── Other (prise normale)
└── Start (prise de départ)
```

### Coordonnées prises
- `centroidStr` : centre de la prise en pixels (format "x y")
- `polygonStr` : points du polygone SVG (format "x,y x,y ...")
- Image référence : 2263 x 3000 pixels

### Statistiques Montoboard
- 1017 climbs
- 776 prises
- 121 grimpeurs
- IDs prises : 828902 → 829677
