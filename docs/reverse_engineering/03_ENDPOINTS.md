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

## ENDPOINT SETUP (COORDONNÉES PRISES) ⭐

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/faces/{faceId}/setup` | GET | **Setup de la face avec polygones des prises** |

### Construction de l'URL (code source ligne 441393-441395)

```javascript
// fetchSetup / fetchStandaloneSetup
r4 = 'api/faces/';
r1 = '/setup';
r1 = HermesInternal.concat(r4, faceId, r1);
// Résultat: 'api/faces/{faceId}/setup'
```

### URL pour Montoboard

```
GET https://www.sostokt.com/api/faces/61b42d14-c629-434a-8827-801512151a18/setup
Authorization: Token {token}
```

**Statut : ✅ TESTÉ ET FONCTIONNEL** (2025-12-21)

### Structure de la réponse (données réelles)

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
      "polygonStr": "559.96,2358.89 536.00,2382.86 ...",
      "touchPolygonStr": "611.34,2537.10 619.79,2525.36 ...",
      "pathStr": "M559.96,2358.89L536.00,2382.86...z",
      "centroidStr": "572.53 2397.11",
      "topPolygonStr": "552.37,2331.13 511.00,2372.50 ...",
      "centerTapeStr": "564.16 2433.00 541.45 2530.39",
      "rightTapeStr": "583.42 2433.00 612.44 2528.69",
      "leftTapeStr": "547.62 2423.70 479.26 2496.69"
    }
  ]
}
```

### Statistiques Montoboard

| Métrique | Valeur |
|----------|--------|
| Nombre de prises | **776** |
| IDs des prises | 828902 → 829677 |
| Image dimensions | 2263 × 3000 px |
| Image taille | ~1.4 Mo |

### Structure d'un Hold

| Champ | Type | Description |
|-------|------|-------------|
| `id` | number | ID unique de la prise (ex: 828902) |
| `area` | string | Surface de la prise en pixels² |
| `polygonStr` | string | Points du polygone pour rendu (format `x,y x,y...`) |
| `touchPolygonStr` | string | Zone tactile élargie du polygone |
| `pathStr` | string | Chemin SVG complet (format `Mx,yLx,y...z`) |
| `centroidStr` | string | Centre de la prise (format `x y`) |
| `topPolygonStr` | string | Polygone élargi pour prises finish (T) |
| `centerTapeStr` | string | Position ligne tape centrale (format `x1 y1 x2 y2`) |
| `rightTapeStr` | string | Position ligne tape droite |
| `leftTapeStr` | string | Position ligne tape gauche |

### URLs des images

Deux résolutions officielles :

| Version | Dimensions | Source | Usage dans l'app |
|---------|------------|--------|------------------|
| Small | 339×450 | `/walls` → `faces[].smallPicture.name` | Vignettes dans les listes de walls |
| Full | 2263×3000 | `/setup` → `picture.name` | Visualisation et création de climb |

### Usage des images par contexte

| Contexte dans l'app | Image utilisée | Endpoint source |
|---------------------|----------------|-----------------|
| Liste des walls/faces | **Small** (339×450) | `api/gyms/{id}/walls` |
| Visualiser un climb existant | **Full** (2263×3000) | `api/faces/{id}/setup` |
| Créer un nouveau climb | **Full** (2263×3000) | `api/faces/{id}/setup` |

**Code source** (lignes 419299-419307, 587496) :
```javascript
// Visualisation/Création climb → image full
r0 = setup.picture;
r5 = r0.name;
url = baseURL + 'media/' + r5;

// Liste walls → image small
r1 = face.smallPicture;
r22 = r1.name;
```

**URLs Montoboard :**

```bash
# Small (40 Ko) - pour vignettes
https://www.sostokt.com/media/CACHE/images/walls/1ab81c9a-ecfa-4a1a-b56e-1490f3445d99/faces/61b42d14-c629-434a-8827-801512151a18/ref_pic_qMsRutJ_small.jpg

# Full haute résolution (1.4 Mo) - pour climbs
https://www.sostokt.com/media/CACHE/images/walls/1ab81c9a-ecfa-4a1a-b56e-1490f3445d99/faces/61b42d14-c629-434a-8827-801512151a18/ref_pic_qMsRutJ/07a8d28cb558f811ef292ca0bb0269f9.jpg
```

### Lien holdsList → holds du setup

Le champ `holdsList` d'un climb contient des tokens de format `{TYPE}{ID}` :

```
holdsList: "S829279 S829528 O828906 O828964 T829009"
            │  │
            │  └── ID numérique → correspond à holds[].id dans setup
            └── Type de prise
```

**Types de prises** (parseHoldsListString, ligne 915642) :
| Code | Type | Description |
|------|------|-------------|
| `S` | Start | Prise de départ |
| `O` | Other | Prise intermédiaire |
| `F` | Feet | Pied obligatoire ("pieds des mains") |
| `T` | Top | Prise finale |

### Algorithme de rendu (ligne 922163-922265)

```javascript
// Pour chaque hold dans holdsList, on cherche le hold correspondant dans setup.holds
// Puis on collecte son polygonStr selon le type :
holds.forEach(hold => {
  holdsListIds.forEach(id => {
    if (hold.id === id) {
      if (type === 'S' || type === 'O') {
        polygons.push(hold.polygonStr);
      } else if (type === 'F') {
        feetPolygons.push(hold.polygonStr);
      } else if (type === 'T') {
        finishPolygons.push(hold.polygonStr, hold.topPolygonStr);
      }
    }
  });
});
```

**Note** : Peut nécessiter des permissions (créateur de mur, abonnement actif).

## ENDPOINTS NON FONCTIONNELS (pour utilisateur standard)

| Endpoint | Statut | Note |
|----------|--------|------|
| `api/gyms/{id}/` | ❌ 404 | Utiliser `/summary` |
| `api/gyms/{id}/faces` | ❌ 404 | Utiliser `/walls` (inclut faces) |
| `api/faces/{faceId}` | ❌ 403 | Permission refusée |
| `api/faces/{faceId}/latest-climbs/paginated` | ❌ 404 | Endpoint protégé |
| `api/users/{id}/sent-climbs` | ❌ 404 | Utiliser `/gyms/{id}/my-sent-climbs` |
| `api/efforts` | ❌ 403 | Permission refusée |

## ENDPOINTS INTERACTIONS SOCIALES (découverts, non testés)

### Likes (lignes 466084-466295)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/climbs/{climbId}/likes` | GET | Liste des likes |
| `api/climbs/{climbId}/likes` | POST | Ajouter un like |
| `api/climbs/{climbId}/likes` | DELETE | Retirer un like |
| `api/gyms/{gymId}/my-liked-climbs` | GET | Mes climbs likés |

### Commentaires (lignes 467185-467380)

| Endpoint | Méthode | Body | Description |
|----------|---------|------|-------------|
| `api/climbs/{climbId}/comments?limit={n}` | GET | - | Liste des commentaires |
| `api/climbs/{climbId}/comments` | POST | `{text, replied_to_id}` | Poster un commentaire |
| `api/climbs/{climbId}/comments/{commentId}` | DELETE | - | Supprimer un commentaire |

### Bookmarks (lignes 466950-467018)

| Endpoint | Méthode | Body | Description |
|----------|---------|------|-------------|
| `api/climbs/{climbId}/bookmarked` | PATCH | `{added, removed}` | Toggle favori |
| `api/gyms/{gymId}/my-bookmarked-climbs` | GET | - | Mes climbs favoris |

### Efforts/Ascensions (lignes 466297-466505)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/efforts` | POST | Enregistrer une ascension |
| `api/efforts/{effortId}` | PATCH | Modifier une ascension |
| `api/efforts/{effortId}` | DELETE | Supprimer une ascension |
| `api/climbs/{climbId}/latest-sends` | GET | Dernières ascensions |

### Notes (lignes 466506-466560)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/ratings` | POST | Soumettre une note de difficulté |
| `api/climbs/{climbId}/crowd-grades` | GET | Notes de la communauté |

## ENDPOINTS DÉCOUVERTS (NON TESTÉS)

### Autres endpoints depuis le code décompilé

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/signup/` | POST | Inscription |
| `api/logout/` | POST | Déconnexion |
| `api/password/reset/` | POST | Reset mot de passe |
| `api/social-auth/apple/login` | POST | Login Apple |
| `api/social-auth/google/login` | POST | Login Google |
| `api/favorite-gyms` | GET | Gyms favoris |
| `api/climbs/` | GET/POST | Climbs |
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

**Dernière mise à jour** : 2025-12-22
**Testé avec** : API v1.3.0, App v6.1.13
