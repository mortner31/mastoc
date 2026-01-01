package com.mastoc.app.data.settings

/**
 * Paramètres de rendu pour la visualisation des blocs.
 *
 * Fidélité au prototype Python (climb_renderer.py).
 */
data class RenderSettings(
    /**
     * Niveau de gris du fond (0.0 = couleur, 1.0 = gris complet).
     * Défaut Python: 0.85 (85%)
     */
    val grayLevel: Float = 0.85f,

    /**
     * Luminosité du fond (0.0 = noir, 1.0 = original).
     * Défaut Python: 0.25 (25%)
     */
    val brightness: Float = 0.25f,

    /**
     * Épaisseur du contour en pixels (1-20).
     * Défaut Python: 8
     */
    val contourWidth: Int = 8,

    /**
     * Afficher l'image de fond.
     */
    val showImage: Boolean = true,

    /**
     * Garder les prises du bloc en couleur originale (effet masque).
     * Défaut Python: true
     */
    val holdsInColor: Boolean = true
) {
    companion object {
        val DEFAULT = RenderSettings()
    }
}
