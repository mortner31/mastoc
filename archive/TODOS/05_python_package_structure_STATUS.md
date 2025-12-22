# STATUS - TODO 05 : Structure Package Python mastock

**Progression** : 100%

## Phase 1 : Structure du package (100%)

- [x] Créer `pyproject.toml` avec metadata et dépendances
- [x] Réorganiser le code en `src/mastock/`
- [x] Refactorer `stokt_api.py` → `api/client.py`
- [x] Créer les dataclasses dans `api/models.py`
- [x] Vérifier installation avec `pip install -e .`

## Phase 2 : Base de données SQLite (100%)

- [x] Définir schéma : tables climbs, holds, faces, sync_metadata
- [x] Créer `db/database.py` avec connexion et migrations
- [x] Créer `db/repository.py` avec ClimbRepository et HoldRepository
- [x] Script `core/import_data.py` pour importer JSON existants
- [x] Stocker date de dernière synchronisation
- [x] **39 tests unitaires passent**

## Phase 3 : Logique métier core (100%)

- [x] `core/sync.py` : synchronisation API ↔ BD locale
- [x] `core/filters.py` : filtres par niveau, auteur, prises
- [x] Tests unitaires pour les filtres

## Phase 4 : GUI PyQtGraph (100%)

- [x] `gui/climb_viewer.py` : visualisation climb avec image
- [x] Détection automatique couleur des prises
- [x] Sliders interactifs (fond gris, contour couleur/blanc, épaisseur)
- [x] Mode sans image (polygones colorés par type)
- [x] `gui/app.py` : fenêtre principale avec liste
- [x] `gui/widgets/climb_list.py` : liste avec filtres
- [x] `gui/dialogs/login.py` : dialog d'authentification

## Phase 5 : Fonctionnalités avancées (100%)

- [x] Mise à jour incrémentale de la BD (sync_incremental)
- [x] Détection expiration token + re-login (TokenExpiredDialog)
- [x] ~~Interface de sélection par prises~~ → **Voir TODO 06**
- [ ] (Optionnel) Création de climb - Non implémenté

## Terminé

- [x] Tests d'intégration complets (90 tests passent)
- [ ] Documentation utilisateur - Non prioritaire

## Fichiers créés

| Fichier | Contenu |
|---------|---------|
| `/mastock/pyproject.toml` | Configuration package Python |
| `/mastock/src/mastock/api/client.py` | API client refactoré |
| `/mastock/src/mastock/api/models.py` | Dataclasses Climb, Hold, Face, etc. |
| `/mastock/src/mastock/db/database.py` | Schéma SQLite et connexion |
| `/mastock/src/mastock/db/repository.py` | ClimbRepository, HoldRepository |
| `/mastock/src/mastock/core/import_data.py` | Import JSON → SQLite |
| `/mastock/src/mastock/gui/climb_viewer.py` | Visualisation climb avec sliders |
| `/mastock/tests/test_models.py` | Tests modèles API |
| `/mastock/tests/test_database.py` | Tests base de données |

## Données de référence

| Fichier | Contenu |
|---------|---------|
| `/extracted/data/montoboard_ALL_climbs.json` | 1017 climbs |
| `/extracted/data/montoboard_setup.json` | 776 prises avec polygones |
| `/extracted/images/face_full_hires.jpg` | Image mur 2263x3000 |
