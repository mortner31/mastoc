# STATUS - TODO 22 : Data & Recherche Android

**Progression** : 80%

## Phase 1 : Refonte UI Recherche (100%)

- [x] Cartouche description filtres actifs
- [x] Clic cartouche → déplie filtres
- [x] Recherche textuelle dans le panneau
- [x] Bouton "Appliquer"

## Phase 2 : Fix Filtre Grade (100%)

- [x] Corriger filtre niveau
- [x] Table FONT_GRADES avec IRCRA (`GradeUtils.kt`)
- [x] Logique epsilon (`getMaxIrcraForIndex`)

## Phase 3 : Filtre Setter Avancé (100%)

- [x] Mode Include/Exclude (`SetterFilterMode` enum)
- [x] UI ComboBox + checkboxes (`SetterFilterSection`)
- [x] Nombre de climbs par setter (`SetterInfo`)

## Phase 4 : Serveur & Sync (100%)

- [x] Fix dates `created_at` (1008 climbs corrigés)
- [x] Script SQL direct `fix_climb_dates_sql.py`
- [x] Endpoint bulk update `/api/climbs/bulk/dates`

## Phase 5 : Lazy Loading (0%)

- [ ] Pagination infinie ClimbListScreen
- [ ] Chargement page suivante
- [ ] Indicateur loading
- [ ] Cache local

## Phase 6 : Rendu Visuel (100%)

- [x] Lignes tapes START (serveur + Android)
- [x] Épaisseur tapes = contours (8px)
- [x] Dark mode + thème GRAY par défaut
- [x] Nouvelle icône app
- [x] Titre "Montoboard"

## Phase 7 : Parcours Santé 25 (0%)

- [ ] Analyse spécificité
- [ ] Fonctionnalité circuit

---

**Dernière mise à jour** : 2026-01-02
**Session** : Phases 4 et 6 complétées, reste Phase 5 (lazy loading) et Phase 7 (circuits)
