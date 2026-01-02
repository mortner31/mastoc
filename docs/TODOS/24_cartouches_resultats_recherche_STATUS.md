# STATUS - TODO 24 : Cartouches Résultats Recherche

**Progression** : 100%

## Phase 1 : Couleurs des Prises (100%)

- [x] `colorRgb: Int?` dans HoldEntity
- [x] `colorRgb: Int?` dans Hold (modèle domaine)
- [x] Mappers mis à jour
- [x] `HoldColorExtractor.kt` créé
- [x] Méthodes `updateHoldColor` dans HoldDao
- [x] Intégration dans ClimbRepository
- [x] Base de données version 3

## Phase 2 : Générateur Picto (100%)

- [x] `PictoGenerator.kt` (port de picto.py)
  - Calcul centroïde/rayon depuis polygone
  - Dessin Canvas (ellipses colorées)
  - Marqueurs TOP (double cercle), FEET (bleu), START (tapes)
  - Top 20 prises grises (contexte)
- [x] `PictoCache.kt`
  - LruCache mémoire (50 entrées)
  - Cache fichier PNG sur disque
  - Méthodes hasPicto/getPicto/savePicto
- [x] `PictoManager.kt`
  - Combine génération + cache
  - Méthode preloadPictos pour batch

## Phase 3 : Nouveau Layout ClimbCard (100%)

- [x] Layout Row 25% | 50% | 25%
- [x] Zone gauche : PictoZone avec Image composable
- [x] Zone centre : InfoZone (titre, auteur, date formatée)
- [x] Zone droite : StatsZone (GradeBadge, ❤️ likes, ✕ croix)
- [x] Placeholder quand pas de picto
- [x] Formatage date français ("15 déc. 2025")

## Phase 4 : Intégration ClimbListScreen (100%)

- [x] ClimbListViewModel + PictoManager
- [x] Cache holds par face (holdsMap)
- [x] Cache pictos (pictosCache)
- [x] Méthodes loadHoldsForFace / loadPictoForClimb
- [x] LaunchedEffect pour génération lazy au scroll
- [x] Passage du picto au ClimbCard

---

## Fichiers créés/modifiés

### Nouveaux fichiers
- `core/HoldColorExtractor.kt` : extraction couleurs depuis image mur
- `core/PictoGenerator.kt` : génération Bitmap picto
- `core/PictoCache.kt` : cache local des pictos
- `core/PictoManager.kt` : gestionnaire combiné

### Fichiers modifiés
- `data/local/HoldEntity.kt` : +colorRgb
- `data/local/HoldDao.kt` : +updateHoldColor, +getHoldsWithoutColor
- `data/local/MastocDatabase.kt` : version 3
- `data/model/Hold.kt` : +colorRgb
- `data/Mappers.kt` : colorRgb dans toDomain
- `data/repository/ClimbRepository.kt` : +extractHoldColors, +needsColorExtraction
- `ui/components/ClimbCard.kt` : nouveau layout avec picto
- `ui/screens/ClimbListScreen.kt` : intégration pictos lazy
- `viewmodel/ClimbListViewModel.kt` : +PictoManager, +holdsMap, +pictosCache
- Autres ViewModels : context passé au repository

---

## Build & Tests

```
BUILD SUCCESSFUL
Tests: PASSED
```

---

**Architecture** : 100% côté client (compatible Stokt + mastoc)
**Dernière mise à jour** : 2026-01-02
