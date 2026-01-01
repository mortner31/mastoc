# Plan Court Terme (1-3 mois)

**Période** : Décembre 2025 - Mars 2026
**Mise à jour** : 2026-01-01

---

## Objectifs principaux

1. ~~Finaliser le prototype Python (TODO 10)~~ ✅ COMPLET
2. ~~Déployer le serveur personnel Railway~~ ✅ COMPLET
3. ~~Portage client vers Railway (TODO 14)~~ ✅ COMPLET
4. ~~Implémenter Sync Incrémentale (TODO 15)~~ ✅ COMPLET
5. ~~Implémenter Authentification (TODO 17)~~ ✅ COMPLET
6. ~~Implémenter Hold Annotations (TODO 12)~~ ✅ COMPLET (95%)
7. ~~Sync Données Sociales (TODO 18)~~ ✅ COMPLET
8. ~~Renforcement Tests (TODO 19)~~ ✅ COMPLET
9. **Application Android Kotlin (TODO 20)** ← PRIORITÉ ACTUELLE

---

## ✅ Phase 1 : Finalisation TODO 10 - COMPLÉTÉ

### État : 100% - Archivé le 2025-12-30

Le wizard de création est fonctionnel, premier bloc créé avec succès.

### Livrables complétés

- [x] Tests edge cases (validation, erreurs API)
- [x] Gestion erreur réseau
- [x] Documentation mise à jour
- [x] TODO 10 archivé

---

## ✅ Phase 2 : Serveur Personnel Railway - COMPLÉTÉ

### État : 100% - Archivé le 2025-12-30 (TODO 13)

Serveur déployé et opérationnel sur Railway.

### Livrables complétés

- [x] Projet Railway créé
- [x] PostgreSQL configuré
- [x] API FastAPI (5 routers)
- [x] Script `init_from_stokt.py`
- [x] Import données (1012 climbs, 776 holds, 79 users)
- [x] Auth par API Key (ADR-002)
- [x] Tests API

### URL Production

https://mastoc-production.up.railway.app

---

## ✅ Phase 2bis : Portage Client Railway - COMPLÉTÉ

### État : 100% - Archivé le 2025-12-31 (TODO 14)

Client Python porté vers Railway avec BackendSwitch.

### Livrables complétés

- [x] Client `MastocAPI` (`railway_client.py`)
- [x] `BackendSwitch` + `BackendSource` (`backend.py`)
- [x] Dual SQLite (ADR-006)
- [x] Config persistante (`config.py`)
- [x] Cache assets (`assets.py`)
- [x] Migration GUI (menu source)
- [x] `RailwaySyncManager`
- [x] 301 tests passent

---

## ✅ Phase 3 : Sync Incrémentale (TODO 15) - COMPLÉTÉ

### État : 100% - Archivé le 2026-01-01

Gain de ~99% sur la bande passante sync.

### Livrables complétés

- [x] `max_age` dynamique (Stokt)
- [x] Endpoints `since_created_at`, `since_synced_at` (Railway)
- [x] Client Railway `sync_incremental()` + `needs_sync()`
- [x] SyncDialog avec choix full/incremental
- [x] ADR-007 créé

---

## ✅ Phase 4 : Authentification (TODO 17) - COMPLÉTÉ

### État : 100% - Archivé le 2026-01-01

Système d'authentification natif mastoc avec JWT.

### Livrables complétés

- [x] Extension modèle User (email, password_hash, role)
- [x] Endpoints auth (register, login, refresh, reset-password)
- [x] Endpoints users (me, profil, avatar)
- [x] Middleware JWT + coexistence API Key
- [x] Client AuthManager + MastocAPI intégré
- [x] UI (MastocLoginDialog, ProfileDialog, PasswordResetDialog)
- [x] Traçabilité (created_by_id, updated_by_id)
- [x] 15 tests JWT automatisés

---

## ✅ Phase 5 : Hold Annotations (TODO 12) - COMPLÉTÉ

### État : 95% - Archivé le 2026-01-01

Système d'annotations de prises crowd-sourcé.

### Livrables complétés

- [x] Backend : modèle HoldAnnotation + 4 endpoints REST + 16 tests
- [x] Client : enums, dataclasses, API methods, AnnotationLoader
- [x] GUI : 3 ColorModes (GRIP_TYPE, CONDITION, DIFFICULTY)
- [x] AnnotationPanel complet
- [x] ADR-008 créé
- [x] 43 tests client

### Optionnel (non bloquant)

- [ ] Intégration hold_selector
- [ ] Filtres par tags annotations

---

## ✅ Phase 6 : Sync Données Sociales (TODO 18) - COMPLÉTÉ

### État : 100% - Complété le 2026-01-01

Refresh des compteurs sociaux depuis Stokt.

### Livrables complétés

- [x] `get_climb_social_stats()` : sends, comments, likes
- [x] `refresh_social_counts()` : refresh unitaire
- [x] `refresh_all_social_counts()` : batch avec throttling 1 req/sec
- [x] Bouton "↻" dans ClimbDetailPanel
- [x] Menu "Outils > Rafraîchir stats sociales"
- [x] Indicateur stale (> 7 jours) avec style orange

---

## ✅ Phase 7 : Renforcement Tests (TODO 19) - COMPLÉTÉ

### État : 100% - Archivé le 2026-01-01

+62 tests ajoutés (353 → 415 tests).

### Livrables complétés

- [x] Tests serveur : test_users.py, test_holds.py, test_permissions.py (+35)
- [x] Tests mastoc : test_auth_manager.py, test_api_errors.py (+27)
- [x] Documentation : docs/06_guide_tests.md

---

## Phase 8 : Application Android Kotlin (TODO 20) - EN COURS

### État : 0%

Première version Android en **lecture seule**.

### Scope

| Inclus | Exclus |
|--------|--------|
| Liste climbs + filtres | Création/édition blocs |
| Visualisation Canvas | Authentification |
| Recherche par prises | Sync bidirectionnelle |
| Heatmaps | Mode offline complet |

### Stack

| Composant | Technologie |
|-----------|-------------|
| UI | Jetpack Compose |
| Architecture | MVVM + Clean Architecture |
| DB | Room |
| Réseau | Retrofit |
| DI | Hilt |

### Phases

| Phase | Description |
|-------|-------------|
| Phase 1 | Setup projet (Gradle, Hilt, Retrofit, Room) |
| Phase 2 | Data Layer (DTOs, Entities, Repository) |
| Phase 3 | Domain Layer (Models, UseCases) |
| Phase 4 | Écran Liste Climbs |
| Phase 5 | Écran Détail (Canvas + polygones) |
| Phase 6 | Recherche par prises |
| Phase 7 | Heatmaps |
| Phase 8 | Tests + Polish |

---

## Calendrier révisé

```
✅ Semaine 1 (Déc 23-29)     : TODO 10 finalisé - FAIT
✅ Semaine 2 (Déc 30-31)     : TODO 13+14 complétés - FAIT
✅ Semaine 3 (Jan 1)         : TODO 15+16+17+18+19 complétés - FAIT
───────────────────────────────────────────────────────────
   Semaine 4 (Jan 6-12)      : TODO 20 - Setup Android + Data Layer
   Semaine 5 (Jan 13-19)     : TODO 20 - Domain + Liste Climbs
   Semaine 6 (Jan 20-26)     : TODO 20 - Détail + Canvas
   Semaine 7 (Jan 27-Fév 2)  : TODO 20 - Recherche prises
   Semaine 8 (Fév 3-9)       : TODO 20 - Heatmaps + Tests
   Semaine 9 (Fév 10-16)     : Polish + Release beta
```

---

## Critères de succès Phase Court Terme

### Technique (Python) - TOUS ATTEINTS ✅

- [x] TODO 10 archivé (100%) ✅
- [x] Serveur Railway opérationnel ✅
- [x] Client porté vers Railway ✅
- [x] Sync incrémentale fonctionnelle (TODO 15) ✅
- [x] Authentification utilisateurs (TODO 17) ✅
- [x] Hold Annotations fonctionnel (TODO 12) ✅
- [x] Sync Données Sociales (TODO 18) ✅
- [x] 375+ tests passent ✅

### Technique (Android) - EN COURS

- [ ] App Android installable (API 24+)
- [ ] Liste climbs avec filtres
- [ ] Visualisation Canvas polygones
- [ ] Recherche par prises
- [ ] 20+ tests unitaires

### Fonctionnel

- [x] Création de blocs complète et stable ✅
- [x] BackendSwitch Stokt/Railway ✅
- [x] Sync optimisée (~99% gain bande passante) ✅
- [x] Login/Register utilisateurs ✅
- [ ] App Android lecture seule

### Business

- [x] Coût serveur < $15/mois ✅
- [x] Zéro downtime API custom ✅

---

## Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| Railway pricing change | Prévoir migration Render/VPS |
| Complexité Compose Canvas | POC polygones en premier |
| Performance rendu prises | Lazy loading, cache bitmap |
| Courbe apprentissage Kotlin | Référence code Python existant |

---

## Budget estimé

| Poste | Coût mensuel |
|-------|--------------|
| Railway (API + PostgreSQL) | $5-10 |
| Domaine (optionnel) | $1 |
| **Total** | **$6-11/mois** |

---

*Plan court terme mis à jour le 2026-01-01*
