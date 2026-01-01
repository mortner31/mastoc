package com.mastoc.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

/**
 * Modes de coloration des prises (heatmaps).
 */
enum class ColorMode(val displayName: String) {
    NONE("Aucun"),
    MIN_GRADE("Grade minimum"),
    MAX_GRADE("Grade maximum"),
    FREQUENCY("Fréquence d'utilisation"),
    RARE("Prises rares");

    companion object {
        /**
         * Calcule la valeur normalisée pour le mode RARE.
         * 0 utilisations = 1.0 (très visible)
         * 1 utilisation = 0.75
         * 2 utilisations = 0.50
         * 3 utilisations = 0.25
         * 4+ utilisations = 0.0 (neutre)
         */
        fun getRareValue(usageCount: Int): Float {
            return when (usageCount) {
                0 -> 1.0f
                1 -> 0.75f
                2 -> 0.50f
                3 -> 0.25f
                else -> 0.0f
            }
        }
    }
}

/**
 * Palettes de couleurs pour les heatmaps.
 * LUT pré-calculées avec 10 échantillons pour interpolation.
 */
enum class ColorPalette(val displayName: String) {
    VIRIDIS("Viridis (recommandé)"),
    PLASMA("Plasma"),
    INFERNO("Inferno"),
    MAGMA("Magma"),
    CIVIDIS("Cividis (daltoniens)"),
    TURBO("Turbo (arc-en-ciel)"),
    COOLWARM("Froid-Chaud");

    /**
     * Retourne la couleur pour une valeur normalisée [0, 1].
     */
    fun getColor(normalizedValue: Float): Color {
        val lut = ColorLut.getLut(this)
        val clampedValue = normalizedValue.coerceIn(0f, 1f)
        val index = (clampedValue * (lut.size - 1)).toInt()
        val nextIndex = (index + 1).coerceAtMost(lut.size - 1)
        val fraction = (clampedValue * (lut.size - 1)) - index

        // Interpolation linéaire entre deux couleurs
        return lerp(lut[index], lut[nextIndex], fraction)
    }

    companion object {
        private fun lerp(start: Color, end: Color, fraction: Float): Color {
            return Color(
                red = start.red + (end.red - start.red) * fraction,
                green = start.green + (end.green - start.green) * fraction,
                blue = start.blue + (end.blue - start.blue) * fraction,
                alpha = 1f
            )
        }
    }
}

/**
 * LUT (Look-Up Tables) pré-calculées pour les palettes.
 * 256 niveaux par palette pour un rendu fluide.
 */
object ColorLut {
    // Cache des LUT générées
    private val cache = mutableMapOf<ColorPalette, List<Color>>()

    /**
     * Retourne la LUT (256 couleurs) pour une palette.
     */
    fun getLut(palette: ColorPalette): List<Color> {
        return cache.getOrPut(palette) { generateLut(palette) }
    }

    private fun generateLut(palette: ColorPalette): List<Color> {
        return when (palette) {
            ColorPalette.VIRIDIS -> generateViridis()
            ColorPalette.PLASMA -> generatePlasma()
            ColorPalette.INFERNO -> generateInferno()
            ColorPalette.MAGMA -> generateMagma()
            ColorPalette.CIVIDIS -> generateCividis()
            ColorPalette.TURBO -> generateTurbo()
            ColorPalette.COOLWARM -> generateCoolwarm()
        }
    }

    private fun generateViridis(): List<Color> {
        return (0 until 256).map { i ->
            val t = i / 255f
            val r = (0.267004f + t * (0.00331f + t * (0.394756f + t * -0.117387f))).coerceIn(0f, 1f)
            val g = (0.004874f + t * (1.306966f + t * (-0.425592f + t * 0.092948f))).coerceIn(0f, 1f)
            val b = (0.329415f + t * (0.565491f + t * (-1.169775f + t * 0.526421f))).coerceIn(0f, 1f)
            Color(r, g, b)
        }
    }

    private fun generatePlasma(): List<Color> {
        return (0 until 256).map { i ->
            val t = i / 255f
            val r = (0.050383f + t * (2.014523f + t * (-1.290058f + t * 0.189539f))).coerceIn(0f, 1f)
            val g = (0.029803f + t * (-0.264776f + t * (1.556932f + t * -0.342479f))).coerceIn(0f, 1f)
            val b = (0.527975f + t * (0.814788f + t * (-2.082147f + t * 0.737692f))).coerceIn(0f, 1f)
            Color(r, g, b)
        }
    }

    private fun generateInferno(): List<Color> {
        return (0 until 256).map { i ->
            val t = i / 255f
            val r = (0.001462f + t * (1.229858f + t * (0.653728f + t * -0.898854f))).coerceIn(0f, 1f)
            val g = (0.000466f + t * (-0.094633f + t * (1.288177f + t * -0.213015f))).coerceIn(0f, 1f)
            val b = (0.013866f + t * (1.100166f + t * (-2.268887f + t * 1.170173f))).coerceIn(0f, 1f)
            Color(r, g, b)
        }
    }

    private fun generateMagma(): List<Color> {
        return (0 until 256).map { i ->
            val t = i / 255f
            val r = (0.001462f + t * (1.015283f + t * (0.557693f + t * -0.575866f))).coerceIn(0f, 1f)
            val g = (0.000466f + t * (-0.113169f + t * (0.965386f + t * 0.141701f))).coerceIn(0f, 1f)
            val b = (0.013866f + t * (1.264213f + t * (-1.869202f + t * 0.605845f))).coerceIn(0f, 1f)
            Color(r, g, b)
        }
    }

    private fun generateCividis(): List<Color> {
        return (0 until 256).map { i ->
            val t = i / 255f
            val r = (-0.046987f + t * (1.286494f + t * (-0.255453f + t * 0.018936f))).coerceIn(0f, 1f)
            val g = (0.135112f + t * (0.594445f + t * (0.260096f + t * 0.010278f))).coerceIn(0f, 1f)
            val b = (0.333333f + t * (-0.016122f + t * (-0.381716f + t * 0.063898f))).coerceIn(0f, 1f)
            Color(r, g, b)
        }
    }

    private fun generateTurbo(): List<Color> {
        return (0 until 256).map { i ->
            val t = i / 255f
            val r = (0.13572138f + t * (4.6153926f + t * (-42.66032258f + t * (
                132.13108234f + t * (-152.94239396f + t * 59.28637943f))))).coerceIn(0f, 1f)
            val g = (0.09140261f + t * (2.19418839f + t * (4.84296658f + t * (
                -14.18503333f + t * (4.27729857f + t * 2.82956604f))))).coerceIn(0f, 1f)
            val b = (0.10667330f + t * (12.64194608f + t * (-60.58204836f + t * (
                110.36276771f + t * (-89.90310912f + t * 27.34824973f))))).coerceIn(0f, 1f)
            Color(r, g, b)
        }
    }

    private fun generateCoolwarm(): List<Color> {
        return (0 until 256).map { i ->
            val t = i / 255f
            if (t < 0.5f) {
                // Bleu → Blanc
                val s = t * 2
                Color(
                    red = 0.230f + s * 0.770f,
                    green = 0.299f + s * 0.701f,
                    blue = 0.754f + s * 0.246f
                )
            } else {
                // Blanc → Rouge
                val s = (t - 0.5f) * 2
                Color(
                    red = 1.0f - s * 0.294f,
                    green = 1.0f - s * 0.713f,
                    blue = 1.0f - s * 0.715f
                )
            }
        }
    }
}

/**
 * Composable pour afficher un aperçu de la palette.
 */
@Composable
fun PalettePreview(
    palette: ColorPalette,
    modifier: Modifier = Modifier
) {
    val lut = ColorLut.getLut(palette)

    Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(24.dp)
    ) {
        val cellWidth = size.width / lut.size
        lut.forEachIndexed { index, color ->
            drawRect(
                color = color,
                topLeft = Offset(index * cellWidth, 0f),
                size = Size(cellWidth + 1f, size.height) // +1 pour éviter les gaps
            )
        }
    }
}

/**
 * Applique une palette à une valeur normalisée avec alpha.
 */
fun applyColormap(value: Float, palette: ColorPalette, alpha: Float = 0.7f): Color {
    return palette.getColor(value).copy(alpha = alpha)
}
