# ADR 005 - Batch Import pour Holds, Users et Climbs

**Date** : 2025-12-30
**Statut** : Accepté

## Contexte

L'import initial des données Stokt comprend :
- ~800 prises (holds) réparties sur plusieurs faces
- ~50 utilisateurs (setters)
- ~1000 blocs (climbs)

Avec les endpoints individuels, chaque entité nécessite :
- 1 requête HTTP
- 1+ lookups en base
- 1 commit SQL

Pour un import complet, cela représente ~2000 requêtes HTTP séquentielles (lent).

## Décision

Ajouter des endpoints **batch** pour les trois types d'entités :
- `/api/sync/import/holds/batch`
- `/api/sync/import/users/batch`
- `/api/sync/import/climbs/batch`

Chaque endpoint :
- Accepte une liste d'entités
- Pré-charge les dépendances en une requête
- Effectue tous les inserts en une seule transaction
- Retourne un résumé `{created, updated, errors, total}`

## Conséquences

### Positives
- Import 10-50x plus rapide
- Moins de requêtes réseau
- Une seule transaction SQL (atomicité)
- Évite les problèmes de timeout

### Négatives
- Moins de détails sur les erreurs individuelles
- Charge mémoire plus importante côté serveur

## Implémentation

### Schémas communs

```python
class BatchImportResult(BaseModel):
    """Résultat du batch import."""
    created: int
    updated: int
    errors: int
    total: int
```

### Endpoint Holds Batch

```python
class BatchImportHoldsRequest(BaseModel):
    holds: list[ImportHoldRequest]

@router.post("/import/holds/batch", response_model=BatchImportResult)
def import_holds_batch(data: BatchImportHoldsRequest, db: Session = Depends(get_db)):
    # Pré-charger les faces
    face_stokt_ids = {h.face_stokt_id for h in data.holds}
    faces = db.query(Face).filter(Face.stokt_id.in_(face_stokt_ids)).all()
    face_map = {f.stokt_id: f for f in faces}

    # Pré-charger les holds existants
    hold_stokt_ids = {h.stokt_id for h in data.holds}
    existing = db.query(Hold).filter(Hold.stokt_id.in_(hold_stokt_ids)).all()
    existing_map = {h.stokt_id: h for h in existing}

    for hold_data in data.holds:
        if hold_data.stokt_id in existing_map:
            updated += 1
            continue
        face = face_map.get(hold_data.face_stokt_id)
        if not face:
            errors += 1
            continue
        # ... créer hold
        created += 1

    db.commit()
```

### Endpoint Users Batch

```python
class BatchImportUsersRequest(BaseModel):
    users: list[ImportUserRequest]

@router.post("/import/users/batch", response_model=BatchImportResult)
def import_users_batch(data: BatchImportUsersRequest, db: Session = Depends(get_db)):
    # Pré-charger les users existants
    user_stokt_ids = {u.stokt_id for u in data.users}
    existing = db.query(User).filter(User.stokt_id.in_(user_stokt_ids)).all()
    existing_map = {u.stokt_id: u for u in existing}

    for user_data in data.users:
        if user_data.stokt_id in existing_map:
            updated += 1
            continue
        # ... créer user
        created += 1

    db.commit()
```

### Endpoint Climbs Batch

```python
class BatchImportClimbsRequest(BaseModel):
    climbs: list[ImportClimbRequest]

@router.post("/import/climbs/batch", response_model=BatchImportResult)
def import_climbs_batch(data: BatchImportClimbsRequest, db: Session = Depends(get_db)):
    # Pré-charger faces, users, climbs existants
    face_map = ...
    user_map = ...
    existing_map = ...

    for climb_data in data.climbs:
        # ... traitement
        pass

    db.commit()
```

### Script d'import modifié

```bash
# Import avec batch (par défaut)
python scripts/init_from_stokt.py \
  --username USER \
  --password PASS \
  --api-key "votre-clé"

# Import sans batch (lent)
python scripts/init_from_stokt.py \
  --username USER \
  --password PASS \
  --api-key "votre-clé" \
  --no-batch

# Batch size personnalisé
python scripts/init_from_stokt.py \
  --username USER \
  --password PASS \
  --api-key "votre-clé" \
  --batch-size 100
```

### Fonctions du script

```python
def import_holds_batch(client, holds, face_stokt_id):
    """Importe les holds d'une face en batch."""
    batch_data = [prepare_hold_data(h, face_stokt_id) for h in holds]
    response = client.post(
        f"{URL}/api/sync/import/holds/batch",
        json={"holds": batch_data}
    )
    result = response.json()
    return result["created"], result["updated"], result["errors"]

def import_climbs_batch(client, climbs, batch_size=50):
    """Import les climbs par batch."""
    # D'abord importer les setters uniques
    setters = {c.setter for c in climbs if c.setter}
    import_users_batch(client, setters)

    # Puis les climbs par lots
    for i in range(0, len(climbs), batch_size):
        batch = climbs[i:i + batch_size]
        response = client.post(
            f"{URL}/api/sync/import/climbs/batch",
            json={"climbs": [prepare_climb_data(c) for c in batch]}
        )
        # ...
```

## Performance

| Mode | ~800 holds | ~1000 climbs | Total |
|------|------------|--------------|-------|
| Sans batch | ~2-3 min | ~5-8 min | ~10 min |
| Avec batch | ~5 sec | ~20 sec | ~30 sec |

## Fichiers concernés

- `server/src/mastoc_api/routers/sync.py` - Endpoints batch
- `server/scripts/init_from_stokt.py` - Script d'import
- `server/tests/test_sync.py` - Tests batch
