# Rapport de Session - TODO 07 Interactions Sociales

**Date** : 2025-12-22 (nuit 5)

## Objectifs Atteints

- API Client social : 10 méthodes ajoutées (sends, comments, likes, bookmarks)
- Modèles de données : `UserRef`, `Effort`, `Comment`, `Like`
- `SocialLoader` : chargement async avec cache TTL 5min
- `SocialActionsService` : actions like/bookmark async
- `SocialPanel` : widget Qt avec 3 onglets
- `MyClimbsPanel` : vue favoris/likes/ascensions
- Intégration dans `hold_selector.py` (mode parcours)
- 33 tests unitaires créés

## Résultats

| Métrique | Valeur |
|----------|--------|
| Tests ajoutés | 33 |
| Tests totaux | 170 |
| Fichiers créés | 6 |
| Fichiers modifiés | 4 |
| Endpoints API | 10 |

## Fichiers Créés

| Fichier | Description |
|---------|-------------|
| `core/social_loader.py` | Chargeur async avec cache |
| `core/social_actions.py` | Service actions (like, bookmark) |
| `gui/widgets/social_panel.py` | Panel affichage données sociales |
| `gui/widgets/my_climbs_panel.py` | Panel "Mes climbs" |
| `tools/test_social_endpoints.py` | Script test endpoints |
| `tests/test_social.py` | 33 tests unitaires |

## Fichiers Modifiés

| Fichier | Modifications |
|---------|---------------|
| `api/models.py` | +`UserRef`, `Effort`, `Comment`, `Like` |
| `api/client.py` | +10 méthodes sociales |
| `gui/widgets/climb_detail.py` | +compteurs, +SocialPanel |
| `gui/hold_selector.py` | +SocialLoader, +SocialPanel mode parcours |

## Bug Fix

- **Noms utilisateurs vides** : L'API utilise `effortBy` au lieu de `user` et `effortDate` au lieu de `date`. Corrigé dans `Effort.from_api()`.

## Architecture

```
API Response (latest-sends)
    |
    v
Effort.from_api() -- parse effortBy, effortDate
    |
    v
SocialLoader._fetch_social_data() -- async + cache
    |
    v
SocialPanel.set_data() -- affichage Qt
```

## Notes Techniques

- **Cache** : TTL 5 minutes, invalidation après action
- **Threading** : Toutes les requêtes API en thread séparé
- **Signaux Qt** : Découplage UI/API via pyqtSignal
- **Token** : Hardcodé temporairement (TODO: dialog login)

## Prochaines Etapes

- TODO 09 : Listes personnalisées (collections)
- TODO 10 : Interface création de blocs
