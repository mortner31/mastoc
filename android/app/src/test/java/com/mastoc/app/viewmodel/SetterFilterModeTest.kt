package com.mastoc.app.viewmodel

import org.junit.Assert.*
import org.junit.Test

/**
 * Tests unitaires pour SetterFilterMode et SetterInfo.
 */
class SetterFilterModeTest {

    @Test
    fun `all setter filter modes have display names`() {
        SetterFilterMode.entries.forEach { mode ->
            assertTrue(
                "Mode ${mode.name} should have non-empty displayName",
                mode.displayName.isNotBlank()
            )
        }
    }

    @Test
    fun `setter filter modes count is 3`() {
        assertEquals(3, SetterFilterMode.entries.size)
    }

    @Test
    fun `displayName is in French`() {
        assertEquals("Tous", SetterFilterMode.NONE.displayName)
        assertEquals("Inclure", SetterFilterMode.INCLUDE.displayName)
        assertEquals("Exclure", SetterFilterMode.EXCLUDE.displayName)
    }

    @Test
    fun `SetterInfo holds name and count`() {
        val info = SetterInfo("Alice Martin", 42)
        assertEquals("Alice Martin", info.name)
        assertEquals(42, info.climbCount)
    }

    @Test
    fun `SetterInfo equality works`() {
        val info1 = SetterInfo("Bob", 10)
        val info2 = SetterInfo("Bob", 10)
        val info3 = SetterInfo("Bob", 20)

        assertEquals(info1, info2)
        assertNotEquals(info1, info3)
    }
}
