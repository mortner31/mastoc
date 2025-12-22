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

## Face Setup (Coordonnées Prises) ✅ TESTÉ

L'endpoint `api/faces/{faceId}/setup` retourne la configuration de la face avec les polygones de toutes les prises.

### Structure réelle (testée 2025-12-21)

```json
{
  "id": "61b42d14-c629-434a-8827-801512151a18",
  "gym": "Montoboard",
  "wall": "Stōkt board",
  "picture": {
    "name": "CACHE/images/walls/.../07a8d28cb558f811ef292ca0bb0269f9.jpg",
    "width": 2263,
    "height": 3000
  },
  "feetRulesOptions": ["Tous pieds", "Pieds des mains", "No foot", ...],
  "hasSymmetry": false,
  "holds": [
    {
      "id": 828902,
      "area": "2226.00",
      "polygonStr": "559.96,2358.89 536.00,2382.86 536.00,2409.59 ...",
      "touchPolygonStr": "611.34,2537.10 619.79,2525.36 ...",
      "pathStr": "M559.96,2358.89L536.00,2382.86L536.00,2409.59...z",
      "centroidStr": "572.53 2397.11",
      "topPolygonStr": "552.37,2331.13 511.00,2372.50 ...",
      "centerTapeStr": "564.16 2433.00 541.45 2530.39",
      "rightTapeStr": "583.42 2433.00 612.44 2528.69",
      "leftTapeStr": "547.62 2423.70 479.26 2496.69"
    }
  ]
}
```

### Structure d'un Hold

| Champ | Type | Description |
|-------|------|-------------|
| `id` | number | ID unique (ex: 828902) - correspond aux IDs dans holdsList |
| `area` | string | Surface en pixels² |
| `polygonStr` | string | Points du polygone SVG (format `x,y x,y...`) |
| `touchPolygonStr` | string | Zone tactile élargie |
| `pathStr` | string | Chemin SVG (format `Mx,yLx,y...z`) |
| `centroidStr` | string | Centre de la prise (format `x y`) |
| `topPolygonStr` | string | Polygone élargi pour prises finish |
| `centerTapeStr` | string | Position tape centrale |
| `rightTapeStr` | string | Position tape droite |
| `leftTapeStr` | string | Position tape gauche |

### Mapping holdsList → polygones

```python
def get_climb_polygons(climb, setup):
    """
    Récupère les polygones d'un climb depuis le setup
    """
    holds_map = {h['id']: h for h in setup['holds']}
    result = {'start': [], 'other': [], 'feet': [], 'top': []}

    for token in climb['holdsList'].split():
        hold_type = token[0]
        hold_id = int(token[1:])
        hold = holds_map.get(hold_id)

        if hold:
            if hold_type == 'S':
                result['start'].append(hold['polygonStr'])
            elif hold_type == 'O':
                result['other'].append(hold['polygonStr'])
            elif hold_type == 'F':
                result['feet'].append(hold['polygonStr'])
            elif hold_type == 'T':
                result['top'].append(hold['polygonStr'])
                result['top'].append(hold['topPolygonStr'])

    return result
```

### Position pixel (via centroidStr)

```python
# centroidStr contient déjà les coordonnées en pixels
centroid = hold['centroidStr'].split()
pixel_x = float(centroid[0])  # ex: 572.53
pixel_y = float(centroid[1])  # ex: 2397.11
```

### Statistiques prises (Montoboard)

- **776 prises** sur la face (setup)
- IDs de 828902 à 829677
- Image : 2263×3000 pixels
- Fichier setup : 504 Ko

## Lignes de Tape (Start Holds) ✅ ANALYSÉ

Les champs `centerTapeStr`, `leftTapeStr`, `rightTapeStr` définissent les lignes de marquage pour les prises de départ.

### Format

```
"centerTapeStr": "x1 y1 x2 y2"
```

4 valeurs séparées par des espaces : coordonnées de début (x1, y1) et fin (x2, y2) de la ligne.

### Logique d'affichage (code décompilé lignes 922271-922322)

| Nb prises START | Affichage |
|-----------------|-----------|
| 1 prise | 2 lignes : `leftTapeStr` + `rightTapeStr` → forme "V" |
| 2+ prises | 1 ligne `centerTapeStr` par prise |

### Code simplifié (extrait décompilé)

```javascript
// stokt_decompiled.js lignes 922271-922322
if (startHolds.length !== 1) {
    // Plus d'une prise de départ → trait central uniquement
    tapeLines.push(hold.centerTapeStr);
} else {
    // Une seule prise de départ → deux traits (gauche + droite)
    tapeLines.push(hold.leftTapeStr, hold.rightTapeStr);
}
```

### Rendu

Les lignes sont dessinées en **blanc**, avec un `strokeWidth` configurable.

### Parser Python

```python
def parse_tape_line(tape_str: str) -> tuple | None:
    """Parse un tapeStr en deux points (p1, p2)."""
    if not tape_str:
        return None
    parts = tape_str.split()
    if len(parts) != 4:
        return None
    x1, y1, x2, y2 = map(float, parts)
    return ((x1, y1), (x2, y2))
```

---

**Dernière mise à jour** : 2025-12-22
**Source des données** : Montoboard (be149ef2-317d-4c73-8d7d-50074577d2fa)
