package com.mastoc.app.ui.components

/**
 * Table de correspondance Grade Fontainebleau ↔ IRCRA.
 * Basée sur le code Python mastoc/src/mastoc/gui/widgets/level_slider.py
 */
data class GradeEntry(
    val font: String,
    val ircra: Float
)

/**
 * Liste ordonnée des grades Fontainebleau avec leurs valeurs IRCRA.
 */
val FONT_GRADES = listOf(
    GradeEntry("4", 12.0f),
    GradeEntry("4+", 13.25f),
    GradeEntry("5", 14.25f),
    GradeEntry("5+", 15.0f),
    GradeEntry("6A", 15.5f),
    GradeEntry("6A+", 16.5f),
    GradeEntry("6B", 17.5f),
    GradeEntry("6B+", 18.0f),
    GradeEntry("6C", 18.5f),
    GradeEntry("6C+", 19.5f),
    GradeEntry("7A", 20.5f),
    GradeEntry("7A+", 21.5f),
    GradeEntry("7B", 22.5f),
    GradeEntry("7B+", 23.5f),
    GradeEntry("7C", 24.5f),
    GradeEntry("8A", 26.5f)
)

/**
 * Nombre total de grades disponibles.
 */
val GRADE_COUNT = FONT_GRADES.size

/**
 * Convertit un index de slider (0-15) en grade Fontainebleau.
 */
fun indexToFont(index: Int): String {
    val safeIndex = index.coerceIn(0, FONT_GRADES.lastIndex)
    return FONT_GRADES[safeIndex].font
}

/**
 * Convertit un index de slider (0-15) en valeur IRCRA.
 */
fun indexToIrcra(index: Int): Float {
    val safeIndex = index.coerceIn(0, FONT_GRADES.lastIndex)
    return FONT_GRADES[safeIndex].ircra
}

/**
 * Calcule la borne IRCRA minimum pour un index donné.
 * Retourne la valeur IRCRA du grade.
 */
fun getMinIrcraForIndex(index: Int): Float {
    return indexToIrcra(index)
}

/**
 * Calcule la borne IRCRA maximum pour un index donné.
 * Utilise la logique epsilon : borne = IRCRA du grade suivant - 0.01
 * Cela permet d'inclure tous les blocs du grade sélectionné.
 */
fun getMaxIrcraForIndex(index: Int): Float {
    val safeIndex = index.coerceIn(0, FONT_GRADES.lastIndex)
    return if (safeIndex < FONT_GRADES.lastIndex) {
        // Borne = valeur IRCRA du grade suivant - epsilon
        FONT_GRADES[safeIndex + 1].ircra - 0.01f
    } else {
        // Pour le dernier grade (8A), on prend une valeur haute
        30.0f
    }
}

/**
 * Trouve l'index le plus proche pour une valeur IRCRA donnée.
 */
fun ircraToIndex(ircra: Float): Int {
    for (i in FONT_GRADES.indices) {
        if (ircra <= FONT_GRADES[i].ircra) {
            return i
        }
    }
    return FONT_GRADES.lastIndex
}

/**
 * Convertit une valeur IRCRA en grade Fontainebleau (approximation).
 */
fun ircraToFont(ircra: Float): String {
    // Trouver le grade le plus proche
    for (i in FONT_GRADES.indices.reversed()) {
        if (ircra >= FONT_GRADES[i].ircra) {
            return FONT_GRADES[i].font
        }
    }
    return FONT_GRADES.first().font
}
