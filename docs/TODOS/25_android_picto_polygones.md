# TODO 25 - Pictos polygonaux dans l'application Android

## Objectif

Intégrer le nouveau mode de rendu des pictos en polylignes dilatées dans l'application Android, avec les paramètres configurables par l'utilisateur.

## Configuration de référence (finalbest.json)

```json
{
  "background_color": [93, 93, 93],
  "use_polygon_shape": true,
  "polygon_dilation": 6.37,
  "polygon_fill_opacity": 0.46,
  "polygon_outline_opacity": 1.0,
  "polygon_outline_width": 5,
  "use_fixed_bounds": true
}
```

## Paramètres configurables par l'utilisateur

| Paramètre | Description | Valeur par défaut | Plage |
|-----------|-------------|-------------------|-------|
| `polygon_dilation` | Facteur de dilatation des polygones | 6.37 | 1.0 - 10.0 |
| `polygon_outline_width` | Épaisseur des contours | 5 | 0 - 20 |
| `background_color` | Couleur de fond (niveau de gris) | 93 | 0 - 255 |
| `polygon_fill_opacity` | Transparence du remplissage | 0.46 | 0.0 - 1.0 |

## Paramètres fixes (non configurables)

- `use_polygon_shape = true` (toujours actif)
- `polygon_outline_opacity = 1.0` (contour toujours opaque)
- `use_fixed_bounds = true` (cadre fixe)
- `top_marker_width = 0` (pas de marqueur TOP)
- `feet_width = 0` (pas de marqueur FEET)
- `tape_width = 1` (lignes de tape fines)
- Couleur du contour = couleur de la prise

## Tâches

### Phase 1 : Modèle de données

- [ ] Créer `PictoSettings` data class dans `data/model/`
  - `dilation: Float = 6.37f`
  - `outlineWidth: Int = 5`
  - `backgroundColor: Int = 93` (niveau de gris 0-255)
  - `fillOpacity: Float = 0.46f`

- [ ] Ajouter table `picto_settings` dans Room (ou SharedPreferences si simple)

### Phase 2 : Logique de rendu

- [ ] Créer `PictoRenderer.kt` dans `core/` ou `ui/components/`
  - Fonction `renderClimbPicto(climb, holds, settings): Bitmap`
  - Parser les polygones depuis `Hold.polygonStr`
  - Implémenter `dilatePolygon(points, factor, center)`
  - Dessiner avec `Canvas` :
    - Fond gris paramétrable
    - Polygones dilatés avec fill semi-transparent
    - Contours opaques (même couleur que la prise)

- [ ] Fonction `getHoldColor(hold, faceImage): Color`
  - Extraire la couleur dominante autour du centroïde
  - Utiliser `Palette` ou échantillonnage manuel

### Phase 3 : Interface utilisateur

**Wireframe section Pictos dans Settings :**

```
┌─────────────────────────────────────┐
│ 🎨 Pictos                           │
├─────────────────────────────────────┤
│ Dilatation          [====●=====] 6.4│
│ Épaisseur contour   [===●======]  5 │
│ Couleur fond        [==●=======] 93 │
│ Transparence        [====●=====] 46%│
├─────────────────────────────────────┤
│        ┌──────────────┐             │
│        │   Aperçu     │             │
│        │   en temps   │             │
│        │    réel      │             │
│        └──────────────┘             │
├─────────────────────────────────────┤
│  [🔄 Régénérer tous les pictos]     │
│  [↩️ Réinitialiser par défaut]      │
└─────────────────────────────────────┘
```

- [ ] Ajouter section "Pictos" dans `SettingsScreen.kt`
  - Titre de section avec icône
  - Slider "Dilatation" (1.0 - 10.0)
  - Slider "Épaisseur contour" (0 - 20)
  - Slider "Fond" (noir → blanc, 0-255)
  - Slider "Transparence" (0% - 100%)
  - Aperçu en temps réel (picto exemple qui se met à jour)

- [ ] Boutons d'action dans la section Pictos :
  - **"Régénérer tous les pictos"** : vide le cache et régénère
  - **"Réinitialiser par défaut"** : remet les valeurs par défaut

- [ ] Feedback utilisateur :
  - ProgressIndicator pendant la régénération
  - Snackbar "X pictos régénérés" à la fin

### Phase 4 : Intégration

- [ ] Modifier `ClimbCard.kt` pour utiliser `PictoRenderer`
- [ ] Mettre en cache les pictos générés (par climb_id + settings hash)
- [ ] Invalider le cache quand les settings changent

### Phase 5 : Optimisation

- [ ] Génération asynchrone des pictos (coroutines)
- [ ] Placeholder pendant le chargement
- [ ] Limiter la taille du cache (LRU)

## Fichiers concernés

### À créer
- `android/app/src/main/java/com/mastoc/app/core/PictoRenderer.kt`
- `android/app/src/main/java/com/mastoc/app/data/model/PictoSettings.kt`

### À modifier
- `android/app/src/main/java/com/mastoc/app/ui/screens/SettingsScreen.kt`
- `android/app/src/main/java/com/mastoc/app/ui/components/ClimbCard.kt`
- `android/app/src/main/java/com/mastoc/app/data/local/MastocDatabase.kt` (si Room)

## Références

- Config Python : `/home/mortner/mastock/data/pictos/finalbest.json`
- Implémentation Python : `/mastoc/src/mastoc/core/picto.py`
  - `dilate_polygon()` : ligne 289
  - `get_hold_polygon_scaled()` : ligne 329
  - `generate_climb_picto()` : ligne 448

## Notes techniques

### Dilatation de polygone
```kotlin
fun dilatePolygon(points: List<PointF>, factor: Float): List<PointF> {
    val cx = points.map { it.x }.average().toFloat()
    val cy = points.map { it.y }.average().toFloat()
    return points.map { p ->
        PointF(
            cx + (p.x - cx) * factor,
            cy + (p.y - cy) * factor
        )
    }
}
```

### Rendu Canvas
```kotlin
// Fond
canvas.drawColor(Color.rgb(bg, bg, bg))

// Polygone avec transparence
val fillPaint = Paint().apply {
    color = holdColor
    alpha = (fillOpacity * 255).toInt()
    style = Paint.Style.FILL
}
canvas.drawPath(polygonPath, fillPaint)

// Contour opaque
val strokePaint = Paint().apply {
    color = holdColor
    style = Paint.Style.STROKE
    strokeWidth = outlineWidth.toFloat()
}
canvas.drawPath(polygonPath, strokePaint)
```
