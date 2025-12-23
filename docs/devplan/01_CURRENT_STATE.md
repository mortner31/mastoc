# État Actuel du Projet mastoc

**Date** : 2025-12-23

---

## 1. Architecture du code

### Structure du package Python

```
mastoc/
├── pyproject.toml              # Configuration package
├── src/mastoc/
│   ├── api/                    # Communication API Stokt
│   │   ├── client.py           # 564 lignes - Client HTTP
│   │   └── models.py           # 406 lignes - Dataclasses
│   ├── core/                   # Logique métier
│   │   ├── colormaps.py        # Palettes de couleurs heatmaps
│   │   ├── filters.py          # Filtres par grade, setter
│   │   ├── hold_index.py       # 317 lignes - Index prises ↔ blocs
│   │   ├── picto.py            # 347 lignes - Génération pictos
│   │   ├── picto_cache.py      # Cache disque des miniatures
│   │   ├── social_actions.py   # Actions like/bookmark/send
│   │   ├── social_loader.py    # 226 lignes - Chargement async
│   │   └── sync.py             # 244 lignes - Synchronisation API
│   ├── db/                     # Persistance
│   │   ├── database.py         # Connexion SQLite
│   │   └── repository.py       # 337 lignes - CRUD climbs/holds
│   └── gui/                    # Interface graphique
│       ├── app.py              # 689 lignes - Application principale
│       ├── climb_viewer.py     # 463 lignes - Visualiseur bloc
│       ├── hold_selector.py    # 779 lignes - Sélection par prises
│       ├── creation/           # Module création de blocs
│       │   ├── controller.py   # 254 lignes - Navigation wizard
│       │   ├── state.py        # 282 lignes - État partagé
│       │   ├── wizard.py       # 458 lignes - Fenêtre principale
│       │   └── screens/
│       │       ├── select_holds.py  # 374 lignes
│       │       └── climb_info.py    # 288 lignes
│       ├── widgets/
│       │   ├── climb_detail.py     # 472 lignes
│       │   ├── climb_list.py       # 381 lignes
│       │   ├── hold_overlay.py     # 542 lignes - Overlay pyqtgraph
│       │   ├── climb_renderer.py   # Rendu PIL
│       │   ├── social_panel.py     # Affichage interactions
│       │   └── my_climbs_panel.py
│       └── dialogs/
│           └── login.py            # Dialog authentification
└── tests/                      # 225 tests
    ├── test_api.py
    ├── test_creation.py        # 43 tests création
    ├── test_filters.py
    ├── test_hold_index.py
    ├── test_models.py
    ├── test_repository.py
    ├── test_social.py
    └── test_sync.py
```

### Métriques de code

| Module | Lignes | Tests | Couverture |
|--------|--------|-------|------------|
| api/ | ~970 | 45 | Complète |
| core/ | ~1 400 | 80 | Complète |
| db/ | ~450 | 35 | Complète |
| gui/ | ~4 500 | 65 | Partielle (UI) |
| **Total** | ~10 100 | 225 | ~85% |

---

## 2. Fonctionnalités implémentées

### 2.1 API Stokt

| Fonctionnalité | Méthode | Statut |
|----------------|---------|--------|
| Authentification | `POST /api/token-auth` | OK |
| Liste climbs | `GET /api/gyms/{id}/climbs` | OK |
| Détail climb | `GET /api/climbs/{id}` | OK |
| Setup face | `GET /api/faces/{id}/setup` | OK |
| Création climb | `POST /api/faces/{id}/climbs` | OK |
| Interactions sociales | GET likes/comments/sends | OK |
| Like/Unlike | `POST/DELETE` | OK |
| Bookmark | `POST/DELETE` | OK |

### 2.2 Interface graphique

| Application | Description | Statut |
|-------------|-------------|--------|
| `app.py` | Liste principale + visualisation | OK |
| `hold_selector.py` | Recherche par prises | OK |
| `creation_app.py` | Wizard création bloc | OK (97%) |
| `climb_viewer.py` | Visualisation standalone | OK |

### 2.3 Visualisation

| Feature | Description | Statut |
|---------|-------------|--------|
| Image haute résolution | 2263x3000 pixels | OK |
| Polygones des prises | Contours colorés | OK |
| Marqueurs START | Lignes tape (V ou centrale) | OK |
| Marqueurs TOP | Double polygone 135% | OK |
| Marqueurs FEET | Contour cyan | OK |
| Heatmaps | 7 palettes + 4 modes | OK |
| Pictos (miniatures) | Cache disque | OK |

### 2.4 Modes de coloration (hold_overlay)

| Mode | Description |
|------|-------------|
| MIN | Couleur selon grade minimum des blocs |
| MAX | Couleur selon grade maximum |
| FREQUENCY | Quantiles de fréquence d'utilisation |
| RARITY | 5 niveaux de rareté |

---

## 3. TODOs et progression

### TODOs terminés (archivés)

| TODO | Description | Date |
|------|-------------|------|
| 01 | Analyse app Stokt | 2025-11 |
| 02 | Schéma SQLite | Fusionné TODO 05 |
| 03 | Analyse Hermes | 2025-12-20 |
| 04 | Extraction Montoboard | 2025-12-21 |
| 05 | Package Python | 2025-12-21 |
| 06 | Interface filtrage | 2025-12-22 |
| 07 | Interactions sociales | 2025-12-22 |
| 08 | Heatmaps | 2025-12-22 |
| 11 | Ergonomie UI/UX | 2025-12-22 |

### TODOs en cours

| TODO | Description | Progression | Reste |
|------|-------------|-------------|-------|
| 09 | Listes personnalisées | 5% | Investigation API |
| 10 | Création de blocs | 97% | Tests edge cases |
| 12 | Hold Annotations | 0% | Nécessite serveur |

---

## 4. Données locales

### Base SQLite

| Table | Enregistrements |
|-------|-----------------|
| climbs | 1017 |
| holds | 776 |
| faces | 1 |
| sync_status | 1 |

### Fichiers

| Type | Emplacement | Taille |
|------|-------------|--------|
| Image mur | `data/montoboard.jpg` | ~2 MB |
| Base SQLite | `data/mastoc.db` | ~500 KB |
| Pictos cache | `~/.mastoc/pictos/` | ~50 MB |

---

## 5. Dépendances

### Python packages

```
PyQt6>=6.4.0
pyqtgraph>=0.13.0
Pillow>=10.0.0
requests>=2.28.0
numpy>=1.24.0
```

### Versions

| Composant | Version |
|-----------|---------|
| Python | 3.11+ |
| PyQt6 | 6.4.0 |
| SQLite | 3.x |

---

## 6. Points forts

1. **Architecture modulaire** : Séparation claire api/core/db/gui
2. **Tests solides** : 225 tests, couverture >85%
3. **Documentation** : TODOs structurés, timeline complète
4. **Offline-first** : Toutes les données en local
5. **Performance** : Chargement rapide, cache pictos

---

## 7. Points d'amélioration

1. **UI Python** : PyQt6 n'est pas idéal pour mobile
2. **Pas de serveur custom** : Dépendance totale à Stokt
3. **Single-user** : Pas de support multi-utilisateurs
4. **Pas d'export** : Données non portables

---

## 8. Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| API Stokt change | Moyenne | Élevé | Serveur personnel |
| Ban compte Stokt | Faible | Critique | Backup local |
| Perte données locales | Faible | Moyen | Export JSON |
| PyQt6 obsolète | Faible | Moyen | Migration Compose |

---

*Document généré le 2025-12-23*
