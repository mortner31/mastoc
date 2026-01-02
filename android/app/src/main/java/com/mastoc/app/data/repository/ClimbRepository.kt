package com.mastoc.app.data.repository

import com.mastoc.app.data.api.ApiClient
import com.mastoc.app.data.local.ClimbDao
import com.mastoc.app.data.local.FaceDao
import com.mastoc.app.data.local.HoldDao
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.Face
import com.mastoc.app.data.model.FaceWithHolds
import com.mastoc.app.data.model.Hold
import com.mastoc.app.data.toDomain
import com.mastoc.app.data.toEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

/**
 * Repository pour accéder aux données climbs, faces et holds.
 * Combine API réseau et cache local Room.
 */
class ClimbRepository(
    private val climbDao: ClimbDao,
    private val holdDao: HoldDao,
    private val faceDao: FaceDao
) {
    private val api = ApiClient.apiService

    // --- Climbs ---

    /**
     * Récupère les climbs depuis l'API et les cache localement.
     */
    suspend fun refreshClimbs(
        faceId: String? = null,
        search: String? = null,
        page: Int = 1,
        pageSize: Int = 500
    ): Result<List<Climb>> {
        return try {
            val response = api.getClimbs(
                faceId = faceId,
                search = search,
                page = page,
                pageSize = pageSize
            )
            if (response.isSuccessful) {
                val climbsDto = response.body()?.results ?: emptyList()
                val entities = climbsDto.map { it.toEntity() }
                climbDao.insertClimbs(entities)
                Result.success(climbsDto.map { it.toDomain() })
            } else {
                Result.failure(Exception("API error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Observe les climbs depuis le cache local.
     */
    fun observeClimbs(): Flow<List<Climb>> {
        return climbDao.getAllClimbs().map { entities ->
            entities.map { it.toDomain() }
        }
    }

    /**
     * Observe les climbs d'une face spécifique.
     */
    fun observeClimbsByFace(faceId: String): Flow<List<Climb>> {
        return climbDao.getClimbsByFace(faceId).map { entities ->
            entities.map { it.toDomain() }
        }
    }

    /**
     * Récupère un climb par ID.
     */
    suspend fun getClimb(climbId: String): Climb? {
        return climbDao.getClimbById(climbId)?.toDomain()
    }

    // --- Face Setup (avec holds) ---

    /**
     * Récupère le setup complet d'une face depuis l'API.
     */
    suspend fun refreshFaceSetup(faceId: String): Result<FaceWithHolds> {
        return try {
            val response = api.getFaceSetup(faceId)
            if (response.isSuccessful) {
                val setup = response.body()
                    ?: return Result.failure(Exception("Empty response"))

                // Sauvegarder la face
                val faceEntity = setup.toEntity()
                faceDao.insertFace(faceEntity)

                // Sauvegarder les holds
                val holdEntities = setup.holds.map { it.toEntity(faceId) }
                holdDao.deleteHoldsByFace(faceId) // Clear old holds
                holdDao.insertHolds(holdEntities)

                // Retourner le domaine
                val face = faceEntity.toDomain()
                val holds = holdEntities.map { it.toDomain() }
                Result.success(FaceWithHolds(face, holds))
            } else {
                Result.failure(Exception("API error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Récupère une face depuis le cache local.
     */
    suspend fun getFace(faceId: String): Face? {
        return faceDao.getFaceById(faceId)?.toDomain()
    }

    /**
     * Observe les holds d'une face.
     */
    fun observeHoldsByFace(faceId: String): Flow<List<Hold>> {
        return holdDao.getHoldsByFace(faceId).map { entities ->
            entities.map { it.toDomain() }
        }
    }

    /**
     * Récupère les holds d'une face (synchrone).
     */
    suspend fun getHoldsByFace(faceId: String): List<Hold> {
        return holdDao.getHoldsByFaceSync(faceId).map { it.toDomain() }
    }

    /**
     * Récupère les holds par leurs IDs.
     */
    suspend fun getHoldsByIds(ids: List<Int>): List<Hold> {
        return holdDao.getHoldsByIds(ids).map { it.toDomain() }
    }

    // --- Faces List ---

    /**
     * Récupère la liste des faces depuis l'API.
     */
    suspend fun refreshFaces(): Result<List<Face>> {
        return try {
            val response = api.getFaces()
            if (response.isSuccessful) {
                val facesDto = response.body() ?: emptyList()
                val entities = facesDto.map { it.toEntity() }
                faceDao.insertFaces(entities)
                Result.success(facesDto.map { it.toDomain() })
            } else {
                Result.failure(Exception("API error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Observe les faces depuis le cache local.
     */
    fun observeFaces(): Flow<List<Face>> {
        return faceDao.getAllFaces().map { entities ->
            entities.map { it.toDomain() }
        }
    }

    // --- Health Check ---

    /**
     * Vérifie la connexion à l'API.
     */
    suspend fun checkHealth(): Boolean {
        return try {
            val response = api.health()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }
}
