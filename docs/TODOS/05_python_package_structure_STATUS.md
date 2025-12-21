# STATUS - TODO 05 : Structure Package Python mastock

**Progression** : 0%

## Phase 1 : Structure du package (0%)

- [ ] Créer `pyproject.toml` avec metadata et dépendances
- [ ] Réorganiser le code en `src/mastock/`
- [ ] Refactorer `stokt_api.py` → `api/client.py`
- [ ] Créer les dataclasses dans `api/models.py`
- [ ] Vérifier installation avec `pip install -e .`

## Phase 2 : Base de données SQLite (0%)

- [ ] Définir schéma : tables climbs, holds, faces, sync_metadata
- [ ] Créer `db/database.py` avec connexion et migrations
- [ ] Créer `db/models.py` avec classes ORM
- [ ] Importer données JSON existantes dans SQLite
- [ ] Stocker date de dernière synchronisation

## Phase 3 : Logique métier core (0%)

- [ ] `core/sync.py` : synchronisation API ↔ BD locale
- [ ] `core/filters.py` : filtres par niveau, auteur, prises
- [ ] Tests unitaires pour les filtres

## Phase 4 : GUI PyQtGraph (0%)

- [ ] `gui/app.py` : fenêtre principale
- [ ] `gui/widgets/board_view.py` : vue du mur avec polygones
- [ ] `gui/widgets/climb_list.py` : liste avec filtres
- [ ] `gui/widgets/climb_viewer.py` : visualisation climb
- [ ] `gui/dialogs/login.py` : dialog d'authentification

## Phase 5 : Fonctionnalités avancées (0%)

- [ ] Mise à jour incrémentale de la BD
- [ ] Détection expiration token + re-login
- [ ] Interface de sélection par prises
- [ ] (Optionnel) Création de climb

## En attente

- [ ] Tests d'intégration complets
- [ ] Documentation utilisateur

## Fichiers de référence

| Fichier | Contenu |
|---------|---------|
| `/mastock/src/stokt_api.py` | API client existant |
| `/extracted/data/montoboard_ALL_climbs.json` | 1017 climbs |
| `/extracted/data/montoboard_setup.json` | 776 prises avec polygones |
| `/extracted/images/face_full_hires.jpg` | Image mur 2263x3000 |
