package com.mastoc.app.data

import androidx.compose.ui.geometry.Offset
import com.mastoc.app.data.model.Hold
import org.junit.Assert.*
import org.junit.Test

/**
 * Tests unitaires pour le modèle Hold.
 */
class HoldTest {

    @Test
    fun `getPolygonPoints parses polygon string correctly`() {
        val hold = Hold(
            id = 1,
            faceId = "face1",
            polygonStr = "100 200, 150 200, 150 250, 100 250"
        )

        val points = hold.getPolygonPoints()

        assertEquals(4, points.size)
        assertEquals(100f, points[0].x, 0.01f)
        assertEquals(200f, points[0].y, 0.01f)
        assertEquals(150f, points[1].x, 0.01f)
        assertEquals(250f, points[3].y, 0.01f)
    }

    @Test
    fun `getPolygonPoints handles empty string`() {
        val hold = Hold(
            id = 1,
            faceId = "face1",
            polygonStr = ""
        )

        val points = hold.getPolygonPoints()

        assertTrue(points.isEmpty())
    }

    @Test
    fun `centroid returns correct offset`() {
        val hold = Hold(
            id = 1,
            faceId = "face1",
            polygonStr = "",
            centroidX = 125f,
            centroidY = 225f
        )

        val centroid = hold.centroid

        assertNotNull(centroid)
        assertEquals(125f, centroid!!.x, 0.01f)
        assertEquals(225f, centroid.y, 0.01f)
    }

    @Test
    fun `centroid returns null when coordinates missing`() {
        val hold = Hold(
            id = 1,
            faceId = "face1",
            polygonStr = "",
            centroidX = null,
            centroidY = 225f
        )

        assertNull(hold.centroid)
    }

    @Test
    fun `parseTapeLine parses valid tape string`() {
        val hold = Hold(
            id = 1,
            faceId = "face1",
            polygonStr = ""
        )

        val result = hold.parseTapeLine("100 200 150 250")

        assertNotNull(result)
        assertEquals(100f, result!!.first.x, 0.01f)
        assertEquals(200f, result.first.y, 0.01f)
        assertEquals(150f, result.second.x, 0.01f)
        assertEquals(250f, result.second.y, 0.01f)
    }

    @Test
    fun `parseTapeLine returns null for invalid string`() {
        val hold = Hold(
            id = 1,
            faceId = "face1",
            polygonStr = ""
        )

        assertNull(hold.parseTapeLine(""))
        assertNull(hold.parseTapeLine("100 200"))
        assertNull(hold.parseTapeLine("invalid"))
    }

    @Test
    fun `getTapeLines returns V shape for single start`() {
        val hold = Hold(
            id = 1,
            faceId = "face1",
            polygonStr = "",
            leftTapeStr = "0 0 10 20",
            rightTapeStr = "20 0 10 20",
            centerTapeStr = "10 0 10 20"
        )

        val lines = hold.getTapeLines(singleStart = true)

        assertEquals(2, lines.size) // left + right
    }

    @Test
    fun `getTapeLines returns center for multiple starts`() {
        val hold = Hold(
            id = 1,
            faceId = "face1",
            polygonStr = "",
            leftTapeStr = "0 0 10 20",
            rightTapeStr = "20 0 10 20",
            centerTapeStr = "10 0 10 20"
        )

        val lines = hold.getTapeLines(singleStart = false)

        assertEquals(1, lines.size) // center only
    }
}
