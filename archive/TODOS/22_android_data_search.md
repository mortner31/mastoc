# TODO 22 - Data & Recherche Android

## Objectif

Améliorer le chargement des données et le moteur de recherche de l'application Android.

## Tâches

### Phase 1 : Refonte UI Recherche

- [ ] Remplacer la barre de recherche textuelle par un cartouche de description des filtres actifs
- [ ] Clic sur le cartouche → déplie les filtres (même action que menu hamburger)
- [ ] Déplacer la recherche textuelle dans le panneau des filtres
- [ ] Ajouter un bouton "Appliquer" qui referme le panneau des filtres

### Phase 2 : Fix Filtre Grade

- [ ] Corriger le filtre par niveau (ne fonctionne pas actuellement)
- [ ] Utiliser la table FONT_GRADES du Python avec valeurs IRCRA correctes
- [ ] Implémenter la logique epsilon (grade_max = next_ircra - 0.01)

### Phase 3 : Filtre Setter Avancé

- [ ] Ajouter mode Include/Exclude pour les setters (comme Python)
- [ ] UI : ComboBox "Tous / Inclure / Exclure" + liste de checkboxes
- [ ] Afficher le nombre de climbs par setter

### Phase 4 : Serveur & Sync

- [ ] Déployer fix `date_created` → `created_at` sur Railway
- [ ] Re-sync données Stokt pour corriger les dates de création
- [ ] Vérifier que les dates s'affichent correctement

### Phase 5 : Lazy Loading

- [ ] Implémenter pagination infinie dans `ClimbListScreen`
- [ ] Charger page suivante quand on approche de la fin de la liste
- [ ] Indicateur de chargement en bas de liste
- [ ] Gérer le cache local avec les nouvelles pages

### Phase 6 : Rendu Visuel

- [ ] Ajouter lignes de prise de départ (tapes START)
- [ ] Vérifier rendu conforme au Python (climb_renderer.py)

### Phase 7 : Parcours Santé 25

- [ ] Analyser spécificité "parcours santé 25"
- [ ] Implémenter fonctionnalité circuit/parcours

## Références

- Python : `mastoc/src/mastoc/gui/widgets/level_slider.py` (FONT_GRADES)
- Python : `mastoc/src/mastoc/gui/hold_selector.py` (setter include/exclude)
- Python : `mastoc/src/mastoc/core/filters.py` (ClimbFilter)
- ADR 010 : Gestion des Gestes Zoom/Swipe
- TODO 21 : Conformité UX/Design Android
