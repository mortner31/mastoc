# TODO 09 - Listes Personnalisées (Collections)

## Objectif

Permettre de gérer des collections de climbs personnalisées :
- Créer/modifier/supprimer des listes
- Ajouter/retirer des climbs d'une liste
- Suivre des listes d'autres utilisateurs
- Consulter les listes par gym/style

## Endpoints API (confirmés par analyse code décompilé)

### Données utilisateur "my-*"

| Endpoint | Méthode | Description | Ligne code |
|----------|---------|-------------|------------|
| `api/gyms/{gymId}/my-sent-climbs` | GET | Mes ascensions validées | 442409 |
| `api/gyms/{gymId}/my-liked-climbs` | GET | Mes climbs likés | 442480 |
| `api/gyms/{gymId}/my-bookmarked-climbs` | GET | Mes climbs favoris | 442551 |
| `api/gyms/{gymId}/my-set-climbs` | GET | Mes climbs créés (ouvreur) | 442622 |

### Récupération de listes

| Endpoint | Méthode | Paramètres | Description | Ligne |
|----------|---------|------------|-------------|-------|
| `api/users/lists/{userId}/personal` | GET | `ordering` | Listes personnelles utilisateur | 458793 |
| `api/lists` | GET | `filter_for`, `owner_id`, `gym_id`, `climbs_count_gte` | Listes avec filtres | 458870 |
| `api/lists/{listId}` | GET | - | Détail d'une liste | 459215 |
| `api/lists/{listId}/items` | GET | `page_size`, `exclude_mine`, `grade_from`, `grade_to`, `ordering`, `tags`, `search`, `show_circuit_only` | Items d'une liste | 459520 |
| `api/lists/{listId}/suggestions` | GET | `face_id`, `page_size` | Suggestions de climbs | 459288 |
| `api/users/lists/{userId}/expo-share-list-url` | GET | - | URL de partage | 459649 |

**Valeurs `filter_for`** :
- `user` : listes d'un utilisateur (requiert `owner_id`)
- `gym` : listes d'un gym (requiert `gym_id`)
- `style` : listes par style (requiert `gym_id`, `climbs_count_gte=1`)
- `from_others` : listes d'autres utilisateurs

### Création de listes

| Endpoint | Méthode | Body | Description | Ligne |
|----------|---------|------|-------------|-------|
| `api/users/{userId}/lists` | POST | `{data}` | Créer liste utilisateur | 459722 |
| `api/gyms/{gymId}/lists` | POST | `{data}` | Créer liste gym | 444160 |

### Modification de listes

| Endpoint | Méthode | Body | Description | Ligne |
|----------|---------|------|-------------|-------|
| `api/lists/{listId}` | PATCH | `{data}` | Modifier liste | 459795 |
| `api/gyms/{gymId}/lists/{listId}` | PATCH | `{data}` | Modifier liste gym | 459870 |
| `api/lists/{listId}/image` | PATCH | `multipart/form-data` | Modifier image liste | 459943 |

### Suppression de listes

| Endpoint | Méthode | Description | Ligne |
|----------|---------|-------------|-------|
| `api/lists/{listId}` | DELETE | Supprimer liste | 460015 |
| `api/gyms/{gymId}/lists/{listId}` | DELETE | Supprimer liste gym | 460088 |

### Gestion des items (climbs dans une liste)

| Endpoint | Méthode | Body | Description | Ligne |
|----------|---------|------|-------------|-------|
| `api/lists/{listId}/items` | POST | `{data}` | Ajouter climb à liste | 459367 |
| `api/lists/{listId}/items/{itemId}` | DELETE | - | Retirer climb de liste | 460165 |
| `api/gyms/{gymId}/lists/control` | POST | `{data}` | Réordonner items | 459439 |

### Suivi de listes

| Endpoint | Méthode | Description | Ligne |
|----------|---------|-------------|-------|
| `api/lists/{listId}/follow` | POST | Suivre une liste | 459071 |
| `api/lists/{listId}/follow` | DELETE | Ne plus suivre | 459142 |

### Listes Gym (populaires/styles)

| Endpoint | Méthode | Paramètres | Description | Ligne |
|----------|---------|------------|-------------|-------|
| `api/gyms/{gymId}/lists` | GET | `page_size` | Listes populaires | 443947 |
| `api/gyms/{gymId}/style-lists` | GET | - | Listes par style | 444017 |
| `api/gyms/{gymId}/lists` | GET | `kind` | Listes par type | 444090 |

### Divers

| Endpoint | Méthode | Description | Ligne |
|----------|---------|-------------|-------|
| `api/climb-lists/{id}/shuffle` | GET | Thumbnail liste | 460238 |

## Modèles de données (à confirmer)

```python
@dataclass
class ClimbList:
    id: str
    name: str
    description: str | None
    owner_id: str
    owner_name: str
    gym_id: str | None
    image: str | None
    climbs_count: int
    followers_count: int
    is_following: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class ListItem:
    id: str
    list_id: str
    climb_id: str
    climb: Climb  # Objet climb complet
    order: int
    added_at: datetime
```

## Tâches

### Phase 1 : Lecture seule
- [ ] Tester `api/gyms/{gymId}/my-sent-climbs`
- [ ] Tester `api/gyms/{gymId}/my-set-climbs`
- [ ] Tester `api/lists?filter_for=user&owner_id={userId}`
- [ ] Tester `api/lists/{listId}`
- [ ] Tester `api/lists/{listId}/items`
- [ ] Afficher "Mes listes" dans l'UI

### Phase 2 : Gestion de listes
- [ ] Créer une liste (`POST api/users/{userId}/lists`)
- [ ] Modifier une liste (`PATCH api/lists/{listId}`)
- [ ] Supprimer une liste (`DELETE api/lists/{listId}`)
- [ ] UI création/édition de liste

### Phase 3 : Gestion des items
- [ ] Ajouter climb à liste (`POST api/lists/{listId}/items`)
- [ ] Retirer climb de liste (`DELETE api/lists/{listId}/items/{itemId}`)
- [ ] Réordonner items
- [ ] UI drag & drop pour réordonner

### Phase 4 : Social
- [ ] Suivre une liste (`POST api/lists/{listId}/follow`)
- [ ] Ne plus suivre (`DELETE api/lists/{listId}/follow`)
- [ ] Listes populaires du gym
- [ ] Partage de liste

## Références

- `/docs/reverse_engineering/03_ENDPOINTS.md` - Liste des endpoints
- Code décompilé : lignes 443947-460239 (fonctions lists)
- TODO 07 pour les endpoints sociaux de base (likes, bookmarks)
