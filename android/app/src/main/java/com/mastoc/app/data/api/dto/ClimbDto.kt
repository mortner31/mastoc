package com.mastoc.app.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO pour un climb (bloc) depuis l'API.
 */
data class ClimbDto(
    val id: String,
    @SerializedName("stokt_id")
    val stoktId: String? = null,
    @SerializedName("face_id")
    val faceId: String,
    @SerializedName("setter_id")
    val setterId: String? = null,
    @SerializedName("setter_name")
    val setterName: String? = null,
    val name: String,
    @SerializedName("holds_list")
    val holdsList: String,
    @SerializedName("grade_font")
    val gradeFont: String? = null,
    @SerializedName("grade_ircra")
    val gradeIrcra: Float? = null,
    @SerializedName("feet_rule")
    val feetRule: String? = null,
    val description: String? = null,
    @SerializedName("is_private")
    val isPrivate: Boolean = false,
    @SerializedName("climbed_by")
    val climbedBy: Int = 0,
    @SerializedName("total_likes")
    val totalLikes: Int = 0,
    val source: String,
    @SerializedName("personal_notes")
    val personalNotes: String? = null,
    @SerializedName("is_project")
    val isProject: Boolean = false,
    @SerializedName("created_at")
    val createdAt: String? = null
)

/**
 * DTO pour la liste paginée de climbs.
 */
data class ClimbsListDto(
    val results: List<ClimbDto>,
    val count: Int,
    val page: Int,
    @SerializedName("page_size")
    val pageSize: Int
)
