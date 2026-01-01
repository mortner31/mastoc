package com.mastoc.app.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface HoldDao {

    @Query("SELECT * FROM holds WHERE face_id = :faceId ORDER BY id")
    fun getHoldsByFace(faceId: String): Flow<List<HoldEntity>>

    @Query("SELECT * FROM holds WHERE face_id = :faceId ORDER BY id")
    suspend fun getHoldsByFaceSync(faceId: String): List<HoldEntity>

    @Query("SELECT * FROM holds WHERE id = :id")
    suspend fun getHoldById(id: Int): HoldEntity?

    @Query("SELECT * FROM holds WHERE id IN (:ids)")
    suspend fun getHoldsByIds(ids: List<Int>): List<HoldEntity>

    @Query("SELECT COUNT(*) FROM holds WHERE face_id = :faceId")
    suspend fun getHoldCountByFace(faceId: String): Int

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertHolds(holds: List<HoldEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertHold(hold: HoldEntity)

    @Query("DELETE FROM holds WHERE face_id = :faceId")
    suspend fun deleteHoldsByFace(faceId: String)

    @Query("DELETE FROM holds")
    suspend fun deleteAll()
}
