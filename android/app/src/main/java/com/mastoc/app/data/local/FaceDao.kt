package com.mastoc.app.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface FaceDao {

    @Query("SELECT * FROM faces ORDER BY id")
    fun getAllFaces(): Flow<List<FaceEntity>>

    @Query("SELECT * FROM faces WHERE gym_id = :gymId ORDER BY id")
    fun getFacesByGym(gymId: String): Flow<List<FaceEntity>>

    @Query("SELECT * FROM faces WHERE id = :id")
    suspend fun getFaceById(id: String): FaceEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertFaces(faces: List<FaceEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertFace(face: FaceEntity)

    @Query("DELETE FROM faces WHERE id = :id")
    suspend fun deleteFace(id: String)

    @Query("DELETE FROM faces")
    suspend fun deleteAll()
}
