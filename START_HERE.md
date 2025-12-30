# Start Here - mastoc

**Point d'entrée rapide pour comprendre le projet et commencer à travailler.**

## Qu'est-ce que mastoc ?

mastoc est un projet visant à créer une application personnelle pour visualiser et gérer des blocs d'escalade. Le projet part de l'analyse d'une application existante (Stokt) qui présente des problèmes en mode hors ligne, avec pour objectif de créer une version simplifiée et optimisée pour un usage offline-first, spécialisée sur la salle **Montoboard** (Caraman, France).

## Objectif Actuel

**Prototype Python mastoc** : COMPLET

Le package Python est fonctionnel avec deux applications :

### 1. Application principale (`gui/app.py`)
- Liste de climbs avec filtres (grade, setter, texte)
- Visualisation des blocs sur le mur
- Synchronisation API

```bash
cd /media/veracrypt1/Repositories/mastoc/mastoc
python -m mastoc.gui.app
```

### 2. Sélecteur par prises (`gui/hold_selector.py`)

**Deux modes distincts :**

1. **Mode Sélection** : Overlay pyqtgraph avec couleurs par niveau
   - Double slider de niveau (4 → 8A)
   - Coloration dynamique (vert→rouge)
   - Multi-sélection de prises (logique ET)
   - Bouton Undo pour annuler

2. **Mode Parcours** : Rendu PIL identique à `app.py`
   - Prises du bloc en couleur originale
   - Contours blancs, FEET cyan, TOP double contour
   - Navigation Préc/Suiv

```bash
cd /media/veracrypt1/Repositories/mastoc/mastoc
python -m mastoc.gui.hold_selector
```

### 3. Création de bloc (`gui/creation_app.py`) - TODO 10

Wizard multi-écrans pour créer de nouveaux blocs :

1. **Écran 1** : Sélection des prises par type (START, OTHER, FEET, TOP)
2. **Écran 2** : Formulaire (nom, grade, description)
3. **Soumission** : POST vers l'API Stokt

```bash
cd /media/veracrypt1/Repositories/mastoc/mastoc
python -m mastoc.gui.creation_app
```

## TODOs

| TODO | Description | Statut |
|------|-------------|--------|
| 01 | Analyse de l'app Stokt | 80% - Termine |
| 02 | Conception schema SQLite | Fusionne dans TODO 05 |
| 03 | Analyse Hermes via agents | 95% - Termine |
| 04 | Test extraction Montoboard | 100% - Termine |
| 05 | Structure Package Python | 100% - **Archive** |
| 06 | Interface Filtrage Blocs | 100% - **Termine** |
| 07 | Interactions Blocs | 45% - En cours |
| 08 | Modes Coloration Heatmaps | 100% - **Termine** |
| 09 | Listes Personnalisees | 60% - API OK |
| 10 | Creation de Blocs | 93% - En cours |
| 11 | Principes Ergonomie UI/UX | 100% - **Termine** |

## Données clés

| Information | Valeur |
|-------------|--------|
| Backend API | `https://www.sostokt.com/api/` |
| Endpoint auth | `POST /api/token-auth` (username + password) |
| Salle cible | Montoboard |
| Gym ID | `be149ef2-317d-4c73-8d7d-50074577d2fa` |
| Climbs | 1017 |
| Prises | 776 |

## Architecture du Package

```
mastoc/
├── pyproject.toml          # Configuration package
├── src/mastoc/
│   ├── api/
│   │   ├── client.py       # API Stokt
│   │   └── models.py       # Dataclasses Climb, Hold, etc.
│   ├── db/
│   │   ├── database.py     # SQLite connexion
│   │   └── repository.py   # ClimbRepository, HoldRepository
│   ├── core/
│   │   ├── sync.py         # Synchronisation API ↔ BD
│   │   ├── filters.py      # Filtres par grade, setter, prises
│   │   └── hold_index.py   # Index prises ↔ blocs
│   └── gui/
│       ├── app.py          # Application principale
│       ├── hold_selector.py # Sélecteur par prises (TODO 06)
│       ├── climb_viewer.py  # Visualisation climb
│       ├── widgets/
│       │   ├── climb_renderer.py  # Renderer commun (PIL)
│       │   ├── hold_overlay.py    # Overlay prises (pyqtgraph)
│       │   └── ...
│       └── dialogs/        # Login, etc.
└── tests/                  # 111 tests
```

## Tests

```bash
cd /media/veracrypt1/Repositories/mastoc/mastoc
python -m pytest tests/ -v
# 111 tests passent
```

## Résumé des sessions

### Session 2025-12-23
- TODO 09 Listes Personnalisées avancé de 5% à 60%
- Analyse code décompilé : 25 endpoints, 18 fonctions JS
- Modèles ClimbList et ListItem créés
- 14 méthodes API ajoutées dans client.py
- Tests réels OK (3 listes perso, 45 listes gym)
- 224 tests passent

### Session 2025-12-22 (après-midi)
- Refactoring TODO 06 : architecture deux modes
- Renderer commun `climb_renderer.py` créé
- Bouton Undo + slider luminosité
- 111 tests passent

### Session 2025-12-22 (nuit)
- TODO 06 complété (100%)
- Interface de sélection par prises fonctionnelle
- 108 tests passent

### Session 2025-12-21 (nuit)
- TODO 05 complété et archivé (100%)
- Package Python mastoc fonctionnel
- 90 tests passent

### Session 2025-12-21 (soir)
- TODO 06 créé : Interface de Filtrage et Sélection de Blocs
- TODO 05 avancé à 50%

### Session 2025-12-21
- TODO 04 complété (100%)
- 776 prises avec polygones récupérées
- TODO 05 créé

## Documentation

- `/docs/TIMELINE.md` - Historique complet
- `/docs/TODOS/06_interface_filtrage_blocs.md` - TODO 06
- `/archive/TODOS/05_python_package_structure.md` - TODO 05 (archivé)
- `/docs/reverse_engineering/` - Documentation API

## Prochaines étapes possibles

1. **Application mobile** : Porter le prototype vers React Native ou Flutter
2. **Synchronisation** : Améliorer la sync incrémentale
3. **Création de blocs** : Ajouter la fonctionnalité de création

---

**Dernière mise à jour** : 2025-12-23
**Statut du projet** : Prototype Python complet - API listes OK
