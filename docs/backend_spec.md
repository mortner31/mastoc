# Spécification : Backend mastoc indépendant

## Résumé

Créer un backend REST compatible avec mastoc pour remplacer l'API Stokt, avec :
- **Multi-utilisateur** : Chaque grimpeur a ses propres blocs et ascensions
- **Images locales** : Photos de mur hébergées sur votre serveur
- **Compatibilité lecture** : Import initial des données Stokt

---

## Architecture cible

```
┌─────────────────┐      HTTPS/REST       ┌──────────────────────────┐
│   mastoc       │ ◄───────────────────► │  Votre Backend           │
│   (PyQt6)       │                       │  (Django/FastAPI/autre)  │
└─────────────────┘                       ├──────────────────────────┤
                                          │  PostgreSQL/SQLite       │
                                          │  + Stockage images       │
                                          └──────────────────────────┘
                                                     ▲
                                                     │ Import initial
                                          ┌──────────────────────────┐
                                          │  API Stokt (lecture)     │
                                          └──────────────────────────┘
```

---

## Modèle de données

### Tables principales

```sql
-- Utilisateurs
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    avatar TEXT,  -- chemin vers image avatar
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tokens d'authentification
CREATE TABLE auth_tokens (
    token TEXT PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Salles d'escalade
CREATE TABLE gyms (
    id UUID PRIMARY KEY,
    display_name TEXT NOT NULL,
    location_string TEXT,
    gym_type TEXT,  -- 'commercial', 'home', etc.
    wall_type TEXT,  -- 'spray_wall', 'moonboard', etc.
    created_at TIMESTAMP DEFAULT NOW()
);

-- Murs
CREATE TABLE walls (
    id UUID PRIMARY KEY,
    gym_id UUID REFERENCES gyms(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    angle TEXT,
    is_angle_adjustable BOOLEAN DEFAULT FALSE,
    default_angle TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Faces (une face = une configuration de prises)
CREATE TABLE faces (
    id UUID PRIMARY KEY,
    wall_id UUID REFERENCES walls(id) ON DELETE CASCADE,
    picture_path TEXT NOT NULL,  -- chemin local vers l'image
    picture_width INTEGER NOT NULL,
    picture_height INTEGER NOT NULL,
    feet_rules_options JSONB DEFAULT '[]',
    has_symmetry BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_modified TIMESTAMP DEFAULT NOW()
);

-- Prises physiques sur le mur
CREATE TABLE holds (
    id SERIAL PRIMARY KEY,
    face_id UUID REFERENCES faces(id) ON DELETE CASCADE,
    area REAL,
    polygon_str TEXT NOT NULL,      -- "x1,y1 x2,y2 x3,y3..."
    touch_polygon_str TEXT,
    path_str TEXT,                   -- SVG path pour rendu
    centroid_x REAL NOT NULL,
    centroid_y REAL NOT NULL,
    top_polygon_str TEXT,
    center_tape_str TEXT,
    right_tape_str TEXT,
    left_tape_str TEXT
);
CREATE INDEX idx_holds_face ON holds(face_id);

-- Blocs/Problèmes
CREATE TABLE climbs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    face_id UUID REFERENCES faces(id) ON DELETE CASCADE,
    setter_id UUID REFERENCES users(id),
    name TEXT NOT NULL,
    holds_list TEXT NOT NULL,        -- "S123 O456 O789 T012"
    mirror_holds_list TEXT,
    feet_rule TEXT,
    description TEXT,
    is_private BOOLEAN DEFAULT FALSE,
    is_benchmark BOOLEAN DEFAULT FALSE,
    has_symmetric BOOLEAN DEFAULT FALSE,
    angle TEXT,
    circuit TEXT,
    tags TEXT,
    date_created TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_climbs_face ON climbs(face_id);
CREATE INDEX idx_climbs_setter ON climbs(setter_id);

-- Grades communautaires (agrégation des votes)
CREATE TABLE crowd_grades (
    climb_id UUID PRIMARY KEY REFERENCES climbs(id) ON DELETE CASCADE,
    ircra REAL,       -- 0-30+
    hueco TEXT,       -- V0-V17
    font TEXT,        -- 4-9A
    dankyu TEXT,      -- 6Q-6D
    votes_count INTEGER DEFAULT 0
);

-- Votes de grade individuels
CREATE TABLE grade_votes (
    id SERIAL PRIMARY KEY,
    climb_id UUID REFERENCES climbs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    grade_value TEXT NOT NULL,       -- "6a+", "V4", etc.
    grading_system TEXT NOT NULL,    -- "Font", "Hueco", etc.
    grade_feel INTEGER DEFAULT 0,    -- -1 (soft), 0 (ok), +1 (hard)
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(climb_id, user_id)
);

-- Ascensions (sends)
CREATE TABLE efforts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    climb_id UUID REFERENCES climbs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    is_flash BOOLEAN DEFAULT FALSE,
    attempts_number INTEGER,
    grade_feel INTEGER DEFAULT 0,
    effort_date TIMESTAMP DEFAULT NOW(),
    UNIQUE(climb_id, user_id, effort_date::DATE)
);
CREATE INDEX idx_efforts_climb ON efforts(climb_id);
CREATE INDEX idx_efforts_user ON efforts(user_id);

-- Likes
CREATE TABLE likes (
    climb_id UUID REFERENCES climbs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (climb_id, user_id)
);

-- Commentaires
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    climb_id UUID REFERENCES climbs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    replied_to_id UUID REFERENCES comments(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_comments_climb ON comments(climb_id);

-- Bookmarks
CREATE TABLE bookmarks (
    climb_id UUID REFERENCES climbs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (climb_id, user_id)
);
```

---

## Spécification des Endpoints

### Authentification

#### `POST /api/token-auth`

Authentifie un utilisateur et retourne un token.

**Request:**
```
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secret123
```

**Response 200:**
```json
{
    "token": "abc123def456..."
}
```

**Response 401:**
```json
{
    "detail": "Invalid credentials"
}
```

**Implémentation:**
- Vérifier email/password contre `users.password_hash` (bcrypt recommandé)
- Générer token aléatoire (32+ caractères)
- Insérer dans `auth_tokens`
- Retourner le token

---

#### `GET /api/users/me`

Retourne le profil de l'utilisateur connecté.

**Headers:** `Authorization: Token <token>`

**Response 200:**
```json
{
    "id": "uuid-here",
    "email": "user@example.com",
    "fullName": "Jean Dupont",
    "avatar": "/media/avatars/user123.jpg"
}
```

---

### Gymnases/Salles

#### `GET /api/gyms/{gymId}/summary`

**Response 200:**
```json
{
    "id": "gym-uuid",
    "displayName": "Ma Salle",
    "locationString": "Paris, France",
    "numberOfClimbs": 150,
    "numberOfClimbers": 25,
    "numberOfSends": 890,
    "gymType": "home",
    "wallType": "spray_wall",
    "isFavorite": true,
    "isEditable": true
}
```

---

#### `GET /api/gyms/{gymId}/walls`

Liste les murs d'une salle.

**Response 200:**
```json
[
    {
        "id": "wall-uuid",
        "name": "Mur Principal",
        "isActive": true,
        "angle": "40°",
        "isAngleAdjustable": true,
        "defaultAngle": "40°",
        "faces": [
            {
                "id": "face-uuid",
                "isActive": true,
                "totalClimbs": 150
            }
        ]
    }
]
```

---

#### `GET /api/gyms/{gymId}/climbs`

Liste les blocs d'une salle (paginé).

**Query params:**
- `max_age` (int) : Filtrer les blocs créés dans les N derniers jours
- `page` (int) : Numéro de page (défaut: 1)

**Response 200:**
```json
{
    "count": 150,
    "next": "/api/gyms/xxx/climbs?page=2",
    "previous": null,
    "results": [
        {
            "id": "climb-uuid",
            "name": "Projet Rouge",
            "holdsList": "S12345 O12346 O12347 T12348",
            "mirrorHoldsList": "",
            "feetRule": "Pieds des mains",
            "faceId": "face-uuid",
            "wallId": "wall-uuid",
            "wallName": "Mur Principal",
            "dateCreated": "2025-01-15T14:30:00Z",
            "isPrivate": false,
            "isBenchmark": false,
            "climbedBy": 12,
            "totalLikes": 5,
            "totalComments": 3,
            "hasSymmetric": false,
            "angle": "40°",
            "isAngleAdjustable": true,
            "circuit": "",
            "tags": "technique,équilibre",
            "climbSetters": {
                "id": "user-uuid",
                "fullName": "Marie Martin",
                "avatar": "/media/avatars/marie.jpg"
            },
            "crowdGrade": {
                "ircra": 18.5,
                "hueco": "V5",
                "font": "6b+",
                "dankyu": "3D"
            }
        }
    ]
}
```

---

### Faces & Prises

#### `GET /api/faces/{faceId}/setup`

Retourne la configuration complète d'une face avec toutes ses prises.

**Response 200:**
```json
{
    "id": "face-uuid",
    "gym": "Ma Salle",
    "wall": "Mur Principal",
    "picture": {
        "name": "/media/walls/mur-principal.jpg",
        "width": 2263,
        "height": 3000
    },
    "smallPicture": {
        "name": "/media/walls/mur-principal-small.jpg",
        "width": 339,
        "height": 450
    },
    "feetRulesOptions": [
        "Pieds des mains",
        "Pieds libres",
        "Pieds en volume"
    ],
    "hasSymmetry": true,
    "holds": [
        {
            "id": 12345,
            "area": "2226.00",
            "polygonStr": "559.96,2358.89 536.00,2382.86 520.76,2397.11 ...",
            "touchPolygonStr": "...",
            "pathStr": "M559.96,2358.89L536.00,2382.86L520.76,2397.11...z",
            "centroidStr": "572.53 2397.11",
            "topPolygonStr": "",
            "centerTapeStr": "",
            "rightTapeStr": "",
            "leftTapeStr": ""
        }
    ]
}
```

**Note sur les polygones:**
- `polygonStr` : Liste de points "x,y" séparés par espaces
- `centroidStr` : Centre de la prise "x y"
- `pathStr` : Chemin SVG pour rendu vectoriel

---

### Blocs (Climbs)

#### `POST /api/faces/{faceId}/climbs`

Crée un nouveau bloc.

**Headers:** `Authorization: Token <token>`

**Request:**
```json
{
    "name": "Mon nouveau bloc",
    "holdsList": {
        "start": ["12345", "12346"],
        "others": ["12347", "12348", "12349"],
        "top": ["12350"],
        "feetOnly": []
    },
    "grade": {
        "gradingSystem": "Font",
        "value": "6a+"
    },
    "description": "Bloc technique avec un mouvement de coordination",
    "isPrivate": false,
    "feetRule": "Pieds des mains"
}
```

**Response 201:**
```json
{
    "id": "new-climb-uuid",
    "name": "Mon nouveau bloc",
    "holdsList": "S12345 S12346 O12347 O12348 O12349 T12350",
    "faceId": "face-uuid",
    "dateCreated": "2025-01-20T10:00:00Z",
    "climbSetters": {
        "id": "current-user-uuid",
        "fullName": "Jean Dupont"
    }
}
```

**Logique de conversion holdsList:**
- `start` → préfixe "S"
- `others` → préfixe "O"
- `top` → préfixe "T"
- `feetOnly` → préfixe "F"

---

#### `PATCH /api/faces/{faceId}/climbs/{climbId}`

Modifie un bloc existant.

**Headers:** `Authorization: Token <token>`

**Request:** (champs partiels)
```json
{
    "name": "Nouveau nom",
    "holdsList": {
        "start": ["12345"],
        "others": ["12347", "12348"],
        "top": ["12350"],
        "feetOnly": []
    }
}
```

**Response 200:** Bloc mis à jour (même format que GET)

**Permissions:** Seul le setter ou un admin peut modifier

---

#### `DELETE /api/climbs/{climbId}`

Supprime un bloc.

**Headers:** `Authorization: Token <token>`

**Response 204:** No content

**Permissions:** Seul le setter ou un admin peut supprimer

---

#### `GET /api/climbs/{climbId}/permissions-to-modify`

Vérifie si l'utilisateur peut modifier le bloc.

**Response 200:**
```json
{
    "canEdit": true,
    "canDelete": true,
    "reason": "owner"
}
```

---

#### `PATCH /api/climbs/{climbId}/privacy-status`

Change la visibilité d'un bloc.

**Request:**
```json
{
    "isPrivate": true
}
```

---

### Interactions sociales

#### `GET /api/climbs/{climbId}/latest-sends`

**Query params:** `limit` (défaut: 10)

**Response 200:**
```json
{
    "results": [
        {
            "id": "effort-uuid",
            "climbId": "climb-uuid",
            "effortBy": {
                "id": "user-uuid",
                "fullName": "Alice Grimpeuse",
                "avatar": "/media/avatars/alice.jpg"
            },
            "effortDate": "2025-01-18T16:30:00Z",
            "isFlash": true,
            "attemptsNumber": 1,
            "gradeFeel": 0
        }
    ]
}
```

---

#### `GET /api/climbs/{climbId}/comments`

**Response 200:**
```json
{
    "results": [
        {
            "id": "comment-uuid",
            "climbId": "climb-uuid",
            "user": {
                "id": "user-uuid",
                "fullName": "Bob Grimpeur"
            },
            "text": "Super bloc, le mouvement de droite est costaud !",
            "date": "2025-01-17T14:00:00Z",
            "repliedToId": null
        }
    ]
}
```

---

#### `POST /api/climbs/{climbId}/comments`

**Request:**
```json
{
    "text": "Mon commentaire",
    "repliedToId": null
}
```

**Response 201:** Commentaire créé

---

#### `DELETE /api/climbs/{climbId}/comments/{commentId}`

**Response 204:** No content

---

#### `GET /api/climbs/{climbId}/likes`

**Response 200:**
```json
{
    "count": 5,
    "results": [
        {
            "user": {
                "id": "user-uuid",
                "fullName": "Charlie Fan"
            },
            "dateCreated": "2025-01-16T12:00:00Z"
        }
    ]
}
```

---

#### `POST /api/climbs/{climbId}/likes`

Ajoute un like.

**Response 201:** `{"liked": true}`

---

#### `DELETE /api/climbs/{climbId}/likes`

Retire un like.

**Response 200:** `{"liked": false}`

---

#### `PATCH /api/climbs/{climbId}/bookmarked`

**Request:**
```json
{
    "bookmarked": true
}
```

---

#### `GET /api/climbs/{climbId}/crowd-grades`

**Response 200:**
```json
{
    "crowdGrade": {
        "ircra": 18.5,
        "hueco": "V5",
        "font": "6b+",
        "dankyu": "3D"
    },
    "votesCount": 8,
    "userVote": {
        "gradeValue": "6b",
        "gradingSystem": "Font",
        "gradeFeel": 1
    }
}
```

---

## Gestion des images

### Structure des fichiers

```
/media/
├── walls/
│   ├── {face-id}.jpg           # Image haute résolution
│   └── {face-id}-small.jpg     # Thumbnail
├── avatars/
│   └── {user-id}.jpg
└── uploads/
    └── temp/
```

### Endpoint pour récupérer les images

Les images sont servies comme fichiers statiques :
```
GET /media/walls/face-uuid.jpg
```

### Import initial depuis Stokt

Pour copier les images depuis Stokt :

```bash
# Télécharger l'image d'une face
curl -o /media/walls/{face-id}.jpg \
  "https://www.sostokt.com/media/CACHE/images/walls/.../full.jpg"
```

---

## Modification requise côté mastoc

### Fichier : `mastoc/src/mastoc/api/client.py`

Modifier `StoktConfig` pour accepter une URL configurable :

```python
@dataclass
class StoktConfig:
    base_url: str = "http://localhost:8000"  # ou variable d'env
    timeout: int = 60
```

### Fichier : Configuration

Ajouter un fichier de config ou variable d'environnement :

```bash
export MASTOCK_API_URL="http://votre-serveur:8000"
```

---

## Recommandations techniques

### Framework backend

| Option | Avantages | Inconvénients |
|--------|-----------|---------------|
| **Django + DRF** | Compatibilité maximale, même format | Plus lourd |
| **FastAPI** | Moderne, rapide, docs auto | Moins de "batteries incluses" |
| **Node.js/Express** | Large écosystème | Stack différente |

### Base de données

- **PostgreSQL** : Recommandé pour multi-utilisateur, support UUID natif
- **SQLite** : Acceptable pour usage perso/petit groupe

### Déploiement

Options simples :
- **Docker Compose** : PostgreSQL + Backend + Nginx
- **VPS** (DigitalOcean, Hetzner) : ~5€/mois suffit
- **Raspberry Pi** : Possible pour usage local

---

## Étapes d'implémentation

1. **Setup projet backend**
   - Créer projet Django/FastAPI
   - Configurer PostgreSQL
   - Créer schéma BDD

2. **Authentification**
   - `POST /api/token-auth`
   - `GET /api/users/me`
   - Middleware validation token

3. **Endpoints lecture**
   - `/api/faces/{id}/setup`
   - `/api/gyms/{id}/climbs`
   - `/api/gyms/{id}/walls`

4. **Endpoints écriture**
   - CRUD climbs
   - Interactions (likes, comments, sends)

5. **Script import Stokt**
   - Login Stokt
   - Télécharger climbs + holds
   - Télécharger images
   - Insérer en BDD locale

6. **Configuration mastoc**
   - Variable d'environnement URL
   - Test connexion

---

## Fichiers clés à consulter (référence)

| Fichier | Contenu |
|---------|---------|
| `mastoc/src/mastoc/api/client.py` | Client API actuel (à adapter) |
| `mastoc/src/mastoc/api/models.py` | Modèles de données Python |
| `mastoc/src/mastoc/db/database.py` | Schéma SQLite existant |
| `docs/reverse_engineering/03_ENDPOINTS.md` | Documentation complète API Stokt |
