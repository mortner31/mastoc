package com.mastoc.app.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface ClimbDao {

    @Query("SELECT * FROM climbs ORDER BY created_at DESC")
    fun getAllClimbs(): Flow<List<ClimbEntity>>

    @Query("SELECT * FROM climbs WHERE face_id = :faceId ORDER BY created_at DESC")
    fun getClimbsByFace(faceId: String): Flow<List<ClimbEntity>>

    @Query("SELECT * FROM climbs WHERE id = :id")
    suspend fun getClimbById(id: String): ClimbEntity?

    @Query("""
        SELECT * FROM climbs
        WHERE (:faceId IS NULL OR face_id = :faceId)
        AND (:search IS NULL OR name LIKE '%' || :search || '%')
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    suspend fun getClimbsFiltered(
        faceId: String?,
        search: String?,
        limit: Int,
        offset: Int
    ): List<ClimbEntity>

    @Query("SELECT COUNT(*) FROM climbs WHERE face_id = :faceId")
    suspend fun getClimbCountByFace(faceId: String): Int

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertClimbs(climbs: List<ClimbEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertClimb(climb: ClimbEntity)

    @Query("DELETE FROM climbs WHERE id = :id")
    suspend fun deleteClimb(id: String)

    @Query("DELETE FROM climbs WHERE face_id = :faceId")
    suspend fun deleteClimbsByFace(faceId: String)

    @Query("DELETE FROM climbs")
    suspend fun deleteAll()
}
