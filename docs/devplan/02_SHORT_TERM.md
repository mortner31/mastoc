# Plan Court Terme (1-3 mois)

**Période** : Décembre 2025 - Mars 2026

---

## Objectifs principaux

1. **Finaliser le prototype Python** (TODO 10)
2. **Déployer le serveur personnel Railway**
3. **Implémenter Hold Annotations** (TODO 12)
4. **Préparer la migration mobile**

---

## Phase 1 : Finalisation TODO 10 (Semaine 1)

### État actuel : 97%

Le wizard de création est fonctionnel, premier bloc créé avec succès.

### Tâches restantes

| Tâche | Priorité | Effort |
|-------|----------|--------|
| Tests edge cases (validation, erreurs API) | Haute | 2h |
| Gestion erreur réseau (retry, queue offline) | Moyenne | 4h |
| Amélioration feedback utilisateur | Basse | 2h |
| Documentation utilisation | Basse | 1h |

### Critères de complétion

- [ ] 100% des tests passent
- [ ] Gestion erreur réseau implémentée
- [ ] Documentation mise à jour
- [ ] TODO 10 archivé

---

## Phase 2 : Serveur Personnel Railway (Semaines 2-3)

### Objectif

Déployer un backend indépendant avec **architecture Railway-First** :
- **Import initial des données Stokt** (one-shot)
- **Duplication des images** (critique pour résilience)
- Hold Annotations et features custom
- Support pan personnel
- Indépendance totale si Stokt ferme

### Architecture Railway-First avec Mapping

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
│   │  • id (UUID mastoc)                          │          │
│   │  • stokt_id (nullable) ◄─── MAPPING          │          │
│   └─────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

**Répartition des données :**
| Données | Railway | Stokt | Notes |
|---------|---------|-------|-------|
| Blocs (travail quotidien) | ✓ | - | Créés sur mastoc |
| Blocs Montoboard (copie) | ✓ | ✓ | Import initial |
| **Images murs** | ✓ | ✓ | **CRITIQUE: dupliquées** |
| Features custom | ✓ | - | Hold annotations, etc. |

### Tâches

| Tâche | Priorité | Effort |
|-------|----------|--------|
| Créer projet Railway | Haute | 1h |
| Setup PostgreSQL | Haute | 2h |
| API FastAPI (endpoints base) | Haute | 8h |
| **Script `init_from_stokt.py`** | **Haute** | 4h |
| **Duplication images murs** | **Critique** | 2h |
| Client `RailwayAPI` Python | Haute | 4h |
| Tests API | Moyenne | 4h |

### Script d'Import Initial (`init_from_stokt.py`)

Script one-shot pour importer les données Stokt vers Railway :

```bash
python init_from_stokt.py --stokt-token "abc123..." --railway-url "https://mastoc-api.railway.app"
```

**Ce que le script fait :**
| Étape | Action | Données |
|-------|--------|---------|
| 1 | Fetch faces | Faces + 776 prises avec polygones |
| 2 | **Duplicate images** | Images HD des murs → Railway + backup local |
| 3 | Fetch climbs | ~1000+ blocs avec pagination |
| 4 | Create users | Setters uniques + avatars (mapping Stokt ID) |
| 5 | Push Railway | Bulk insert vers API Railway |

Voir `/docs/04_strategie_independance.md` pour le code complet.

### Stack technique

- **Backend** : FastAPI (Python)
- **Base de données** : PostgreSQL
- **Hébergement** : Railway (~$5-10/mois)
- **Auth** : Token simple (pas de OAuth)

### Schéma PostgreSQL

```sql
-- Synchronisé depuis Stokt
CREATE TABLE climbs (
    id UUID PRIMARY KEY,
    stokt_id UUID UNIQUE,
    face_id UUID,
    name TEXT NOT NULL,
    holds_list TEXT,
    grade_font TEXT,
    setter_name TEXT,
    is_synced BOOLEAN DEFAULT FALSE,
    synced_at TIMESTAMP
);

CREATE TABLE holds (
    id SERIAL PRIMARY KEY,
    stokt_id INTEGER,
    face_id UUID,
    polygon_str TEXT NOT NULL,
    centroid_x REAL,
    centroid_y REAL
);

-- Fonctionnalités custom
CREATE TABLE hold_annotations (
    hold_id INTEGER REFERENCES holds(id),
    user_id UUID,
    grip_type TEXT,
    condition TEXT,
    difficulty TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (hold_id, user_id)
);
```

### Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health` | GET | Status serveur |
| `/api/sync/stokt` | POST | Sync depuis Stokt |
| `/api/climbs` | GET | Liste climbs |
| `/api/climbs/{id}` | GET | Détail climb |
| `/api/holds/{id}/annotations` | GET/PUT | Annotations |
| `/api/holds/annotations/batch` | POST | Batch annotations |

---

## Phase 3 : Hold Annotations (Semaines 4-6)

### Objectif

Permettre aux grimpeurs d'annoter les prises avec :
- Type de prise (réglette, bac, pince...)
- État (OK, à brosser, tournée...)
- Difficulté relative

### Dépendances

- [ ] Serveur Railway déployé
- [ ] API annotations fonctionnelle

### Tâches client (mastoc Python)

| Tâche | Priorité | Effort |
|-------|----------|--------|
| Modèles Python (enums, dataclasses) | Haute | 2h |
| Client API annotations | Haute | 4h |
| Loader async avec cache | Moyenne | 4h |
| Panel d'annotation UI | Haute | 8h |
| Nouveaux ColorModes (grip_type, condition) | Moyenne | 4h |
| Filtres par annotations | Moyenne | 4h |
| Tests | Haute | 4h |

### UI Panel d'annotation

```
┌─────────────────────────────────────┐
│ Prise #829279                       │
├─────────────────────────────────────┤
│ Consensus communautaire             │
│ ┌───────────────────────────────┐   │
│ │ Type : Réglette (4 votes)     │   │
│ │ État : OK (3 votes)           │   │
│ │ Difficulté : -                │   │
│ └───────────────────────────────┘   │
├─────────────────────────────────────┤
│ Mon annotation                      │
│ Type     [▼ Réglette          ]     │
│ État     [▼ OK                ]     │
│ Diff.    [▼ Normale           ]     │
│ Notes    [                    ]     │
│                                     │
│ [   Enregistrer   ] [   Effacer   ] │
└─────────────────────────────────────┘
```

---

## Phase 4 : Préparation Migration Mobile (Semaines 7-8)

### Objectif

Documenter et préparer le portage vers Android.

### Tâches

| Tâche | Priorité | Effort |
|-------|----------|--------|
| Audit API client (ce qui doit être porté) | Haute | 4h |
| Documentation modèles de données | Haute | 4h |
| Wireframes Android (Figma ou similaire) | Moyenne | 8h |
| Setup projet Android skeleton | Moyenne | 4h |
| POC Jetpack Compose + Canvas | Moyenne | 8h |

### Livrables

- [ ] Document de spécification Android
- [ ] Wireframes haute fidélité
- [ ] Projet Android initialisé
- [ ] POC rendu prises avec Compose Canvas

---

## Calendrier prévisionnel

```
Semaine 1 (Déc 23-29)     : Finalisation TODO 10
Semaine 2 (Déc 30-Jan 5)  : Setup Railway + PostgreSQL
Semaine 3 (Jan 6-12)      : API FastAPI + Sync Stokt
Semaine 4 (Jan 13-19)     : Hold Annotations - Backend
Semaine 5 (Jan 20-26)     : Hold Annotations - Client
Semaine 6 (Jan 27-Fév 2)  : Tests + Polish
Semaine 7 (Fév 3-9)       : Préparation Android
Semaine 8 (Fév 10-16)     : POC Jetpack Compose
```

---

## Critères de succès Phase Court Terme

### Technique

- [ ] TODO 10 archivé (100%)
- [ ] Serveur Railway opérationnel
- [ ] Hold Annotations fonctionnel (TODO 12 à 100%)
- [ ] 250+ tests passent
- [ ] Latence API < 200ms

### Fonctionnel

- [ ] Création de blocs complète et stable
- [ ] Annotations communautaires des prises
- [ ] Backup automatique des données Stokt
- [ ] Documentation à jour

### Business

- [ ] Coût serveur < $15/mois
- [ ] Zéro downtime API custom

---

## Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| Railway pricing change | Prévoir migration Render/VPS |
| API Stokt rate limit | Throttling + cache agressif |
| Bugs création blocs | Tests exhaustifs avant déploiement |
| Complexité annotations | MVP simple puis itérer |

---

## Budget estimé

| Poste | Coût mensuel |
|-------|--------------|
| Railway (API + PostgreSQL) | $5-10 |
| Domaine (optionnel) | $1 |
| **Total** | **$6-11/mois** |

---

*Plan court terme créé le 2025-12-23*
