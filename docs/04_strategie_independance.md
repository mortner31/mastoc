# Stratégie d'indépendance vis-à-vis de Stokt

## Contexte

Ce document capture la stratégie pour :
1. Travailler principalement sur le serveur mastoc (Railway)
2. Maintenir un mapping d'identifiants avec Stokt
3. Permettre le push/import bidirectionnel entre les deux systèmes
4. Préparer une indépendance totale si nécessaire

---

## Stratégie Retenue : Railway-First avec Mapping

### Principe

mastoc se connecte à **UN seul backend à la fois** (Railway ou Stokt), avec un **mapping d'identifiants** permettant la synchronisation manuelle entre les deux.

```
┌─────────────────────────────────────────────────────────────┐
│                     mastoc CLIENT                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────┐         ┌─────────────────┐          │
│   │  MODE: RAILWAY  │   OU    │  MODE: STOKT    │          │
│   │  (par défaut)   │         │  (optionnel)    │          │
│   └────────┬────────┘         └────────┬────────┘          │
│            │                           │                    │
│            ▼                           ▼                    │
│   ┌─────────────────────────────────────────────┐          │
│   │           SQLite Local                       │          │
│   │  ┌─────────────────────────────────────┐    │          │
│   │  │ climbs                               │    │          │
│   │  │  • id (UUID mastoc)                  │    │          │
│   │  │  • stokt_id (UUID, nullable) ◄───────┼── MAPPING    │
│   │  │  • name, holds_list, grade...        │    │          │
│   │  └─────────────────────────────────────┘    │          │
│   └─────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Avantages de cette approche

| Aspect | Bénéfice |
|--------|----------|
| **Simplicité** | Un seul backend actif, pas de sync automatique complexe |
| **Contrôle** | Push/Import explicite, pas de surprises |
| **Évolutivité** | Peut évoluer vers double-source si besoin |
| **Indépendance** | Fonctionne 100% sur Railway sans Stokt |

---

## Mapping d'Identifiants

### Concept clé

Chaque entité (climb, list, user) possède :
- **`id`** : UUID mastoc (toujours présent, généré localement)
- **`stokt_id`** : UUID Stokt (nullable, rempli après sync)

```
┌──────────────────────────────────────────────────────────┐
│                    MAPPING DES IDS                        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Bloc créé sur mastoc    Bloc importé de Stokt           │
│  ┌─────────────────┐     ┌─────────────────┐             │
│  │ id: abc-123     │     │ id: def-456     │             │
│  │ stokt_id: NULL  │     │ stokt_id: xyz-789│             │
│  └─────────────────┘     └─────────────────┘             │
│           │                       │                       │
│           ▼                       │                       │
│  Push vers Stokt                  │                       │
│  ┌─────────────────┐              │                       │
│  │ id: abc-123     │              │                       │
│  │ stokt_id: uvw-012│◄── ID retourné par Stokt           │
│  └─────────────────┘                                      │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Scénarios de mapping

| Scénario | `id` (mastoc) | `stokt_id` | État |
|----------|---------------|------------|------|
| Bloc créé sur mastoc | `abc-123` | `NULL` | Local uniquement |
| Bloc poussé vers Stokt | `abc-123` | `uvw-012` | Synchronisé ✓ |
| Bloc importé depuis Stokt | `def-456` | `xyz-789` | Importé ✓ |
| Bloc modifié après sync | `abc-123` | `uvw-012` | À re-sync |

### Flux de synchronisation

```
1. TRAVAIL SUR MASTOC (quotidien)
   └─► Création/modification locale
   └─► stokt_id reste NULL pour les nouveaux blocs

2. PUSH VERS STOKT (ponctuel, manuel)
   └─► Sélectionner les blocs à pousser
   └─► POST vers Stokt API
   └─► Stokt retourne son UUID
   └─► UPDATE local: stokt_id = UUID_retourné

3. IMPORT DEPUIS STOKT (ponctuel, manuel)
   └─► GET blocs depuis Stokt
   └─► Pour chaque bloc:
       └─► Si stokt_id existe localement → UPDATE
       └─► Sinon → INSERT avec stokt_id = UUID_Stokt
```

---

## Répartition des Données

### Par Source

| Données | Railway | Stokt | Notes |
|---------|---------|-------|-------|
| Blocs Montoboard | ✓ (copie) | ✓ (original) | Sync manuelle |
| Prises/Polygones | ✓ (copie) | ✓ (original) | Import initial |
| Images murs | ✓ (dupliquées) | ✓ (original) | **CRITIQUE** |
| Blocs perso (nouveaux) | ✓ | - | Créés sur mastoc |
| Hold Annotations | ✓ | - | Feature custom |
| Listes custom | ✓ | - | Feature custom |
| Pan personnel | ✓ | - | Feature custom |

### Ce qui reste sur Stokt uniquement

- Interactions sociales (likes publics, comments publics)
- Authentification originale
- Profils utilisateurs publics

---

## Schéma de Base de Données

### Tables principales (Railway/SQLite)

```sql
-- Source des données
CREATE TYPE data_source AS ENUM ('mastoc', 'stokt');

-- Gyms
CREATE TABLE gyms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stokt_id UUID UNIQUE,              -- Mapping Stokt
    display_name TEXT NOT NULL,
    location_string TEXT,
    source data_source DEFAULT 'mastoc',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Faces (configuration de prises)
CREATE TABLE faces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stokt_id UUID UNIQUE,              -- Mapping Stokt
    gym_id UUID REFERENCES gyms(id),
    picture_path TEXT NOT NULL,
    picture_width INTEGER,
    picture_height INTEGER,
    feet_rules_options JSONB DEFAULT '[]',
    has_symmetry BOOLEAN DEFAULT FALSE,
    source data_source DEFAULT 'mastoc',
    synced_at TIMESTAMP
);

-- Prises
CREATE TABLE holds (
    id SERIAL PRIMARY KEY,
    stokt_id INTEGER UNIQUE,           -- Mapping Stokt (INTEGER sur Stokt)
    face_id UUID REFERENCES faces(id),
    polygon_str TEXT NOT NULL,
    centroid_x REAL,
    centroid_y REAL,
    path_str TEXT
);

-- Blocs
CREATE TABLE climbs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stokt_id UUID UNIQUE,              -- Mapping Stokt (NULL si créé sur mastoc)
    face_id UUID REFERENCES faces(id),
    setter_id UUID REFERENCES users(id),
    name TEXT NOT NULL,
    holds_list TEXT NOT NULL,
    grade_font TEXT,
    grade_ircra REAL,
    is_private BOOLEAN DEFAULT FALSE,
    source data_source DEFAULT 'mastoc',
    created_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP,               -- Dernière sync avec Stokt
    -- Données custom (mastoc only)
    personal_notes TEXT,
    personal_rating INTEGER,
    is_project BOOLEAN DEFAULT FALSE
);
CREATE INDEX idx_climbs_stokt_id ON climbs(stokt_id);

-- Users avec mapping
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stokt_id UUID UNIQUE,              -- Mapping Stokt
    full_name TEXT NOT NULL,
    avatar_path TEXT,
    source data_source DEFAULT 'mastoc',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table de mapping explicite (audit/debug)
CREATE TABLE id_mappings (
    id SERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL,         -- 'climb', 'list', 'user', 'face'
    mastoc_id UUID NOT NULL,
    stokt_id UUID NOT NULL,
    sync_direction TEXT NOT NULL,      -- 'stokt_to_mastoc', 'mastoc_to_stokt'
    synced_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(entity_type, mastoc_id),
    UNIQUE(entity_type, stokt_id)
);
```

### Tables custom (mastoc only)

```sql
-- Listes personnalisées
CREATE TABLE climb_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stokt_id UUID UNIQUE,              -- NULL si liste mastoc-only
    owner_id UUID REFERENCES users(id),
    name TEXT NOT NULL,
    description TEXT,
    list_type TEXT DEFAULT 'personal', -- 'personal', 'circuit', 'project'
    is_public BOOLEAN DEFAULT FALSE,
    source data_source DEFAULT 'mastoc',
    created_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP
);

-- Items des listes
CREATE TABLE list_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stokt_id UUID UNIQUE,
    list_id UUID REFERENCES climb_lists(id) ON DELETE CASCADE,
    climb_id UUID REFERENCES climbs(id),
    position INTEGER DEFAULT 0,
    notes TEXT,
    status TEXT DEFAULT 'todo',        -- 'todo', 'in_progress', 'done'
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(list_id, climb_id)
);

-- Hold Annotations (feature custom)
CREATE TABLE hold_annotations (
    hold_id INTEGER REFERENCES holds(id),
    user_id UUID REFERENCES users(id),
    grip_type TEXT,                    -- 'crimp', 'sloper', 'jug', 'pinch'...
    condition TEXT,                    -- 'ok', 'needs_brushing', 'broken'
    difficulty TEXT,                   -- 'easy', 'normal', 'hard'
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (hold_id, user_id)
);
```

---

## Architecture Client

### BackendSwitch (remplace DataSourceManager)

```python
from enum import Enum
from typing import Protocol

class BackendType(Enum):
    RAILWAY = "railway"
    STOKT = "stokt"

class ClimbAPI(Protocol):
    """Interface commune pour les backends."""
    def get_climbs(self, gym_id: str) -> list[Climb]: ...
    def get_climb(self, climb_id: str) -> Climb: ...
    def create_climb(self, face_id: str, payload: dict) -> Climb: ...
    def update_climb(self, climb_id: str, payload: dict) -> Climb: ...
    def delete_climb(self, climb_id: str) -> bool: ...

class MastocClient:
    """Client unifié avec sélection de backend."""

    def __init__(self, backend: BackendType = BackendType.RAILWAY):
        self.backend_type = backend
        self._init_backend()

    def _init_backend(self):
        if self.backend_type == BackendType.RAILWAY:
            from mastoc.api.railway_client import RailwayAPI
            self.api = RailwayAPI()
        else:
            from mastoc.api.client import StoktAPI
            self.api = StoktAPI()

    def switch_backend(self, backend: BackendType):
        """Change de backend à chaud."""
        self.backend_type = backend
        self._init_backend()

    # --- Opérations CRUD standard ---

    def get_climbs(self, gym_id: str) -> list[Climb]:
        return self.api.get_climbs(gym_id)

    def create_climb(self, face_id: str, payload: dict) -> Climb:
        """Crée un climb. stokt_id sera NULL si backend=RAILWAY."""
        return self.api.create_climb(face_id, payload)

    # --- Opérations de synchronisation ---

    def push_to_stokt(self, climb_id: str) -> str:
        """
        Pousse un climb mastoc vers Stokt.

        Returns:
            stokt_id généré par Stokt
        """
        if self.backend_type != BackendType.RAILWAY:
            raise ValueError("Push uniquement depuis Railway")

        # 1. Récupérer le climb local
        climb = self.api.get_climb(climb_id)
        if climb.stokt_id:
            raise ValueError(f"Climb déjà synchronisé: {climb.stokt_id}")

        # 2. Créer sur Stokt
        stokt_api = StoktAPI()
        stokt_climb = stokt_api.create_climb(
            face_id=climb.face_stokt_id,  # Nécessite mapping face
            payload=climb.to_stokt_payload()
        )

        # 3. Mettre à jour le mapping local
        self.api.update_stokt_id(climb_id, stokt_climb.id)

        return stokt_climb.id

    def import_from_stokt(self, stokt_climb_id: str) -> Climb:
        """
        Importe un climb depuis Stokt vers mastoc.

        Returns:
            Climb créé/mis à jour localement
        """
        if self.backend_type != BackendType.RAILWAY:
            raise ValueError("Import uniquement vers Railway")

        # 1. Récupérer depuis Stokt
        stokt_api = StoktAPI()
        stokt_climb = stokt_api.get_climb(stokt_climb_id)

        # 2. Vérifier si déjà importé
        existing = self.api.get_climb_by_stokt_id(stokt_climb_id)
        if existing:
            # Update
            return self.api.update_from_stokt(existing.id, stokt_climb)
        else:
            # Insert avec mapping
            return self.api.create_from_stokt(stokt_climb)

    def bulk_import_from_stokt(self, gym_id: str, callback=None) -> int:
        """
        Import en masse depuis Stokt.

        Returns:
            Nombre de climbs importés/mis à jour
        """
        stokt_api = StoktAPI()
        stokt_climbs = stokt_api.get_all_gym_climbs(gym_id, callback)

        count = 0
        for stokt_climb in stokt_climbs:
            self.import_from_stokt(stokt_climb.id)
            count += 1

        return count
```

### Configuration

```python
# config.py
from dataclasses import dataclass
from enum import Enum

class BackendType(Enum):
    RAILWAY = "railway"
    STOKT = "stokt"

@dataclass
class MastocConfig:
    """Configuration globale mastoc."""

    # Backend actif
    backend: BackendType = BackendType.RAILWAY

    # Railway
    railway_url: str = "https://mastoc-api.railway.app"
    railway_token: str = ""

    # Stokt (pour sync)
    stokt_token: str = ""

    # Local
    cache_dir: str = "~/.mastoc"
    db_path: str = "~/.mastoc/mastoc.db"

    @classmethod
    def load(cls) -> "MastocConfig":
        """Charge la config depuis fichier/env."""
        # TODO: Implémenter
        pass
```

---

## Scripts de Synchronisation

### 1. Import Initial (`init_from_stokt.py`)

Script one-shot pour importer toutes les données Stokt vers Railway :

```python
#!/usr/bin/env python3
"""
init_from_stokt.py - Import initial Stokt → Railway

Usage:
    python init_from_stokt.py --stokt-token <token> --railway-url <url>
"""

import asyncio
from pathlib import Path

async def run_initial_import(stokt_token: str, railway_url: str):
    """Import complet depuis Stokt."""

    print("=== IMPORT INITIAL STOKT → MASTOC ===\n")

    # 1. Faces et prises
    print("[1/4] Import des faces et prises...")
    faces = await import_faces(stokt_token)

    # 2. Images (CRITIQUE)
    print("[2/4] Duplication des images...")
    await duplicate_images(faces, railway_url)

    # 3. Blocs
    print("[3/4] Import des blocs...")
    climbs = await import_climbs(stokt_token)

    # 4. Users (setters)
    print("[4/4] Import des utilisateurs...")
    users = await import_users(climbs)

    print(f"\n✓ Import terminé:")
    print(f"  - {len(faces)} faces")
    print(f"  - {sum(len(f.holds) for f in faces)} prises")
    print(f"  - {len(climbs)} blocs")
    print(f"  - {len(users)} utilisateurs")
```

### 2. Sync Incrémentale (`sync_stokt.py`)

Script pour synchroniser les nouveaux blocs :

```python
#!/usr/bin/env python3
"""
sync_stokt.py - Synchronisation incrémentale

Usage:
    python sync_stokt.py --direction stokt-to-mastoc
    python sync_stokt.py --direction mastoc-to-stokt --climb-ids abc,def,ghi
"""

def sync_stokt_to_mastoc(since: datetime = None):
    """Importe les nouveaux blocs Stokt."""

    # Récupérer les blocs récents
    stokt_climbs = stokt_api.get_gym_climbs(gym_id, max_age=7)

    imported = 0
    updated = 0

    for climb in stokt_climbs:
        existing = db.get_by_stokt_id(climb.id)
        if existing:
            if climb.date_modified > existing.synced_at:
                db.update_from_stokt(existing.id, climb)
                updated += 1
        else:
            db.create_from_stokt(climb)
            imported += 1

    print(f"Sync terminée: {imported} importés, {updated} mis à jour")

def sync_mastoc_to_stokt(climb_ids: list[str]):
    """Pousse des blocs mastoc vers Stokt."""

    pushed = 0
    errors = []

    for climb_id in climb_ids:
        climb = db.get(climb_id)
        if climb.stokt_id:
            errors.append(f"{climb_id}: déjà synchronisé")
            continue

        try:
            stokt_climb = stokt_api.create_climb(climb.to_payload())
            db.update_stokt_id(climb_id, stokt_climb.id)
            pushed += 1
        except Exception as e:
            errors.append(f"{climb_id}: {e}")

    print(f"Push terminé: {pushed} poussés, {len(errors)} erreurs")
```

---

## Analyse de Stokt

### Modèle économique

| Aspect | Détail |
|--------|--------|
| Fondation | 2018, Brooklyn (STŌKT LLC) |
| Financement | Aucune levée de fonds connue |
| Modèle | Freemium B2B |
| Revenus | Stokt Pro (abonnement salles) |
| Utilisateurs | App gratuite pour grimpeurs |

### Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Fermeture du service | Faible | Critique | Images dupliquées sur Railway |
| Changement API | Moyenne | Élevé | Mapping permet de continuer sur Railway |
| Banissement compte | Faible | Critique | 100% Railway possible |
| Rate limit API | Moyenne | Moyen | Cache agressif + throttling |

---

## Plan d'Implémentation

### Phase 1 : Infrastructure Railway

- [ ] Créer le projet Railway (FastAPI + PostgreSQL)
- [ ] Implémenter les endpoints de base
- [ ] Créer `RailwayAPI` client Python
- [ ] Script `init_from_stokt.py`
- [ ] **Dupliquer les images** (critique)

### Phase 2 : Client Unifié

- [ ] Créer `MastocClient` avec `BackendSwitch`
- [ ] Adapter l'UI pour supporter les deux backends
- [ ] Tester le switch Railway ↔ Stokt

### Phase 3 : Synchronisation

- [ ] Implémenter `push_to_stokt()`
- [ ] Implémenter `import_from_stokt()`
- [ ] Script `sync_stokt.py`
- [ ] UI pour déclencher les syncs

### Phase 4 : Features Custom

- [ ] Hold Annotations (Railway only)
- [ ] Listes custom
- [ ] Pan personnel

---

## Décisions Prises

| Question | Décision | Justification |
|----------|----------|---------------|
| **Architecture** | Railway-first, single-source | Simplicité, contrôle |
| **Mapping** | `stokt_id` nullable sur chaque entité | Flexible, auditable |
| **Sync** | Manuelle (pas auto) | Contrôle total |
| **Images** | Dupliquées sur Railway | Critique pour indépendance |
| **Backend switch** | À chaud, dans le client | Flexibilité |

## Décisions Ouvertes

| Question | Options | Statut |
|----------|---------|--------|
| Sync automatique en arrière-plan | Oui / Non | À décider plus tard |
| Fréquence de sync recommandée | Quotidienne / Hebdo / Manuel | À décider |
| Gestion des conflits (même bloc modifié) | Timestamp / Manuel | À décider |

---

## Références

| Document | Contenu |
|----------|---------|
| `docs/devplan/02_SHORT_TERM.md` | Plan court terme |
| `docs/devplan/05_ARCHITECTURE.md` | Décisions architecturales |
| `mastoc/src/mastoc/api/client.py` | Client Stokt actuel |
| `mastoc/src/mastoc/api/models.py` | Modèles de données |

---

*Document créé le 2025-12-23*
*Dernière mise à jour : 2025-12-30*
*Version : 3.0 - Railway-First avec Mapping*
