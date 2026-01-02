package com.mastoc.app.core

import android.content.Context
import android.graphics.Bitmap
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.Hold
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Gestionnaire de pictos combinant génération et cache.
 *
 * Point d'entrée unique pour obtenir les pictos des climbs.
 */
class PictoManager(context: Context) {

    private val generator = PictoGenerator()
    private val cache = PictoCache(context)

    /**
     * Obtient le picto d'un climb, le génère si nécessaire.
     *
     * @param climb Le climb
     * @param holdsMap Map des holds par ID
     * @param topHoldIds IDs des prises populaires (pour le fond gris)
     * @param size Taille du picto
     * @return Bitmap du picto ou null
     */
    suspend fun getPicto(
        climb: Climb,
        holdsMap: Map<Int, Hold>,
        topHoldIds: Set<Int> = emptySet(),
        size: Int = PictoGenerator.DEFAULT_SIZE
    ): Bitmap? = withContext(Dispatchers.Default) {
        // Vérifier le cache d'abord
        cache.getPicto(climb.id)?.let { return@withContext it }

        // Générer le picto
        val bitmap = generator.generatePicto(climb, holdsMap, size, topHoldIds)
            ?: return@withContext null

        // Sauvegarder dans le cache
        cache.savePicto(climb.id, bitmap)

        bitmap
    }

    /**
     * Vérifie si un picto est déjà en cache.
     */
    fun hasPicto(climbId: String): Boolean {
        return cache.hasPicto(climbId)
    }

    /**
     * Pré-génère les pictos pour une liste de climbs.
     * Utile pour pré-charger au scroll.
     *
     * @param climbs Liste des climbs
     * @param holdsMap Map des holds par ID
     * @param topHoldIds IDs des prises populaires
     * @param onProgress Callback de progression (current, total)
     */
    suspend fun preloadPictos(
        climbs: List<Climb>,
        holdsMap: Map<Int, Hold>,
        topHoldIds: Set<Int> = emptySet(),
        onProgress: ((current: Int, total: Int) -> Unit)? = null
    ) = withContext(Dispatchers.Default) {
        val toGenerate = climbs.filterNot { cache.hasPicto(it.id) }
        val total = toGenerate.size

        toGenerate.forEachIndexed { index, climb ->
            val bitmap = generator.generatePicto(climb, holdsMap, topHoldIds = topHoldIds)
            if (bitmap != null) {
                cache.savePicto(climb.id, bitmap)
            }
            onProgress?.invoke(index + 1, total)
        }
    }

    /**
     * Invalide le cache (après modification des holds).
     */
    suspend fun invalidateCache() {
        cache.clearAll()
    }

    /**
     * Regénère le picto d'un climb spécifique.
     * Supprime du cache et force une nouvelle génération.
     */
    suspend fun regeneratePicto(
        climb: Climb,
        holdsMap: Map<Int, Hold>,
        topHoldIds: Set<Int> = emptySet(),
        size: Int = PictoGenerator.DEFAULT_SIZE
    ): Bitmap? = withContext(Dispatchers.Default) {
        // Supprimer du cache
        cache.removePicto(climb.id)

        // Regénérer
        val bitmap = generator.generatePicto(climb, holdsMap, size, topHoldIds)
            ?: return@withContext null

        // Sauvegarder dans le cache
        cache.savePicto(climb.id, bitmap)

        bitmap
    }

    /**
     * Statistiques du cache.
     */
    data class CacheStats(
        val memoryCount: Int,
        val diskCount: Int,
        val diskSizeBytes: Long
    )

    fun getCacheStats(): CacheStats {
        return CacheStats(
            memoryCount = cache.getMemoryCacheCount(),
            diskCount = cache.getDiskCacheCount(),
            diskSizeBytes = cache.getDiskCacheSize()
        )
    }
}
