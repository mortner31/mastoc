package com.mastoc.app.data.api

import com.mastoc.app.data.api.dto.ClimbDto
import com.mastoc.app.data.api.dto.ClimbsListDto
import com.mastoc.app.data.api.dto.FaceDto
import com.mastoc.app.data.api.dto.FaceSetupDto
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * Service Retrofit pour l'API Mastoc (Railway).
 */
interface MastocApiService {

    // --- Health ---

    @GET("health")
    suspend fun health(): Response<Map<String, String>>

    // --- Climbs ---

    @GET("api/climbs")
    suspend fun getClimbs(
        @Query("face_id") faceId: String? = null,
        @Query("grade_min") gradeMin: String? = null,
        @Query("grade_max") gradeMax: String? = null,
        @Query("setter_id") setterId: String? = null,
        @Query("search") search: String? = null,
        @Query("source") source: String? = null,
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 50
    ): Response<ClimbsListDto>

    @GET("api/climbs/{climbId}")
    suspend fun getClimb(
        @Path("climbId") climbId: String
    ): Response<ClimbDto>

    // --- Faces ---

    @GET("api/faces")
    suspend fun getFaces(
        @Query("gym_id") gymId: String? = null
    ): Response<List<FaceDto>>

    @GET("api/faces/{faceId}")
    suspend fun getFace(
        @Path("faceId") faceId: String
    ): Response<FaceDto>

    @GET("api/faces/{faceId}/setup")
    suspend fun getFaceSetup(
        @Path("faceId") faceId: String
    ): Response<FaceSetupDto>

    companion object {
        const val BASE_URL = "https://mastoc-production.up.railway.app/"
    }
}
