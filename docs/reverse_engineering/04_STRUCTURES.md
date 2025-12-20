# Structures de Données Stōkt

**Source** : Analyse du code décompilé + Réponses API réelles

## Climb (Bloc/Problème)

### Structure complète (depuis API)

```json
{
  "id": "82861103-b552-4b5d-99fd-8519ed905809",
  "name": "200€ To 500€",
  "climbSetters": {
    "id": "ea5ae2eb-15ee-4c4d-98d6-d809aa9c9608",
    "fullName": "Thomas Pamies",
    "avatar": "CACHE/images/users/avatars/ea/ea5ae2eb-...jpg"
  },
  "holdsList": "S829284 F829104 F829656 O829309 O829341 O829441 O829651 T829220",
  "mirrorHoldsList": "",
  "feetRule": "Pieds des mains",
  "dateCreated": "2025-12-17T10:56:38.491973-05:00",
  "isPrivate": false,
  "isBenchmark": false,
  "crowdGrade": {
    "ircra": 20.5,
    "hueco": "V6",
    "font": "7A",
    "dankyu": "1Q"
  },
  "crowdGrades": [],
  "faceId": "61b42d14-c629-434a-8827-801512151a18",
  "wallId": "1ab81c9a-ecfa-4a1a-b56e-1490f3445d99",
  "wallName": "Stōkt board",
  "isAngleAdjustable": false,
  "angle": "",
  "climbedBy": 0,
  "totalLikes": 0,
  "totalComments": 1,
  "likedByUser": false,
  "bookmarkedByUser": false,
  "hasSymmetric": false,
  "circuit": "",
  "tags": "",
  "attemptsToSendMirror": 0,
  "attemptsToSendOriginal": 0,
  "lastAttemptDate": null,
  "lastEffortDate": null,
  "lastEffortIsFlashed": null
}
```

### Champs principaux

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique |
| `name` | string | Nom du problème |
| `holdsList` | string | Prises du climb (voir format ci-dessous) |
| `mirrorHoldsList` | string | Prises en version miroir |
| `feetRule` | string | Règle pour les pieds |
| `crowdGrade` | object | Note de difficulté communautaire |
| `climbSetters` | object | Créateur du climb |
| `faceId` | UUID | ID de la face |
| `wallId` | UUID | ID du mur |
| `climbedBy` | int | Nombre de grimpeurs qui l'ont validé |
| `totalLikes` | int | Nombre de likes |
| `isPrivate` | bool | Climb privé |
| `isBenchmark` | bool | Climb de référence |

## Format holdsList

### Syntaxe

```
{TYPE}{ID} {TYPE}{ID} ...
```

### Types de prises

| Type | Signification | Description |
|------|---------------|-------------|
| `S` | Start | Prise de départ (main) |
| `O` | Other | Prise normale |
| `F` | Feet | Prise de pied obligatoire |
| `T` | Top | Prise finale (top) |

### Exemples

```
# Climb avec 2 départs, 6 prises et 1 top
S829279 S829528 O828906 O828964 O828985 O829120 O829377 O829459 T829009

# Climb "pieds des mains" avec pieds obligatoires
S829284 F829104 F829656 O829309 O829341 O829441 O829651 T829220
```

### Parser Python

```python
def parse_holds_list(holds_str: str) -> list[dict]:
    """
    Parse le format holdsList d'un climb

    Returns: [{"type": "S", "id": 829279}, ...]
    """
    if not holds_str:
        return []

    holds = []
    for hold in holds_str.split():
        if len(hold) > 1:
            hold_type = hold[0]
            hold_id = int(hold[1:])
            holds.append({"type": hold_type, "id": hold_id})
    return holds

# Exemple
holds = parse_holds_list("S829279 O828906 T829009")
# [{'type': 'S', 'id': 829279}, {'type': 'O', 'id': 828906}, {'type': 'T', 'id': 829009}]
```

## Système de Notation (crowdGrade)

### Structure

```json
{
  "ircra": 20.5,
  "hueco": "V6",
  "font": "7A",
  "dankyu": "1Q"
}
```

### Échelles

| Système | Origine | Exemple |
|---------|---------|---------|
| `ircra` | IRCRA (International) | 0-30+ (numérique) |
| `hueco` | USA | V0, V1, V2... V17 |
| `font` | Fontainebleau (France) | 4, 4+, 5, 5+, 6A, 6A+... 9A |
| `dankyu` | Japon | 6Q, 5Q, 4Q... 1Q, 1D, 2D... |

### Correspondance approximative

| Font | Hueco | IRCRA |
|------|-------|-------|
| 4 | V0 | 12 |
| 5 | V1 | 14 |
| 6A | V2 | 16 |
| 6B | V3 | 17 |
| 6C | V4 | 18 |
| 7A | V6 | 20 |
| 7B | V8 | 22 |
| 7C | V10 | 24 |
| 8A | V11 | 25 |

## Gym Summary

### Structure

```json
{
  "id": "be149ef2-317d-4c73-8d7d-50074577d2fa",
  "displayName": "Montoboard",
  "unit": "FEET",
  "numberOfClimbs": 1174,
  "numberOfClimbers": 121,
  "numberOfSends": 5745,
  "isFavorite": false,
  "walls": [...],
  "pictures": [],
  "isEditable": false,
  "description": null,
  "defaultPictures": ["CACHE/images/walls/.../ref_pic.jpg"],
  "gymType": "COMMERCIAL",
  "gymManagers": [...],
  "locationString": "Caraman, France",
  "wallType": "Commercial"
}
```

## Wall

### Structure

```json
{
  "id": "1ab81c9a-ecfa-4a1a-b56e-1490f3445d99",
  "name": "Stōkt board",
  "angle": null,
  "isActive": true,
  "faces": [...],
  "angles": [],
  "defaultAngle": "",
  "isAngleAdjustable": false
}
```

## Face

### Structure

```json
{
  "id": "61b42d14-c629-434a-8827-801512151a18",
  "isActive": true,
  "dateModified": "2023-03-24T14:21:22.104010-05:00",
  "smallPicture": {
    "name": "CACHE/images/walls/.../ref_pic_small.jpg",
    "width": 339,
    "height": 450
  },
  "totalClimbs": 1017
}
```

## Règles de Pieds (feetRule)

| Valeur | Description |
|--------|-------------|
| `Tous pieds` | Toutes les prises comme pieds |
| `Pieds des mains` | Pieds uniquement sur prises de mains utilisées |
| `Pieds définis` | Pieds sur prises marquées F |
| `No foot` | Pas de pieds (campus) |
| `Petits pieds` | Petites prises pour pieds |
| `Tous pieds + pieds jaunes` | Prises jaunes additionnelles |

## User Profile

### Structure (api/users/me)

```json
{
  "id": "35722f7d-79d2-4688-a856-9d9caf34be7b",
  "username": "...",
  "email": "...",
  "firstName": "...",
  "lastName": "...",
  "fullName": "...",
  "avatar": "...",
  "homeGym": {
    "id": "be149ef2-317d-4c73-8d7d-50074577d2fa",
    "displayName": "Montoboard"
  },
  "subscriptionStatus": "INACTIVE",
  "isStaff": false,
  "gradePreference": "font",
  "gradeFeel": 0
}
```

## Pagination (Django REST)

```json
{
  "count": 1017,
  "next": "https://www.sostokt.com/api/...?page=2",
  "previous": null,
  "results": [...]
}
```

## Face Setup (Coordonnées Prises)

L'endpoint `api/faces/{faceId}/setup` retourne la configuration de la face avec les coordonnées de toutes les prises.

### Structure attendue

```json
{
  "picture": {
    "name": "CACHE/images/walls/.../ref_pic.jpg",
    "width": 905,
    "height": 1200
  },
  "holds": [
    {
      "id": 829279,
      "x": 0.45,
      "y": 0.32
    }
  ]
}
```

### Mapping ID → Position

Les IDs de prises dans `holdsList` (ex: `S829279`) correspondent aux `id` dans le setup.
Les coordonnées `x` et `y` sont probablement des ratios (0-1) par rapport aux dimensions de l'image.

**Position pixel** :
```python
pixel_x = hold.x * picture.width   # ex: 0.45 * 905 = 407px
pixel_y = hold.y * picture.height  # ex: 0.32 * 1200 = 384px
```

### Statistiques prises (Montoboard)

- **738 prises uniques** sur la face
- Prise la plus utilisée : **829098** (78 fois sur 1017 climbs)
- Total utilisations : 8785 prises dans tous les climbs

---

**Dernière mise à jour** : 2025-12-20
**Source des données** : Montoboard (be149ef2-317d-4c73-8d7d-50074577d2fa)
