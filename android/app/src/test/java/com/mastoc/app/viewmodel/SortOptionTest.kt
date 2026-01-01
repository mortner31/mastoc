package com.mastoc.app.viewmodel

import org.junit.Assert.*
import org.junit.Test

/**
 * Tests unitaires pour SortOption.
 */
class SortOptionTest {

    @Test
    fun `all sort options have display names`() {
        SortOption.entries.forEach { option ->
            assertTrue(
                "Option ${option.name} should have non-empty displayName",
                option.displayName.isNotBlank()
            )
        }
    }

    @Test
    fun `sort options count is correct`() {
        assertEquals(7, SortOption.entries.size)
    }

    @Test
    fun `displayName is in French`() {
        assertEquals("Date (récent)", SortOption.DATE_DESC.displayName)
        assertEquals("Grade (facile)", SortOption.GRADE_ASC.displayName)
        assertEquals("Popularité", SortOption.POPULARITY.displayName)
    }
}
