package com.mastoc.app.data.model

/**
 * Modèle de domaine pour une face (configuration de mur).
 */
data class Face(
    val id: String,
    val stoktId: String? = null,
    val gymId: String,
    val picturePath: String,
    val pictureWidth: Int? = null,
    val pictureHeight: Int? = null,
    val holdsCount: Int = 0,
    val totalClimbs: Int = 0,
    val hasSymmetry: Boolean = false,
    val isActive: Boolean = true
) {
    /**
     * URL complète de l'image du mur.
     */
    val pictureUrl: String
        get() = if (picturePath.startsWith("http")) {
            picturePath
        } else {
            "https://mastoc-production.up.railway.app/static/$picturePath"
        }
}

/**
 * Face avec tous ses holds chargés.
 */
data class FaceWithHolds(
    val face: Face,
    val holds: List<Hold>
)
