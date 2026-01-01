package com.mastoc.app.data.model

import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Path

/**
 * Modèle de domaine pour un hold (prise).
 */
data class Hold(
    val id: Int,
    val stoktId: Int? = null,
    val faceId: String,
    val polygonStr: String,
    val centroidX: Float? = null,
    val centroidY: Float? = null,
    val pathStr: String? = null,
    val area: Float? = null,
    val centerTapeStr: String = "",
    val rightTapeStr: String = "",
    val leftTapeStr: String = ""
) {
    /**
     * Parse le polygonStr et retourne une liste de points.
     * Format API: "x1,y1 x2,y2 x3,y3 ..." (points séparés par espaces, coords par virgules)
     */
    fun getPolygonPoints(): List<Offset> {
        if (polygonStr.isBlank()) return emptyList()
        return polygonStr.trim().split(" ")
            .mapNotNull { pointStr ->
                val parts = pointStr.split(",")
                if (parts.size >= 2) {
                    val x = parts[0].toFloatOrNull()
                    val y = parts[1].toFloatOrNull()
                    if (x != null && y != null) Offset(x, y) else null
                } else null
            }
    }

    /**
     * Retourne le centroid comme Offset.
     */
    val centroid: Offset?
        get() = if (centroidX != null && centroidY != null) {
            Offset(centroidX, centroidY)
        } else null

    /**
     * Crée un Path Compose depuis le polygone.
     */
    fun toPath(): Path {
        val points = getPolygonPoints()
        val path = Path()
        if (points.isEmpty()) return path

        path.moveTo(points.first().x, points.first().y)
        for (i in 1 until points.size) {
            path.lineTo(points[i].x, points[i].y)
        }
        path.close()
        return path
    }

    /**
     * Parse un tapeStr en deux points.
     * Format: "x1 y1 x2 y2"
     * @return Pair de Offset ou null si invalide
     */
    fun parseTapeLine(tapeStr: String): Pair<Offset, Offset>? {
        if (tapeStr.isBlank()) return null
        val parts = tapeStr.trim().split(" ")
        if (parts.size != 4) return null
        return try {
            val x1 = parts[0].toFloat()
            val y1 = parts[1].toFloat()
            val x2 = parts[2].toFloat()
            val y2 = parts[3].toFloat()
            Pair(Offset(x1, y1), Offset(x2, y2))
        } catch (e: NumberFormatException) {
            null
        }
    }

    /**
     * Retourne les lignes de tape à dessiner selon le nombre de prises de départ.
     * @param singleStart true si c'est la seule prise de départ (dessine V avec left+right)
     * @return Liste de paires de points pour les lignes
     */
    fun getTapeLines(singleStart: Boolean): List<Pair<Offset, Offset>> {
        return if (singleStart) {
            // Une seule prise de départ : dessine V avec left + right
            listOfNotNull(
                parseTapeLine(leftTapeStr),
                parseTapeLine(rightTapeStr)
            )
        } else {
            // Plusieurs prises de départ : dessine ligne centrale
            listOfNotNull(parseTapeLine(centerTapeStr))
        }
    }
}
