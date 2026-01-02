package com.mastoc.app.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat
import com.mastoc.app.data.settings.AppTheme

// ============================================================================
// COLOR SCHEMES - COLORFUL (Rouge/Vert/Jaune)
// ============================================================================

private val ColorfulDarkColorScheme = darkColorScheme(
    primary = ColorfulPrimaryDark,
    onPrimary = ColorfulOnPrimaryDark,
    primaryContainer = ColorfulPrimaryContainerDark,
    onPrimaryContainer = ColorfulOnPrimaryContainerDark,
    secondary = ColorfulSecondaryDark,
    onSecondary = ColorfulOnSecondaryDark,
    secondaryContainer = ColorfulSecondaryContainerDark,
    onSecondaryContainer = ColorfulOnSecondaryContainerDark,
    tertiary = ColorfulTertiaryDark,
    onTertiary = ColorfulOnTertiaryDark,
    tertiaryContainer = ColorfulTertiaryContainerDark,
    onTertiaryContainer = ColorfulOnTertiaryContainerDark,
    error = ErrorDark,
    onError = OnErrorDark,
    errorContainer = ErrorContainerDark,
    onErrorContainer = OnErrorContainerDark,
    background = BackgroundDark,
    onBackground = OnBackgroundDark,
    surface = SurfaceDark,
    onSurface = OnSurfaceDark,
    surfaceVariant = SurfaceVariantDark,
    onSurfaceVariant = OnSurfaceVariantDark,
    outline = OutlineDark
)

private val ColorfulLightColorScheme = lightColorScheme(
    primary = ColorfulPrimaryLight,
    onPrimary = ColorfulOnPrimaryLight,
    primaryContainer = ColorfulPrimaryContainerLight,
    onPrimaryContainer = ColorfulOnPrimaryContainerLight,
    secondary = ColorfulSecondaryLight,
    onSecondary = ColorfulOnSecondaryLight,
    secondaryContainer = ColorfulSecondaryContainerLight,
    onSecondaryContainer = ColorfulOnSecondaryContainerLight,
    tertiary = ColorfulTertiaryLight,
    onTertiary = ColorfulOnTertiaryLight,
    tertiaryContainer = ColorfulTertiaryContainerLight,
    onTertiaryContainer = ColorfulOnTertiaryContainerLight,
    error = ErrorLight,
    onError = OnErrorLight,
    errorContainer = ErrorContainerLight,
    onErrorContainer = OnErrorContainerLight,
    background = BackgroundLight,
    onBackground = OnBackgroundLight,
    surface = SurfaceLight,
    onSurface = OnSurfaceLight,
    surfaceVariant = SurfaceVariantLight,
    onSurfaceVariant = OnSurfaceVariantLight,
    outline = OutlineLight
)

// ============================================================================
// COLOR SCHEMES - BLUE (Bleu/Teal)
// ============================================================================

private val BlueDarkColorScheme = darkColorScheme(
    primary = BluePrimaryDark,
    onPrimary = BlueOnPrimaryDark,
    primaryContainer = BluePrimaryContainerDark,
    onPrimaryContainer = BlueOnPrimaryContainerDark,
    secondary = BlueSecondaryDark,
    onSecondary = BlueOnSecondaryDark,
    secondaryContainer = BlueSecondaryContainerDark,
    onSecondaryContainer = BlueOnSecondaryContainerDark,
    tertiary = BlueTertiaryDark,
    onTertiary = BlueOnTertiaryDark,
    tertiaryContainer = BlueTertiaryContainerDark,
    onTertiaryContainer = BlueOnTertiaryContainerDark,
    error = ErrorDark,
    onError = OnErrorDark,
    errorContainer = ErrorContainerDark,
    onErrorContainer = OnErrorContainerDark,
    background = BackgroundDark,
    onBackground = OnBackgroundDark,
    surface = SurfaceDark,
    onSurface = OnSurfaceDark,
    surfaceVariant = SurfaceVariantDark,
    onSurfaceVariant = OnSurfaceVariantDark,
    outline = OutlineDark
)

private val BlueLightColorScheme = lightColorScheme(
    primary = BluePrimaryLight,
    onPrimary = BlueOnPrimaryLight,
    primaryContainer = BluePrimaryContainerLight,
    onPrimaryContainer = BlueOnPrimaryContainerLight,
    secondary = BlueSecondaryLight,
    onSecondary = BlueOnSecondaryLight,
    secondaryContainer = BlueSecondaryContainerLight,
    onSecondaryContainer = BlueOnSecondaryContainerLight,
    tertiary = BlueTertiaryLight,
    onTertiary = BlueOnTertiaryLight,
    tertiaryContainer = BlueTertiaryContainerLight,
    onTertiaryContainer = BlueOnTertiaryContainerLight,
    error = ErrorLight,
    onError = OnErrorLight,
    errorContainer = ErrorContainerLight,
    onErrorContainer = OnErrorContainerLight,
    background = BackgroundLight,
    onBackground = OnBackgroundLight,
    surface = SurfaceLight,
    onSurface = OnSurfaceLight,
    surfaceVariant = SurfaceVariantLight,
    onSurfaceVariant = OnSurfaceVariantLight,
    outline = OutlineLight
)

// ============================================================================
// COLOR SCHEMES - GRAY (Neutre)
// ============================================================================

private val GrayDarkColorScheme = darkColorScheme(
    primary = GrayPrimaryDark,
    onPrimary = GrayOnPrimaryDark,
    primaryContainer = GrayPrimaryContainerDark,
    onPrimaryContainer = GrayOnPrimaryContainerDark,
    secondary = GraySecondaryDark,
    onSecondary = GrayOnSecondaryDark,
    secondaryContainer = GraySecondaryContainerDark,
    onSecondaryContainer = GrayOnSecondaryContainerDark,
    tertiary = GrayTertiaryDark,
    onTertiary = GrayOnTertiaryDark,
    tertiaryContainer = GrayTertiaryContainerDark,
    onTertiaryContainer = GrayOnTertiaryContainerDark,
    error = ErrorDark,
    onError = OnErrorDark,
    errorContainer = ErrorContainerDark,
    onErrorContainer = OnErrorContainerDark,
    background = BackgroundDark,
    onBackground = OnBackgroundDark,
    surface = SurfaceDark,
    onSurface = OnSurfaceDark,
    surfaceVariant = SurfaceVariantDark,
    onSurfaceVariant = OnSurfaceVariantDark,
    outline = OutlineDark
)

private val GrayLightColorScheme = lightColorScheme(
    primary = GrayPrimaryLight,
    onPrimary = GrayOnPrimaryLight,
    primaryContainer = GrayPrimaryContainerLight,
    onPrimaryContainer = GrayOnPrimaryContainerLight,
    secondary = GraySecondaryLight,
    onSecondary = GrayOnSecondaryLight,
    secondaryContainer = GraySecondaryContainerLight,
    onSecondaryContainer = GrayOnSecondaryContainerLight,
    tertiary = GrayTertiaryLight,
    onTertiary = GrayOnTertiaryLight,
    tertiaryContainer = GrayTertiaryContainerLight,
    onTertiaryContainer = GrayOnTertiaryContainerLight,
    error = ErrorLight,
    onError = OnErrorLight,
    errorContainer = ErrorContainerLight,
    onErrorContainer = OnErrorContainerLight,
    background = BackgroundLight,
    onBackground = OnBackgroundLight,
    surface = SurfaceLight,
    onSurface = OnSurfaceLight,
    surfaceVariant = SurfaceVariantLight,
    onSurfaceVariant = OnSurfaceVariantLight,
    outline = OutlineLight
)

// ============================================================================
// LEGACY ALIASES (compatibilité avec ancien code)
// ============================================================================

private val DarkColorScheme = ColorfulDarkColorScheme
private val LightColorScheme = ColorfulLightColorScheme

/**
 * Retourne le ColorScheme approprié selon le thème et le mode sombre.
 */
fun getColorScheme(appTheme: AppTheme, darkTheme: Boolean): ColorScheme {
    return when (appTheme) {
        AppTheme.COLORFUL -> if (darkTheme) ColorfulDarkColorScheme else ColorfulLightColorScheme
        AppTheme.BLUE -> if (darkTheme) BlueDarkColorScheme else BlueLightColorScheme
        AppTheme.GRAY -> if (darkTheme) GrayDarkColorScheme else GrayLightColorScheme
    }
}

@Composable
fun MastocTheme(
    darkTheme: Boolean = true,  // Dark mode par défaut
    dynamicColor: Boolean = false,
    appTheme: AppTheme = AppTheme.GRAY,  // Thème gris par défaut
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        else -> getColorScheme(appTheme, darkTheme)
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
