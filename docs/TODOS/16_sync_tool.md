# TODO 16 - Outil de Synchronisation Bidirectionnelle mastoc <-> Stokt

## Objectif

Créer un outil Python avec interface PyQtGraph permettant d'analyser les différences entre mastoc (Railway) et Stokt, et de proposer des options de resynchronisation interactive.

## Contexte

**Situation actuelle (ADR-006 : Deux bases SQLite séparées) :**
- Deux bases SQLite locales : `~/.mastoc/stokt.db` et `~/.mastoc/railway.db`
- `stokt.db` : données synchronisées depuis l'API Stokt
- `railway.db` : données synchronisées depuis l'API Railway
- Les blocs créés sur mastoc ont `stokt_id = NULL` (locaux uniquement)
- Les blocs importés ont `stokt_id` renseigné (mapping)

**Besoin :**
- **Sync en 3 temps :**
  1. Sync Stokt API → stokt.db (SyncManager existant)
  2. Sync Railway API → railway.db (RailwaySyncManager existant)
  3. Analyse des différences entre les deux bases locales
- Voir quels blocs existent sur mastoc mais pas sur Stokt (à pousser)
- Voir quels blocs existent sur Stokt mais pas sur mastoc (à importer)
- Détecter les blocs modifiés après sync (conflits potentiels)
- Actions interactives : Push, Import, Ignorer

**Limitation TODO 15 (sync incrémentale) :**
> La sync incrémentale filtre par `created_at` (date de création du climb).
> Elle ne détecte **PAS** les changements sociaux car ils ne modifient pas cette date :
> - Quelqu'un réalise un climb (send/effort) → `created_at` inchangé
> - Quelqu'un ajoute un commentaire → `created_at` inchangé
> - Quelqu'un ajoute un like → `created_at` inchangé
>
> **Solution TODO 16** : Sync sociale dédiée qui interroge périodiquement
> les endpoints sociaux (`/latest-sends`, `/comments`, `/likes`) pour les
> blocs synchronisés. Voir Phase 2c.

## Architecture Cible (ADR-006)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sync Tool (PyQtGraph)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐     ┌──────────────────────┐          │
│  │   STOKT API          │     │   RAILWAY API        │          │
│  │   (upstream)         │     │   (mastoc-api)       │          │
│  └──────────┬───────────┘     └──────────┬───────────┘          │
│             │ sync                        │ sync                 │
│             ▼                             ▼                      │
│  ┌──────────────────────┐     ┌──────────────────────┐          │
│  │   stokt.db           │     │   railway.db         │          │
│  │   (cache local)      │     │   (cache local)      │          │
│  └──────────┬───────────┘     └──────────┬───────────┘          │
│             │                             │                      │
│             └──────────┬──────────────────┘                      │
│                        ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Diff Engine                            │   │
│  │  Compare stokt.db vs railway.db (offline, rapide)        │   │
│  │                                                           │   │
│  │  CLIMBS:                                                  │   │
│  │  • railway_only (stokt_id=NULL) → à pousser vers Stokt   │   │
│  │  • stokt_only → à importer vers Railway                   │   │
│  │  • conflicts (modifié des deux côtés) → résolution        │   │
│  └──────────────────────────────────────────────────────────┘   │
│            │                                                     │
│            ▼                                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Actions                                │   │
│  │  [Push → Stokt] [Import → Railway] [Résoudre conflit]     │   │
│  │  + mise à jour des APIs correspondantes                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Tâches

### Phase 1 : Diff Engine - Climbs

- [ ] Créer `mastoc/core/diff_engine.py`
- [ ] Récupérer tous les climbs de Railway (avec `stokt_id`)
- [ ] Récupérer tous les climbs de Stokt
- [ ] Calculer les catégories :
  - [ ] `local_only` : climbs mastoc avec `stokt_id = NULL`
  - [ ] `stokt_only` : climbs Stokt sans correspondance locale
  - [ ] `synced` : climbs avec mapping valide
  - [ ] `modified` : climbs où date_modified diffère (conflit)
- [ ] Retourner un `ClimbDiffReport` avec statistiques

### Phase 1b : Diff Engine - Users

- [ ] Récupérer tous les users de Railway (avec `stokt_id`)
- [ ] Extraire les setters uniques depuis les climbs Stokt
- [ ] Calculer les catégories users :
  - [ ] `new_users` : setters Stokt sans correspondance locale
  - [ ] `updated_users` : users avec nom/avatar modifié
  - [ ] `synced_users` : users avec mapping valide et à jour
- [ ] Retourner un `UserDiffReport`

### Phase 2 : API Push/Import Climbs

- [ ] Implémenter `push_climb_to_stokt(climb_id)` dans MastocAPI
  - Créer le climb sur Stokt via POST
  - Mettre à jour `stokt_id` local avec l'ID retourné
- [ ] Implémenter `import_climb_from_stokt(stokt_climb_id)` dans MastocAPI
  - Récupérer le climb depuis Stokt
  - Créer/mettre à jour en local avec mapping
- [ ] Endpoints Railway nécessaires :
  - [ ] `PATCH /api/climbs/{id}/stokt-id` (mettre à jour le mapping)

### Phase 2b : Sync Users

- [ ] Implémenter `import_users_from_stokt()` (batch)
- [ ] Mettre à jour les users existants si nom/avatar changé
- [ ] Créer les nouveaux setters découverts

### Phase 2c : Sync Données Sociales

**Objectif** : Détecter et synchroniser les changements sociaux (réalisations,
commentaires, likes) qui ne sont pas captés par la sync incrémentale TODO 15.

**Stratégie** :
- Interroger périodiquement les endpoints sociaux Stokt pour les blocs sync
- Comparer avec les données locales (Railway)
- Importer les nouvelles données

**Implémentation** :
- [ ] Implémenter `sync_climb_social(climb_id)` :
  - [ ] GET `/api/climbs/{stokt_id}/latest-sends` → importer réalisations
  - [ ] GET `/api/climbs/{stokt_id}/comments` → importer commentaires
  - [ ] GET `/api/climbs/{stokt_id}/likes` → mettre à jour compteur
  - [ ] Mettre à jour `climbed_by` et `total_likes` localement
- [ ] Tables Railway pour stocker :
  - [ ] `sends` : user_id, climb_id, date, attempts, rating
  - [ ] `comments` : user_id, climb_id, text, date, replied_to
- [ ] Modes de sync :
  - [ ] **À la demande** : sync social pour un bloc spécifique (clic UI)
  - [ ] **Batch** : sync social pour tous les blocs avec `stokt_id` non NULL
  - [ ] **Intelligent** : ne sync que les blocs où `climbed_by` ou `total_likes` a changé
- [ ] Détection des changements :
  - [ ] Comparer `climbed_by` local vs remote → si différent, sync sends
  - [ ] Comparer `total_comments` local vs remote → si différent, sync comments
  - [ ] Comparer `total_likes` local vs remote → mettre à jour compteur

### Phase 3 : Interface Graphique

- [ ] Créer `mastoc/gui/sync_app.py` (application PyQtGraph)
- [ ] **Onglet Climbs** :
  - Dashboard : locaux / Stokt / synchronisés / conflits
  - Liste des différences avec actions Push/Import
  - Tri par état, nom, date
- [ ] **Onglet Users** :
  - Dashboard : nouveaux / modifiés / à jour
  - Liste des setters avec actions Import/Ignorer
  - Affichage avatar + nom
- [ ] **Onglet Social** (par bloc sélectionné) :
  - Nombre de sends local vs Stokt
  - Liste des nouveaux commentaires à importer
  - Évolution likes/climbed_by
  - Bouton "Sync social ce bloc"
- [ ] Boutons d'action globaux :
  - Push sélection vers Stokt
  - Import sélection depuis Stokt
  - Sync users
  - Sync social (tous les blocs sync)
- [ ] Barre de progression pour sync en cours
- [ ] Confirmation avant actions de masse

### Phase 4 : Gestion des Conflits

- [ ] Détecter les blocs modifiés des deux côtés
- [ ] UI de résolution de conflit :
  - Affichage côte-à-côte (mastoc vs Stokt)
  - Choix : Garder mastoc / Garder Stokt / Fusionner
- [ ] Historique des actions de sync (log)

### Phase 5 : Polish et Tests

- [ ] Chargement asynchrone (pas de freeze UI)
- [ ] Cache des données Stokt (éviter appels répétés)
- [ ] Tests unitaires DiffEngine
- [ ] Tests d'intégration (mock API)
- [ ] Documentation utilisateur

## Modèles de Données

```python
@dataclass
class ClimbDiffReport:
    """Résultat de l'analyse des différences - Climbs."""
    local_only: list[Climb]      # mastoc only (stokt_id=NULL)
    stokt_only: list[StoktClimb] # Stokt only (pas en local)
    synced: list[SyncedClimb]    # Mapping OK
    conflicts: list[Conflict]     # Modifié des deux côtés
    timestamp: datetime

@dataclass
class UserDiffReport:
    """Résultat de l'analyse des différences - Users."""
    new_users: list[StoktUser]   # Stokt only (pas en local)
    updated_users: list[tuple[User, StoktUser]]  # Nom/avatar différent
    synced_users: list[User]     # À jour
    timestamp: datetime

@dataclass
class SocialDiffReport:
    """Résultat de l'analyse des différences - Données sociales d'un bloc."""
    climb_id: str
    stokt_id: str

    # Sends (réalisations)
    local_sends: int
    remote_sends: int
    new_sends: list[StoktEffort]  # À importer

    # Comments
    local_comments: int
    remote_comments: int
    new_comments: list[StoktComment]  # À importer

    # Stats
    local_likes: int
    remote_likes: int
    local_climbed_by: int
    remote_climbed_by: int

@dataclass
class SyncedClimb:
    """Climb synchronisé entre les deux systèmes."""
    local: Climb
    remote: StoktClimb
    stokt_id: str

@dataclass
class Conflict:
    """Conflit de sync (modifié des deux côtés)."""
    local: Climb
    remote: StoktClimb
    local_modified: datetime
    remote_modified: datetime

class SyncAction(Enum):
    PUSH = "push"           # mastoc → Stokt
    IMPORT = "import"       # Stokt → mastoc
    IGNORE = "ignore"       # Ne rien faire
    RESOLVE = "resolve"     # Résolution manuelle de conflit
    SYNC_SOCIAL = "social"  # Importer données sociales
```

## UI Wireframe

### Onglet Climbs (principal)

```
┌─────────────────────────────────────────────────────────────────┐
│  Sync mastoc <-> Stokt                             [Actualiser] │
├─────────────────────────────────────────────────────────────────┤
│  [Climbs] [Users] [Social]                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ Locaux: 5  │ │ Stokt: 12  │ │ Sync: 987  │ │ Conflits: 2│   │
│  │   [à push] │ │[à importer]│ │    [OK]    │ │ [à résoudre│   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ État      │ Nom           │ Grade │ Setter    │ Action    │  │
│  ├───────────┼───────────────┼───────┼───────────┼───────────┤  │
│  │ 🟢 Local  │ Mon projet    │ 6B    │ Moi       │ [Push]    │  │
│  │ 🟢 Local  │ Nouveau bloc  │ 5+    │ Moi       │ [Push]    │  │
│  │ 🔵 Stokt  │ Bloc externe  │ 7A    │ Alice     │ [Import]  │  │
│  │ 🟡 Conflit│ Bloc modifié  │ 6C    │ Moi       │ [Résoudre]│  │
│  │ ✓ Sync   │ Bloc OK       │ 5     │ Claude    │    -      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [Push sélection] [Import sélection] [Tout pousser] [Tout imp.] │
└─────────────────────────────────────────────────────────────────┘
```

### Onglet Users

```
┌─────────────────────────────────────────────────────────────────┐
│  [Climbs] [Users] [Social]                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐       │
│  │ Nouveaux: 3    │ │ Modifiés: 1    │ │ À jour: 47     │       │
│  │ [à importer]   │ │ [à mettre à j] │ │     [OK]       │       │
│  └────────────────┘ └────────────────┘ └────────────────┘       │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ État      │ Avatar │ Nom             │ Blocs │ Action     │  │
│  ├───────────┼────────┼─────────────────┼───────┼────────────┤  │
│  │ 🔵 Nouveau│  [?]   │ NouveauSetter   │  12   │ [Import]   │  │
│  │ 🟡 Modifié│  [A]   │ Alice → Alice B │   8   │ [Maj]      │  │
│  │ ✓ OK     │  [B]   │ Bob             │  45   │    -       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [Importer nouveaux] [Tout mettre à jour]                        │
└─────────────────────────────────────────────────────────────────┘
```

### Onglet Social (pour un bloc sélectionné)

```
┌─────────────────────────────────────────────────────────────────┐
│  [Climbs] [Users] [Social]                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Bloc sélectionné: "Mon bloc préféré" (6A+)                      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      SENDS (Réalisations)                    ││
│  │  Local: 5    Stokt: 8    Nouveaux: 3                        ││
│  │  ┌────────────────────────────────────────────────────────┐ ││
│  │  │ Alice      │ 2025-12-28 │ Flash      │ [Import]        │ ││
│  │  │ Bob        │ 2025-12-27 │ 3 essais   │ [Import]        │ ││
│  │  │ Charlie    │ 2025-12-26 │ Projet     │ [Import]        │ ││
│  │  └────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      COMMENTS                                ││
│  │  Local: 2    Stokt: 4    Nouveaux: 2                        ││
│  │  ┌────────────────────────────────────────────────────────┐ ││
│  │  │ Alice: "Super bloc, pied gauche délicat!"  │ [Import]  │ ││
│  │  │ Bob: "Merci pour l'ouverture"              │ [Import]  │ ││
│  │  └────────────────────────────────────────────┘            ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Stats: Likes 12→15 (+3)  Climbed_by 5→8 (+3)                    │
│                                                                  │
│  [Sync social ce bloc] [Sync social tous les blocs]              │
└─────────────────────────────────────────────────────────────────┘
```

### Log (commun à tous les onglets)

```
─────────── Log ────────────
12:34 - Analyse terminée: 5 locaux, 12 Stokt, 2 conflits
12:35 - Push "Mon projet" → Stokt : OK (stokt_id=abc-123)
12:36 - Import 3 nouveaux users
12:37 - Sync social "Mon bloc préféré": +3 sends, +2 comments
```

## Fichiers à Créer

```
mastoc/src/mastoc/
├── core/
│   ├── diff_engine.py      # Analyse des différences
│   └── sync_actions.py     # Push, Import, Resolve
├── gui/
│   └── sync_app.py         # Interface graphique PyQtGraph
└── tests/
    ├── test_diff_engine.py
    └── test_sync_actions.py
```

## Dépendances

- TODO 14 (Portage Client Railway) : nécessaire pour `MastocAPI`
- Endpoints Railway à créer si manquants :
  - `PATCH /api/climbs/{id}/stokt-id`
- Authentification Stokt requise pour push/import

## Références

- ADR 001 : Architecture Railway-First avec Mapping d'IDs
- `/docs/04_strategie_independance.md` - Section "Vue Comparaison"
- `server/scripts/init_from_stokt.py` - Script d'import comme référence
- `mastoc/src/mastoc/api/client.py` - Client Stokt existant
