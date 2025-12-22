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

**Option C : Hybride (cache intelligent)**
- Données récupérées via API puis cachées localement
- TTL (Time To Live) configurable
- Refresh manuel ou automatique en arrière-plan
- Fallback sur cache si offline

### 2. Endpoints API à investiguer

Depuis l'analyse du code décompilé, endpoints probables :
- `GET /api/climbs/{climbId}/ascents` - Liste des ascensions
- `GET /api/climbs/{climbId}/comments` - Commentaires
- `POST /api/climbs/{climbId}/bookmark` - Ajouter aux favoris
- `DELETE /api/climbs/{climbId}/bookmark` - Retirer des favoris
- `GET /api/users/me/bookmarks` - Mes favoris

### 3. Modèle de données

```python
# Ascension (qui a passé le bloc)
class Ascent:
    id: str
    climb_id: str
    user_id: str
    user_name: str
    user_avatar: str | None
    date: datetime
    is_flash: bool  # Réussi du premier coup
    attempts: int   # Nombre d'essais
    grade_feel: int # -1 (soft), 0 (ok), +1 (hard)

# Commentaire
class Comment:
    id: str
    climb_id: str
    user_id: str
    user_name: str
    user_avatar: str | None
    text: str
    date: datetime

# Favori (bookmark)
class Bookmark:
    climb_id: str
    date_added: datetime
```

### 4. UX à définir

- Où afficher ces infos ? (widget dédié, onglet, popup)
- Chargement lazy vs eager
- Indicateur de chargement
- Gestion des erreurs réseau
- Mode offline (afficher cache ou message)

## Tâches

- [ ] Investiguer les endpoints API réels (tests avec token)
- [ ] Définir le modèle de données SQLite
- [ ] Implémenter le cache intelligent (TTL)
- [ ] Créer les widgets d'affichage
- [ ] Gérer l'authentification pour les actions (favoris)
- [ ] Tests unitaires et d'intégration

## Références

- `/docs/reverse_engineering/02_ENDPOINTS.md` - Liste des endpoints connus
- `/docs/reverse_engineering/04_STRUCTURES.md` - Structures de données
- `/mastock/src/mastock/api/client.py` - Client API existant
