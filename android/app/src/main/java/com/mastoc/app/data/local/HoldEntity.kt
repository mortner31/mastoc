package com.mastoc.app.data.local

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entity Room pour stocker les holds en cache local.
 */
@Entity(tableName = "holds")
data class HoldEntity(
    @PrimaryKey
    val id: Int,

    @ColumnInfo(name = "stokt_id")
    val stoktId: Int? = null,

    @ColumnInfo(name = "face_id")
    val faceId: String,

    @ColumnInfo(name = "polygon_str")
    val polygonStr: String,

    @ColumnInfo(name = "centroid_x")
    val centroidX: Float? = null,

    @ColumnInfo(name = "centroid_y")
    val centroidY: Float? = null,

    @ColumnInfo(name = "path_str")
    val pathStr: String? = null,

    val area: Float? = null,

    @ColumnInfo(name = "center_tape_str")
    val centerTapeStr: String = "",

    @ColumnInfo(name = "right_tape_str")
    val rightTapeStr: String = "",

    @ColumnInfo(name = "left_tape_str")
    val leftTapeStr: String = "",

    @ColumnInfo(name = "cached_at")
    val cachedAt: Long = System.currentTimeMillis()
)
