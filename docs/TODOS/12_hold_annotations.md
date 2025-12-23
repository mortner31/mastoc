# TODO 12 - Hold Annotations (Annotations de prises)

## Objectif

Permettre aux utilisateurs d'annoter les prises avec des informations de **type**, **état de maintenance** et **difficulté relative**, partagées entre tous les grimpeurs (crowd-sourcing).

### Cas d'usage

1. **Filtre par type** : "Montre-moi les blocs avec des réglettes"
2. **Éviter prises sales** : "Cache les blocs avec prises à brosser"
3. **Maintenance collaborative** : Signaler les prises usées/tournées
4. **Identifier prises-clés** : Marquer les prises difficiles

---

## Prérequis

- [ ] **Serveur Railway déployé** avec PostgreSQL (voir `/docs/04_strategie_independance.md`)
- [ ] Authentification utilisateur fonctionnelle sur le serveur custom

---

## Tâches Backend

### Base de données PostgreSQL

```sql
-- Types énumérés
CREATE TYPE hold_grip_type AS ENUM (
    'plat', 'reglette', 'bi_doigt', 'tri_doigt', 'mono_doigt',
    'pince', 'colonnette', 'inverse', 'bac', 'prise_volume', 'micro', 'autre'
);

CREATE TYPE hold_condition AS ENUM (
    'ok', 'a_brosser', 'sale', 'tournee', 'usee', 'cassee'
);

CREATE TYPE hold_relative_difficulty AS ENUM (
    'facile', 'normale', 'dure'
);

-- Table principale
CREATE TABLE hold_annotations (
    id SERIAL PRIMARY KEY,
    hold_id INTEGER NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    grip_type hold_grip_type,
    condition hold_condition,
    relative_difficulty hold_relative_difficulty,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(hold_id, user_id)
);

-- Vue matérialisée pour le consensus
CREATE MATERIALIZED VIEW hold_consensus AS
SELECT
    hold_id,
    mode() WITHIN GROUP (ORDER BY grip_type) AS consensus_grip_type,
    COUNT(grip_type) AS grip_type_votes,
    mode() WITHIN GROUP (ORDER BY condition) AS consensus_condition,
    COUNT(condition) AS condition_votes,
    mode() WITHIN GROUP (ORDER BY relative_difficulty) AS consensus_difficulty,
    COUNT(relative_difficulty) AS difficulty_votes,
    COUNT(DISTINCT user_id) AS total_annotators,
    MAX(updated_at) AS last_updated
FROM hold_annotations
GROUP BY hold_id;

-- Trigger pour rafraîchir automatiquement
CREATE OR REPLACE FUNCTION refresh_hold_consensus()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY hold_consensus;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_refresh_consensus
AFTER INSERT OR UPDATE OR DELETE ON hold_annotations
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_hold_consensus();
```

### Endpoints API REST

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/holds/{holdId}/annotations` | GET | Récupère consensus + annotation utilisateur |
| `/api/holds/{holdId}/annotations` | PUT | Crée/modifie son annotation |
| `/api/holds/{holdId}/annotations` | DELETE | Supprime son annotation |
| `/api/holds/annotations/batch` | POST | Récupère annotations pour plusieurs prises |
| `/api/gyms/{gymId}/holds/stats` | GET | Statistiques d'annotations de la salle |

#### Format de réponse GET `/api/holds/{holdId}/annotations`

```json
{
    "hold_id": 12345,
    "consensus": {
        "grip_type": "reglette",
        "grip_type_confidence": 0.8,
        "grip_type_votes": 4,
        "condition": "a_brosser",
        "condition_confidence": 0.66,
        "condition_votes": 3,
        "difficulty": null,
        "difficulty_votes": 0,
        "total_annotators": 5
    },
    "user_annotation": {
        "grip_type": "reglette",
        "condition": "ok",
        "difficulty": "dure",
        "notes": "Bien cacher les doigts",
        "created_at": "2025-01-15T14:30:00Z"
    }
}
```

#### Format requête PUT `/api/holds/{holdId}/annotations`

```json
{
    "grip_type": "reglette",
    "condition": "a_brosser",
    "difficulty": "dure",
    "notes": "Très polished"
}
```

---

## Tâches Client (mastock)

### 1. Modèles Python

**Fichier** : `mastock/src/mastock/api/models.py`

```python
class HoldGripType(Enum):
    PLAT = "plat"
    REGLETTE = "reglette"
    BI_DOIGT = "bi_doigt"
    TRI_DOIGT = "tri_doigt"
    MONO_DOIGT = "mono_doigt"
    PINCE = "pince"
    COLONNETTE = "colonnette"
    INVERSE = "inverse"
    BAC = "bac"
    PRISE_VOLUME = "prise_volume"
    MICRO = "micro"
    AUTRE = "autre"

class HoldCondition(Enum):
    OK = "ok"
    A_BROSSER = "a_brosser"
    SALE = "sale"
    TOURNEE = "tournee"
    USEE = "usee"
    CASSEE = "cassee"

class HoldRelativeDifficulty(Enum):
    FACILE = "facile"
    NORMALE = "normale"
    DURE = "dure"

@dataclass
class HoldAnnotation:
    hold_id: int
    user_id: str
    grip_type: Optional[HoldGripType] = None
    condition: Optional[HoldCondition] = None
    difficulty: Optional[HoldRelativeDifficulty] = None
    notes: str = ""

@dataclass
class HoldConsensus:
    hold_id: int
    grip_type: Optional[HoldGripType] = None
    grip_type_confidence: float = 0.0
    condition: Optional[HoldCondition] = None
    condition_confidence: float = 0.0
    difficulty: Optional[HoldRelativeDifficulty] = None
    total_annotators: int = 0
```

### 2. Extension API Client

**Fichier** : `mastock/src/mastock/api/client.py`

- `get_hold_annotations(hold_id)` → `(HoldConsensus, Optional[HoldAnnotation])`
- `get_holds_annotations_batch(hold_ids)` → `dict[int, (HoldConsensus, Optional[HoldAnnotation])]`
- `set_hold_annotation(hold_id, grip_type, condition, difficulty, notes)` → `HoldAnnotation`
- `delete_hold_annotation(hold_id)` → `bool`

### 3. Loader Asynchrone

**Nouveau fichier** : `mastock/src/mastock/core/annotation_loader.py`

Pattern identique à `social_loader.py` :
- Thread worker en arrière-plan
- Cache avec TTL (10 min)
- Callbacks `on_data_loaded`, `on_error`
- Méthode `invalidate(hold_id)` pour rafraîchir après modification

### 4. Modes de Coloration

**Fichier** : `mastock/src/mastock/gui/widgets/hold_overlay.py`

Nouveaux `ColorMode` :

| Mode | Description | Mapping |
|------|-------------|---------|
| `GRIP_TYPE` | Couleur par type de prise | Bac (vert) → Mono (rouge) |
| `CONDITION` | Couleur par état | OK (vert) → Cassée (rouge) |
| `DIFFICULTY` | Couleur par difficulté | Facile (vert) → Dure (rouge) |

### 5. Panel d'Annotation

**Nouveau fichier** : `mastock/src/mastock/gui/widgets/annotation_panel.py`

Widget avec :
- Section "Consensus communautaire" (lecture seule, votes affichés)
- Section "Mon annotation" (3 combobox + textarea notes)
- Boutons "Enregistrer" / "Effacer"
- Signal `annotation_changed(hold_id, annotation)`

**Interaction** : Double-clic sur une prise → ouvre le panel

### 6. Filtrage par Tags

**Fichier** : `mastock/src/mastock/core/hold_index.py`

Étendre `get_filtered_climbs()` avec :

```python
include_grip_types: set[HoldGripType]   # Blocs avec AU MOINS une prise de ce type
exclude_conditions: set[HoldCondition]  # Exclure blocs avec prises dans cet état
```

### 7. Intégration UI

**Fichier** : `mastock/src/mastock/gui/hold_selector.py`

- Ajouter les 3 nouveaux ColorModes au combo
- Intégrer `AnnotationPanel` dans le panneau gauche
- Panneau de filtres par tags (checkboxes types + conditions)
- Connecter `hold_overlay.annotation_requested` au panel

---

## Fichiers à créer

| Fichier | Description |
|---------|-------------|
| `mastock/src/mastock/core/annotation_loader.py` | Loader async (~150 lignes) |
| `mastock/src/mastock/gui/widgets/annotation_panel.py` | Panel UI (~200 lignes) |

## Fichiers à modifier

| Fichier | Modifications |
|---------|---------------|
| `mastock/src/mastock/api/models.py` | +3 enums, +2 dataclasses |
| `mastock/src/mastock/api/client.py` | +4 méthodes API |
| `mastock/src/mastock/gui/widgets/hold_overlay.py` | +3 ColorModes, cache |
| `mastock/src/mastock/core/hold_index.py` | +filtres par tags |
| `mastock/src/mastock/gui/hold_selector.py` | Intégration complète |

---

## Système de Consensus

### Règles

| Type de tag | Votes minimum | Ratio accord | Justification |
|-------------|---------------|--------------|---------------|
| `grip_type` | 3 | 50% | Subjectif, tolérance |
| `condition` | 2 | 60% | Sécurité, plus strict |
| `difficulty` | 3 | 50% | Très subjectif |

### Calcul de confiance

```
confidence = votes_majoritaires / total_votes
```

Le consensus n'est "officiel" que si :
1. `total_votes >= min_votes`
2. `confidence >= ratio_accord`

---

## Références

- `/docs/04_strategie_independance.md` - Architecture serveur personnel
- `/docs/backend_spec.md` - Spécifications API existantes
- `/mastock/src/mastock/core/social_loader.py` - Pattern loader async
- `/mastock/src/mastock/gui/widgets/hold_overlay.py` - Modes coloration existants
