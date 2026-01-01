package com.mastoc.app.data.local

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entity Room pour stocker les climbs en cache local.
 */
@Entity(tableName = "climbs")
data class ClimbEntity(
    @PrimaryKey
    val id: String,

    @ColumnInfo(name = "stokt_id")
    val stoktId: String? = null,

    @ColumnInfo(name = "face_id")
    val faceId: String,

    @ColumnInfo(name = "setter_id")
    val setterId: String? = null,

    @ColumnInfo(name = "setter_name")
    val setterName: String? = null,

    val name: String,

    @ColumnInfo(name = "holds_list")
    val holdsList: String,

    @ColumnInfo(name = "grade_font")
    val gradeFont: String? = null,

    @ColumnInfo(name = "grade_ircra")
    val gradeIrcra: Float? = null,

    @ColumnInfo(name = "feet_rule")
    val feetRule: String? = null,

    val description: String? = null,

    @ColumnInfo(name = "is_private")
    val isPrivate: Boolean = false,

    @ColumnInfo(name = "climbed_by")
    val climbedBy: Int = 0,

    @ColumnInfo(name = "total_likes")
    val totalLikes: Int = 0,

    val source: String,

    @ColumnInfo(name = "personal_notes")
    val personalNotes: String? = null,

    @ColumnInfo(name = "is_project")
    val isProject: Boolean = false,

    @ColumnInfo(name = "created_at")
    val createdAt: String? = null,

    @ColumnInfo(name = "cached_at")
    val cachedAt: Long = System.currentTimeMillis()
)
