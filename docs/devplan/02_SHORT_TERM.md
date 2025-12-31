# Plan Court Terme (1-3 mois)

**Période** : Décembre 2025 - Mars 2026
**Mise à jour** : 2025-12-31

---

## Objectifs principaux

1. ~~Finaliser le prototype Python (TODO 10)~~ ✅ COMPLET
2. ~~Déployer le serveur personnel Railway~~ ✅ COMPLET
3. ~~Portage client vers Railway (TODO 14)~~ ✅ COMPLET
4. **Implémenter Sync Incrémentale (TODO 15)** ← PRIORITÉ
5. **Implémenter Authentification (TODO 17)** ← PRIORITÉ
6. Implémenter Hold Annotations (TODO 12)

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

## Phase 3 : Sync Incrémentale (TODO 15) - À FAIRE

### État : 0%

Objectif : Réduire le volume de données téléchargées de ~99%.

### Contexte

| Scénario | Actuel | Avec filtrage | Gain |
|----------|--------|--------------|------|
| Sync quotidienne | ~1000 climbs | ~5-10 climbs | **~99%** |
| Sync hebdomadaire | ~1000 climbs | ~50-70 climbs | **~93%** |

### Tâches

| Phase | Description | Effort |
|-------|-------------|--------|
| **Phase 1** | Stokt quick win (`max_age` dynamique) | 4h |
| **Phase 2** | Railway serveur (`since_created_at`) | 4h |
| **Phase 3** | Railway client (utiliser le filtre) | 4h |
| Phase 4 | UI et feedback | 2h |
| Phase 5 | Tests et documentation | 2h |

### Critères de complétion

- [ ] `max_age` calculé dynamiquement (Stokt)
- [ ] Endpoint avec `since_created_at` (Railway)
- [ ] Client utilise les filtres
- [ ] Tests de performance

---

## Phase 4 : Authentification (TODO 17) - À FAIRE

### État : 0%

Objectif : Système d'authentification natif mastoc.

### Décisions

| Aspect | Décision |
|--------|----------|
| Auth type | Email/password + JWT |
| Rôles | User + Admin |
| Reset password | Oui (par email) |

### Tâches

| Phase | Description | Effort |
|-------|-------------|--------|
| **Phase 1** | Extension modèle User (serveur) | 4h |
| **Phase 2** | Endpoints auth (register, login, refresh) | 8h |
| **Phase 3** | Endpoints users (me, profil, avatar) | 4h |
| **Phase 4** | Middleware JWT | 4h |
| **Phase 5** | Client AuthManager | 4h |
| **Phase 6** | UI (dialogs login/register) | 4h |
| Phase 7 | Traçabilité (`created_by_id`) | 2h |

### Critères de complétion

- [ ] Inscription/Connexion fonctionnels
- [ ] JWT valide
- [ ] UI intégrée dans le client
- [ ] Tests sécurité

---

## Phase 5 : Hold Annotations (TODO 12) - À FAIRE

### État : 0%

Permettre aux grimpeurs d'annoter les prises.

### Dépendances

- [x] Serveur Railway déployé ✅
- [ ] Authentification utilisateurs (TODO 17)

### Tâches

| Tâche | Priorité | Effort |
|-------|----------|--------|
| Modèles Python (enums, dataclasses) | Haute | 2h |
| Client API annotations | Haute | 4h |
| API serveur annotations | Haute | 4h |
| Loader async avec cache | Moyenne | 4h |
| Panel d'annotation UI | Haute | 8h |
| Nouveaux ColorModes | Moyenne | 4h |
| Filtres par annotations | Moyenne | 4h |
| Tests | Haute | 4h |

---

## Calendrier révisé

```
✅ Semaine 1 (Déc 23-29)     : TODO 10 finalisé - FAIT
✅ Semaine 2 (Déc 30-31)     : TODO 13+14 complétés - FAIT
───────────────────────────────────────────────────────────
   Semaine 3 (Jan 6-12)      : TODO 15 - Sync Incrémentale
   Semaine 4 (Jan 13-19)     : TODO 17 - Auth Phase 1-3
   Semaine 5 (Jan 20-26)     : TODO 17 - Auth Phase 4-6
   Semaine 6 (Jan 27-Fév 2)  : TODO 12 - Hold Annotations Backend
   Semaine 7 (Fév 3-9)       : TODO 12 - Hold Annotations Client
   Semaine 8 (Fév 10-16)     : Tests + Polish
```

---

## Critères de succès Phase Court Terme

### Technique

- [x] TODO 10 archivé (100%) ✅
- [x] Serveur Railway opérationnel ✅
- [x] Client porté vers Railway ✅
- [ ] Sync incrémentale fonctionnelle (TODO 15)
- [ ] Authentification utilisateurs (TODO 17)
- [ ] Hold Annotations fonctionnel (TODO 12)
- [x] 300+ tests passent ✅

### Fonctionnel

- [x] Création de blocs complète et stable ✅
- [x] BackendSwitch Stokt/Railway ✅
- [ ] Sync optimisée (<100 climbs par sync quotidienne)
- [ ] Login/Register utilisateurs

### Business

- [x] Coût serveur < $15/mois ✅
- [x] Zéro downtime API custom ✅

---

## Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| Railway pricing change | Prévoir migration Render/VPS |
| API Stokt rate limit | Throttling + cache agressif |
| Complexité JWT | Utiliser bibliothèques standard (python-jose) |
| Complexité annotations | MVP simple puis itérer |

---

## Budget estimé

| Poste | Coût mensuel |
|-------|--------------|
| Railway (API + PostgreSQL) | $5-10 |
| Domaine (optionnel) | $1 |
| **Total** | **$6-11/mois** |

---

*Plan court terme mis à jour le 2025-12-31*
