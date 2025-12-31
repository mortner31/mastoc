# TODO 18 - Synchronisation Données Sociales

## Objectif

Synchroniser les données sociales (réalisations, commentaires, likes) depuis Stokt vers mastoc pour les climbs déjà synchronisés.

## Contexte

**Limitation de la sync incrémentale (TODO 15) :**

La sync incrémentale filtre par `created_at` (date de création du climb). Elle ne détecte **pas** les changements sociaux car ils ne modifient pas cette date :

| Événement | Impact sur `created_at` | Détecté par sync incrémentale ? |
|-----------|------------------------|--------------------------------|
| Nouveau climb créé | Nouvelle valeur | ✅ Oui |
| Quelqu'un réalise le climb | Inchangé | ❌ Non |
| Quelqu'un commente | Inchangé | ❌ Non |
| Quelqu'un like | Inchangé | ❌ Non |

**Besoin :**
- Voir qui a réalisé un bloc (sends/efforts)
- Voir les commentaires récents
- Avoir les compteurs à jour (likes, climbed_by)

## Stratégie

### Approche Légère (recommandée)

Stocker uniquement les **compteurs agrégés** dans les champs existants de `climbs` :
- `climbed_by` : nombre de personnes ayant réalisé
- `total_likes` : nombre de likes
- `total_comments` : nombre de commentaires

**Avantages** : Pas de nouvelles tables, pas de migration, rapide.

### Approche Complète (future)

Créer des tables dédiées pour stocker le détail :
- `sends` : user_id, climb_id, date, attempts, rating
- `comments` : user_id, climb_id, text, date

**À évaluer** : Utile seulement si on veut afficher "qui a fait quoi".

## Tâches

### Phase 1 : Refresh Compteurs (Approche Légère)

- [ ] Identifier les endpoints Stokt pertinents
  - [ ] `GET /api/climbs/{id}` retourne-t-il `climbed_by`, `total_likes` ?
  - [ ] Ou faut-il appeler `/latest-sends`, `/comments` séparément ?
- [ ] Implémenter `StoktAPI.get_climb_social_stats(stokt_id)`
- [ ] Implémenter `refresh_social_counts(climb_id)` dans sync
  - [ ] Récupérer stats depuis Stokt
  - [ ] Mettre à jour les champs locaux
- [ ] Mode batch : `refresh_all_social_counts()`
  - [ ] Throttling (ex: 1 req/sec)
  - [ ] Progress callback

### Phase 2 : Intégration UI

- [ ] Bouton "Rafraîchir" sur ClimbDetailPanel
- [ ] Menu "Outils > Rafraîchir stats sociales (tous)"
- [ ] Indicateur visuel quand stats sont "stale" (> 7 jours)

### Phase 3 : Approche Complète (optionnel, si besoin confirmé)

- [ ] Tables `sends` et `comments` sur Railway
- [ ] Endpoints CRUD correspondants
- [ ] Affichage liste des réalisations
- [ ] Affichage liste des commentaires

## Endpoints Stokt à Investiguer

```
GET /api/climbs/{id}                    # Stats dans la réponse ?
GET /api/climbs/{id}/latest-sends       # Liste des réalisations
GET /api/climbs/{id}/comments           # Liste des commentaires
GET /api/climbs/{id}/likes              # Liste des likes (ou juste compteur ?)
```

## Prérequis

- TODO 15 (Sync Incrémentale) : ✅ Pour avoir `stokt_id` sur les climbs
- TODO 16 (Dashboard) : Pour avoir visibilité sur l'état

## Risques

| Risque | Mitigation |
|--------|------------|
| Rate limiting Stokt | Throttling agressif (1 req/sec) |
| Endpoints non documentés | Tester sur quelques climbs d'abord |
| Volume de données | Commencer par compteurs, pas le détail |

## Références

- TODO 07 : Interactions avec les Blocs (endpoints sociaux documentés)
- `/mastoc/src/mastoc/api/client.py` : Client Stokt existant
