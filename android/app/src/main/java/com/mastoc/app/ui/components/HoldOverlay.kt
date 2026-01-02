package com.mastoc.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.ClimbHold
import com.mastoc.app.data.model.Hold
import com.mastoc.app.data.model.HoldType
import kotlin.math.sqrt

// Constantes de style (fidélité Python)
private const val CONTOUR_WIDTH = 8f
private const val TOP_EXPANSION = 15f
private val NEON_BLUE = Color(0xFF31DAFF)

/**
 * Overlay Canvas pour dessiner les polygones des prises.
 * Version basique pour HoldSelector (toutes les prises).
 */
@Composable
fun HoldOverlay(
    allHolds: List<Hold>,
    highlightedHolds: List<Hold>,
    imageWidth: Float,
    imageHeight: Float,
    modifier: Modifier = Modifier,
    highlightColor: Color = MaterialTheme.colorScheme.primary,
    dimColor: Color = Color.Gray.copy(alpha = 0.3f)
) {
    val highlightedIds = highlightedHolds.map { it.id }.toSet()

    Canvas(modifier = modifier.fillMaxSize()) {
        val scaleX = size.width / imageWidth
        val scaleY = size.height / imageHeight

        // Dessiner toutes les prises (atténuées)
        allHolds.forEach { hold ->
            val isHighlighted = hold.id in highlightedIds
            drawHold(
                hold = hold,
                scaleX = scaleX,
                scaleY = scaleY,
                fillColor = if (isHighlighted) highlightColor.copy(alpha = 0.4f) else dimColor,
                strokeColor = if (isHighlighted) highlightColor else Color.Gray,
                strokeWidth = if (isHighlighted) 4f else 2f
            )
        }
    }
}

/**
 * Overlay Canvas pour un climb spécifique avec rendu fidèle au Python.
 * Dessine les prises avec leurs types (START, TOP, FEET, OTHER).
 *
 * @param contourWidth Épaisseur du contour (défaut 8px)
 */
@Composable
fun ClimbHoldOverlay(
    climb: Climb,
    holdsMap: Map<Int, Hold>,
    imageWidth: Float,
    imageHeight: Float,
    contourWidth: Float = CONTOUR_WIDTH,
    modifier: Modifier = Modifier
) {
    val climbHolds = climb.getClimbHolds()
    val startHolds = climbHolds.filter { it.holdType == HoldType.START }

    Canvas(modifier = modifier.fillMaxSize()) {
        val scaleX = size.width / imageWidth
        val scaleY = size.height / imageHeight

        // Dessiner chaque prise du climb
        climbHolds.forEach { climbHold ->
            val hold = holdsMap[climbHold.holdId] ?: return@forEach

            // Couleur du contour selon le type (FEET=cyan, autres=blanc)
            val strokeColor = when (climbHold.holdType) {
                HoldType.FEET -> NEON_BLUE
                else -> Color.White
            }

            // Dessiner le contour principal
            drawHoldContour(
                hold = hold,
                scaleX = scaleX,
                scaleY = scaleY,
                strokeColor = strokeColor,
                strokeWidth = contourWidth
            )

            // TOP : ajouter double contour écarté
            if (climbHold.holdType == HoldType.TOP) {
                drawExpandedContour(
                    hold = hold,
                    scaleX = scaleX,
                    scaleY = scaleY,
                    expansion = TOP_EXPANSION,
                    strokeColor = Color.White,
                    strokeWidth = contourWidth
                )
            }

            // START : dessiner les lignes de tape
            if (climbHold.holdType == HoldType.START) {
                val singleStart = startHolds.size == 1
                drawTapeLines(
                    hold = hold,
                    singleStart = singleStart,
                    scaleX = scaleX,
                    scaleY = scaleY,
                    strokeWidth = contourWidth
                )
            }
        }
    }
}

/**
 * Dessine un hold sur le Canvas (remplissage + contour).
 */
private fun DrawScope.drawHold(
    hold: Hold,
    scaleX: Float,
    scaleY: Float,
    fillColor: Color,
    strokeColor: Color,
    strokeWidth: Float
) {
    val points = hold.getPolygonPoints()
    if (points.isEmpty()) return

    val scaledPoints = points.map { point ->
        Offset(point.x * scaleX, point.y * scaleY)
    }

    val path = Path().apply {
        moveTo(scaledPoints.first().x, scaledPoints.first().y)
        for (i in 1 until scaledPoints.size) {
            lineTo(scaledPoints[i].x, scaledPoints[i].y)
        }
        close()
    }

    // Remplissage
    drawPath(path, fillColor)

    // Contour
    drawPath(path, strokeColor, style = Stroke(width = strokeWidth))
}

/**
 * Dessine uniquement le contour d'un hold (sans remplissage).
 */
private fun DrawScope.drawHoldContour(
    hold: Hold,
    scaleX: Float,
    scaleY: Float,
    strokeColor: Color,
    strokeWidth: Float
) {
    val points = hold.getPolygonPoints()
    if (points.isEmpty()) return

    val scaledPoints = points.map { point ->
        Offset(point.x * scaleX, point.y * scaleY)
    }

    val path = Path().apply {
        moveTo(scaledPoints.first().x, scaledPoints.first().y)
        for (i in 1 until scaledPoints.size) {
            lineTo(scaledPoints[i].x, scaledPoints[i].y)
        }
        close()
    }

    drawPath(path, strokeColor, style = Stroke(width = strokeWidth))
}

/**
 * Dessine un contour dilaté (pour TOP).
 * Dilate les points du polygone depuis le centroïde.
 */
private fun DrawScope.drawExpandedContour(
    hold: Hold,
    scaleX: Float,
    scaleY: Float,
    expansion: Float,
    strokeColor: Color,
    strokeWidth: Float
) {
    val points = hold.getPolygonPoints()
    if (points.isEmpty()) return

    val centroid = hold.centroid ?: return
    val cx = centroid.x
    val cy = centroid.y

    // Dilater les points depuis le centroïde
    val expandedPoints = points.map { point ->
        val dx = point.x - cx
        val dy = point.y - cy
        val dist = sqrt(dx * dx + dy * dy)
        if (dist > 0) {
            val scale = (dist + expansion) / dist
            Offset((cx + dx * scale) * scaleX, (cy + dy * scale) * scaleY)
        } else {
            Offset(point.x * scaleX, point.y * scaleY)
        }
    }

    val path = Path().apply {
        moveTo(expandedPoints.first().x, expandedPoints.first().y)
        for (i in 1 until expandedPoints.size) {
            lineTo(expandedPoints[i].x, expandedPoints[i].y)
        }
        close()
    }

    drawPath(path, strokeColor, style = Stroke(width = strokeWidth))
}

/**
 * Dessine les lignes de tape pour une prise START.
 */
private fun DrawScope.drawTapeLines(
    hold: Hold,
    singleStart: Boolean,
    scaleX: Float,
    scaleY: Float,
    strokeWidth: Float = 4f
) {
    val tapeLines = hold.getTapeLines(singleStart)

    tapeLines.forEach { (start, end) ->
        drawLine(
            color = Color.White,
            start = Offset(start.x * scaleX, start.y * scaleY),
            end = Offset(end.x * scaleX, end.y * scaleY),
            strokeWidth = strokeWidth
        )
    }
}

/**
 * Marqueur de type (START, TOP, etc.) - Version legacy.
 */
enum class HoldMarkerType {
    START,      // Tape de départ
    TOP,        // Prise finale
    FEET_ONLY   // Pieds uniquement
}

/**
 * Dessine un marqueur sur une prise - Version legacy.
 */
@Composable
fun HoldMarker(
    hold: Hold,
    markerType: HoldMarkerType,
    scaleX: Float,
    scaleY: Float,
    modifier: Modifier = Modifier
) {
    val color = when (markerType) {
        HoldMarkerType.START -> Color(0xFF4CAF50) // Vert
        HoldMarkerType.TOP -> Color(0xFFF44336)   // Rouge
        HoldMarkerType.FEET_ONLY -> Color(0xFF2196F3) // Bleu
    }

    Canvas(modifier = modifier.fillMaxSize()) {
        val centroid = hold.centroid ?: return@Canvas
        val scaledCenter = Offset(centroid.x * scaleX, centroid.y * scaleY)
        val radius = 20f

        when (markerType) {
            HoldMarkerType.START -> {
                // Rectangle "tape" de départ
                drawRect(
                    color = color,
                    topLeft = Offset(scaledCenter.x - radius, scaledCenter.y - 5f),
                    size = androidx.compose.ui.geometry.Size(radius * 2, 10f)
                )
            }
            HoldMarkerType.TOP -> {
                // Double cercle pour TOP
                drawCircle(color = color, radius = radius, center = scaledCenter)
                drawCircle(
                    color = Color.White,
                    radius = radius - 4f,
                    center = scaledCenter,
                    style = Stroke(width = 2f)
                )
            }
            HoldMarkerType.FEET_ONLY -> {
                // Cercle plein bleu
                drawCircle(color = color.copy(alpha = 0.5f), radius = radius, center = scaledCenter)
            }
        }
    }
}
