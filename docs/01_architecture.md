# Architecture de mastoc

## Vue d'Ensemble

mastoc est une application PyQt6 pour visualiser et explorer les blocs d'escalade du gym Montoboard, synchronisés depuis l'API Stokt.

```
mastoc/
├── src/mastoc/
│   ├── api/           # Client API Stokt
│   ├── core/          # Logique métier
│   ├── db/            # Base de données SQLite
│   └── gui/           # Interface PyQt6
└── tests/             # Tests unitaires
```

## Modules

### api/
- `client.py` : Client HTTP pour l'API Stokt (authentification, requêtes)
- `models.py` : Modèles de données (Climb, Hold, Face, Grade, Setter)

### core/
- `filters.py` : Filtrage des blocs (grade, setter, prises)
- `sync.py` : Synchronisation API → SQLite
- `hold_index.py` : Index inversé prises → blocs
- `picto.py` : Génération des pictos (miniatures)
- `picto_cache.py` : Cache persistant des pictos

### db/
- `database.py` : Connexion SQLite, repositories
- Stockage : `~/.mastoc/mastoc.db`

### gui/
- `app.py` : Fenêtre principale (MastockApp)
- `widgets/climb_list.py` : Liste des blocs avec filtres
- `widgets/hold_overlay.py` : Overlay des prises sur image
- `widgets/level_slider.py` : Double slider de niveau
- `dialogs/login.py` : Dialog de connexion

## Flux de Données

```
API Stokt → SyncManager → SQLite
                ↓
         ClimbRepository
                ↓
         ClimbFilterService → ClimbListWidget
                ↓
         ClimbViewerWidget (visualisation)
```

## Stockage Local

| Chemin | Contenu |
|--------|---------|
| `~/.mastoc/mastoc.db` | Base SQLite (blocs, prises) |
| `~/.mastoc/pictos/` | Cache des miniatures PNG |
| `extracted/images/face_full_hires.jpg` | Image du mur |

## Interface Utilisateur

### Fenêtre Principale
- **Gauche** : Liste des blocs avec filtres et pictos
- **Droite** : Visualisation du bloc sélectionné

### Filtres
- Grade min/max (sliders)
- Setter (combo)
- Pieds (combo)
- Benchmarks (checkbox)
- Tri (date, grade, nom, popularité)

### Viewer
- Image du mur avec prises colorées
- Contours selon couleur dominante des prises
- Marqueurs START (trait 45°) et TOP (double polygone)
- Sliders : gris, luminosité, contour blanc, épaisseur

## Dépendances Principales

- PyQt6 : Interface graphique
- pyqtgraph : Visualisation rapide
- Pillow : Traitement d'images
- requests : Client HTTP
