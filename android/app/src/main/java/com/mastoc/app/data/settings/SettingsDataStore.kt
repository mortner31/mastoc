package com.mastoc.app.data.settings

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

/**
 * Thèmes disponibles dans l'application.
 */
enum class AppTheme(val displayName: String) {
    COLORFUL("Coloré"),
    BLUE("Bleu"),
    GRAY("Gris")
}

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "mastoc_settings")

/**
 * DataStore pour les préférences utilisateur.
 */
class SettingsDataStore(private val context: Context) {

    companion object {
        private val THEME_KEY = stringPreferencesKey("app_theme")
        private val RENDER_GRAY_LEVEL = floatPreferencesKey("render_gray_level")
        private val RENDER_BRIGHTNESS = floatPreferencesKey("render_brightness")
        private val RENDER_CONTOUR_WIDTH = intPreferencesKey("render_contour_width")
        private val RENDER_SHOW_IMAGE = booleanPreferencesKey("render_show_image")
        private val RENDER_HOLDS_IN_COLOR = booleanPreferencesKey("render_holds_in_color")
    }

    /**
     * Flow du thème actuel.
     */
    val appTheme: Flow<AppTheme> = context.dataStore.data.map { preferences ->
        val themeName = preferences[THEME_KEY] ?: AppTheme.COLORFUL.name
        try {
            AppTheme.valueOf(themeName)
        } catch (e: IllegalArgumentException) {
            AppTheme.COLORFUL
        }
    }

    /**
     * Sauvegarde le thème sélectionné.
     */
    suspend fun setAppTheme(theme: AppTheme) {
        context.dataStore.edit { preferences ->
            preferences[THEME_KEY] = theme.name
        }
    }

    /**
     * Flow des paramètres de rendu.
     */
    val renderSettings: Flow<RenderSettings> = context.dataStore.data.map { preferences ->
        RenderSettings(
            grayLevel = preferences[RENDER_GRAY_LEVEL] ?: RenderSettings.DEFAULT.grayLevel,
            brightness = preferences[RENDER_BRIGHTNESS] ?: RenderSettings.DEFAULT.brightness,
            contourWidth = preferences[RENDER_CONTOUR_WIDTH] ?: RenderSettings.DEFAULT.contourWidth,
            showImage = preferences[RENDER_SHOW_IMAGE] ?: RenderSettings.DEFAULT.showImage,
            holdsInColor = preferences[RENDER_HOLDS_IN_COLOR] ?: RenderSettings.DEFAULT.holdsInColor
        )
    }

    /**
     * Sauvegarde les paramètres de rendu.
     */
    suspend fun setRenderSettings(settings: RenderSettings) {
        context.dataStore.edit { preferences ->
            preferences[RENDER_GRAY_LEVEL] = settings.grayLevel
            preferences[RENDER_BRIGHTNESS] = settings.brightness
            preferences[RENDER_CONTOUR_WIDTH] = settings.contourWidth
            preferences[RENDER_SHOW_IMAGE] = settings.showImage
            preferences[RENDER_HOLDS_IN_COLOR] = settings.holdsInColor
        }
    }
}
