# STATUS - TODO 09 : Listes Personnalisées

**Progression** : 70%

## Phase 0 : Investigation API (100%)

- [x] Identifier tous les endpoints (analyse code décompilé)
- [x] Documenter 25 endpoints découverts
- [x] Identifier 18 fonctions JavaScript correspondantes
- [x] Documenter structure ClimbList (champs confirmés)
- [x] Documenter paramètres de filtrage fetchListItems
- [x] Mettre à jour 03_ENDPOINTS.md

## Phase 0.5 : Implémentation Code (100%)

- [x] Créer modèle ClimbList dans models.py
- [x] Créer modèle ListItem dans models.py
- [x] Ajouter get_user_lists() dans client.py
- [x] Ajouter get_lists() dans client.py
- [x] Ajouter get_list() dans client.py
- [x] Ajouter get_list_items() dans client.py
- [x] Ajouter get_my_set_climbs() dans client.py
- [x] Ajouter create_list() dans client.py
- [x] Ajouter update_list() dans client.py
- [x] Ajouter delete_list() dans client.py
- [x] Ajouter add_climb_to_list() dans client.py
- [x] Ajouter remove_climb_from_list() dans client.py
- [x] Ajouter follow_list() dans client.py
- [x] Ajouter unfollow_list() dans client.py
- [x] Ajouter get_gym_lists() dans client.py
- [x] Tests passent (224/225)

## Phase 1 : Lecture seule (100%)

- [x] Tester get_user_lists() - 3 listes personnelles
- [x] Tester get_gym_lists() - 45 listes populaires
- [x] Tester get_list() - détail liste
- [x] Tester get_list_items() - items de liste
- [x] Tester get_my_set_climbs() - 4 climbs créés
- [x] Tester get_my_sent_climbs() - 3 climbs envoyés
- [x] UI "Mes listes" (MyListsPanel widget)

## Phase 2 : Gestion de listes (0%)

- [ ] Créer liste (`POST api/users/{userId}/lists`)
- [ ] Modifier liste (`PATCH api/lists/{listId}`)
- [ ] Supprimer liste (`DELETE api/lists/{listId}`)
- [ ] UI création/édition

## Phase 3 : Gestion des items (0%)

- [ ] Ajouter climb (`POST api/lists/{listId}/items`)
- [ ] Retirer climb (`DELETE api/lists/{listId}/items/{itemId}`)
- [ ] Réordonner (`POST api/gyms/{gymId}/lists/control`)
- [ ] UI drag & drop

## Phase 4 : Social (0%)

- [ ] Suivre liste (`POST api/lists/{listId}/follow`)
- [ ] Ne plus suivre (`DELETE api/lists/{listId}/follow`)
- [ ] Listes populaires du gym
- [ ] URL de partage (`GET api/users/lists/{id}/expo-share-list-url`)

## Notes

### Analyse complète terminée (2025-12-23)

**25 endpoints identifiés** dans le code décompilé (lignes 443947-460239)

**18 fonctions JavaScript** documentées :
- fetchUserLists, fetchLists, fetchList, fetchListItems
- postList, patchList, deleteList (CRUD listes)
- postClimbToList, deleteListItem (gestion items)
- postFollowList, deleteFollowList (suivi)

**Structure ClimbList confirmée** :
- id, name, list_type, gym, user
- climbs_count, is_following
- image, image_thumbnail

**Filtres fetchListItems** :
- page_size, exclude_mine, grade_from, grade_to
- ordering, tags, search, show_circuit_only

### UI "Mes listes" (2025-12-23)

**Widget MyListsPanel créé** (`gui/widgets/my_lists_panel.py`) :
- Onglet "Mes listes" : listes personnelles de l'utilisateur
- Onglet "Populaires" : listes du gym
- Affichage des items (climbs) d'une liste sélectionnée
- Double-clic sur un climb pour l'afficher dans le viewer

**Intégration app.py** :
- Nouvel onglet "Listes" dans le panneau gauche
- Rafraîchissement automatique au changement d'onglet
- Mise à jour du user_id après connexion
