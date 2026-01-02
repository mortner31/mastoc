package com.mastoc.app.core

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Color
import coil.imageLoader
import coil.request.ImageRequest
import coil.request.SuccessResult
import com.mastoc.app.data.local.HoldDao
import com.mastoc.app.data.local.HoldEntity
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Extrait la couleur dominante des prises depuis l'image du mur.
 *
 * Algorithme (porté de picto.py) :
 * 1. Sample les pixels autour du centroïde de chaque prise
 * 2. Ignore les pixels gris (max_diff < 30)
 * 3. Quantifie les couleurs (pas de 32) pour regrouper les couleurs similaires
 * 4. Retourne la couleur la plus fréquente
 */
class HoldColorExtractor(
    private val context: Context,
    private val holdDao: HoldDao
) {
    companion object {
        private const val SAMPLE_RADIUS = 15
        private const val SAMPLE_STEP = 3
        private const val GRAY_THRESHOLD = 30
        private const val QUANTIZATION_STEP = 32
        private val DEFAULT_COLOR = Color.rgb(200, 200, 200)
    }

    /**
     * Extrait les couleurs pour tous les holds sans couleur d'une face.
     *
     * @param faceId ID de la face
     * @param pictureUrl URL de l'image du mur
     * @param onProgress Callback de progression (current, total)
     * @return Nombre de holds traités
     */
    suspend fun extractColorsForFace(
        faceId: String,
        pictureUrl: String,
        onProgress: ((current: Int, total: Int) -> Unit)? = null
    ): Int = withContext(Dispatchers.IO) {
        // Récupérer les holds sans couleur
        val holdsWithoutColor = holdDao.getHoldsWithoutColor(faceId)
        if (holdsWithoutColor.isEmpty()) return@withContext 0

        val total = holdsWithoutColor.size
        onProgress?.invoke(0, total)

        // Charger l'image du mur
        val bitmap = loadBitmap(pictureUrl) ?: return@withContext 0

        // Extraire les couleurs pour chaque hold
        holdsWithoutColor.forEachIndexed { index, hold ->
            val color = extractDominantColor(bitmap, hold)
            holdDao.updateHoldColor(hold.id, color)
            onProgress?.invoke(index + 1, total)
        }

        bitmap.recycle()
        total
    }

    /**
     * Charge une image depuis une URL avec Coil.
     * IMPORTANT: On demande la taille originale pour avoir les bonnes coordonnées.
     */
    private suspend fun loadBitmap(url: String): Bitmap? {
        val request = ImageRequest.Builder(context)
            .data(url)
            .allowHardware(false) // Nécessaire pour accéder aux pixels
            .size(coil.size.Size.ORIGINAL) // Taille originale pour correspondre aux centroïdes
            .build()

        return when (val result = context.imageLoader.execute(request)) {
            is SuccessResult -> {
                val drawable = result.drawable
                if (drawable is android.graphics.drawable.BitmapDrawable) {
                    android.util.Log.d("HoldColorExtractor", "Image loaded: ${drawable.bitmap.width}x${drawable.bitmap.height}")
                    drawable.bitmap
                } else {
                    android.util.Log.e("HoldColorExtractor", "Drawable is not BitmapDrawable: ${drawable?.javaClass}")
                    null
                }
            }
            else -> {
                android.util.Log.e("HoldColorExtractor", "Failed to load image: $url")
                null
            }
        }
    }

    /**
     * Extrait la couleur dominante autour du centroïde d'un hold.
     */
    private fun extractDominantColor(bitmap: Bitmap, hold: HoldEntity): Int {
        val cx = hold.centroidX?.toInt() ?: return DEFAULT_COLOR
        val cy = hold.centroidY?.toInt() ?: return DEFAULT_COLOR

        val colorCounts = mutableMapOf<Int, Int>()

        // Sample les pixels autour du centroïde
        for (dx in -SAMPLE_RADIUS..SAMPLE_RADIUS step SAMPLE_STEP) {
            for (dy in -SAMPLE_RADIUS..SAMPLE_RADIUS step SAMPLE_STEP) {
                val x = cx + dx
                val y = cy + dy

                if (x < 0 || x >= bitmap.width || y < 0 || y >= bitmap.height) continue

                val pixel = bitmap.getPixel(x, y)
                val r = Color.red(pixel)
                val g = Color.green(pixel)
                val b = Color.blue(pixel)

                // Ignorer les pixels gris (pas de couleur)
                val maxDiff = maxOf(
                    kotlin.math.abs(r - g),
                    kotlin.math.abs(g - b),
                    kotlin.math.abs(r - b)
                )
                if (maxDiff <= GRAY_THRESHOLD) continue

                // Quantifier la couleur (arrondir au multiple de QUANTIZATION_STEP)
                val qr = (r / QUANTIZATION_STEP) * QUANTIZATION_STEP
                val qg = (g / QUANTIZATION_STEP) * QUANTIZATION_STEP
                val qb = (b / QUANTIZATION_STEP) * QUANTIZATION_STEP
                val quantizedColor = Color.rgb(qr, qg, qb)

                colorCounts[quantizedColor] = (colorCounts[quantizedColor] ?: 0) + 1
            }
        }

        // Retourner la couleur la plus fréquente
        return colorCounts.maxByOrNull { it.value }?.key ?: DEFAULT_COLOR
    }

    /**
     * Vérifie si une face a des holds sans couleur.
     */
    suspend fun needsColorExtraction(faceId: String): Boolean {
        return holdDao.getHoldsWithoutColorCount(faceId) > 0
    }
}
