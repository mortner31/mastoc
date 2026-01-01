package com.mastoc.app.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO pour l'image d'une face.
 */
data class PictureDto(
    val name: String,
    val width: Int,
    val height: Int
)

/**
 * DTO pour une face (liste).
 */
data class FaceDto(
    val id: String,
    @SerializedName("stokt_id")
    val stoktId: String? = null,
    @SerializedName("gym_id")
    val gymId: String,
    @SerializedName("picture_path")
    val picturePath: String,
    @SerializedName("picture_width")
    val pictureWidth: Int? = null,
    @SerializedName("picture_height")
    val pictureHeight: Int? = null,
    @SerializedName("holds_count")
    val holdsCount: Int = 0,
    @SerializedName("climbs_count")
    val climbsCount: Int = 0
)

/**
 * DTO pour le setup complet d'une face avec tous ses holds.
 */
data class FaceSetupDto(
    val id: String,
    @SerializedName("stokt_id")
    val stoktId: String? = null,
    @SerializedName("is_active")
    val isActive: Boolean = true,
    @SerializedName("total_climbs")
    val totalClimbs: Int = 0,
    val picture: PictureDto? = null,
    @SerializedName("small_picture")
    val smallPicture: PictureDto? = null,
    @SerializedName("feet_rules_options")
    val feetRulesOptions: List<String> = emptyList(),
    @SerializedName("has_symmetry")
    val hasSymmetry: Boolean = false,
    val holds: List<HoldDto> = emptyList()
)
