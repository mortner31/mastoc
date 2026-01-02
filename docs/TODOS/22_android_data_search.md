# TODO 22 - Data & Recherche Android

## Objectif

Améliorer le chargement des données et le moteur de recherche de l'application Android.

## Tâches

### Phase 1 : Serveur & Sync

- [ ] Déployer fix `date_created` → `created_at` sur Railway
- [ ] Re-sync données Stokt pour corriger les dates de création
- [ ] Vérifier que les dates s'affichent correctement

### Phase 2 : Lazy Loading

- [ ] Implémenter pagination infinie dans `ClimbListScreen`
- [ ] Charger page suivante quand on approche de la fin de la liste
- [ ] Indicateur de chargement en bas de liste
- [ ] Gérer le cache local avec les nouvelles pages

### Phase 3 : Moteur de Recherche

- [ ] Analyser les problèmes actuels du moteur de recherche
- [ ] Améliorer les filtres (grade, setter, date, etc.)
- [ ] Recherche par nom plus intuitive
- [ ] Recherche par prises (intégration HoldSelector)
- [ ] Tri des résultats (date, grade, popularité)

### Phase 4 : Rendu Visuel

- [ ] Ajouter lignes de prise de départ (tapes START)
- [ ] Vérifier rendu conforme au Python (climb_renderer.py)

### Phase 5 : Parcours Santé 25

- [ ] Analyser spécificité "parcours santé 25"
- [ ] Implémenter fonctionnalité circuit/parcours

## Références

- ADR 010 : Gestion des Gestes Zoom/Swipe
- TODO 21 : Conformité UX/Design Android
