# Plan de Développement mastoc - Vue d'ensemble

**Version** : 3.0
**Date** : 2026-01-01
**Statut** : Document de référence (mis à jour post-TODO 19, pré-Android)

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
| Lignes de code | ~15 000 |
| Tests | **375+** (passent) |
| ADRs | 8 |
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
| **20** | **App Android Kotlin (Lecture Seule)** | **0% - PRIORITÉ** |
| 09 | Listes Personnalisées | 70% - API OK |
| ~~12~~ | ~~Hold Annotations~~ | ✅ 95% Archivé |
| ~~15~~ | ~~Sync Incrémentale~~ | ✅ Archivé |
| ~~16~~ | ~~Dashboard Sync~~ | ✅ Archivé |
| ~~17~~ | ~~Authentification & Users~~ | ✅ Archivé |
| ~~18~~ | ~~Sync Données Sociales~~ | ✅ Archivé |
| ~~19~~ | ~~Renforcement Tests~~ | ✅ Archivé |

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

### 2. ✅ Optimisation et authentification - COMPLÉTÉ

- **TODO 15** : Sync incrémentale ✅ (gain ~99% bande passante)
- **TODO 17** : Authentification JWT ✅
- **TODO 12** : Hold Annotations ✅ (95%)
- **TODO 18** : Sync Données Sociales ✅

### 3. Migration mobile Android (Priorité actuelle)

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
Court terme       │ ✅ TODO 10-19    │ TODO 20 Android  │                  │
(1-3 mois)        │ ✅ Serveur Rail. │ Kotlin Lecture   │                  │
                  │ ✅ Auth+Sync+Ann │ Seule            │                  │
                  ──────────────────────────────────────────────────────────
Moyen terme                          │ Android écriture │ Sync bidirect.   │
(3-6 mois)                           │ Auth Android     │ Pan personnel    │
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

*Plan de développement mis à jour le 2026-01-01*
