package com.mastoc.app.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO pour un hold (prise) depuis l'API.
 * Utilisé dans FaceSetupDto.
 */
data class HoldDto(
    val id: Int,
    @SerializedName("stokt_id")
    val stoktId: Int? = null,
    @SerializedName("polygon_str")
    val polygonStr: String,
    @SerializedName("centroid_x")
    val centroidX: Float? = null,
    @SerializedName("centroid_y")
    val centroidY: Float? = null,
    @SerializedName("path_str")
    val pathStr: String? = null,
    val area: Float? = null,
    @SerializedName("touch_polygon_str")
    val touchPolygonStr: String = "",
    @SerializedName("centroid_str")
    val centroidStr: String = "",
    @SerializedName("top_polygon_str")
    val topPolygonStr: String = "",
    @SerializedName("center_tape_str")
    val centerTapeStr: String = "",
    @SerializedName("right_tape_str")
    val rightTapeStr: String = "",
    @SerializedName("left_tape_str")
    val leftTapeStr: String = ""
)
