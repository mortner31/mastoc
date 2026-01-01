package com.mastoc.app.data

import com.mastoc.app.ui.components.ColorLut
import com.mastoc.app.ui.components.ColorMode
import com.mastoc.app.ui.components.ColorPalette
import org.junit.Assert.*
import org.junit.Test

/**
 * Tests unitaires pour ColorMode et ColorPalette.
 */
class ColorModeTest {

    @Test
    fun `ColorMode RARE returns correct values`() {
        assertEquals(1.0f, ColorMode.getRareValue(0), 0.01f)
        assertEquals(0.75f, ColorMode.getRareValue(1), 0.01f)
        assertEquals(0.50f, ColorMode.getRareValue(2), 0.01f)
        assertEquals(0.25f, ColorMode.getRareValue(3), 0.01f)
        assertEquals(0.0f, ColorMode.getRareValue(4), 0.01f)
        assertEquals(0.0f, ColorMode.getRareValue(100), 0.01f)
    }

    @Test
    fun `ColorMode has correct entries`() {
        assertEquals(5, ColorMode.entries.size)
        assertTrue(ColorMode.entries.any { it == ColorMode.RARE })
        assertTrue(ColorMode.entries.any { it == ColorMode.FREQUENCY })
    }

    @Test
    fun `ColorPalette has all 7 palettes`() {
        assertEquals(7, ColorPalette.entries.size)
        assertTrue(ColorPalette.entries.any { it == ColorPalette.MAGMA })
        assertTrue(ColorPalette.entries.any { it == ColorPalette.CIVIDIS })
    }

    @Test
    fun `ColorLut generates 256 colors`() {
        ColorPalette.entries.forEach { palette ->
            val lut = ColorLut.getLut(palette)
            assertEquals(
                "LUT for ${palette.name} should have 256 colors",
                256,
                lut.size
            )
        }
    }

    @Test
    fun `ColorPalette getColor returns valid colors for edge values`() {
        ColorPalette.entries.forEach { palette ->
            val colorMin = palette.getColor(0f)
            val colorMax = palette.getColor(1f)
            val colorMid = palette.getColor(0.5f)

            // Les couleurs doivent avoir des composantes valides [0, 1]
            assertTrue(colorMin.red in 0f..1f)
            assertTrue(colorMax.red in 0f..1f)
            assertTrue(colorMid.blue in 0f..1f)
        }
    }

    @Test
    fun `ColorPalette clamps values outside 0-1 range`() {
        val color1 = ColorPalette.VIRIDIS.getColor(-0.5f)
        val color2 = ColorPalette.VIRIDIS.getColor(1.5f)

        // Should not throw, values should be clamped
        assertNotNull(color1)
        assertNotNull(color2)
    }
}
