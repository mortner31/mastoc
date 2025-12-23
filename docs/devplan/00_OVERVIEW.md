# Plan de Développement mastoc - Vue d'ensemble

**Version** : 1.0
**Date** : 2025-12-23
**Statut** : Document de référence

---

## Vision du projet

**mastoc** est une application personnelle de gestion de blocs d'escalade, conçue en **offline-first**, avec comme objectifs :

1. **Visualisation interactive** des blocs sur images de murs
2. **Fonctionnement 100% hors-ligne**
3. **Indépendance progressive** de l'API Stokt
4. **Support multi-murs** (Montoboard + pan personnel)

---

## État actuel (Décembre 2025)

### Prototype Python fonctionnel

| Métrique | Valeur |
|----------|--------|
| Lignes de code | ~10 000 |
| Tests | 225 (passent) |
| Couverture modules | api, core, db, gui |
| Données | 1017 climbs, 776 prises |

### Fonctionnalités implémentées

- **Liste de blocs** avec filtres (grade, setter, texte)
- **Visualisation** sur image du mur avec polygones des prises
- **Sélection par prises** (recherche avancée)
- **Modes de coloration** (heatmaps, quantiles, rareté)
- **Création de blocs** (wizard multi-écrans, POST vers API)
- **Interactions sociales** (likes, comments, sends - lecture)
- **Synchronisation API** Stokt

### TODOs en cours

| TODO | Description | Progression |
|------|-------------|-------------|
| 09 | Listes Personnalisées | 5% |
| 10 | Création de Blocs | 97% |
| 12 | Hold Annotations | 0% |

---

## Axes stratégiques

### 1. Finalisation du prototype Python

Compléter les fonctionnalités restantes avant migration mobile :
- Création de blocs (TODO 10) - quasi terminé
- Hold Annotations (TODO 12) - crowdsourcing état des prises
- Listes personnalisées (TODO 09) - collections de blocs

### 2. Infrastructure indépendante

Déploiement d'un serveur personnel (Railway) pour :
- Résilience (backup des données Stokt)
- Fonctionnalités custom impossibles sur Stokt
- Support du pan personnel
- Hold annotations communautaires

### 3. Migration mobile Android

Portage vers application native Android :
- Stack : Kotlin + Jetpack Compose + Room
- Design : Material Design 3
- Architecture : MVVM + Clean Architecture

### 4. Écosystème complet

- Synchronisation bi-directionnelle
- Support multi-utilisateurs (grimpeurs locaux)
- Export/Import de données
- Statistiques avancées

---

## Horizon temporel

```
                     2025 Q4              2026 Q1              2026 Q2
                  ──────────────────  ──────────────────  ──────────────────
Court terme       │ TODO 10 finalisé │                   │                  │
(1-3 mois)        │ Serveur Railway  │                   │                  │
                  │ Hold Annotations │                   │                  │
                  ──────────────────────────────────────────────────────────
Moyen terme                          │ App Android MVP  │                  │
(3-6 mois)                           │ Sync bidirect.   │                  │
                                     │ Pan personnel    │                  │
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
| `/docs/04_strategie_independance.md` | Stratégie serveur personnel |
| `/docs/03_ergonomie_ui_ux.md` | Guide UX Android |

---

## Principes directeurs

1. **Offline-first** : L'application doit fonctionner sans internet
2. **Simplicité** : Pas de sur-engineering, fonctionnalités essentielles
3. **Résilience** : Toujours une solution de repli si Stokt disparaît
4. **Itératif** : Livrer souvent, améliorer continuellement
5. **Testé** : Chaque fonctionnalité doit être couverte par des tests

---

*Plan de développement créé le 2025-12-23*
