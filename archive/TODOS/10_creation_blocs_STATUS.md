# STATUS - TODO 10 : Interface de Création de Blocs

**Progression** : 97% (28/29 tâches)

---

## Phase 0 : Investigation (100%)

- [x] Identifier endpoints création (POST, PATCH, DELETE)
- [x] Documenter structure de données (holdsList, grade, etc.)
- [x] Analyser gestion public/privé (isPrivate, permissions)
- [x] Comprendre workflow UI (SelectHolds → ClimbInfo → POST)
- [x] Identifier validations (min 2 START, nom min 3 chars)

## Phase 0.5 : Infrastructure Navigation (100%)

- [x] Créer `QStackedWidget` pour navigation wizard (`CreationWizard`)
- [x] Réutiliser `HoldOverlay` avec spécialisation (`CreationHoldOverlay`)
- [x] Créer `ClimbCreationState` dataclass
- [x] Implémenter navigation back/next
- [x] Créer `WizardController`

## Phase 1 : Sélection de prises (100%)

- [x] Créer `SelectHoldsScreen(QWidget)`
- [x] Boutons de type (START, OTHER, FEET, TOP)
- [x] Visualisation couleur par type
- [x] Liste prises sélectionnées groupées
- [x] Validation min 2 START
- [x] Bouton "Suivant"

## Phase 2 : Formulaire + API Client (100%)

- [x] Créer `ClimbInfoScreen(QWidget)`
- [x] Input nom (min 3 chars)
- [x] Sélecteur grade
- [x] Sélecteur règle pieds
- [x] Input description
- [x] Toggle public/privé
- [x] API: `create_climb()`
- [x] API: `update_climb()`
- [x] API: `delete_climb()`

## Phase 3 : Soumission et Feedback (75%)

- [x] Construire payload
- [x] POST vers API
- [x] Loading state animé
- [x] Erreurs nonFieldErrors
- [ ] Erreurs par champ (highlight)
- [ ] Gestion timeout/retry
- [x] Feedback succès + refresh
- [ ] Sauvegarde locale (optionnel)

## Intégration (100%)

- [x] Bouton "Créer un bloc" dans hold_selector.py
- [x] Dialog modal avec le wizard
- [x] Callback succès avec message

---

## Hors scope

- **TODO 11** : Édition de blocs existants (reporté)
- **TODO 12** : Mode Circuit (reporté)

---

## Notes

### Session 2025-12-23 (matin)

**CREATION API FONCTIONNELLE !**

Premier bloc créé via mastoc : `509345cb-8c01-477d-bfba-dd4d55ee4ddd`

**Bugs corrigés** :
- Fix boucle infinie de signaux dans `ClimbInfoScreen._load_state()` (freeze au clic "Suivant")
- Fix bouton "Suivant" jamais activé (connexion `state_changed` → `_update_navigation`)
- Fix style bouton désactivé invisible (CSS `:disabled` ajouté)
- Fix face_id incorrect (`61b42d14-...` au lieu de `6e428bf6-...`)

**Corrections API découvertes par analyse du code décompilé** :
- `gradingSystem` : valeurs en **minuscule** (`"font"`, `"hueco"`, `"dankyu"`)
- Grades Font : lettres en **majuscule** (`"6A+"`, pas `"6a+"`)
- `attemptsNumber` : champ **requis** (peut être `null`)

**Améliorations** :
- User-Agent "Stokt/6.1.13 (Android)" ajouté au client API
- Face ID corrigé dans creation_app.py

### Session 2025-12-23 (précédente)

**Phase 3 avancée** : Feedback amélioré

**Améliorations UI** :
- Spinner animé avec barre de progression indéterminée
- Points animés "Publication en cours..."
- Écran succès avec icône ✓ et ID du climb
- Écran erreur avec icône ✗ et message détaillé

**Intégration hold_selector.py** :
- Bouton "+ Créer un bloc" (vert, style Material)
- Dialog modal 1200x800
- Callback `_on_climb_created()` avec message de succès

**Tests** : 225 tests passent

### Prochaines étapes

1. **Investiguer 404 API Stokt** : capturer requêtes app mobile avec proxy
2. **Alternative** : créer backend indépendant (voir `docs/backend_spec.md`)
3. Améliorer highlight erreurs par champ
4. Ajouter gestion timeout/retry

### Comment tester

```bash
# Application principale avec bouton "Créer"
python -m mastoc.gui.hold_selector

# Application de test standalone
python -m mastoc.gui.creation_app
```

### Payload curl pour test API (FONCTIONNEL)

```bash
TOKEN="dba723cbee34ff3cf049b12150a21dc8919c3cf8"
FACE_ID="61b42d14-c629-434a-8827-801512151a18"

curl -v -X POST "https://www.sostokt.com/api/faces/${FACE_ID}/climbs" \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Stokt/6.1.13 (Android)" \
  -d '{
    "name": "essai",
    "holdsList": {
      "start": ["829314", "829039"],
      "others": ["829447", "829436", "828917", "829598", "829098", "829380", "829193"],
      "top": ["829416"],
      "feetOnly": []
    },
    "grade": {
      "gradingSystem": "font",
      "value": "5+"
    },
    "attemptsNumber": null,
    "isPrivate": true,
    "description": "pour tester"
  }'
```
