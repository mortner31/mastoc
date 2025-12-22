# TODO 10 - Interface de Création de Blocs

## Objectif

Implémenter une interface de création de blocs (climbs) avec :
- Sélection interactive des prises sur l'image du mur
- Définition des types de prises (START, TOP, FEET, OTHER)
- Saisie des informations (nom, grade, description)
- Mode public ou privé
- Validation et soumission vers l'API

## Analyse Critique (2025-12-22)

### Risques identifiés

1. **GAP Architectural** : L'UI actuelle (splitter plat) ne supporte pas le workflow wizard multi-écrans
2. **API Client incomplet** : Seuls les GET sont implémentés, manquent POST/PATCH/DELETE
3. **HoldSelectorApp** : Application standalone, pas un widget réutilisable
4. **Phases 4-5** : Trop vagues, risque d'explosion de scope

### Décisions

- Ajout Phase 0.5 : Infrastructure Navigation (prérequis)
- Extension API Client intégrée à Phase 2
- Extraction HoldOverlayWidget avant Phase 1
- Phases 4-5 reportées à TODO 11 et TODO 12

---

## Endpoints API (confirmés par analyse code décompilé)

### Création

| Endpoint | Méthode | Description | Ligne code |
|----------|---------|-------------|------------|
| `api/faces/{faceId}/climbs` | POST | Créer un climb | 415263 |
| `api/climbs/{climbId}/circuit` | POST | Ajouter un circuit | 415336 |

### Modification

| Endpoint | Méthode | Description | Ligne code |
|----------|---------|-------------|------------|
| `api/faces/{faceId}/climbs/{climbId}` | PATCH | Modifier un climb | 415410 |
| `api/climbs/{climbId}/circuit` | PATCH | Modifier le circuit | 415486 |
| `api/climbs/{climbId}/privacy-status` | PATCH | Toggle public/privé | 467019 |
| `api/climbs/{climbId}/as-spam` | PATCH | Marquer comme spam | 441249 |

### Suppression

| Endpoint | Méthode | Description | Ligne code |
|----------|---------|-------------|------------|
| `api/climbs/{climbId}` | DELETE | Supprimer un climb | 441178 |
| `api/climbs/{climbId}/circuit` | DELETE | Supprimer le circuit | 415560 |

### Permissions

| Endpoint | Méthode | Description | Ligne code |
|----------|---------|-------------|------------|
| `api/climbs/{climbId}/permissions-to-modify` | GET | Récupérer les permissions | 465890 |

## Structure de données pour POST

### Body de création (lignes 952298-952325)

```python
{
    # OBLIGATOIRES
    "name": str,                    # Nom du climb (min 3 caractères)
    "holdsList": {
        "start": List[str],         # IDs prises de départ (min 2)
        "others": List[str],        # IDs prises intermédiaires
        "top": List[str],           # IDs prises de finition
        "feetOnly": List[str]       # IDs prises pieds uniquement
    },
    "grade": {
        "gradingSystem": str,       # Ex: "V-Scale", "Font"
        "value": str                # Ex: "V0", "6a+"
    },

    # OPTIONNELS
    "description": str | None,      # Description du climb
    "isPrivate": bool,              # Défaut: False
    "feetRule": str | None,         # Règle des pieds
    "attemptsNumber": int,          # Nombre de tentatives (défaut: 0)
    "tags_list": List[str],         # IDs des tags
    "angle": int | None             # Angle si mur ajustable
}
```

### Types de prises (format holdsList string)

| Code | Type | Description |
|------|------|-------------|
| `S` | Start | Prise de départ |
| `O` | Other | Prise intermédiaire |
| `F` | Feet | Pied obligatoire |
| `T` | Top | Prise finale |

Exemple: `"S829279 S829528 O828906 O828964 T829009"`

## Validations

### Prises (lignes 903059-903110)

| Validation | Condition | Message |
|------------|-----------|---------|
| Prises START | `len(start) >= 2` | Min 2 prises START |
| Prises TOP | `len(top) >= 1` | Min 1 prise TOP (édition) |

### Nom (lignes 952433-952500)

| Validation | Condition | Clé i18n |
|------------|-----------|----------|
| Non vide | `name != ''` | `nameYourClimb` |
| Min 3 caractères | `len(name) >= 3` | `climbCharLength` |
| Caractères valides | Pas d'injection | (à implémenter) |

### Grade

| Validation | Condition |
|------------|-----------|
| Système valide | `gradingSystem in ["V-Scale", "Font", "Dankyu"]` |
| Valeur cohérente | `value` compatible avec `gradingSystem` |

### Réseau

| Validation | Condition |
|------------|-----------|
| Timeout | 60s max (configurable) |
| Retry | 3 tentatives sur erreur réseau |

## Gestion Public/Privé

### Champs de permissions (lignes 913285-913290)

```python
{
    "canDelete": bool,              # Supprimer le climb
    "canEditHolds": bool,           # Modifier les prises
    "canEditNameAndGrade": bool,    # Modifier nom/grade
    "canHide": bool,                # Masquer le climb
    "canSetPrivate": bool,          # Rendre privé
    "canSetPublic": bool            # Rendre public
}
```

### Toggle privacy (ligne 467019)

```http
PATCH api/climbs/{climbId}/privacy-status
Content-Type: application/json

{"is_private": true}
```

## État Redux (lignes 414464-414505)

```python
{
    # Prises sélectionnées
    "startHolds": [],               # Prises START
    "finishHolds": [],              # Prises TOP
    "footHolds": [],                # Prises FEET
    "otherHolds": [],               # Prises OTHER
    "circuitHolds": [],             # Prises circuit
    "selectionType": "other",       # Type actif

    # Informations
    "name": "",
    "description": "",
    "feetSelection": None,
    "selectedTags": [],

    # Options
    "makePrivate": False,
    "circuitNumber": 0,

    # États UI
    "publishDisabled": False,
    "publishPending": False,
    "publishSuccess": False,
    "isPublishError": False,
    "publishError": ""
}
```

## Workflow UI (lignes 903059-960320)

```
1. ÉCRAN: Liste récente (myGym)
   └─ Bouton "CREATE_NEW_CLIMB"
   └─ handleCreateClimb() → navigate('SelectHolds')

2. ÉCRAN: Sélection prises (SelectHoldsSubscreen)
   ├─ Image du mur avec prises cliquables
   ├─ Boutons de type: START | OTHER | FEET | TOP
   ├─ Liste des prises sélectionnées par type
   └─ Bouton "Suivant" → navigate('ClimbInfo')

3. ÉCRAN: Informations (ClimbInfo)
   ├─ Input: Nom du climb
   ├─ Sélecteur: Grade
   ├─ Sélecteur: Règle des pieds
   ├─ Input: Description (optionnel)
   ├─ Toggle: Privé/Public
   ├─ Tags (optionnel)
   └─ Bouton "Publier" → POST api/faces/{faceId}/climbs

4. RÉSULTAT
   ├─ Succès → Retour myGym + refresh liste
   └─ Erreur → Affichage message (nonFieldErrors)
```

## Gestion des erreurs (lignes 414061-414077)

```python
# Structure erreur API
{
    "nonFieldErrors": ["Message d'erreur général"],
    # OU
    "fieldName": ["Message d'erreur pour ce champ"]
}

# Erreur connexion
if error.code == "ECONNABORTED":
    message = "There is a problem with your connection"
```

---

## Tâches

### Phase 0 : Investigation (100%)
- [x] Identifier endpoints création (POST, PATCH, DELETE)
- [x] Documenter structure de données (holdsList, grade, etc.)
- [x] Analyser gestion public/privé (isPrivate, permissions)
- [x] Comprendre workflow UI (SelectHolds → ClimbInfo → POST)
- [x] Identifier validations (min 2 START, nom min 3 chars)

### Phase 0.5 : Infrastructure Navigation (0%)
- [ ] Créer `QStackedWidget` pour navigation wizard
- [ ] Extraire `HoldOverlayWidget` de `HoldSelectorApp` (réutilisable)
- [ ] Créer `ClimbCreationState` dataclass (état partagé entre écrans)
- [ ] Implémenter navigation back/next avec préservation état
- [ ] Créer `WizardController` pour gérer les transitions

### Phase 1 : Sélection de prises (0%)
- [ ] Créer `SelectHoldsScreen(QWidget)` utilisant `HoldOverlayWidget`
- [ ] Boutons de type (START, OTHER, FEET, TOP) avec état actif
- [ ] Visualisation couleur par type de prise sélectionnée
- [ ] Liste des prises sélectionnées groupées par type
- [ ] Validation temps réel : min 2 START (désactive "Suivant")
- [ ] Bouton "Suivant" → écran ClimbInfo

### Phase 2 : Formulaire + API Client (0%)
- [ ] Créer `ClimbInfoScreen(QWidget)` avec formulaire
- [ ] Input nom avec validation temps réel (min 3 chars)
- [ ] Sélecteur de grade (`QComboBox` V-Scale/Font + valeur)
- [ ] Sélecteur règle des pieds (depuis `feetRulesOptions`)
- [ ] Input description (`QTextEdit`, optionnel)
- [ ] Toggle public/privé (`QCheckBox`)
- [ ] **API Client** : Ajouter `create_climb()` dans `StoktAPI`
- [ ] **API Client** : Ajouter `update_climb()` dans `StoktAPI`
- [ ] **API Client** : Ajouter `delete_climb()` dans `StoktAPI`

### Phase 3 : Soumission et Feedback (0%)
- [ ] Construire le payload selon la structure documentée
- [ ] POST vers `api/faces/{faceId}/climbs`
- [ ] Affichage loading pendant soumission
- [ ] Gestion erreurs : `nonFieldErrors` → message général
- [ ] Gestion erreurs : `fieldName` → highlight champ
- [ ] Gestion timeout/réseau → message + retry
- [ ] Feedback succès → retour liste + refresh
- [ ] Sauvegarde locale en cas d'échec réseau (optionnel)

---

## Hors scope (reporté)

### TODO 11 : Édition de blocs existants
- Charger un climb existant dans le wizard
- Vérifier permissions avant édition (`canEditHolds`, etc.)
- PATCH pour modifications
- DELETE avec confirmation
- UI pour "permission denied"

### TODO 12 : Mode Circuit
- Sélection de prises en séquence numérotée
- UI différente (numéros sur prises)
- POST/PATCH circuit séparé

---

## Références

- Code décompilé : `stokt_decompiled.js`
  - Endpoints : lignes 415263-467019
  - Structure données : lignes 952298-952325
  - Validations : lignes 903059-952500
  - État Redux : lignes 414464-414505
  - Actions : lignes 414225-414463
  - Permissions : lignes 913285-913290
- `/docs/reverse_engineering/03_ENDPOINTS.md`
- `/docs/reverse_engineering/04_STRUCTURES.md`
