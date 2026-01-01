# ADR 008 - Hold Annotations (Annotations Crowd-Sourcées)

**Date** : 2026-01-01
**Statut** : Accepté

## Contexte

Les grimpeurs souhaitent pouvoir filtrer les blocs en fonction des caractéristiques des prises (type de préhension, état de maintenance, difficulté relative). Ces informations ne sont pas disponibles dans les données Stokt et doivent être collectées de manière collaborative.

### Besoins identifiés

1. **Filtrage par type** : "Montre-moi les blocs avec des réglettes"
2. **Éviter prises sales** : "Cache les blocs avec prises à brosser"
3. **Maintenance collaborative** : Signaler les prises usées/tournées
4. **Identification prises-clés** : Marquer les prises difficiles

## Décision

Implémenter un système d'annotations crowd-sourcées avec consensus communautaire.

### Architecture

```
Utilisateur 1 ──┐
Utilisateur 2 ──┼── Annotations individuelles ──► Calcul Consensus ──► Vue partagée
Utilisateur 3 ──┘                                     (mode statistique)
```

### Modèle de données

Une annotation par utilisateur par prise, avec 3 dimensions :

| Dimension | Valeurs | Description |
|-----------|---------|-------------|
| **grip_type** | plat, reglette, bi_doigt, tri_doigt, mono_doigt, pince, colonnette, inverse, bac, prise_volume, micro, autre | Type de préhension |
| **condition** | ok, a_brosser, sale, tournee, usee, cassee | État de maintenance |
| **difficulty** | facile, normale, dure | Difficulté relative au bloc |

### Calcul du consensus

Le consensus est la **valeur modale** (la plus fréquente) avec un indice de confiance :

```
confidence = votes_majoritaires / total_votes
```

Seuils de validation :
- `grip_type` : 3 votes min, 50% accord (subjectif, tolérant)
- `condition` : 2 votes min, 60% accord (sécurité, plus strict)
- `difficulty` : 3 votes min, 50% accord (très subjectif)

### Stockage

Enums stockés comme **String** (pas PostgreSQL ENUM) pour compatibilité SQLite des tests.

## Conséquences

### Positives

- Données enrichies par la communauté
- Filtrage avancé des blocs
- Signalement maintenance collaborative
- Coût nul (pas d'import de données)

### Négatives

- Bootstrap froid (pas de données au départ)
- Votes potentiellement divergents
- Charge serveur pour calcul consensus

### Mitigations

- Afficher "Pas assez de votes" si < seuil
- Cache TTL 10 min pour consensus côté client
- Calculer consensus en SQL (pas en Python)

## Implémentation

### Backend (Railway)

**Fichiers** :
- `server/src/mastoc_api/models/hold_annotation.py`
- `server/src/mastoc_api/routers/hold_annotations.py`

**Endpoints** :

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/api/holds/{id}/annotations` | GET | API Key | Consensus + mon annotation |
| `/api/holds/{id}/annotations` | PUT | JWT | Créer/modifier |
| `/api/holds/{id}/annotations` | DELETE | JWT | Supprimer |
| `/api/holds/annotations/batch` | POST | API Key | Batch fetch |

### Client (mastoc)

**Fichiers** :
- `mastoc/src/mastoc/core/annotation_loader.py` (pattern SocialLoader)
- `mastoc/src/mastoc/gui/widgets/annotation_panel.py`
- Extensions : `models.py`, `railway_client.py`, `hold_overlay.py`

**ColorModes** : GRIP_TYPE, CONDITION, DIFFICULTY

### Schéma DB

```sql
CREATE TABLE hold_annotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hold_id INTEGER NOT NULL REFERENCES holds(id),
    user_id UUID NOT NULL REFERENCES users(id),
    grip_type VARCHAR(50),
    condition VARCHAR(50),
    difficulty VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    UNIQUE(hold_id, user_id)
);

CREATE INDEX idx_annotations_hold ON hold_annotations(hold_id);
CREATE INDEX idx_annotations_user ON hold_annotations(user_id);
```

## Références

- TODO 12 : `/docs/TODOS/12_hold_annotations.md`
- Pattern loader : `mastoc/src/mastoc/core/social_loader.py`
- ColorModes : `mastoc/src/mastoc/gui/widgets/hold_overlay.py`
