# Rapport de Session - Analyse Profonde du Plan de Développement

**Date** : 2025-12-30

## Objectifs de la Session

- Analyser en profondeur le plan de développement mastoc
- Évaluer l'écart entre documentation et implémentation
- Vérifier la compatibilité de l'architecture pour la synchronisation
- Produire des recommandations actionnables

---

## Méthodologie

Analyse multi-agents en parallèle :
1. **Agent 1** : Exploration des documents de planification (`/docs/devplan/`, stratégie)
2. **Agent 2** : Exploration de l'implémentation (`/mastoc/src/`, `/server/`)
3. **Agent 3** : État des TODOs et progression (`/docs/TODOS/`, `/archive/`)

---

## Résultats de l'Analyse

### 1. État Global du Projet

| Métrique | Valeur |
|----------|--------|
| Lignes de code (client) | ~10,000 |
| Lignes de code (serveur) | ~1,069 |
| Tests | 225 |
| TODOs actifs | 13 |
| TODOs archivés | 3 |
| Climbs en base | 1,017 |
| Holds mappées | 776 |

### 2. Comparaison Documentation vs Implémentation

| Composant | Documentation | Code | Statut |
|-----------|---------------|------|--------|
| Client mastoc (GUI) | Complet | 97% | Aligné |
| API Stokt | Complet | 100% (856 LOC) | Aligné |
| Sync download | Complet | 100% | Aligné |
| Serveur Railway | Complet (780 lignes spec) | 40% | **GAP** |
| Backend Switch | Pseudo-code détaillé | 0% | **GAP** |
| Railway Client | Interface définie | 0% | **GAP** |
| Sync push | Design complet | 0% | **GAP** |
| Mapping stokt_id | Tables SQL définies | Absent du SQLite | **GAP** |
| Images dupliquées | Marqué CRITIQUE | Non implémenté | **GAP** |

### 3. Analyse des Dépendances et Blocages

```
TODO 13 (Serveur Railway) ──── 40% ────┐
                                       │
    ┌──────────────────────────────────┘
    │
    ├──► TODO 12 (Hold Annotations) ── 0% (BLOQUÉ)
    │
    ├──► Sync bidirectionnelle ── 0% (BLOQUÉ)
    │
    └──► Android MVP ── 0% (BLOQUÉ)
```

**Conclusion** : TODO 13 est le goulot d'étranglement critique.

### 4. État du Serveur `/server/`

```
server/
├── pyproject.toml        ✅ Complet
├── README.md             ✅ Documenté
├── Procfile              ✅ Railway-ready
├── src/mastoc_api/
│   ├── main.py           ✅ Complet (non testé)
│   ├── config.py         ✅ Pydantic settings
│   ├── database.py       ✅ SQLAlchemy engine
│   ├── models/           ✅ 7 modèles avec stokt_id
│   │   ├── gym.py
│   │   ├── face.py
│   │   ├── hold.py
│   │   ├── climb.py
│   │   ├── user.py
│   │   └── mapping.py
│   └── routers/          ⚠️ Squelettes incomplets
│       ├── health.py     ✅ Fonctionnel
│       ├── climbs.py     ⚠️ CRUD partiel
│       ├── holds.py      ⚠️ GET only
│       └── sync.py       ⚠️ Non implémenté
```

**Manquant** :
- [ ] Logique métier dans les routers
- [ ] Script `init_from_stokt.py`
- [ ] Tests unitaires
- [ ] Déploiement Railway

### 5. Problème de Schéma SQLite

Le schéma SQLite actuel (`/mastoc/data/mastoc.db`) ne contient **pas** les champs `stokt_id` :

**Schéma actuel** :
```sql
CREATE TABLE climbs (
    id TEXT PRIMARY KEY,
    name TEXT,
    holds_list TEXT,
    grade_font TEXT,
    -- ... pas de stokt_id
);
```

**Schéma requis** (selon `04_strategie_independance.md`) :
```sql
CREATE TABLE climbs (
    id UUID PRIMARY KEY,
    stokt_id UUID UNIQUE,        -- ← MANQUANT
    source TEXT DEFAULT 'mastoc', -- ← MANQUANT
    synced_at TIMESTAMP,          -- ← MANQUANT
    -- ...
);
```

**Impact** : Migration de données nécessaire avant intégration Railway.

---

## Question Architecturale : Visualisation Simultanée

### Demande Utilisateur
> "Si j'ai deux identifiants (mastoc et stokt), est-ce que je pourrais voir les blocs des deux en même temps ?"

### Réponse
L'architecture actuelle (Railway-First single-source) ne permet **pas** l'affichage simultané.

### Solution Retenue
**Vue Comparaison Ponctuelle** (Sync Preview) - Ajoutée comme évolution future :
- Fetch Stokt à la demande (pas permanent)
- Comparaison via `stokt_id` comme clé de jointure
- Affichage des états : Local / Synchronisé / À importer / Conflit
- Actions : Importer, Pousser, Ignorer

**Priorité** : Basse (après Phase 3 - Synchronisation de base)

Cette fonctionnalité a été documentée dans `docs/04_strategie_independance.md`.

---

## Risques Identifiés

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Retard Android MVP | Élevée | Critique | Prioriser TODO 13 |
| Perte images Stokt | Moyenne | Critique | Dupliquer sur Railway |
| Migration DB douloureuse | Moyenne | Élevé | Migrer maintenant |
| Scope creep | Élevée | Moyen | Focus sur chemin critique |
| Serveur non testé | Élevée | Moyen | Tests avant déploiement |

---

## Recommandations

### Priorité 1 : Débloquer TODO 13 (Cette semaine)

| Action | Effort | Impact |
|--------|--------|--------|
| Compléter routers (CRUD fonctionnel) | 4h | Élevé |
| Ajouter tests minimaux | 2h | Moyen |
| Tester localement (Docker PostgreSQL) | 1h | Élevé |
| Déployer sur Railway | 2h | Critique |

### Priorité 2 : Préparer l'Intégration (Semaine prochaine)

| Action | Effort | Impact |
|--------|--------|--------|
| Migration SQLite (ajouter stokt_id) | 3h | Critique |
| Créer `RailwayAPI` client | 4h | Élevé |
| Implémenter `BackendSwitch` | 3h | Élevé |
| Script `init_from_stokt.py` | 4h | Élevé |

### Priorité 3 : Sécuriser l'Indépendance (2 semaines)

| Action | Effort | Impact |
|--------|--------|--------|
| Dupliquer images sur Railway | 2h | Critique |
| Implémenter sync push | 4h | Élevé |
| Tester cycle complet (import/export) | 2h | Élevé |

### Décisions Prises

| Question | Décision | Justification |
|----------|----------|---------------|
| Hébergement images | Railway (volume) | Simplicité, coût inclus |
| Test serveur | Docker local d'abord | Évite déploiements cassés |
| Migration SQLite | Maintenant | Évite dette technique |
| Vue comparaison | Évolution future | Pas critique pour MVP |

---

## Modifications Effectuées

1. **`docs/04_strategie_independance.md`** - Ajout de :
   - Ligne dans "Décisions Ouvertes" pour vue comparaison
   - Nouvelle section "Évolutions Futures" avec Sync Preview
   - Note de mise à jour

---

## Prochaines Étapes

### Immédiat
1. [ ] Compléter les routers du serveur Railway
2. [ ] Tester localement avec Docker PostgreSQL
3. [ ] Déployer sur Railway

### Court Terme
4. [ ] Migrer schéma SQLite (ajouter stokt_id)
5. [ ] Créer client RailwayAPI
6. [ ] Implémenter BackendSwitch
7. [ ] Dupliquer images sur Railway

### Moyen Terme
8. [ ] Débloquer TODO 12 (Hold Annotations)
9. [ ] Préparer migration Android
10. [ ] Implémenter sync bidirectionnelle

---

## Métriques de Succès

| Critère | Cible | Actuel |
|---------|-------|--------|
| Serveur Railway opérationnel | 100% | 40% |
| Tests serveur | >20 | 0 |
| Latence API | <200ms | N/A |
| Coût mensuel Railway | <$15 | N/A |
| Images dupliquées | 100% | 0% |

---

## Annexes

### Agents Utilisés
- `a007d13` : Exploration documentation devplan
- `ad7371a` : Exploration implémentation mastoc
- `a32672e` : Exploration TODOs et serveur

### Documents de Référence
- `/docs/04_strategie_independance.md` - Architecture Railway-First
- `/docs/devplan/00_OVERVIEW.md` - Vision globale
- `/docs/devplan/02_SHORT_TERM.md` - Plan court terme
- `/docs/backend_spec.md` - Spécification API indépendante

---

*Rapport généré le 2025-12-30*
*Durée de session : ~30 minutes*
