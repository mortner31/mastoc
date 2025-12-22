# STATUS - TODO 10 : Interface de Création de Blocs

**Progression** : 17% (5/29 tâches)

---

## Phase 0 : Investigation (100%)

- [x] Identifier endpoints création (POST, PATCH, DELETE)
- [x] Documenter structure de données (holdsList, grade, etc.)
- [x] Analyser gestion public/privé (isPrivate, permissions)
- [x] Comprendre workflow UI (SelectHolds → ClimbInfo → POST)
- [x] Identifier validations (min 2 START, nom min 3 chars)

## Phase 0.5 : Infrastructure Navigation (0%)

- [ ] Créer `QStackedWidget` pour navigation wizard
- [ ] Extraire `HoldOverlayWidget` de `HoldSelectorApp`
- [ ] Créer `ClimbCreationState` dataclass
- [ ] Implémenter navigation back/next
- [ ] Créer `WizardController`

## Phase 1 : Sélection de prises (0%)

- [ ] Créer `SelectHoldsScreen(QWidget)`
- [ ] Boutons de type (START, OTHER, FEET, TOP)
- [ ] Visualisation couleur par type
- [ ] Liste prises sélectionnées groupées
- [ ] Validation min 2 START
- [ ] Bouton "Suivant"

## Phase 2 : Formulaire + API Client (0%)

- [ ] Créer `ClimbInfoScreen(QWidget)`
- [ ] Input nom (min 3 chars)
- [ ] Sélecteur grade
- [ ] Sélecteur règle pieds
- [ ] Input description
- [ ] Toggle public/privé
- [ ] API: `create_climb()`
- [ ] API: `update_climb()`
- [ ] API: `delete_climb()`

## Phase 3 : Soumission et Feedback (0%)

- [ ] Construire payload
- [ ] POST vers API
- [ ] Loading state
- [ ] Erreurs nonFieldErrors
- [ ] Erreurs par champ
- [ ] Gestion timeout/retry
- [ ] Feedback succès + refresh
- [ ] Sauvegarde locale (optionnel)

---

## Hors scope

- **TODO 11** : Édition de blocs existants (reporté)
- **TODO 12** : Mode Circuit (reporté)

---

## Notes

### Analyse critique (2025-12-22)

Risques identifiés par analyse multi-agents :

1. **GAP Architectural** : UI splitter plat incompatible avec wizard multi-écrans
2. **API Client incomplet** : Manquent POST/PATCH/DELETE
3. **HoldSelectorApp** : Application standalone, pas widget réutilisable
4. **Phases 4-5** : Trop vagues → reportées TODO 11/12

### Décisions prises

- Phase 0.5 ajoutée comme prérequis (infrastructure navigation)
- Extension API Client intégrée à Phase 2
- Extraction HoldOverlayWidget prioritaire
- Scope réduit : création seule (pas édition/circuit)
