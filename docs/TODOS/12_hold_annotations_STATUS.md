# STATUS - TODO 12 : Hold Annotations

**Progression** : 0%

---

## Prérequis

- [ ] Serveur Railway déployé avec PostgreSQL

---

## Backend

- [ ] Créer tables PostgreSQL (hold_annotations, hold_consensus)
- [ ] Implémenter endpoints REST
- [ ] Tests API

---

## Client (mastoc)

### Modèles et API
- [ ] Ajouter enums (HoldGripType, HoldCondition, HoldRelativeDifficulty)
- [ ] Ajouter dataclasses (HoldAnnotation, HoldConsensus)
- [ ] Étendre StoktAPI avec méthodes annotations

### Core
- [ ] Créer annotation_loader.py (loader async)
- [ ] Étendre hold_index.py (filtres par tags)

### GUI
- [ ] Créer annotation_panel.py (widget annotation)
- [ ] Ajouter ColorModes dans hold_overlay.py
- [ ] Intégrer dans hold_selector.py
- [ ] Ajouter panneau filtres par tags

### Tests
- [ ] Tests unitaires modèles
- [ ] Tests API client
- [ ] Tests intégration UI
