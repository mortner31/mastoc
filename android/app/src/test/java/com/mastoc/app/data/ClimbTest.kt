package com.mastoc.app.data

import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.HoldType
import org.junit.Assert.*
import org.junit.Test

/**
 * Tests unitaires pour le modèle Climb.
 */
class ClimbTest {

    @Test
    fun `getClimbHolds parses holdsList correctly`() {
        val climb = Climb(
            id = "1",
            faceId = "face1",
            name = "Test Climb",
            holdsList = "S123 S124 O125 O126 F127 T128",
            source = "test"
        )

        val holds = climb.getClimbHolds()

        assertEquals(6, holds.size)
        assertEquals(HoldType.START, holds[0].holdType)
        assertEquals(123, holds[0].holdId)
        assertEquals(HoldType.START, holds[1].holdType)
        assertEquals(124, holds[1].holdId)
        assertEquals(HoldType.OTHER, holds[2].holdType)
        assertEquals(HoldType.OTHER, holds[3].holdType)
        assertEquals(HoldType.FEET, holds[4].holdType)
        assertEquals(HoldType.TOP, holds[5].holdType)
        assertEquals(128, holds[5].holdId)
    }

    @Test
    fun `getClimbHolds handles empty holdsList`() {
        val climb = Climb(
            id = "1",
            faceId = "face1",
            name = "Empty Climb",
            holdsList = "",
            source = "test"
        )

        val holds = climb.getClimbHolds()

        assertTrue(holds.isEmpty())
    }

    @Test
    fun `getClimbHolds handles comma-separated format`() {
        val climb = Climb(
            id = "1",
            faceId = "face1",
            name = "Comma Climb",
            holdsList = "S100,O101,T102",
            source = "test"
        )

        val holds = climb.getClimbHolds()

        assertEquals(3, holds.size)
        assertEquals(HoldType.START, holds[0].holdType)
        assertEquals(HoldType.OTHER, holds[1].holdType)
        assertEquals(HoldType.TOP, holds[2].holdType)
    }

    @Test
    fun `getHoldIds returns correct list`() {
        val climb = Climb(
            id = "1",
            faceId = "face1",
            name = "Test",
            holdsList = "S10 O20 T30",
            source = "test"
        )

        val ids = climb.getHoldIds()

        assertEquals(listOf(10, 20, 30), ids)
    }

    @Test
    fun `displayGrade returns gradeFont when available`() {
        val climb = Climb(
            id = "1",
            faceId = "face1",
            name = "Test",
            holdsList = "",
            gradeFont = "6A+",
            gradeIrcra = 28f,
            source = "test"
        )

        assertEquals("6A+", climb.displayGrade)
    }

    @Test
    fun `displayGrade falls back to IRCRA when no gradeFont`() {
        val climb = Climb(
            id = "1",
            faceId = "face1",
            name = "Test",
            holdsList = "",
            gradeFont = null,
            gradeIrcra = 28f,
            source = "test"
        )

        assertEquals("IRCRA 28.0", climb.displayGrade)
    }

    @Test
    fun `displayGrade returns question mark when no grade`() {
        val climb = Climb(
            id = "1",
            faceId = "face1",
            name = "Test",
            holdsList = "",
            gradeFont = null,
            gradeIrcra = null,
            source = "test"
        )

        assertEquals("?", climb.displayGrade)
    }
}
