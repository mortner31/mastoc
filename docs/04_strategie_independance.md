# Stratégie d'indépendance vis-à-vis de Stokt

## Contexte

Ce document capture la réflexion stratégique pour :
1. Réduire la dépendance à l'API Stokt
2. Préparer une migration potentielle (banissement, fermeture du service, changement de conditions)
3. Permettre l'ajout de fonctionnalités custom impossibles sur Stokt
4. Supporter plusieurs murs (Montoboard sur Stokt + pan personnel en local)

---

## Analyse de Stokt

### Modèle économique

| Aspect | Détail |
|--------|--------|
| Fondation | 2018, Brooklyn (STŌKT LLC) |
| Financement | Aucune levée de fonds |
| Modèle | Freemium B2B |
| Revenus | Stokt Pro (abonnement salles commerciales) |
| Utilisateurs | App gratuite pour grimpeurs individuels |

### Risques identifiés

| Risque | Probabilité | Impact |
|--------|-------------|--------|
| Fermeture du service | Faible | Critique |
| Changement API (breaking) | Moyenne | Élevé |
| Banissement compte | Faible | Critique |
| Limitation API (rate limit) | Moyenne | Moyen |
| Passage payant utilisateurs | Faible | Moyen |

### Ce que Stokt fournit

- Hébergement des images de murs
- Mapping des prises (polygones, centroïdes)
- Base de données des blocs
- Système de grades communautaires
- Interactions sociales (likes, comments, sends)
- Authentification utilisateurs

---

## Options stratégiques

### Option A : Dépendance totale (statu quo)

```
mastoc ←→ Stokt API
```

**Avantages :** Aucun effort, fonctionnel aujourd'hui
**Risques :** Aucune résilience

### Option B : Mode hybride (recommandé court terme)

```
mastoc ←→ Stokt API (blocs, prises, grades)
    └────→ Serveur perso (features custom)
```

**Avantages :**
- Pas de migration
- Fonctionnalités custom (brossage, stats avancées)
- Coût minimal (~$5/mois)

**Cas d'usage :**
- Tracking du brossage des prises
- Notes personnelles sur les blocs
- Statistiques avancées
- Export PDF

### Option C : Indépendance partielle (recommandé moyen terme)

```
mastoc ←→ Serveur perso (principal)
    └────→ Stokt API (sync silencieuse, lecture seule)
```

**Avantages :**
- Données dupliquées localement
- Survie si Stokt disparaît
- Support multi-murs (Stokt + pan perso)

**Architecture :**
- Montoboard : sync depuis Stokt → serveur perso
- Pan personnel : 100% sur serveur perso

### Option D : Indépendance totale

```
mastoc ←→ Serveur perso uniquement
```

**Avantages :** Contrôle total
**Inconvénients :** Perte des interactions sociales Stokt

---

## Architecture recommandée : Multi-murs hybride

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                          mastoc                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐                    ┌─────────────┐            │
│   │ MONTOBOARD  │                    │  PAN PERSO  │            │
│   │ (via Stokt) │                    │  (natif)    │            │
│   └──────┬──────┘                    └──────┬──────┘            │
│          │                                  │                   │
│          ▼                                  │                   │
│   ┌─────────────┐      Sync silencieuse     │                   │
│   │ API Stokt   │ ─────────────────────┐    │                   │
│   └─────────────┘                      │    │                   │
│                                        ▼    ▼                   │
│                                 ┌─────────────────┐             │
│                                 │  Serveur perso  │             │
│                                 │  (Railway)      │             │
│                                 │  ─────────────  │             │
│                                 │  • Montoboard   │             │
│                                 │    (copie)      │             │
│                                 │  • Pan perso    │             │
│                                 │    (natif)      │             │
│                                 │  • Brossage     │             │
│                                 │  • Stats custom │             │
│                                 └─────────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Flux de données

| Source | Destination | Fréquence | Données |
|--------|-------------|-----------|---------|
| Stokt | Serveur perso | Horaire | Nouveaux blocs Montoboard |
| Stokt | Serveur perso | Initiale | Prises, image mur |
| Serveur perso | mastoc | Temps réel | Tous les murs |
| mastoc | Serveur perso | Temps réel | Blocs pan perso, brossage |
| mastoc | Stokt | Optionnel | Blocs Montoboard (dual-write) |

---

## Schéma de base de données

### Tables principales

```sql
-- Source des données
CREATE TYPE data_source AS ENUM ('stokt', 'local');

-- Salles/Gyms
CREATE TABLE gyms (
    id UUID PRIMARY KEY,
    source data_source NOT NULL,
    stokt_id UUID,
    display_name TEXT NOT NULL,
    location_string TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Murs
CREATE TABLE walls (
    id UUID PRIMARY KEY,
    gym_id UUID REFERENCES gyms(id),
    source data_source NOT NULL,
    stokt_id UUID,
    name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Faces (configuration de prises)
CREATE TABLE faces (
    id UUID PRIMARY KEY,
    wall_id UUID REFERENCES walls(id),
    source data_source NOT NULL,
    stokt_id UUID,
    picture_path TEXT NOT NULL,
    picture_width INTEGER,
    picture_height INTEGER,
    feet_rules_options JSONB DEFAULT '[]',
    has_symmetry BOOLEAN DEFAULT FALSE,
    last_synced TIMESTAMP
);

-- Prises
CREATE TABLE holds (
    id SERIAL PRIMARY KEY,
    face_id UUID REFERENCES faces(id),
    stokt_id INTEGER,
    polygon_str TEXT NOT NULL,
    centroid_x REAL,
    centroid_y REAL,
    path_str TEXT,
    -- Données custom (pas sur Stokt)
    needs_brushing BOOLEAN DEFAULT FALSE,
    last_brushed TIMESTAMP,
    brushed_by UUID REFERENCES users(id)
);

-- Blocs
CREATE TABLE climbs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    face_id UUID REFERENCES faces(id),
    source data_source NOT NULL,
    stokt_id UUID,
    setter_id UUID REFERENCES users(id),
    name TEXT NOT NULL,
    holds_list TEXT NOT NULL,
    grade_font TEXT,
    grade_ircra REAL,
    is_private BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_synced TIMESTAMP,
    -- Données custom
    personal_notes TEXT,
    personal_rating INTEGER,
    is_project BOOLEAN DEFAULT FALSE
);

-- Sync metadata
CREATE TABLE sync_log (
    id SERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL,  -- 'climb', 'face', etc.
    stokt_id TEXT,
    action TEXT NOT NULL,       -- 'create', 'update', 'delete'
    synced_at TIMESTAMP DEFAULT NOW(),
    details JSONB
);
```

### Tables custom (non-Stokt)

```sql
-- Brossage des prises
CREATE TABLE hold_maintenance (
    hold_id INTEGER REFERENCES holds(id),
    reported_by UUID REFERENCES users(id),
    reported_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'needs_brushing',  -- 'needs_brushing', 'brushed', 'broken'
    notes TEXT,
    PRIMARY KEY (hold_id, reported_at)
);

-- Projets personnels
CREATE TABLE user_projects (
    user_id UUID REFERENCES users(id),
    climb_id UUID REFERENCES climbs(id),
    added_at TIMESTAMP DEFAULT NOW(),
    priority INTEGER DEFAULT 0,
    notes TEXT,
    PRIMARY KEY (user_id, climb_id)
);

-- Sessions d'entraînement
CREATE TABLE training_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    notes TEXT
);

CREATE TABLE session_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES training_sessions(id),
    climb_id UUID REFERENCES climbs(id),
    attempted_at TIMESTAMP DEFAULT NOW(),
    sent BOOLEAN DEFAULT FALSE,
    is_flash BOOLEAN DEFAULT FALSE,
    notes TEXT
);
```

---

## Création d'un nouveau pan

### Étapes

1. **Photo haute résolution**
   - Prendre une photo frontale du pan
   - Résolution recommandée : 2000-3000px de large
   - Éclairage uniforme

2. **Mapping des prises**
   - Créer les polygones pour chaque prise
   - Calculer les centroïdes
   - Générer les chemins SVG

3. **Import dans le serveur**
   - Upload image → `/media/walls/mon-pan.jpg`
   - INSERT face + holds

### Outil de mapping (à développer)

Interface pour dessiner les polygones des prises :
- Charger l'image du pan
- Cliquer pour dessiner le contour de chaque prise
- Calculer automatiquement centroïde et path SVG
- Exporter en SQL ou JSON

---

## Synchronisation Stokt

### Script de sync initiale

```python
# sync_stokt.py (pseudo-code)

def sync_initial(gym_id: str, face_id: str):
    """Synchronisation initiale depuis Stokt."""

    # 1. Récupérer la config du mur
    face = stokt_api.get_face_setup(face_id)

    # 2. Télécharger l'image
    download_image(face.picture.name, f"/media/walls/{face_id}.jpg")

    # 3. Insérer la face
    db.insert_face(face, source='stokt', stokt_id=face_id)

    # 4. Insérer les prises
    for hold in face.holds:
        db.insert_hold(hold, face_id=face.id, stokt_id=hold.id)

    # 5. Récupérer tous les blocs
    climbs = stokt_api.get_all_gym_climbs(gym_id)

    # 6. Insérer les blocs
    for climb in climbs:
        db.insert_climb(climb, source='stokt', stokt_id=climb.id)

def sync_incremental(gym_id: str):
    """Synchronisation incrémentale (nouveaux blocs)."""

    last_sync = db.get_last_sync_time()

    # Récupérer les blocs récents
    climbs = stokt_api.get_gym_climbs(gym_id, max_age=1)

    for climb in climbs:
        existing = db.get_climb_by_stokt_id(climb.id)
        if existing:
            db.update_climb(climb)
        else:
            db.insert_climb(climb, source='stokt', stokt_id=climb.id)

    db.set_last_sync_time(now())
```

### Cron job

```bash
# Sync toutes les heures
0 * * * * /path/to/python sync_stokt.py --incremental
```

---

## Coûts estimés

| Composant | Coût mensuel |
|-----------|--------------|
| Railway (API + PostgreSQL) | $5-10 |
| Stockage images | Inclus |
| Domaine (optionnel) | ~$1 |
| **Total** | **$5-15/mois** |

---

## Plan de migration

### Phase 1 : Préparation (maintenant)

- [x] Documenter l'API Stokt (fait : `docs/backend_spec.md`)
- [x] Analyser l'architecture (ce document)
- [ ] Créer le serveur Railway
- [ ] Implémenter la sync initiale

### Phase 2 : Mode hybride

- [ ] Déployer le serveur avec features custom (brossage)
- [ ] Adapter mastoc pour lire depuis les deux sources
- [ ] Tester la sync incrémentale

### Phase 3 : Pan personnel

- [ ] Créer l'outil de mapping de prises
- [ ] Mapper le pan personnel
- [ ] Intégrer dans mastoc

### Phase 4 : Indépendance (si nécessaire)

- [ ] Basculer mastoc vers serveur perso uniquement
- [ ] Désactiver la sync Stokt
- [ ] Migrer les interactions sociales (optionnel)

---

## Décisions ouvertes

| Question | Options | Décision |
|----------|---------|----------|
| Framework backend | Django / FastAPI / Node | À décider |
| Hébergement | Railway / Render / VPS | Railway (recommandé) |
| Dual-write Stokt | Oui / Non | À décider |
| Auth utilisateurs | Simple token / OAuth | Simple token |
| Mapping prises | Manuel / Semi-auto / Payer Stokt | À décider |

---

## Références

| Document | Contenu |
|----------|---------|
| `docs/backend_spec.md` | Spécification API complète |
| `docs/reverse_engineering/03_ENDPOINTS.md` | Endpoints Stokt documentés |
| `mastoc/src/mastoc/api/client.py` | Client API actuel |
| `mastoc/src/mastoc/api/models.py` | Modèles de données |

---

*Document créé le 2025-12-23*
*Dernière mise à jour : 2025-12-23*
