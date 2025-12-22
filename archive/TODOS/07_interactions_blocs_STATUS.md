# STATUS - TODO 07 : Interactions avec les Blocs

**Progression** : 100%

## Phase 1 : Investigation API ✅

- [x] Identifier tous les endpoints (analyse code décompilé)
- [x] Documenter les endpoints likes, comments, bookmarks, efforts
- [x] Identifier les données déjà disponibles dans Climb (compteurs)
- [x] Tester les endpoints avec token réel

## Phase 1.5 : Implémentation API Client ✅

- [x] Dataclasses : `UserRef`, `Effort`, `Comment`, `Like` dans models.py
- [x] Méthodes API dans client.py :
  - `get_climb_sends()` - ascensions récentes
  - `get_climb_comments()` - commentaires
  - `get_climb_likes()` - likes
  - `like_climb()` / `unlike_climb()` - toggle like
  - `post_comment()` / `delete_comment()` - gestion commentaires
  - `bookmark_climb()` - toggle favori
  - `get_my_bookmarked_climbs()` - mes favoris
  - `get_my_liked_climbs()` - mes likes
  - `get_crowd_grades()` - notes communauté
- [x] Tests endpoints : tous fonctionnels (5/5)

## Phase 2 : Lecture seule ✅

- [x] Afficher compteurs dans vue détail (👤 ascensions, ❤ likes, 💬 comments)
- [x] `SocialLoader` : chargement async avec cache TTL 5min
- [x] `SocialPanel` : widget onglets (Ascensions/Commentaires/Likes)
- [x] Intégration dans `ClimbDetailWidget`

## Phase 3 : Actions utilisateur ✅

- [x] `SocialActionsService` : service pour actions async
- [x] Toggle like (async avec callback)
- [x] Toggle bookmark (async avec callback)
- [x] Post comment (async)
- [x] Signaux `like_toggled` et `bookmark_toggled` dans ClimbDetailWidget

## Phase 4 : Mes données ✅

- [x] `MyClimbsPanel` : vue mes favoris/likes/ascensions
- [x] Onglets : ⭐ Favoris | ❤ Likes | 👤 Ascensions
- [x] Double-click → sélection climb
- [x] Bouton rafraîchir

## Phase 5 : Tests et intégration ✅

- [x] Tests unitaires pour SocialLoader (9 tests)
- [x] Tests unitaires pour SocialActionsService (11 tests)
- [x] Tests unitaires pour modèles (UserRef, Effort, Comment, Like) (9 tests)
- [x] Intégration SocialPanel dans hold_selector.py

## Fichiers créés

| Fichier | Description |
|---------|-------------|
| `core/social_loader.py` | Chargeur async avec cache |
| `core/social_actions.py` | Service actions (like, bookmark, comment) |
| `gui/widgets/social_panel.py` | Panel affichage données sociales |
| `gui/widgets/my_climbs_panel.py` | Panel "Mes climbs" (favoris, likes, sends) |
| `tools/test_social_endpoints.py` | Script de test des endpoints |
| `tests/test_social.py` | 33 tests unitaires pour modules sociaux |

## Fichiers modifiés

| Fichier | Modifications |
|---------|---------------|
| `api/models.py` | +`UserRef`, `Effort`, `Comment`, `Like` |
| `api/client.py` | +10 méthodes sociales |
| `gui/widgets/climb_detail.py` | +compteurs, +SocialPanel, +signaux |
| `gui/hold_selector.py` | +SocialLoader, +SocialPanel en mode parcours |

## Notes

- **Cache** : TTL 5 minutes, invalidation après action
- **Architecture** : Signaux Qt pour découplage UI/API
- **Async** : Toutes les actions réseau en thread séparé
