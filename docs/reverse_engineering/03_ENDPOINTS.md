# Endpoints API Stōkt

**Source** : Analyse du code décompilé (`stokt_decompiled.js`) + Tests réels

## Base URL

```
https://www.sostokt.com/
```

## ENDPOINTS TESTÉS ET FONCTIONNELS

### Authentification

| Endpoint | Méthode | Statut | Description |
|----------|---------|--------|-------------|
| `api/token-auth` | POST | ✅ 200 | Authentification |
| `api/users/me` | GET | ✅ 200 | Profil utilisateur |
| `api/version` | GET | ✅ 200 | Version API (1.3.0) |
| `api/my-notifications` | GET | ✅ 200 | Notifications |

#### Exemple : Authentification

```bash
# Login
curl -X POST "https://www.sostokt.com/api/token-auth" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=EMAIL&password=PASSWORD"

# Réponse
{"token":"dba723cbee34ff3cf049b12150a21dc8919c3cf8"}

# Profil
curl "https://www.sostokt.com/api/users/me" \
  -H "Authorization: Token dba723cbee34ff3cf049b12150a21dc8919c3cf8"
```

### Gyms

| Endpoint | Méthode | Statut | Description |
|----------|---------|--------|-------------|
| `api/gyms/{id}/summary` | GET | ✅ 200 | Résumé gym (stats, walls, managers) |
| `api/gyms/{id}/walls` | GET | ✅ 200 | Liste des murs avec faces |
| `api/gyms/{id}/climbs?max_age={days}` | GET | ✅ 200 | Climbs (paginé) |
| `api/gyms/{id}/my-sent-climbs` | GET | ✅ 200 | Mes climbs validés |

#### Exemple : Récupérer le résumé d'un gym

```bash
GYM_ID="be149ef2-317d-4c73-8d7d-50074577d2fa"

curl "https://www.sostokt.com/api/gyms/$GYM_ID/summary" \
  -H "Authorization: Token $TOKEN"
```

**Réponse** :
```json
{
  "id": "be149ef2-317d-4c73-8d7d-50074577d2fa",
  "displayName": "Montoboard",
  "unit": "FEET",
  "numberOfClimbs": 1174,
  "numberOfClimbers": 121,
  "numberOfSends": 5745,
  "walls": [
    {
      "id": "1ab81c9a-ecfa-4a1a-b56e-1490f3445d99",
      "name": "Stōkt board",
      "isAngleAdjustable": false,
      "feetRules": [
        {"name": "Tous pieds", "isDefault": true},
        {"name": "Pieds des mains", "isDefault": false}
      ]
    }
  ],
  "defaultPictures": ["CACHE/images/walls/.../ref_pic.jpg"],
  "gymManagers": [...],
  "locationString": "Caraman, France"
}
```

#### Exemple : Récupérer les murs et faces

```bash
curl "https://www.sostokt.com/api/gyms/$GYM_ID/walls" \
  -H "Authorization: Token $TOKEN"
```

**Réponse** :
```json
[
  {
    "id": "1ab81c9a-ecfa-4a1a-b56e-1490f3445d99",
    "name": "Stōkt board",
    "angle": null,
    "isActive": true,
    "faces": [
      {
        "id": "61b42d14-c629-434a-8827-801512151a18",
        "isActive": true,
        "smallPicture": {
          "name": "CACHE/images/walls/.../ref_pic_small.jpg",
          "width": 339,
          "height": 450
        },
        "totalClimbs": 1017
      }
    ],
    "angles": [],
    "isAngleAdjustable": false
  }
]
```

#### Exemple : Récupérer TOUS les climbs

```bash
# Pour avoir tous les climbs, utiliser max_age=9999
curl "https://www.sostokt.com/api/gyms/$GYM_ID/climbs?max_age=9999" \
  -H "Authorization: Token $TOKEN"
```

**Réponse** :
```json
{
  "count": 1017,
  "next": "https://www.sostokt.com/api/gyms/.../climbs?max_age=9999&page=2",
  "previous": null,
  "results": [
    {
      "id": "82861103-b552-4b5d-99fd-8519ed905809",
      "name": "200€ To 500€",
      "holdsList": "S829284 F829104 F829656 O829309 O829341 O829441 O829651 T829220",
      "feetRule": "Pieds des mains",
      "crowdGrade": {"ircra": 20.5, "hueco": "V6", "font": "7A", "dankyu": "1Q"},
      "climbSetters": {"id": "...", "fullName": "Thomas Pamies", "avatar": "..."},
      "faceId": "61b42d14-c629-434a-8827-801512151a18",
      "wallId": "1ab81c9a-ecfa-4a1a-b56e-1490f3445d99",
      "climbedBy": 0,
      "totalLikes": 0,
      "dateCreated": "2025-12-17T10:56:38.491973-05:00"
    }
  ]
}
```

#### Exemple : Mes climbs validés

```bash
curl "https://www.sostokt.com/api/gyms/$GYM_ID/my-sent-climbs" \
  -H "Authorization: Token $TOKEN"
```

**Réponse** :
```json
[
  {
    "id": "0fb29bba-9ab3-434a-ba2f-a8bb7b27597f",
    "name": "Dwarfito",
    "holdsList": "S829279 S829528 O828906 O828964 O828985 O829120 O829377 O829459 T829009",
    "crowdGrade": {"ircra": 13.25, "hueco": "V0", "font": "4+", "dankyu": "6Q"},
    "attemptsToSendOriginal": null,
    "lastEffortDate": null
  }
]
```

## ENDPOINTS NON FONCTIONNELS

| Endpoint | Statut | Note |
|----------|--------|------|
| `api/gyms/{id}/` | ❌ 404 | Utiliser `/summary` |
| `api/gyms/{id}/faces` | ❌ 404 | Utiliser `/walls` (inclut faces) |
| `api/faces/{faceId}` | ❌ 403 | Permission refusée |
| `api/faces/{faceId}/latest-climbs/paginated` | ❌ 404 | Endpoint protégé |
| `api/users/{id}/sent-climbs` | ❌ 404 | Utiliser `/gyms/{id}/my-sent-climbs` |
| `api/efforts` | ❌ 403 | Permission refusée |
| `api/gyms/paginated` | ❌ 404 | Non testé en détail |

## ENDPOINTS DÉCOUVERTS (NON TESTÉS)

### Depuis le code décompilé

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/signup/` | POST | Inscription |
| `api/logout/` | POST | Déconnexion |
| `api/password/reset/` | POST | Reset mot de passe |
| `api/social-auth/apple/login` | POST | Login Apple |
| `api/social-auth/google/login` | POST | Login Google |
| `api/favorite-gyms` | GET | Gyms favoris |
| `api/climbs/` | GET/POST | Climbs |
| `api/efforts/` | POST | Enregistrer effort |
| `api/ratings` | POST | Notes |
| `api/lists/` | GET | Listes |
| `api/follow/` | POST | Suivre |
| `api/feeds/` | GET | Flux social |
| `api/led-kit/` | GET | LED Kit |
| `api/videos` | GET | Vidéos |

## CONSTRUCTION DES URLS

### Pattern découvert dans le code

```javascript
// fetchMySentClimbs (ligne 442389)
r4 = 'api/gyms/';
r1 = '/my-sent-climbs';
r1 = HermesInternal.concat(r4, gymId, r1);
// Résultat: 'api/gyms/{gymId}/my-sent-climbs'

// fetchGymRecentClimbs (ligne 458971)
r2 = 'api/gyms/';
r1 = '/climbs?max_age=';
r3 = HermesInternal.concat(r2, gymId, r1, maxAge);
// Résultat: 'api/gyms/{gymId}/climbs?max_age={maxAge}'
```

## PAGINATION

L'API utilise le format Django REST Framework :

```json
{
  "count": 1017,
  "next": "https://www.sostokt.com/api/...?page=2",
  "previous": null,
  "results": [...]
}
```

Pour récupérer toutes les pages :
```python
all_results = []
url = f"{BASE}/api/gyms/{gym_id}/climbs?max_age=9999"

while url:
    response = requests.get(url, headers=headers)
    data = response.json()
    all_results.extend(data['results'])
    url = data.get('next')
```

## HEADERS REQUIS

```http
Authorization: Token {token}
Content-Type: application/x-www-form-urlencoded  # Pour POST
```

## IMAGES

Les images sont accessibles via :
```
https://www.sostokt.com/media/{chemin_image}
```

Exemple :
```
https://www.sostokt.com/media/CACHE/images/walls/1ab81c9a.../ref_pic_small.jpg
```

---

**Dernière mise à jour** : 2025-12-20
**Testé avec** : API v1.3.0, App v6.1.13
