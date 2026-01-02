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
- [x] **Appel extraction dans loadHoldsForFaceAsync**
- [x] **Image chargée en taille originale (Coil)**

## Phase 2 : Générateur Picto (100%)

- [x] `PictoGenerator.kt` (port de picto.py)
  - Calcul centroïde/rayon depuis polygone
  - Dessin Canvas (ellipses colorées)
  - Marqueurs TOP (double cercle), FEET (bleu), START (tapes)
  - Top 20 prises grises (contexte)
  - **Marge réduite à 2%**
- [x] `PictoCache.kt`
  - LruCache mémoire (50 entrées)
  - Cache fichier PNG sur disque
  - Méthodes hasPicto/getPicto/savePicto
- [x] `PictoManager.kt`
  - Combine génération + cache
  - Méthode preloadPictos pour batch
  - **+regeneratePicto() pour regénération**

## Phase 3 : Nouveau Layout ClimbCard (100%)

- [x] Layout Row 25% | 50% | 25%
- [x] Zone gauche : PictoZone avec Image composable
- [x] Zone centre : InfoZone (titre, auteur, date formatée)
- [x] Zone droite : StatsZone (GradeBadge, likes, croix)
- [x] Placeholder quand pas de picto
- [x] Formatage date français ("15 déc. 2025")
- [x] **fillMaxSize + FillBounds (remplit le cadre)**

## Phase 4 : Intégration ClimbListScreen (100%)

- [x] ClimbListViewModel + PictoManager
- [x] Cache holds par face (holdsMap)
- [x] Cache pictos (pictosCache)
- [x] Méthodes loadHoldsForFace / loadPictoForClimb
- [x] LaunchedEffect pour génération lazy au scroll
- [x] Passage du picto au ClimbCard
- [x] **computeTopHoldsForFace / getTopHoldsForFace**
- [x] **Extraction couleurs automatique si manquantes**

## Phase 5 : SettingsScreen (100%)

- [x] Sections dépliables avec animation
- [x] Section Thème de couleurs
- [x] Section Cache et pictos (stats + regénérer)
- [x] Section Apparence des blocs (rendu)
- [x] Section À propos

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
- `ui/components/ClimbCard.kt` : nouveau layout avec picto, fillMaxSize
- `ui/screens/ClimbListScreen.kt` : intégration pictos lazy
- `ui/screens/SettingsScreen.kt` : sections dépliables
- `viewmodel/ClimbListViewModel.kt` : +PictoManager, +holdsMap, +pictosCache, +topHolds

---

**Architecture** : 100% côté client (compatible Stokt + mastoc)
**Dernière mise à jour** : 2026-01-02
