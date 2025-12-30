# ADR 004 - Client Python avec PyQtGraph + SQLite

**Date** : 2025-12-30
**Statut** : Accepté

## Contexte

Le projet mastoc nécessite une interface graphique pour :
- Visualiser les faces de mur avec les prises
- Créer et éditer des blocs en cliquant sur les prises
- Afficher des heatmaps et statistiques
- Fonctionner hors-ligne avec synchronisation optionnelle

Options considérées :

| Option | Avantages | Inconvénients |
|--------|-----------|---------------|
| Web (React/Vue) | Cross-platform, déploiement facile | Pas d'accès fichiers local |
| Electron | Cross-platform, web tech | Lourd, JavaScript |
| **PyQtGraph** | Performant, Python natif | Dépendances Qt |
| Tkinter | Standard Python | Limité graphiquement |
| Kivy | Mobile-ready | API moins intuitive |

## Décision

Utiliser **PyQtGraph** avec **PySide6** et **SQLite** local :
- PyQtGraph pour le rendu des images et prises (performant)
- PySide6 comme binding Qt (licence LGPL)
- SQLite local pour le cache et mode offline
- httpx pour les appels API au serveur Railway

## Conséquences

### Positives
- Excellent performance pour le rendu de nombreuses prises
- Interactivité fluide (zoom, pan, click)
- Mode offline natif avec SQLite
- Écosystème Python (numpy, scipy pour les stats)
- Possibilité future de packaging (PyInstaller)

### Négatives
- Installation Qt peut être complexe
- Non portable directement sur mobile
- UI moins moderne que web

## Implémentation

### Structure du client

```
mastoc/
├── pyproject.toml
├── src/
│   └── mastoc/
│       ├── __init__.py
│       ├── app.py              # Point d'entrée PySide6
│       ├── api/
│       │   └── client.py       # Client API Stokt + Railway
│       ├── core/
│       │   ├── face_index.py   # Index des faces
│       │   ├── hold_index.py   # Index des prises
│       │   ├── climb_service.py
│       │   └── colormaps.py    # Heatmaps
│       ├── ui/
│       │   ├── main_window.py
│       │   ├── face_viewer.py  # Vue PyQtGraph
│       │   └── widgets/
│       └── db/
│           ├── schema.py       # SQLite schema
│           └── repository.py   # Accès données
└── tests/
```

### Rendu des prises (PyQtGraph)

```python
import pyqtgraph as pg
from PySide6.QtCore import Qt

class HoldOverlay(pg.GraphicsObject):
    """Overlay interactif des prises sur une face."""

    def __init__(self, holds: list[Hold], parent=None):
        super().__init__(parent)
        self.holds = holds
        self.selected_ids: set[int] = set()
        self.setAcceptHoverEvents(True)

    def paint(self, painter, option, widget):
        for hold in self.holds:
            color = self._get_color(hold)
            painter.setBrush(color)
            painter.drawPath(hold.path)

    def mousePressEvent(self, event):
        # Détection du clic sur une prise
        pos = event.pos()
        for hold in self.holds:
            if hold.path.contains(pos):
                self._toggle_selection(hold.id)
                self.update()
                break
```

### Cache SQLite local

```python
import sqlite3
from pathlib import Path

class LocalDatabase:
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS faces (
                id TEXT PRIMARY KEY,
                gym_id TEXT,
                picture_path TEXT,
                last_sync TEXT
            );

            CREATE TABLE IF NOT EXISTS holds (
                id INTEGER PRIMARY KEY,
                face_id TEXT,
                polygon_str TEXT,
                centroid_x REAL,
                centroid_y REAL
            );

            CREATE TABLE IF NOT EXISTS climbs (
                id TEXT PRIMARY KEY,
                face_id TEXT,
                name TEXT,
                holds_list TEXT,
                is_local INTEGER DEFAULT 0
            );
        ''')
```

### Client API

```python
import httpx

class MastocAPI:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.client = httpx.Client(
            headers={"X-API-Key": api_key},
            timeout=30
        )

    def get_climbs(self, face_id: str) -> list[dict]:
        response = self.client.get(
            f"{self.base_url}/api/climbs",
            params={"face_id": face_id}
        )
        response.raise_for_status()
        return response.json()

    def create_climb(self, data: dict) -> dict:
        response = self.client.post(
            f"{self.base_url}/api/climbs",
            json=data
        )
        response.raise_for_status()
        return response.json()
```

### Modes de coloration (heatmaps)

```python
from enum import Enum
import numpy as np

class ColorMode(Enum):
    GRADE_MIN = "min"      # Grade min des blocs utilisant la prise
    GRADE_MAX = "max"      # Grade max
    FREQUENCY = "freq"     # Nombre de blocs

def get_hold_colors(holds: list, climbs: list, mode: ColorMode) -> dict:
    """Calcule les couleurs des prises selon le mode."""
    # ... voir ADR colormaps
```

## Dépendances

```toml
[project]
dependencies = [
    "PySide6>=6.6",
    "pyqtgraph>=0.13",
    "httpx>=0.25",
    "numpy>=1.24",
]
```

## Fichiers concernés

- `mastoc/pyproject.toml` - Configuration projet
- `mastoc/src/mastoc/` - Code source client
- `mastoc/tests/` - Tests pytest
