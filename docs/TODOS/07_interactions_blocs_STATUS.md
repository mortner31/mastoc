# STATUS - TODO 07 : Interactions avec les Blocs

**Progression** : 15%

## Phase 1 : Investigation API ✅

- [x] Identifier tous les endpoints (analyse code décompilé)
- [x] Documenter les endpoints likes, comments, bookmarks, efforts
- [x] Identifier les données déjà disponibles dans Climb (compteurs)
- [ ] Tester les endpoints avec token réel

## Phase 2 : Lecture seule (0%)

- [ ] Afficher compteurs dans vue détail
- [ ] Implémenter `fetchLatestSends`
- [ ] Implémenter `fetchComments`
- [ ] UI pour liste ascensions
- [ ] UI pour liste commentaires

## Phase 3 : Actions utilisateur (0%)

- [ ] Like/unlike
- [ ] Bookmark toggle
- [ ] Poster commentaire

## Phase 4 : Mes données (0%)

- [ ] Mes favoris
- [ ] Mes likes
- [ ] Vue dédiée

## Notes

**Contrainte architecturale** : Chargement async obligatoire.
Les données sociales ne doivent jamais bloquer la navigation des blocs.

Endpoints confirmés par analyse du code décompilé (lignes 466084-467380) :
- Likes : `api/climbs/{id}/likes` (GET/POST/DELETE)
- Comments : `api/climbs/{id}/comments` (GET/POST), `/comments/{id}` (DELETE)
- Bookmarks : `api/climbs/{id}/bookmarked` (PATCH)
- Sends : `api/climbs/{id}/latest-sends` (GET)
