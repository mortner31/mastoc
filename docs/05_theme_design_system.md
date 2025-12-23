# Theme et Design System - mastock

**Document de reference pour le look & feel de l'application mastock Android.**

Base : **Material Design 3**
Approche : **Minimaliste/Tech**
Dark mode : **Auto systeme**

---

## 1. Palette de Couleurs

### 1.1 Couleur Primaire : Bleu

Le bleu evoque la confiance, la stabilite et l'aspect technologique moderne.

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#1976D2` | Actions principales, FAB, boutons |
| `primaryContainer` | `#BBDEFB` | Fonds de selection, chips actifs |
| `onPrimary` | `#FFFFFF` | Texte sur primary |
| `onPrimaryContainer` | `#1565C0` | Texte sur primaryContainer |

### 1.2 Couleur Secondaire : Teal

Pour les actions secondaires, badges, accents complementaires.

| Token | Hex | Usage |
|-------|-----|-------|
| `secondary` | `#00897B` | Actions secondaires, badges |
| `secondaryContainer` | `#B2DFDB` | Fonds secondaires |
| `onSecondary` | `#FFFFFF` | Texte sur secondary |
| `onSecondaryContainer` | `#00695C` | Texte sur secondaryContainer |

### 1.3 Couleurs Semantiques

| Token | Hex | Usage |
|-------|-----|-------|
| `error` | `#D32F2F` | Erreurs, validations echouees |
| `warning` | `#FFA000` | Avertissements, mode offline |
| `success` | `#388E3C` | Succes, validations reussies |
| `info` | `#1976D2` | Information (= primary) |

### 1.4 Surfaces - Light Mode

| Token | Hex | Usage |
|-------|-----|-------|
| `background` | `#FAFAFA` | Fond d'ecran principal |
| `surface` | `#FFFFFF` | Cards, bottom sheets |
| `surfaceVariant` | `#F5F5F5` | Fonds alternatifs |
| `outline` | `#BDBDBD` | Bordures, separateurs |
| `onBackground` | `#212121` | Texte principal |
| `onSurface` | `#424242` | Texte secondaire |

### 1.5 Surfaces - Dark Mode

| Token | Hex | Usage |
|-------|-----|-------|
| `background` | `#121212` | Fond d'ecran principal |
| `surface` | `#1E1E1E` | Cards, bottom sheets |
| `surfaceVariant` | `#2C2C2C` | Fonds alternatifs |
| `outline` | `#616161` | Bordures, separateurs |
| `onBackground` | `#EEEEEE` | Texte principal |
| `onSurface` | `#BDBDBD` | Texte secondaire |

---

## 2. Design Tokens

### 2.1 Typographie

Utiliser la typographie Material Design 3 standard (Roboto) pour :
- Familiarite utilisateur
- Coherence ecosysteme Android
- Pas de surcharge cognitive

| Style | Taille | Poids | Usage |
|-------|--------|-------|-------|
| Display Large | 57sp | 400 | Non utilise |
| Headline Large | 32sp | 400 | Titre ecran |
| Headline Medium | 28sp | 400 | Nom bloc (detail) |
| Title Large | 22sp | 400 | Sections |
| Title Medium | 16sp | 500 | Nom bloc (liste) |
| Body Large | 16sp | 400 | Description, commentaires |
| Body Medium | 14sp | 400 | Texte standard |
| Label Large | 14sp | 500 | Boutons |
| Label Medium | 12sp | 500 | Chips, badges |

### 2.2 Espacements

Multiples de 4dp (conforme M3).

| Token | Valeur | Usage |
|-------|--------|-------|
| `spacing-xs` | 4dp | Espacement minimal |
| `spacing-sm` | 8dp | Entre elements proches |
| `spacing-md` | 16dp | Padding cards, marges ecran |
| `spacing-lg` | 24dp | Sections |
| `spacing-xl` | 32dp | Grandes separations |

### 2.3 Coins (Border Radius)

| Token | Valeur | Usage |
|-------|--------|-------|
| `radius-sm` | 4dp | Chips, badges |
| `radius-md` | 8dp | Cards, boutons |
| `radius-lg` | 16dp | Bottom sheets |
| `radius-xl` | 28dp | FAB |
| `radius-full` | 50% | Avatars, toggles |

### 2.4 Elevations

| Token | Valeur | Usage |
|-------|--------|-------|
| `elevation-0` | 0dp | Flat |
| `elevation-1` | 1dp | Cards au repos |
| `elevation-2` | 3dp | Cards elevees, hover |
| `elevation-3` | 6dp | Bottom sheets, dialogs |
| `elevation-4` | 8dp | Navigation drawer |
| `elevation-5` | 12dp | FAB |

---

## 3. Implementation Jetpack Compose

### 3.1 Structure des Fichiers

```
mastock-android/
└── app/src/main/java/.../ui/theme/
    ├── Color.kt          # Definitions couleurs
    ├── Type.kt           # Typographie
    ├── Shape.kt          # Formes/coins
    ├── Theme.kt          # MaterialTheme personnalise
    └── Dimens.kt         # Espacements custom
```

### 3.2 Color.kt

```kotlin
package com.mastock.ui.theme

import androidx.compose.ui.graphics.Color

// Primary
val MastockBlue = Color(0xFF1976D2)
val MastockBlueLight = Color(0xFFBBDEFB)
val MastockBlueDark = Color(0xFF0D47A1)

// Secondary
val MastockTeal = Color(0xFF00897B)
val MastockTealLight = Color(0xFFB2DFDB)
val MastockTealDark = Color(0xFF00695C)

// Semantic
val MastockError = Color(0xFFD32F2F)
val MastockWarning = Color(0xFFFFA000)
val MastockSuccess = Color(0xFF388E3C)

// Light scheme surfaces
val LightBackground = Color(0xFFFAFAFA)
val LightSurface = Color(0xFFFFFFFF)
val LightSurfaceVariant = Color(0xFFF5F5F5)
val LightOutline = Color(0xFFBDBDBD)
val LightOnBackground = Color(0xFF212121)
val LightOnSurface = Color(0xFF424242)

// Dark scheme surfaces
val DarkBackground = Color(0xFF121212)
val DarkSurface = Color(0xFF1E1E1E)
val DarkSurfaceVariant = Color(0xFF2C2C2C)
val DarkOutline = Color(0xFF616161)
val DarkOnBackground = Color(0xFFEEEEEE)
val DarkOnSurface = Color(0xFFBDBDBD)
```

### 3.3 Theme.kt

```kotlin
package com.mastock.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext

private val LightColorScheme = lightColorScheme(
    primary = MastockBlue,
    onPrimary = Color.White,
    primaryContainer = MastockBlueLight,
    onPrimaryContainer = MastockBlueDark,
    secondary = MastockTeal,
    onSecondary = Color.White,
    secondaryContainer = MastockTealLight,
    onSecondaryContainer = MastockTealDark,
    background = LightBackground,
    onBackground = LightOnBackground,
    surface = LightSurface,
    onSurface = LightOnSurface,
    surfaceVariant = LightSurfaceVariant,
    outline = LightOutline,
    error = MastockError
)

private val DarkColorScheme = darkColorScheme(
    primary = MastockBlueLight,
    onPrimary = MastockBlueDark,
    primaryContainer = MastockBlue,
    onPrimaryContainer = MastockBlueLight,
    secondary = MastockTealLight,
    onSecondary = MastockTealDark,
    secondaryContainer = MastockTeal,
    onSecondaryContainer = MastockTealLight,
    background = DarkBackground,
    onBackground = DarkOnBackground,
    surface = DarkSurface,
    onSurface = DarkOnSurface,
    surfaceVariant = DarkSurfaceVariant,
    outline = DarkOutline,
    error = MastockError
)

@Composable
fun MastockTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
```

---

## 4. Considerations Specifiques Escalade

### 4.1 Visualisation des Prises

Les couleurs des prises proviennent de l'image du mur. Le theme doit garantir un bon contraste.

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Fond mur | Gris moyen (70%) | Gris fonce (50%) |
| Contour prises | Blanc ou couleur dominante | Blanc |
| Prises claires | Lisere noir | Lisere blanc |

**Regle** : Adapter `contourColor` selon le theme actif :

```kotlin
val contourColor = if (isSystemInDarkTheme()) {
    Color.White
} else {
    if (holdColor.luminance() > 0.7f) Color.Black else Color.White
}
```

### 4.2 Pictos (Miniatures)

Les pictos conservent un **fond blanc invariant** pour garantir :
- Lisibilite dans tous les contextes
- Coherence visuelle
- Pas de regeneration necessaire au changement de theme

### 4.3 Cartes de Blocs

```
Light Mode:
- Card Surface (#FFFFFF)
- Elevation 1 (ombre legere)
- Texte OnSurface (#424242)

Dark Mode:
- Card Surface (#1E1E1E)
- Elevation 0 (pas d'ombre, difference de surface suffit)
- Texte OnSurface (#BDBDBD)
```

### 4.4 Modes de Coloration (Heatmaps)

Les colormaps (viridis, plasma, inferno, magma, cividis, turbo, coolwarm) sont deja concues pour :
- Bonne lisibilite sur fond clair ET fonce
- Accessibilite daltonisme

**Aucune adaptation necessaire.**

---

## 5. Persistance du Theme

### 5.1 Parametres Stockes

| Setting | Valeurs | Defaut |
|---------|---------|--------|
| `theme_mode` | `system`, `light`, `dark` | `system` |
| `dynamic_color` | `true`, `false` | `false` |

### 5.2 Interface Parametres

```
Apparence
├── Theme
│   ○ Automatique (systeme)  <- Defaut
│   ○ Clair
│   ○ Sombre
│
└── Couleurs dynamiques (Android 12+)
    [ ] Utiliser les couleurs du fond d'ecran
```

### 5.3 Implementation DataStore

```kotlin
object ThemePreferences {
    val THEME_MODE = stringPreferencesKey("theme_mode")
    val DYNAMIC_COLOR = booleanPreferencesKey("dynamic_color")
}

enum class ThemeMode { SYSTEM, LIGHT, DARK }
```

---

## 6. Resume

| Aspect | Specification |
|--------|---------------|
| **Base** | Material Design 3 |
| **Primaire** | Bleu `#1976D2` |
| **Secondaire** | Teal `#00897B` |
| **Ambiance** | Minimaliste, epure, fonctionnel |
| **Typo** | Roboto (M3 default) |
| **Dark mode** | Auto systeme |
| **Dynamic Color** | Optionnel (Android 12+) |
| **Pictos** | Fond blanc (invariant) |
| **Prises** | Contour adaptatif light/dark |

---

**Version** : 1.0
**Date** : 2025-12-23
