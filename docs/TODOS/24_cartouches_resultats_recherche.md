# TODO 24 - Cartouches de Résultats de Recherche

## Objectif

Refonte des cartes de résultat (ClimbCard) avec un nouveau layout intégrant les pictos générés côté client.

## Design

```
┌─────────────────────────────────────────────────────┐
│ ┌──────────┐  ┌──────────────────┐  ┌────────────┐ │
│ │          │  │ Nom du bloc      │  │    6A+     │ │
│ │  PICTO   │  │ par Mathias      │  │            │ │
│ │  (carré) │  │ 15 déc. 2025     │  │ ❤️12  ✕42  │ │
│ └──────────┘  └──────────────────┘  └────────────┘ │
│    25%              50%                 25%        │
└─────────────────────────────────────────────────────┘
```

### Zones

| Zone | Largeur | Contenu |
|------|---------|---------|
| Gauche | 25% | Picto carré du bloc (miniature) |
| Centre | 50% | Titre (bold), Auteur, Date (de haut en bas) |
| Droite | 25% | Grade (haut), Stats (bas) |

### Stats (zone droite bas)

- `❤️ N` : nombre de likes (total_likes)
- `✕ N` : nombre de croix / ascensions (climbed_by)

## Algorithme Picto (implémenté en Kotlin)

Le picto est généré dans `core/PictoGenerator.kt` (port de `picto.py`) :

1. **Fond blanc** carré (128x128 par défaut)
2. **Top 20 prises populaires** en gris clair (contexte)
3. **Prises du bloc** avec couleur dominante extraite du mur
4. **Marqueurs spéciaux** :
   - TOP : double cercle
   - FEET : contour bleu néon (#31DAFF)
   - START : lignes de tape (V si 1 prise, centrales si plusieurs)
5. **Calcul taille** : rayon proportionnel à l'aire du polygone

### Extraction de couleur

La couleur de chaque prise est extraite via `HoldColorExtractor.kt` :

```kotlin
// Sample pixels autour du centroïde (rayon 15, pas de 3)
// Ignore les pixels gris (max_diff < 30)
// Quantifie les couleurs (pas de 32)
// Retourne la couleur la plus fréquente
```

**Architecture** : Génération 100% côté CLIENT (Android)

Avantages :
- Calcul très léger (~1-5 ms par picto)
- Compatible avec les deux backends (Stokt ET mastoc)
- Pas de dépendance réseau supplémentaire
- Cache local (mémoire + disque)

## Tâches

### Phase 1 : Couleurs des Prises (100%)

- [x] Ajouter `colorRgb: Int?` à `HoldEntity` (Room)
- [x] Créer `HoldColorExtractor.kt` :
  - Charger image mur (via Coil)
  - Pour chaque hold : `extractDominantColor(bitmap, hold)`
  - Ignorer pixels gris, quantifier, retourner majoritaire
- [x] Persister en Room (update HoldEntity)
- [x] Méthodes dans ClimbRepository

### Phase 2 : Générateur Picto Android (100%)

- [x] Créer `PictoGenerator.kt` (port de `picto.py`)
  - Calcul centroïde/rayon depuis polygone
  - Dessin Canvas (ellipses colorées)
  - Marqueurs TOP (double cercle), FEET (bleu), START (tapes)
- [x] Top 20 prises populaires en gris (contexte)
- [x] Créer `PictoCache.kt` :
  - Stockage fichiers PNG : `cacheDir/pictos/{climbId}.png`
  - `hasPicto(climbId)` / `getPicto(climbId)` / `savePicto(climbId, bitmap)`
  - LruCache mémoire (50 entrées) pour accès rapide
- [x] Créer `PictoManager.kt` (combine génération + cache)

### Phase 3 : Nouveau Layout ClimbCard (100%)

- [x] Refactorer `ClimbCard.kt` avec layout Row (25|50|25)
- [x] Zone gauche : `Image` composable avec Bitmap du picto
- [x] Zone centre : Column(titre, auteur, date formatée)
- [x] Zone droite : Column(GradeBadge, Row(❤️ likes, ✕ croix))
- [x] Placeholder quand pas de picto

### Phase 4 : Tests et Polish (À faire)

- [ ] Tests unitaires `PictoGenerator`
- [ ] Tests `HoldColorExtractor`
- [ ] Gestion cas limites (climb sans prises, couleur manquante)
- [ ] Intégration dans ClimbListScreen (génération lazy des pictos au scroll)

## Fichiers impactés

### Android - Nouveaux fichiers
- `core/HoldColorExtractor.kt` : extraction couleurs depuis image mur
- `core/PictoGenerator.kt` : génération Bitmap picto
- `core/PictoCache.kt` : cache local des pictos
- `core/PictoManager.kt` : gestionnaire combiné

### Android - Fichiers modifiés
- `data/local/HoldEntity.kt` : +colorRgb
- `data/local/HoldDao.kt` : +updateHoldColor, +getHoldsWithoutColor
- `data/local/MastocDatabase.kt` : version 3
- `data/model/Hold.kt` : +colorRgb
- `data/Mappers.kt` : colorRgb dans toDomain
- `data/repository/ClimbRepository.kt` : +extractHoldColors, +needsColorExtraction
- `ui/components/ClimbCard.kt` : nouveau layout avec picto
- `viewmodel/*.kt` : context passé au repository

### Python (référence seulement)
- `mastoc/src/mastoc/core/picto.py` : logique portée en Kotlin

## Références

- TODO 22 Phase 1 : Cartouche filtres (déjà implémentée)
- `picto.py` : algorithme de génération Python (source)
