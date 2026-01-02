package com.mastoc.app.ui.components

import org.junit.Assert.*
import org.junit.Test

/**
 * Tests unitaires pour GradeUtils.
 */
class GradeUtilsTest {

    @Test
    fun `FONT_GRADES has 16 entries`() {
        assertEquals(16, FONT_GRADES.size)
    }

    @Test
    fun `GRADE_COUNT equals FONT_GRADES size`() {
        assertEquals(FONT_GRADES.size, GRADE_COUNT)
    }

    @Test
    fun `FONT_GRADES are ordered by IRCRA ascending`() {
        for (i in 0 until FONT_GRADES.size - 1) {
            assertTrue(
                "Grade ${FONT_GRADES[i].font} (${FONT_GRADES[i].ircra}) should be less than ${FONT_GRADES[i+1].font} (${FONT_GRADES[i+1].ircra})",
                FONT_GRADES[i].ircra < FONT_GRADES[i + 1].ircra
            )
        }
    }

    @Test
    fun `indexToFont returns correct grades`() {
        assertEquals("4", indexToFont(0))
        assertEquals("6A", indexToFont(4))
        assertEquals("7A", indexToFont(10))
        assertEquals("8A", indexToFont(15))
    }

    @Test
    fun `indexToFont clamps out of range values`() {
        assertEquals("4", indexToFont(-1))
        assertEquals("8A", indexToFont(100))
    }

    @Test
    fun `indexToIrcra returns correct values`() {
        assertEquals(12.0f, indexToIrcra(0), 0.01f)
        assertEquals(15.5f, indexToIrcra(4), 0.01f) // 6A
        assertEquals(20.5f, indexToIrcra(10), 0.01f) // 7A
    }

    @Test
    fun `getMinIrcraForIndex returns grade IRCRA`() {
        assertEquals(12.0f, getMinIrcraForIndex(0), 0.01f)
        assertEquals(15.5f, getMinIrcraForIndex(4), 0.01f) // 6A
    }

    @Test
    fun `getMaxIrcraForIndex uses epsilon logic`() {
        // Pour 6A (index 4), max devrait être 6A+ IRCRA - 0.01 = 16.5 - 0.01 = 16.49
        assertEquals(16.49f, getMaxIrcraForIndex(4), 0.01f)

        // Pour 7A (index 10), max devrait être 7A+ IRCRA - 0.01 = 21.5 - 0.01 = 21.49
        assertEquals(21.49f, getMaxIrcraForIndex(10), 0.01f)
    }

    @Test
    fun `getMaxIrcraForIndex returns high value for last grade`() {
        // Pour 8A (dernier grade), devrait retourner 30.0
        assertEquals(30.0f, getMaxIrcraForIndex(15), 0.01f)
    }

    @Test
    fun `ircraToIndex finds closest index`() {
        assertEquals(0, ircraToIndex(12.0f)) // 4
        assertEquals(4, ircraToIndex(15.5f)) // 6A
        assertEquals(10, ircraToIndex(20.5f)) // 7A
    }

    @Test
    fun `ircraToFont converts correctly`() {
        assertEquals("4", ircraToFont(12.0f))
        assertEquals("6A", ircraToFont(15.5f))
        assertEquals("6A", ircraToFont(16.0f)) // Entre 6A et 6A+
        assertEquals("7A", ircraToFont(20.5f))
    }

    @Test
    fun `grade filter includes all grades in range`() {
        // Simuler le filtrage pour grade 6A (index 4)
        val minIrcra = getMinIrcraForIndex(4)
        val maxIrcra = getMaxIrcraForIndex(4)

        // 6A devrait être 15.5 <= ircra <= 16.49
        assertTrue(15.5f >= minIrcra && 15.5f <= maxIrcra)
        assertTrue(16.0f >= minIrcra && 16.0f <= maxIrcra)
        assertTrue(16.4f >= minIrcra && 16.4f <= maxIrcra)

        // 6A+ (16.5) ne devrait PAS être inclus
        assertFalse(16.5f <= maxIrcra)
    }
}
