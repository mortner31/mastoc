# STATUS - TODO 12 : Hold Annotations

**Progression** : 95%

---

## Prérequis

- [x] Serveur Railway déployé avec PostgreSQL

---

## Backend

- [x] Modèle HoldAnnotation (server/src/mastoc_api/models/hold_annotation.py)
- [x] Enums : HoldGripType, HoldCondition, HoldRelativeDifficulty
- [x] Endpoints REST (server/src/mastoc_api/routers/hold_annotations.py)
  - GET /api/holds/{id}/annotations
  - PUT /api/holds/{id}/annotations
  - DELETE /api/holds/{id}/annotations
  - POST /api/holds/annotations/batch
- [x] Tests API (16 tests passent)

---

## Client (mastoc)

### Modèles et API
- [x] Enums dans models.py (HoldGripType, HoldCondition, HoldRelativeDifficulty)
- [x] Dataclasses (HoldAnnotation, HoldConsensus, AnnotationData)
- [x] Méthodes API dans railway_client.py

### Core
- [x] annotation_loader.py (pattern SocialLoader, cache 10min)
- [ ] Filtres par tags dans hold_index.py (reporté)

### GUI
- [x] ColorModes : GRIP_TYPE, CONDITION, DIFFICULTY dans hold_overlay.py
- [x] annotation_panel.py (widget édition)
- [ ] Intégration dans hold_selector.py (optionnel)

### Tests
- [x] Tests unitaires annotation_loader (24 tests)
- [x] Tests annotation_panel (19 tests)

---

## Reste à faire

1. Intégration hold_selector.py (optionnel - peut être fait dans TODO 18)
2. Filtres par tags dans hold_index.py (optionnel)

---

## Fichiers créés/modifiés

### Serveur
- `server/src/mastoc_api/models/hold_annotation.py` (nouveau)
- `server/src/mastoc_api/routers/hold_annotations.py` (nouveau)
- `server/tests/test_hold_annotations.py` (nouveau, 16 tests)
- `server/src/mastoc_api/models/__init__.py` (modifié)
- `server/src/mastoc_api/routers/__init__.py` (modifié)
- `server/src/mastoc_api/main.py` (modifié)

### Client
- `mastoc/src/mastoc/api/models.py` (+3 enums, +3 dataclasses)
- `mastoc/src/mastoc/api/railway_client.py` (+4 méthodes)
- `mastoc/src/mastoc/core/annotation_loader.py` (nouveau)
- `mastoc/src/mastoc/gui/widgets/hold_overlay.py` (+3 ColorModes)
- `mastoc/src/mastoc/gui/widgets/annotation_panel.py` (nouveau)
- `mastoc/tests/test_annotation_loader.py` (nouveau, 24 tests)
- `mastoc/tests/test_annotation_panel.py` (nouveau, 19 tests)

### Documentation
- `docs/adr/008_hold_annotations.md` (nouveau)
