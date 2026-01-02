# TODO 23 - Tests Tapes & Endpoints

## Objectif

Corriger les gaps identifiés lors de l'analyse de propagation BD (tapes/dates) pour prévenir les régressions.

## Contexte

Analyse du 2026-01-02 : les changements BD sont propagés correctement, mais quelques gaps mineurs existent :
- Tests serveur sans vérification des champs `tape_str`
- Endpoint `/api/holds` n'expose pas les tapes
- `synced_at`/`updated_at` non retournés dans ClimbResponse

## Tâches

### Phase 1 : Tests Serveur

- [ ] Ajouter tapes à fixture `test_holds` (`test_faces.py`)
- [ ] Assertions tapes dans `test_get_face_setup_success`
- [ ] Test `test_get_face_setup_with_tapes`

### Phase 2 : Endpoints

- [ ] Ajouter tapes à `HoldResponse` (`holds.py`)
- [ ] Ajouter `synced_at`/`updated_at` à `ClimbResponse` (`climbs.py`)

### Phase 3 : Validation

- [ ] Tous tests passent
- [ ] Pas de régression clients

## Fichiers

- `server/tests/test_faces.py`
- `server/src/mastoc_api/routers/holds.py`
- `server/src/mastoc_api/routers/climbs.py`

## Références

- Commits : `22632fe`, `2077179`, `df5d4eb`
- TODO 22 Phase 6
