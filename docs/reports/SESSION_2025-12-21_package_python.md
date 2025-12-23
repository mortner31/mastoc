# Rapport de Session - Package Python mastoc

**Date** : 2025-12-21

## Objectifs Atteints

- Package Python installable (`pip install -e .`)
- Base de données SQLite fonctionnelle
- Viewer PyQtGraph avec rendu avancé
- 39 tests unitaires

## Réalisations

### Phase 1 : Structure du package (100%)

Création d'un package Python moderne avec :
- `pyproject.toml` avec dépendances (PyQt6, pyqtgraph, Pillow, requests)
- Architecture `src/mastoc/` avec modules séparés :
  - `api/` : Client API Stokt avec dataclasses typées
  - `db/` : Base SQLite avec repositories
  - `gui/` : Interface PyQtGraph
  - `core/` : Logique métier

### Phase 2 : Base de données SQLite (100%)

Schéma complet avec :
- Tables : `climbs`, `holds`, `faces`, `setters`, `climb_holds`, `sync_metadata`
- Clé composite `(climb_id, hold_id, hold_type)` pour supporter une même prise avec différents rôles (Start + Top par ex.)
- Repositories avec méthodes de recherche avancées :
  - `get_climbs_by_grade()` : filtrer par niveau
  - `get_climbs_by_hold()` : trouver les climbs utilisant une prise
  - `get_climbs_by_holds()` : trouver les climbs utilisant TOUTES les prises spécifiées

**Données importées** :
- 1017 climbs
- 776 prises avec polygones
- 79 setters

### Phase 4 : GUI PyQtGraph (50%)

#### Climb Viewer

Visualisation d'un climb avec :
- Image haute résolution du mur (2263 x 3000 pixels)
- Effet gris sur le fond, prises en couleur
- Détection automatique de la couleur dominante de chaque prise
- Contour autour des prises avec couleur détectée

**3 sliders interactifs** :
1. **Fond (couleur ↔ gris)** : 0% = image originale, 100% = gris complet
2. **Contour (couleur ↔ blanc)** : blend entre couleur détectée et blanc
3. **Épaisseur contour** : 1px à 20px

#### Heatmap usage des prises

Visualisation de la popularité des prises :
- Couleur froide (bleu) → chaude (rouge) selon le nombre de climbs
- Statistiques :
  - Prise la plus utilisée : 78 climbs
  - Usage moyen : 11.9 climbs par prise
  - 738 prises utilisées au moins une fois

### Tests

**39 tests unitaires** couvrant :
- Parsing des modèles API (Climb, Hold, Face, Grade)
- Opérations CRUD sur la base de données
- Relations climb ↔ holds
- Cas limites (prises dupliquées, types multiples)

## Commandes utiles

```bash
# Installation
cd mastoc && pip install -e .

# Import des données
python3 -m mastoc.core.import_data

# Visualiser un climb
python3 -m mastoc.gui.climb_viewer --name "Nia" --setter "Mathias" --image

# Lister les climbs d'un setter
python3 -m mastoc.gui.climb_viewer --list --setter "Thomas"

# Lancer les tests
python3 -m pytest tests/ -v
```

## Fichiers créés

| Fichier | Lignes | Description |
|---------|--------|-------------|
| `pyproject.toml` | 50 | Configuration package |
| `api/models.py` | 280 | Dataclasses typées |
| `api/client.py` | 150 | Client API Stokt |
| `db/database.py` | 130 | Schéma SQLite |
| `db/repository.py` | 250 | CRUD repositories |
| `core/import_data.py` | 100 | Import JSON → SQLite |
| `gui/climb_viewer.py` | 400 | Viewer avec sliders |
| `tests/test_models.py` | 150 | Tests modèles |
| `tests/test_database.py` | 300 | Tests base de données |

**Total** : ~1800 lignes de code Python

## Prochaines étapes

1. **Phase 3** : Filtres avancés (par niveau, setter, combinaison de prises)
2. **Phase 4** : Interface principale avec liste de climbs scrollable
3. **Phase 5** : Synchronisation API avec delta updates
4. Intégrer la heatmap dans le viewer avec toggle

## Notes techniques

### Détection couleur des prises

Algorithme utilisé :
1. Échantillonner les pixels dans un rayon de 15px autour du centroïde
2. Filtrer les pixels gris (|R-G| + |G-B| + |R-B| < 30)
3. Quantifier les couleurs (division par 32) pour regrouper les similaires
4. Retourner la couleur la plus fréquente

### Performance

- Chargement image + détection couleurs : ~1s
- Mise à jour image avec sliders : ~200ms (acceptable pour interaction)
- Les couleurs sont pré-calculées au chargement, pas à chaque update

---

**Progression TODO 05** : 50%
