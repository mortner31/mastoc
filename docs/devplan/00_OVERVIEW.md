# Plan de Développement mastoc - Vue d'ensemble

**Version** : 2.0
**Date** : 2025-12-31
**Statut** : Document de référence (mis à jour post-TODO 14)

---

## Vision du projet

**mastoc** est une application personnelle de gestion de blocs d'escalade, conçue en **offline-first**, avec comme objectifs :

1. **Visualisation interactive** des blocs sur images de murs
2. **Fonctionnement 100% hors-ligne**
3. **Indépendance progressive** de l'API Stokt ✅ ATTEINT
4. **Support multi-murs** (Montoboard + pan personnel)

---

## État actuel (Décembre 2025)

### Infrastructure opérationnelle

| Composant | Statut | Détails |
|-----------|--------|---------|
| **Serveur Railway** | ✅ Déployé | https://mastoc-production.up.railway.app |
| **Client Python** | ✅ Fonctionnel | BackendSwitch Stokt/Railway |
| **Dual SQLite** | ✅ Implémenté | ADR-006 |
| **Import Stokt** | ✅ Complet | 1012 climbs, 776 holds, 79 users |

### Métriques

| Métrique | Valeur |
|----------|--------|
| Lignes de code | ~12 000 |
| Tests | **301** (passent) |
| ADRs | 6 |
| Données | 1012 climbs, 776 prises |

### Fonctionnalités implémentées

- **Liste de blocs** avec filtres (grade, setter, texte)
- **Visualisation** sur image du mur avec polygones des prises
- **Sélection par prises** (recherche avancée)
- **Modes de coloration** (heatmaps, quantiles, rareté)
- **Création de blocs** (wizard multi-écrans, POST vers API) ✅
- **Interactions sociales** (likes, comments, sends - lecture)
- **Synchronisation API** Stokt ET Railway ✅
- **BackendSwitch** (basculement dynamique Stokt/Railway) ✅

### TODOs

| TODO | Description | Statut |
|------|-------------|--------|
| 09 | Listes Personnalisées | 70% - API OK |
| 12 | Hold Annotations | 0% - À faire |
| **15** | **Sync Incrémentale** | **0% - PRIORITÉ** |
| 16 | Sync Tool mastoc ↔ Stokt | 0% - Planifié |
| **17** | **Authentification & Users** | **0% - PRIORITÉ** |
| ~~10~~ | ~~Création de Blocs~~ | ✅ Archivé |
| ~~13~~ | ~~Serveur Railway~~ | ✅ Archivé |
| ~~14~~ | ~~Portage Client Railway~~ | ✅ Archivé |

---

## Axes stratégiques

### 1. ✅ Infrastructure "Railway-First avec Mapping" - COMPLÉTÉ

**Architecture déployée** : mastoc se connecte à **UN seul backend** (Railway par défaut), avec un **mapping d'identifiants** pour sync avec Stokt.

```
┌─────────────────────────────────────────────────────────────┐
│                     mastoc CLIENT                           │
├─────────────────────────────────────────────────────────────┤
│   BackendSwitch                                             │
│   ┌─────────────────┐         ┌─────────────────┐          │
│   │  MODE: RAILWAY  │   OU    │  MODE: STOKT    │          │
│   │  (par défaut)   │         │  (fallback)     │          │
│   └────────┬────────┘         └────────┬────────┘          │
│            │                           │                    │
│            ▼                           ▼                    │
│   ┌─────────────────┐         ┌─────────────────┐          │
│   │  railway.db     │         │   stokt.db      │          │
│   │  (SQLite)       │         │   (SQLite)      │          │
│   └─────────────────┘         └─────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 2. Optimisation et authentification (Priorité actuelle)

- **TODO 15** : Sync incrémentale (réduire bande passante de ~99%)
- **TODO 17** : Authentification utilisateurs (email/password + JWT)

### 3. Migration mobile Android (À venir)

Portage vers application native Android :
- Stack : Kotlin + Jetpack Compose + Room
- Design : Material Design 3
- Architecture : MVVM + Clean Architecture

### 4. Écosystème complet (Long terme)

- Support multi-utilisateurs
- Statistiques avancées
- Export/Import de données

---

## Horizon temporel

```
                     2025 Q4              2026 Q1              2026 Q2
                  ──────────────────  ──────────────────  ──────────────────
Court terme       │ ✅ TODO 10,13,14 │ TODO 15,17        │                  │
(1-3 mois)        │ ✅ Serveur Rail. │ Sync incrémental  │                  │
                  │ ✅ BackendSwitch │ Auth utilisateurs │                  │
                  ──────────────────────────────────────────────────────────
Moyen terme                          │ App Android MVP  │ Sync bidirect.   │
(3-6 mois)                           │ Hold Annotations │ Pan personnel    │
                  ──────────────────────────────────────────────────────────
Long terme                                               │ Multi-users      │
(6-12 mois)                                              │ Stats avancées   │
                                                         │ Export PDF       │
                  ──────────────────────────────────────────────────────────
```

---

## Documents de référence

| Document | Contenu |
|----------|---------|
| `01_CURRENT_STATE.md` | Analyse détaillée de l'état actuel |
| `02_SHORT_TERM.md` | Plan court terme (1-3 mois) |
| `03_MEDIUM_TERM.md` | Plan moyen terme (3-6 mois) |
| `04_LONG_TERM.md` | Plan long terme (6-12 mois) |
| `05_ARCHITECTURE.md` | Décisions architecturales |
| `/docs/adr/` | 6 ADRs documentés |
| `/docs/04_strategie_independance.md` | Stratégie serveur personnel |

---

## Principes directeurs

1. **Offline-first** : L'application doit fonctionner sans internet ✅
2. **Simplicité** : Pas de sur-engineering, fonctionnalités essentielles
3. **Résilience** : Toujours une solution de repli si Stokt disparaît ✅
4. **Itératif** : Livrer souvent, améliorer continuellement
5. **Testé** : Chaque fonctionnalité doit être couverte par des tests ✅

---

*Plan de développement mis à jour le 2025-12-31*
