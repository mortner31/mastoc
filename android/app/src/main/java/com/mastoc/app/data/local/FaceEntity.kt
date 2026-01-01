package com.mastoc.app.data.local

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entity Room pour stocker les faces (configurations de mur) en cache local.
 */
@Entity(tableName = "faces")
data class FaceEntity(
    @PrimaryKey
    val id: String,

    @ColumnInfo(name = "stokt_id")
    val stoktId: String? = null,

    @ColumnInfo(name = "gym_id")
    val gymId: String,

    @ColumnInfo(name = "picture_path")
    val picturePath: String,

    @ColumnInfo(name = "picture_width")
    val pictureWidth: Int? = null,

    @ColumnInfo(name = "picture_height")
    val pictureHeight: Int? = null,

    @ColumnInfo(name = "holds_count")
    val holdsCount: Int = 0,

    @ColumnInfo(name = "total_climbs")
    val totalClimbs: Int = 0,

    @ColumnInfo(name = "has_symmetry")
    val hasSymmetry: Boolean = false,

    @ColumnInfo(name = "is_active")
    val isActive: Boolean = true,

    @ColumnInfo(name = "cached_at")
    val cachedAt: Long = System.currentTimeMillis()
)
