# ADR 001 - Architecture Railway-First avec Mapping d'IDs

**Date** : 2025-12-30
**Statut** : Accepté

## Contexte

Le projet mastoc a besoin d'accéder aux données Stokt (blocs, prises, faces) tout en :
- Permettant la création de blocs locaux indépendants de Stokt
- Gardant la possibilité de synchroniser avec Stokt si désiré
- Évitant une dépendance totale à l'API Stokt (rate limiting, disponibilité)

Deux approches ont été considérées :
1. **Fork** : Copier les données avec nouveaux UUIDs, perdre la traçabilité
2. **Railway-First** : Utiliser nos propres IDs avec mapping optionnel vers Stokt

## Décision

Adopter l'architecture **Railway-First avec Mapping d'IDs** :

- Chaque entité a son propre `id` (UUID généré par mastoc)
- Un champ `stokt_id` nullable stocke l'ID Stokt original si applicable
- Une table `id_mappings` centralise les correspondances pour référence

## Conséquences

### Positives
- Indépendance totale : mastoc fonctionne sans Stokt
- Traçabilité : on sait quelles données viennent de Stokt
- Flexibilité : création de blocs purement locaux possible
- Migration facile : si Stokt change ses IDs, seul le mapping est affecté

### Négatives
- Complexité accrue : gestion de deux types d'IDs
- Synchronisation bidirectionnelle plus complexe (si implémentée)

## Implémentation

### Modèle de base (SQLAlchemy)

```python
class Gym(Base):
    __tablename__ = "gyms"

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    stokt_id: Mapped[UUID | None] = mapped_column(
        Uuid, unique=True, nullable=True, index=True
    )
    # ... autres champs
```

### Table de mapping

```python
class IDMapping(Base):
    __tablename__ = "id_mappings"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str]  # "gym", "face", "hold", "climb", "user"
    local_id: Mapped[UUID]
    stokt_id: Mapped[UUID]
```

### Import depuis Stokt

```python
@router.post("/sync/import/gym")
def import_gym(data: ImportGymRequest, db: Session):
    # Vérifier si existe déjà via stokt_id
    existing = db.query(Gym).filter(Gym.stokt_id == data.stokt_id).first()
    if existing:
        return {"status": "exists", "id": str(existing.id)}

    # Créer avec nouveau UUID + stokt_id
    gym = Gym(
        id=uuid.uuid4(),
        stokt_id=data.stokt_id,
        display_name=data.display_name
    )
    db.add(gym)
    db.commit()
    return {"status": "created", "id": str(gym.id)}
```

### Création locale (sans Stokt)

```python
@router.post("/climbs")
def create_climb(data: CreateClimbRequest, db: Session):
    # Pas de stokt_id = bloc local
    climb = Climb(
        id=uuid.uuid4(),
        stokt_id=None,  # Local uniquement
        name=data.name,
        # ...
    )
```

## Fichiers concernés

- `server/src/mastoc_api/models/*.py` - Tous les modèles avec `stokt_id`
- `server/src/mastoc_api/models/mapping.py` - Table IDMapping
- `server/src/mastoc_api/routers/sync.py` - Endpoints d'import
- `server/scripts/init_from_stokt.py` - Script d'import initial
