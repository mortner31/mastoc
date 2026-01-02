package com.mastoc.app.core

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import androidx.compose.ui.geometry.Offset
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.ClimbHold
import com.mastoc.app.data.model.Hold
import com.mastoc.app.data.model.HoldType
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.sqrt

/**
 * Génère des pictos (miniatures) pour les blocs.
 *
 * Port de mastoc/src/mastoc/core/picto.py en Kotlin.
 * Représentation simplifiée d'un bloc : cercles colorés sur fond blanc.
 */
class PictoGenerator {

    companion object {
        const val DEFAULT_SIZE = 128
        private val NEON_BLUE = Color.rgb(49, 218, 255)
        private val DEFAULT_HOLD_COLOR = Color.rgb(200, 200, 200)
        private val BACKGROUND_HOLD_COLOR = Color.rgb(220, 220, 220)
        private const val MARGIN_RATIO = 0.02f  // 2% de marge seulement
        private const val MIN_RADIUS = 3f
        private const val TOP_OUTER_RADIUS_OFFSET = 3f
        private const val LUMINANCE_THRESHOLD = 180
    }

    /**
     * Info extraite d'un hold pour le dessin.
     */
    private data class HoldDrawInfo(
        val cx: Float,
        val cy: Float,
        val radius: Float,
        val color: Int,
        val holdType: HoldType,
        val hold: Hold
    )

    /**
     * Génère un picto pour un climb.
     *
     * @param climb Le bloc à représenter
     * @param holdsMap Mapping hold_id -> Hold
     * @param size Taille du picto en pixels (carré)
     * @param topHoldIds IDs des prises les plus utilisées (affichées en gris pour le contexte)
     * @return Bitmap du picto ou null si pas de prises
     */
    fun generatePicto(
        climb: Climb,
        holdsMap: Map<Int, Hold>,
        size: Int = DEFAULT_SIZE,
        topHoldIds: Set<Int> = emptySet()
    ): Bitmap? {
        // Collecter les infos des prises du bloc
        val climbHolds = climb.getClimbHolds()
        val holdInfos = mutableListOf<HoldDrawInfo>()
        val climbHoldIds = mutableSetOf<Int>()
        val startHolds = climbHolds.filter { it.holdType == HoldType.START }

        for (ch in climbHolds) {
            val hold = findHold(ch.holdId, holdsMap) ?: continue
            val info = getHoldDrawInfo(hold, ch.holdType) ?: continue
            holdInfos.add(info)
            climbHoldIds.add(hold.id)
            hold.stoktId?.let { climbHoldIds.add(it) }
        }

        if (holdInfos.isEmpty()) {
            return createEmptyBitmap(size)
        }

        // Collecter les infos des top prises (pour le fond gris)
        val bgHoldInfos = mutableListOf<Triple<Float, Float, Float>>() // cx, cy, radius
        for (holdId in topHoldIds) {
            if (holdId in climbHoldIds) continue
            val hold = findHold(holdId, holdsMap) ?: continue
            val info = getHoldDrawInfo(hold, HoldType.OTHER) ?: continue
            bgHoldInfos.add(Triple(info.cx, info.cy, info.radius))
        }

        // Calculer la bounding box
        val allCentroids = holdInfos.map { Triple(it.cx, it.cy, it.radius) } + bgHoldInfos
        val (scale, offsetX, offsetY) = calculateTransform(allCentroids, size)

        // Créer le bitmap et le canvas
        val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawColor(Color.WHITE)

        val paint = Paint(Paint.ANTI_ALIAS_FLAG)

        // Dessiner les top holds en gris (fond)
        paint.style = Paint.Style.FILL
        paint.color = BACKGROUND_HOLD_COLOR
        for ((cx, cy, radius) in bgHoldInfos) {
            val px = cx * scale + offsetX
            val py = cy * scale + offsetY
            val pr = max(radius * scale, 2f)
            canvas.drawCircle(px, py, pr, paint)
        }

        // Dessiner les prises du bloc (premier plan)
        for (info in holdInfos) {
            drawHold(canvas, paint, info, scale, offsetX, offsetY)
        }

        // Dessiner les lignes de tape pour les prises de départ
        val holdColors = holdInfos
            .filter { it.holdType == HoldType.START }
            .associate { it.hold.id to it.color }
        drawStartTapes(canvas, paint, startHolds, holdsMap, holdColors, scale, offsetX, offsetY)

        return bitmap
    }

    /**
     * Trouve un hold par ID (essaie id puis stoktId).
     */
    private fun findHold(holdId: Int, holdsMap: Map<Int, Hold>): Hold? {
        return holdsMap[holdId]
    }

    /**
     * Extrait les infos de dessin d'un hold.
     */
    private fun getHoldDrawInfo(hold: Hold, holdType: HoldType): HoldDrawInfo? {
        val cx = hold.centroidX ?: return null
        val cy = hold.centroidY ?: return null

        // Calculer le rayon depuis l'aire ou le polygone
        val radius = if (hold.area != null && hold.area > 0) {
            sqrt(hold.area / Math.PI.toFloat())
        } else {
            calculateRadiusFromPolygon(hold)
        }

        val color = hold.colorRgb ?: DEFAULT_HOLD_COLOR

        return HoldDrawInfo(cx, cy, radius, color, holdType, hold)
    }

    /**
     * Calcule le rayon depuis le polygone (formule du lacet).
     */
    private fun calculateRadiusFromPolygon(hold: Hold): Float {
        val points = hold.getPolygonPoints()
        if (points.size < 3) return 10f

        var area = 0f
        val n = points.size
        for (i in 0 until n) {
            val j = (i + 1) % n
            area += points[i].x * points[j].y
            area -= points[j].x * points[i].y
        }
        area = abs(area) / 2

        return sqrt(area / Math.PI.toFloat())
    }

    /**
     * Calcule la transformation (scale, offsetX, offsetY) pour centrer dans le carré.
     */
    private fun calculateTransform(
        holdInfos: List<Triple<Float, Float, Float>>,
        size: Int
    ): Triple<Float, Float, Float> {
        if (holdInfos.isEmpty()) return Triple(1f, 0f, 0f)

        var minX = Float.MAX_VALUE
        var maxX = Float.MIN_VALUE
        var minY = Float.MAX_VALUE
        var maxY = Float.MIN_VALUE

        for ((cx, cy, r) in holdInfos) {
            minX = minOf(minX, cx - r)
            maxX = maxOf(maxX, cx + r)
            minY = minOf(minY, cy - r)
            maxY = maxOf(maxY, cy + r)
        }

        // Ajouter une marge
        val width = maxX - minX
        val height = maxY - minY
        minX -= width * MARGIN_RATIO
        maxX += width * MARGIN_RATIO
        minY -= height * MARGIN_RATIO
        maxY += height * MARGIN_RATIO

        // Recalculer après marge
        val newWidth = maxX - minX
        val newHeight = maxY - minY

        // Facteur d'échelle pour tenir dans le carré
        val scale = size / max(newWidth, newHeight)

        // Offset pour centrer
        val offsetX = (size - newWidth * scale) / 2 - minX * scale
        val offsetY = (size - newHeight * scale) / 2 - minY * scale

        return Triple(scale, offsetX, offsetY)
    }

    /**
     * Dessine un hold sur le canvas.
     */
    private fun drawHold(
        canvas: Canvas,
        paint: Paint,
        info: HoldDrawInfo,
        scale: Float,
        offsetX: Float,
        offsetY: Float
    ) {
        val px = info.cx * scale + offsetX
        val py = info.cy * scale + offsetY
        val pr = max(info.radius * scale, MIN_RADIUS)

        // Remplir le cercle
        paint.style = Paint.Style.FILL
        paint.color = info.color
        canvas.drawCircle(px, py, pr, paint)

        // Liseré noir si couleur claire
        if (isLightColor(info.color)) {
            paint.style = Paint.Style.STROKE
            paint.strokeWidth = 1f
            paint.color = Color.BLACK
            canvas.drawCircle(px, py, pr, paint)
        }

        // Prise TOP : double cercle
        if (info.holdType == HoldType.TOP) {
            val outerPr = pr + TOP_OUTER_RADIUS_OFFSET
            paint.style = Paint.Style.STROKE
            paint.strokeWidth = 2f
            paint.color = if (isLightColor(info.color)) Color.BLACK else info.color
            canvas.drawCircle(px, py, outerPr, paint)
        }

        // Prise FEET : contour bleu néon
        if (info.holdType == HoldType.FEET) {
            paint.style = Paint.Style.STROKE
            paint.strokeWidth = 2f
            paint.color = NEON_BLUE
            canvas.drawCircle(px, py, pr, paint)
        }
    }

    /**
     * Dessine les lignes de tape pour les prises de départ.
     */
    private fun drawStartTapes(
        canvas: Canvas,
        paint: Paint,
        startHolds: List<ClimbHold>,
        holdsMap: Map<Int, Hold>,
        holdColors: Map<Int, Int>,
        scale: Float,
        offsetX: Float,
        offsetY: Float
    ) {
        paint.style = Paint.Style.STROKE
        paint.strokeWidth = 2f

        for (ch in startHolds) {
            val hold = findHold(ch.holdId, holdsMap) ?: continue
            val color = holdColors[hold.id] ?: Color.BLACK
            paint.color = color

            if (startHolds.size == 1) {
                // Une seule prise : deux lignes (V)
                drawTapeLine(canvas, paint, hold.leftTapeStr, scale, offsetX, offsetY)
                drawTapeLine(canvas, paint, hold.rightTapeStr, scale, offsetX, offsetY)
            } else {
                // Plusieurs prises : ligne centrale
                drawTapeLine(canvas, paint, hold.centerTapeStr, scale, offsetX, offsetY)
            }
        }
    }

    /**
     * Dessine une ligne de tape.
     */
    private fun drawTapeLine(
        canvas: Canvas,
        paint: Paint,
        tapeStr: String,
        scale: Float,
        offsetX: Float,
        offsetY: Float
    ) {
        if (tapeStr.isBlank()) return
        val parts = tapeStr.trim().split(" ")
        if (parts.size != 4) return

        try {
            val x1 = parts[0].toFloat()
            val y1 = parts[1].toFloat()
            val x2 = parts[2].toFloat()
            val y2 = parts[3].toFloat()

            val px1 = x1 * scale + offsetX
            val py1 = y1 * scale + offsetY
            val px2 = x2 * scale + offsetX
            val py2 = y2 * scale + offsetY

            canvas.drawLine(px1, py1, px2, py2, paint)
        } catch (e: NumberFormatException) {
            // Ignorer les lignes invalides
        }
    }

    /**
     * Détermine si une couleur est claire (besoin de liseré noir).
     */
    private fun isLightColor(color: Int): Boolean {
        val r = Color.red(color)
        val g = Color.green(color)
        val b = Color.blue(color)
        val luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance > LUMINANCE_THRESHOLD
    }

    /**
     * Crée un bitmap vide (blanc).
     */
    private fun createEmptyBitmap(size: Int): Bitmap {
        val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawColor(Color.WHITE)
        return bitmap
    }
}
