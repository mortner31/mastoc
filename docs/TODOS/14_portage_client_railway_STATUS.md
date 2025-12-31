# STATUS - TODO 14 : Portage Client Railway

**Progression** : 80%

---

## Phase 1 : Client API Railway (100%)

- [x] Créer `mastoc/api/railway_client.py`
- [x] Authentification API Key (header X-API-Key)
- [x] GET /api/climbs (avec filtres et pagination)
- [x] GET /api/climbs/{id}
- [x] GET /api/holds
- [x] POST /api/climbs (création)
- [x] PATCH /api/climbs/{id} (mise à jour)
- [x] DELETE /api/climbs/{id}
- [x] Exporter dans `__init__.py`
- [x] Tests unitaires (16 tests)

## Phase 2 : Backend Switch (100%)

- [x] Créer `mastoc/core/backend.py`
- [x] Interface commune `BackendInterface` (ABC)
- [x] `RailwayBackend` - adapter pour mastoc-api
- [x] `StoktBackend` - adapter pour Stokt (legacy)
- [x] `BackendSwitch` - façade avec fallback automatique
- [x] `BackendConfig` - configuration (source, api_key, token)
- [x] Exporter dans `__init__.py`
- [x] Tests unitaires (27 tests)

## Phase 3 : Migration GUI (100%)

- [x] Adapter `app.py` - BackendSwitch + menu source
- [x] Adapter `hold_selector.py` - BackendSwitch
- [x] Adapter `creation_app.py` - BackendSwitch
- [x] Login dialog - inchangé (spécifique Stokt)
- [x] Tests (267 passent)

## Phase 4 : Endpoints Railway (100%)

- [x] GET /api/faces/{id}/setup - router `faces.py` créé
- [x] GET /api/faces - liste des faces
- [x] GET /api/faces/{id} - détail face
- [x] GET /api/faces/by-stokt-id/{id}/setup
- [x] POST /api/climbs - déjà existant
- [x] MastocAPI.get_face_setup() adapté
- [x] Tests serveur (test_faces.py)
- [ ] Endpoints social (reporté)
- [ ] Endpoints listes (reporté)

## Phase 5 : Sync (0%)

- [ ] Sync Railway → SQLite
- [ ] Gestion conflits
- [ ] Mode offline

---

## Notes

### Dépendances actuelles (18 fichiers)

```
mastoc/src/mastoc/api/client.py          # StoktAPI principal
mastoc/src/mastoc/gui/app.py
mastoc/src/mastoc/gui/hold_selector.py
mastoc/src/mastoc/gui/creation_app.py
mastoc/src/mastoc/gui/creation/wizard.py
mastoc/src/mastoc/gui/dialogs/login.py
mastoc/src/mastoc/gui/widgets/my_lists_panel.py
mastoc/src/mastoc/gui/widgets/my_climbs_panel.py
mastoc/src/mastoc/core/sync.py
mastoc/src/mastoc/core/social_loader.py
mastoc/src/mastoc/core/social_actions.py
mastoc/tests/test_integration.py
mastoc/tests/test_sync.py
mastoc/tests/test_api_crud.py
```

### Endpoints Railway existants

| Endpoint | Disponible |
|----------|------------|
| GET /api/climbs | ✅ |
| GET /api/holds | ✅ |
| GET /api/sync/stats | ✅ |
| POST /api/sync/import/* | ✅ |
| GET /api/faces/{id}/setup | ❌ À créer |
| POST /api/climbs | ❌ À créer |
