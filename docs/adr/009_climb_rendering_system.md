# ADR 009 - Système de Rendu des Blocs (Climb Rendering)

**Date** : 2026-01-01
**Statut** : Accepté

## Contexte

L'affichage d'un bloc sur l'image du mur nécessite un rendu visuel qui :
- Met en évidence les prises du bloc sur le fond
- Distingue les types de prises (START, TOP, FEET, OTHER)
- Permet à l'utilisateur de personnaliser l'affichage
- Fonctionne de manière identique sur Python (desktop) et Kotlin (Android)

Le prototype Python (`climb_renderer.py`) a établi un rendu efficace qui doit être reproduit fidèlement sur Android.

## Décision

Adopter un **système de rendu en 3 couches** avec des **paramètres unifiés** entre Python et Kotlin :

### Architecture 3 couches

```
┌─────────────────────────────────────┐
│ Couche 3 : Contours (Canvas)        │  ← Contours blancs/cyan
├─────────────────────────────────────┤
│ Couche 2 : Prises couleur (Clip)    │  ← Image originale clippée
├─────────────────────────────────────┤
│ Couche 1 : Fond grisé (Image)       │  ← Image filtrée
└─────────────────────────────────────┘
```

### Paramètres de rendu unifiés

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `grayLevel` | Float | 0.85 | Désaturation du fond (0=couleur, 1=gris) |
| `brightness` | Float | 0.25 | Luminosité du fond (0=noir, 1=original) |
| `contourWidth` | Int | 8 | Épaisseur des contours en pixels |
| `holdsInColor` | Bool | true | Prises en couleur originale (masque) |
| `showImage` | Bool | true | Afficher l'image de fond |

### Couleurs des contours par type

| HoldType | Couleur | Code |
|----------|---------|------|
| START | Blanc + Tape | `#FFFFFF` + lignes |
| TOP | Blanc + Double contour | `#FFFFFF` (dilaté) |
| FEET | Cyan (Neon Blue) | `#31DAFF` |
| OTHER | Blanc | `#FFFFFF` |

## Conséquences

### Positives
- Rendu identique entre Python et Android
- Paramètres persistés (DataStore/Settings)
- Personnalisation utilisateur via BottomSheet
- Prises visuellement distinctes du fond

### Négatives
- Double chargement image sur Android (fond + masque)
- Calcul du Path de clip à chaque changement de climb

## Implémentation

### Python (`climb_renderer.py`)

```python
def render_climb(
    img: Image.Image,
    climb: Climb,
    holds_map: dict[int, Hold],
    gray_level: float = 0.85,
    brightness: float = 0.25,
    contour_width: int = 8,
) -> np.ndarray:
    # 1. Fond grisé + assombri
    img_gray = img.convert('L').convert('RGB')
    img_blend = Image.blend(img, img_gray, gray_level)
    enhancer = ImageEnhance.Brightness(img_blend)
    img_blend = enhancer.enhance(brightness)

    # 2. Masque pour les prises (zones en couleur originale)
    mask = Image.new('L', img.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    for ch in climb.get_holds():
        hold = holds_map.get(ch.hold_id)
        points = parse_polygon_points(hold.polygon_str)
        mask_draw.polygon(points, fill=255)

    # 3. Composite : prises en couleur, reste grisé
    result = Image.composite(img, img_blend, mask)

    # 4. Contours sur couche transparente
    contours = Image.new('RGBA', img.size, (0, 0, 0, 0))
    contour_draw = ImageDraw.Draw(contours)
    for ch in climb.get_holds():
        color = NEON_BLUE if ch.hold_type == HoldType.FEET else WHITE
        contour_draw.polygon(points, outline=color, width=contour_width)

        if ch.hold_type == HoldType.TOP:
            # Double contour dilaté
            expanded = dilate_polygon(points, hold.centroid, 1.35)
            contour_draw.polygon(expanded, outline=WHITE, width=contour_width)

    result = Image.alpha_composite(result.convert('RGBA'), contours)
    return np.array(result)
```

### Kotlin (`ClimbDetailScreen.kt`)

```kotlin
@Composable
fun WallImageWithClimbOverlay(
    pictureUrl: String,
    climb: Climb,
    holdsMap: Map<Int, Hold>,
    renderSettings: RenderSettings
) {
    Box {
        // Couche 1 : Image de fond (grisée + assombrie)
        AsyncImage(
            model = pictureUrl,
            colorFilter = createBackgroundColorFilter(
                renderSettings.grayLevel,
                renderSettings.brightness
            )
        )

        // Couche 2 : Prises en couleur originale (clippées)
        if (renderSettings.holdsInColor) {
            val clipPath = createHoldsClipPath(climb, holdsMap, scaleX, scaleY)
            AsyncImage(
                model = pictureUrl,
                modifier = Modifier.clipToHoldsPath(clipPath)
            )
        }

        // Couche 3 : Contours
        ClimbHoldOverlay(
            climb = climb,
            holdsMap = holdsMap,
            contourWidth = renderSettings.contourWidth.toFloat()
        )
    }
}

// ColorFilter combinant saturation + luminosité
fun createBackgroundColorFilter(grayLevel: Float, brightness: Float): ColorFilter {
    val saturationMatrix = ColorMatrix().apply {
        setToSaturation(1f - grayLevel)
    }
    val brightnessMatrix = ColorMatrix(floatArrayOf(
        brightness, 0f, 0f, 0f, 0f,
        0f, brightness, 0f, 0f, 0f,
        0f, 0f, brightness, 0f, 0f,
        0f, 0f, 0f, 1f, 0f
    ))
    saturationMatrix.timesAssign(brightnessMatrix)
    return ColorFilter.colorMatrix(saturationMatrix)
}

// Clip aux polygones des prises
fun Modifier.clipToHoldsPath(path: Path?): Modifier {
    if (path == null) return this
    return graphicsLayer {
        clip = true
        shape = object : Shape {
            override fun createOutline(size: Size, ...): Outline {
                return Outline.Generic(path)
            }
        }
    }
}
```

### Contours (`HoldOverlay.kt`)

```kotlin
@Composable
fun ClimbHoldOverlay(
    climb: Climb,
    holdsMap: Map<Int, Hold>,
    imageWidth: Float,
    imageHeight: Float,
    contourWidth: Float = 8f
) {
    Canvas(modifier = Modifier.fillMaxSize()) {
        val scaleX = size.width / imageWidth
        val scaleY = size.height / imageHeight

        climb.getClimbHolds().forEach { climbHold ->
            val hold = holdsMap[climbHold.holdId] ?: return@forEach

            // Couleur selon type
            val strokeColor = when (climbHold.holdType) {
                HoldType.FEET -> Color(0xFF31DAFF)  // Cyan
                else -> Color.White
            }

            // Contour principal
            drawHoldContour(hold, scaleX, scaleY, strokeColor, contourWidth)

            // TOP : double contour dilaté
            if (climbHold.holdType == HoldType.TOP) {
                drawExpandedContour(hold, scaleX, scaleY, 15f, Color.White, contourWidth)
            }

            // START : lignes de tape
            if (climbHold.holdType == HoldType.START) {
                drawTapeLines(hold, startHolds.size == 1, scaleX, scaleY)
            }
        }
    }
}
```

### Persistance des paramètres

```kotlin
// RenderSettings.kt
data class RenderSettings(
    val grayLevel: Float = 0.85f,
    val brightness: Float = 0.25f,
    val contourWidth: Int = 8,
    val showImage: Boolean = true,
    val holdsInColor: Boolean = true
)

// SettingsDataStore.kt
class SettingsDataStore(context: Context) {
    val renderSettings: Flow<RenderSettings> = dataStore.data.map { prefs ->
        RenderSettings(
            grayLevel = prefs[RENDER_GRAY_LEVEL] ?: 0.85f,
            brightness = prefs[RENDER_BRIGHTNESS] ?: 0.25f,
            // ...
        )
    }
}
```

## Diagramme de flux

```
┌─────────────────────────────────────────────────────────────┐
│                    ClimbDetailScreen                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  WallImageWithClimbOverlay                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. AsyncImage (grisé+sombre)                        │    │
│  │    colorFilter = saturation(0.15) × brightness(0.25)│    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 2. AsyncImage (originale)                           │    │
│  │    modifier = clipToHoldsPath(Path des polygones)   │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 3. ClimbHoldOverlay (Canvas)                        │    │
│  │    - Contours blancs/cyan                           │    │
│  │    - Double contour TOP                             │    │
│  │    - Lignes tape START                              │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Fichiers concernés

### Python
- `mastoc/src/mastoc/gui/widgets/climb_renderer.py` - Rendu PIL
- `mastoc/src/mastoc/gui/widgets/hold_overlay.py` - Overlay PyQtGraph

### Kotlin
- `android/.../data/settings/RenderSettings.kt` - Paramètres
- `android/.../data/settings/SettingsDataStore.kt` - Persistance
- `android/.../ui/components/HoldOverlay.kt` - Contours Canvas
- `android/.../ui/components/RenderSettingsSheet.kt` - UI paramètres
- `android/.../ui/screens/ClimbDetailScreen.kt` - Rendu composé

## Références

- [ADR 004](004_client_pyqtgraph.md) - Client PyQtGraph
- [PIL ImageEnhance](https://pillow.readthedocs.io/en/stable/reference/ImageEnhance.html)
- [Compose ColorMatrix](https://developer.android.com/reference/kotlin/androidx/compose/ui/graphics/ColorMatrix)
