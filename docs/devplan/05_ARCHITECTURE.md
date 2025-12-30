# Décisions Architecturales

**Date** : 2025-12-23

Ce document capture les décisions architecturales majeures du projet mastoc.

---

## ADR-001 : Approche Offline-First

### Contexte

L'application Stokt originale souffre de problèmes de fonctionnement hors-ligne.

### Décision

**mastoc sera conçu en offline-first** : toutes les fonctionnalités de base doivent fonctionner sans connexion internet.

### Conséquences

- Base de données locale obligatoire (SQLite/Room)
- Synchronisation en arrière-plan
- Queue d'actions offline
- Résolution de conflits lors de la reconnexion

---

## ADR-002 : Prototype Python avant Mobile

### Contexte

Développer directement une app mobile Android est coûteux en temps de développement et itération.

### Décision

**Développer d'abord un prototype Python** (PyQt6 + pyqtgraph) pour valider :
- L'architecture des données
- Les algorithmes de filtrage
- Les interactions UI
- L'intégration API

### Conséquences

- Itération rapide sur desktop
- Validation des concepts avant portage
- Code de référence pour l'implémentation mobile
- Documentation des edge cases découverts

### Statut

Prototype Python **fonctionnel** (10 000 lignes, 225 tests).

---

## ADR-003 : Stack Android

### Contexte

Choix de la stack technique pour l'application Android.

### Options évaluées

| Option | Avantages | Inconvénients |
|--------|-----------|---------------|
| React Native | Code partagé iOS | Performance dessin |
| Flutter | Performance, cross-platform | Langage Dart |
| Jetpack Compose | Performance native, officiel Google | Android only |

### Décision

**Jetpack Compose + Kotlin** pour :
- Performance native maximale (important pour le rendu Canvas)
- Support officiel Google
- Intégration optimale avec Room, WorkManager
- Architecture moderne (MVVM, Coroutines)

### Conséquences

- Pas de portage iOS immédiat
- Courbe d'apprentissage Compose
- Écosystème Android riche

---

## ADR-004 : Serveur Personnel Railway

### Contexte

Dépendance totale à l'API Stokt = risque de perte de service.

### Options évaluées

| Option | Coût | Complexité | Résilience |
|--------|------|------------|------------|
| Stokt only | $0 | Faible | Nulle |
| Serveur VPS | $5-20 | Élevée | Haute |
| Railway | $5-10 | Moyenne | Haute |
| Firebase | $0-20 | Moyenne | Moyenne |

### Décision

**Railway (FastAPI + PostgreSQL)** pour :
- Coût raisonnable (~$5-10/mois)
- Setup simplifié (PaaS)
- PostgreSQL inclus
- Scaling automatique
- SSL automatique

### Conséquences

- Coût mensuel récurrent
- Maintenance backend à gérer
- Possibilité de migration vers VPS si nécessaire

---

## ADR-005 : Stratégie de Synchronisation "Railway-First avec Mapping"

### Contexte

Comment synchroniser les données entre :
- API Stokt (source originale Montoboard)
- Serveur personnel Railway (backend principal)
- Application mobile/desktop locale

### Décision

**Architecture Railway-First** : mastoc se connecte à **UN seul backend à la fois** (Railway par défaut), avec un **mapping d'identifiants** permettant la synchronisation manuelle avec Stokt.

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

### Principe du mapping

Chaque entité possède :
- **`id`** : UUID mastoc (toujours présent)
- **`stokt_id`** : UUID Stokt (nullable, rempli après sync)

| Scénario | `id` (mastoc) | `stokt_id` | État |
|----------|---------------|------------|------|
| Bloc créé sur mastoc | `abc-123` | `NULL` | Local uniquement |
| Bloc poussé vers Stokt | `abc-123` | `uvw-012` | Synchronisé |
| Bloc importé depuis Stokt | `def-456` | `xyz-789` | Importé |

### Répartition des données

| Données | Railway | Stokt | Notes |
|---------|---------|-------|-------|
| Blocs (travail quotidien) | ✓ | - | Créés sur mastoc |
| Blocs Montoboard (copie) | ✓ | ✓ | Import initial |
| **Images murs** | ✓ | ✓ | **CRITIQUE: dupliquées** |
| Features custom | ✓ | - | Hold annotations, etc. |

### Opérations de synchronisation

| Opération | Description |
|-----------|-------------|
| **Import initial** | Stokt → Railway (script `init_from_stokt.py`) |
| **Push vers Stokt** | Climb mastoc → POST Stokt → MAJ `stokt_id` |
| **Import depuis Stokt** | GET Stokt → INSERT/UPDATE local avec mapping |

### Avantages

- **Simplicité** : Un seul backend actif, pas de sync auto complexe
- **Contrôle** : Push/Import explicite, pas de surprises
- **Indépendance** : Fonctionne 100% sur Railway sans Stokt

Voir `/docs/04_strategie_independance.md` pour les détails complets.

---

## ADR-006 : Format des Coordonnées des Prises

### Contexte

Comment stocker et manipuler les positions des prises sur l'image du mur.

### Options évaluées

| Format | Avantages | Inconvénients |
|--------|-----------|---------------|
| Pixels absolus | Simple | Dépend résolution |
| Pourcentages (0-1) | Indépendant résolution | Calcul à chaque rendu |
| Polygones SVG | Forme précise | Parsing complexe |

### Décision

**Polygones avec coordonnées relatives (0.0 - 1.0)** :
- Compatible Stokt (même format)
- Indépendant de la résolution d'affichage
- Centroïde calculé pour chaque prise

### Format de stockage

```python
# Polygone : liste de points (x, y) relatifs
polygon_str = "0.234,0.456 0.238,0.462 0.245,0.458 0.240,0.450"

# Centroïde : point central
centroid_x = 0.239
centroid_y = 0.456
```

---

## ADR-007 : Authentification Multi-Utilisateurs

### Contexte

Support de plusieurs utilisateurs sur le serveur personnel.

### Options évaluées

| Option | Complexité | Sécurité |
|--------|------------|----------|
| Token simple | Faible | Moyenne |
| JWT | Moyenne | Haute |
| OAuth2 | Élevée | Très haute |

### Décision

**JWT avec refresh token** :
- Sécurité suffisante pour usage personnel
- Pas de dépendance externe (OAuth)
- Refresh token pour éviter re-auth fréquente

### Implémentation

```python
# Login → JWT + Refresh Token
POST /api/auth/login
{
    "email": "user@example.com",
    "password": "***"
}
Response: {
    "access_token": "eyJ...",  # 15 min
    "refresh_token": "abc...", # 30 jours
}

# Refresh
POST /api/auth/refresh
{
    "refresh_token": "abc..."
}
Response: {
    "access_token": "eyJ..."
}
```

---

## ADR-008 : Hold Annotations - Consensus

### Contexte

Comment calculer le consensus des annotations de prises par les utilisateurs.

### Décision

**Mode statistique avec seuils** :

| Attribut | Votes min | Accord min | Justification |
|----------|-----------|------------|---------------|
| grip_type | 3 | 50% | Subjectif |
| condition | 2 | 60% | Sécurité, plus strict |
| difficulty | 3 | 50% | Très subjectif |

### Calcul

```sql
-- Vue matérialisée PostgreSQL
CREATE MATERIALIZED VIEW hold_consensus AS
SELECT
    hold_id,
    mode() WITHIN GROUP (ORDER BY grip_type) AS consensus_grip_type,
    COUNT(grip_type) AS grip_type_votes
FROM hold_annotations
GROUP BY hold_id;
```

---

## ADR-009 : Gestion des Images

### Contexte

Les images des murs sont volumineuses (~2-5 MB par mur).

### Décision

**Stockage local + cache intelligent** :

| Type | Stockage | Taille |
|------|----------|--------|
| Image HD | Téléchargée une fois, stockée localement | 2-5 MB |
| Pictos | Générés localement, cachés sur disque | ~50 KB/bloc |
| Thumbnails | Générés à la demande | ~5 KB |

### Cache

```
~/.mastoc/
├── images/
│   └── montoboard_face_xxx.jpg
├── pictos/
│   ├── climb_abc.png
│   └── climb_def.png
└── cache.db  # Métadonnées cache
```

---

## ADR-010 : Tests et Qualité

### Contexte

Garantir la fiabilité du code sur la durée.

### Décision

**Stratégie de tests pyramidale** :

```
        ╱╲
       ╱  ╲        E2E (5%)
      ╱────╲       - Parcours utilisateur complets
     ╱      ╲
    ╱  Int.  ╲     Intégration (25%)
   ╱──────────╲    - API, DB, sync
  ╱            ╲
 ╱    Unit      ╲  Unit (70%)
╱────────────────╲ - Logique métier, modèles
```

### Couverture cible

| Module | Couverture cible |
|--------|------------------|
| core/ | >90% |
| api/ | >85% |
| db/ | >85% |
| gui/ | >50% (UI difficile à tester) |

---

## ADR-011 : Versioning et Releases

### Contexte

Gestion des versions de l'application.

### Décision

**Semantic Versioning (SemVer)** :

```
MAJOR.MINOR.PATCH

1.0.0 - Première release stable
1.1.0 - Nouvelles fonctionnalités
1.1.1 - Corrections de bugs
2.0.0 - Breaking changes
```

### Branches Git

```
main        ─────────────────────────────────────────▶
                    │
feature/xxx ────────┼─────▶ (merge via PR)
                    │
release/1.0 ────────┴─────▶ (tag v1.0.0)
```

---

## Décisions à prendre

| Question | Options | Statut |
|----------|---------|--------|
| Dual-write vers Stokt | Oui / Non | À décider |
| Support iOS | SwiftUI / React Native / Non | Reporté |
| Monétisation | Gratuit / Donation / Premium | À décider |
| Open Source | Oui / Non | À décider |

---

*Document mis à jour le 2025-12-23*
