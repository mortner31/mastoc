# TODO 07 - Interactions avec les Blocs (Ascensions, Commentaires, Favoris)

## Objectif

Permettre de consulter et gérer les interactions sociales d'un bloc :
- Qui a passé le bloc (liste des ascensions)
- Commentaires sur le bloc
- Ajouter/retirer des favoris

## Questions à résoudre

### 1. Source des données

**Option A : API officielle Stokt**
- Avantages :
  - Données à jour en temps réel
  - Pas de duplication de stockage
  - Possibilité d'écrire (favoris, commentaires)
- Inconvénients :
  - Dépendance réseau
  - Risque de latence/timeout
  - Risque de changement d'API
  - Authentification requise

**Option B : Stockage local mastock**
- Avantages :
  - Fonctionne offline
  - Rapide
  - Données persistantes
- Inconvénients :
  - Données potentiellement obsolètes
  - Pas de synchronisation avec l'app officielle
  - Duplication de données

**Option C : Hybride (cache intelligent)** ✅ RECOMMANDÉ
- Données récupérées via API puis cachées localement
- TTL (Time To Live) configurable
- Refresh manuel ou automatique en arrière-plan
- Fallback sur cache si offline

### Contrainte architecturale : Chargement asynchrone obligatoire

**IMPORTANT** : Les données sociales (likes, comments, sends) sont secondaires par rapport à la navigation des blocs. Elles doivent **toujours** être chargées de manière asynchrone pour ne jamais bloquer le parcours.

**Principe** :
```
┌─────────────────────────────────────────────────┐
│  Climb sélectionné                              │
│  ↓                                              │
│  Affichage immédiat : nom, grade, prises       │
│  (données locales SQLite)                       │
│  ↓                                              │
│  Chargement async en arrière-plan :            │
│  - Compteurs (climbedBy, totalLikes, etc.)     │
│  - Liste des sends (si demandée)               │
│  - Commentaires (si demandés)                  │
│  ↓                                              │
│  UI mise à jour quand données disponibles      │
└─────────────────────────────────────────────────┘
```

**Implications** :
- Les widgets sociaux affichent un état "chargement" ou vide initialement
- L'utilisateur peut naviguer sans attendre les données sociales
- Les requêtes réseau sont annulées si l'utilisateur change de climb
- Cache local pour éviter les requêtes répétées

### 2. Endpoints API (confirmés par analyse code décompilé)

#### Likes
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/climbs/{climbId}/likes` | GET | Liste des likes |
| `api/climbs/{climbId}/likes` | POST | Ajouter un like |
| `api/climbs/{climbId}/likes` | DELETE | Retirer un like |
| `api/gyms/{gymId}/my-liked-climbs` | GET | Mes climbs likés |

#### Commentaires
| Endpoint | Méthode | Body | Description |
|----------|---------|------|-------------|
| `api/climbs/{climbId}/comments?limit={n}` | GET | - | Liste des commentaires |
| `api/climbs/{climbId}/comments` | POST | `{text, replied_to_id}` | Poster un commentaire |
| `api/climbs/{climbId}/comments/{commentId}` | DELETE | - | Supprimer un commentaire |

#### Bookmarks (Favoris)
| Endpoint | Méthode | Body | Description |
|----------|---------|------|-------------|
| `api/climbs/{climbId}/bookmarked` | PATCH | `{added: bool, removed: bool}` | Toggle favori |
| `api/gyms/{gymId}/my-bookmarked-climbs` | GET | - | Mes climbs favoris |

#### Efforts (Ascensions)
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/efforts` | POST | Enregistrer une ascension |
| `api/efforts/{effortId}` | PATCH | Modifier une ascension |
| `api/efforts/{effortId}` | DELETE | Supprimer une ascension |
| `api/climbs/{climbId}/latest-sends` | GET | Dernières ascensions du climb |

#### Notes (Crowd Grade)
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/ratings` | POST | Soumettre une note de difficulté |
| `api/climbs/{climbId}/crowd-grades` | GET | Notes de la communauté |

### 3. Données déjà disponibles dans Climb

L'objet Climb retourné par l'API contient déjà des compteurs :
```json
{
  "climbedBy": 0,        // Nombre de grimpeurs ayant validé
  "totalLikes": 0,       // Nombre de likes
  "totalComments": 1,    // Nombre de commentaires
  "likedByUser": false,  // L'utilisateur a-t-il liké ?
  "bookmarkedByUser": false  // L'utilisateur a-t-il ajouté aux favoris ?
}
```

### 4. Modèles de données pour détails

```python
# Effort (ascension)
@dataclass
class Effort:
    id: str
    climb_id: str
    user_id: str
    user_name: str
    user_avatar: str | None
    date: datetime
    is_flash: bool        # Réussi du premier coup
    attempts: int | None  # Nombre d'essais
    grade_feel: int       # -1 (soft), 0 (ok), +1 (hard)

# Commentaire
@dataclass
class Comment:
    id: str
    climb_id: str
    user_id: str
    user_name: str
    user_avatar: str | None
    text: str
    date: datetime
    replied_to_id: str | None  # Réponse à un autre commentaire

# Like
@dataclass
class Like:
    user_id: str
    user_name: str
    user_avatar: str | None
```

### 5. UX à définir

- Où afficher ces infos ? (widget dédié, onglet, popup)
- Chargement lazy vs eager
- Indicateur de chargement
- Gestion des erreurs réseau
- Mode offline (afficher cache ou message)

## Tâches

### Phase 1 : Lecture seule (priorité)
- [ ] Afficher `climbedBy`, `totalLikes`, `totalComments` dans la vue détail
- [ ] Tester endpoint `api/climbs/{id}/latest-sends` (liste ascensions)
- [ ] Tester endpoint `api/climbs/{id}/comments?limit=20`
- [ ] Afficher la liste des ascensions récentes
- [ ] Afficher les commentaires

### Phase 2 : Actions utilisateur
- [ ] Implémenter like/unlike (`POST/DELETE api/climbs/{id}/likes`)
- [ ] Implémenter bookmark toggle (`PATCH api/climbs/{id}/bookmarked`)
- [ ] Poster un commentaire (`POST api/climbs/{id}/comments`)

### Phase 3 : Mes données
- [ ] Endpoint `api/gyms/{gymId}/my-bookmarked-climbs` - mes favoris
- [ ] Endpoint `api/gyms/{gymId}/my-liked-climbs` - mes likes
- [ ] Vue "Mes favoris" dans l'interface

## Références

- `/docs/reverse_engineering/03_ENDPOINTS.md` - Liste des endpoints connus
- `/docs/reverse_engineering/04_STRUCTURES.md` - Structures de données
- Code décompilé : lignes 466084-467380 (fonctions fetch/post)
