# STATUS - TODO 14 : Portage Client Railway

**Progression** : 95%

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

- [x] Adapter `app.py` - BackendSwitch + menu source + AppConfig
- [x] Adapter `hold_selector.py` - BackendSwitch + AppConfig
- [x] Adapter `creation_app.py` - BackendSwitch + AppConfig
- [x] Login dialog - inchangé (spécifique Stokt)
- [x] Tests (277 passent)

## Phase 4 : Endpoints Railway (100%)

- [x] GET /api/faces/{id}/setup - router `faces.py` créé
- [x] GET /api/faces - liste des faces
- [x] GET /api/faces/{id} - détail face
- [x] GET /api/faces/by-stokt-id/{id}/setup
- [x] POST /api/climbs - déjà existant
- [x] MastocAPI.get_face_setup() adapté
- [x] Tests serveur (test_faces.py)
- [ ] Endpoints social (reporté → TODO 16)
- [ ] Endpoints listes (reporté → TODO 16)

## Phase 5 : Sync et Données (100%)

- [x] ADR-006 : Deux bases SQLite séparées (stokt.db + railway.db)
- [x] RailwaySyncManager pour sync Railway → SQLite
- [x] Basculement automatique de DB selon BackendSource
- [x] Sync holds (prises) automatique avec face_id
- [x] Configuration persistante (API key + source) - `core/config.py`
- [x] Tests config (10 tests)
- [x] Intégration AppConfig dans toutes les apps GUI

## Phase 6 : Validation (100%)

- [x] Synchronisation Railway testée : 1012 climbs, 776 prises
- [x] Base railway.db créée et peuplée
- [x] Config sauvegardée dans ~/.mastoc/config.json
- [x] 3 apps fonctionnelles : app.py, hold_selector.py, creation_app.py

## Phase 7 : Assets (À FAIRE - Prochaine session)

- [ ] Sync image mur (face_full_hires.jpg) depuis Railway
- [ ] Sync avatars utilisateurs
- [ ] Stockage local dans ~/.mastoc/images/
- [ ] Gestion cache/invalidation

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
| GET /api/faces | ✅ (nouveau) |
| GET /api/faces/{id} | ✅ (nouveau) |
| GET /api/faces/{id}/setup | ✅ (nouveau) |
| POST /api/climbs | ✅ |
| PATCH /api/climbs/{id} | ✅ |
| DELETE /api/climbs/{id} | ✅ |
| GET /api/users | ❌ À créer |
| GET /api/users/{id}/avatar | ❌ À créer |
