package com.mastoc.app.data.model

/**
 * Type de prise dans un climb.
 */
enum class HoldType(val code: Char) {
    START('S'),   // Prise de départ
    OTHER('O'),   // Prise normale
    FEET('F'),    // Prise de pied obligatoire
    TOP('T');     // Prise finale

    companion object {
        fun fromCode(code: Char): HoldType? = entries.find { it.code == code }
    }
}

/**
 * Référence à une prise dans un climb avec son type.
 */
data class ClimbHold(
    val holdType: HoldType,
    val holdId: Int
)

/**
 * Modèle de domaine pour un climb (bloc).
 */
data class Climb(
    val id: String,
    val stoktId: String? = null,
    val faceId: String,
    val setterId: String? = null,
    val setterName: String? = null,
    val name: String,
    val holdsList: String,
    val gradeFont: String? = null,
    val gradeIrcra: Float? = null,
    val feetRule: String? = null,
    val description: String? = null,
    val isPrivate: Boolean = false,
    val climbedBy: Int = 0,
    val totalLikes: Int = 0,
    val source: String,
    val personalNotes: String? = null,
    val isProject: Boolean = false,
    val createdAt: String? = null
) {
    /**
     * Retourne la liste des IDs de holds utilisés par ce climb.
     */
    fun getHoldIds(): List<Int> {
        return getClimbHolds().map { it.holdId }
    }

    /**
     * Parse holdsList et retourne la liste des prises avec leur type.
     * Format: "S829279 S829528 O828906 T829009"
     * - S = Start (prise de départ)
     * - O = Other (prise normale)
     * - F = Feet (pied obligatoire)
     * - T = Top (prise finale)
     */
    fun getClimbHolds(): List<ClimbHold> {
        if (holdsList.isBlank()) return emptyList()
        return holdsList.split(" ", ",")
            .mapNotNull { token ->
                val trimmed = token.trim()
                if (trimmed.length > 1) {
                    val typeCode = trimmed[0]
                    val holdIdStr = trimmed.substring(1)
                    val holdType = HoldType.fromCode(typeCode)
                    val holdId = holdIdStr.toIntOrNull()
                    if (holdType != null && holdId != null) {
                        ClimbHold(holdType, holdId)
                    } else null
                } else null
            }
    }

    /**
     * Grade d'affichage (Font ou IRCRA converti).
     */
    val displayGrade: String
        get() = gradeFont ?: gradeIrcra?.let { "IRCRA $it" } ?: "?"
}
