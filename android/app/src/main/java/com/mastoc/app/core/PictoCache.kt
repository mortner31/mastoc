package com.mastoc.app.core

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.LruCache
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

/**
 * Cache pour les pictos générés.
 *
 * Stockage à deux niveaux :
 * 1. LruCache mémoire pour accès ultra-rapide
 * 2. Fichiers PNG sur disque pour persistance
 */
class PictoCache(private val context: Context) {

    companion object {
        private const val CACHE_DIR_NAME = "pictos"
        private const val MEMORY_CACHE_SIZE = 50 // Nombre de pictos en mémoire
        private const val PNG_QUALITY = 90
    }

    // Cache mémoire LRU
    private val memoryCache = LruCache<String, Bitmap>(MEMORY_CACHE_SIZE)

    // Répertoire cache sur disque
    private val cacheDir: File by lazy {
        File(context.cacheDir, CACHE_DIR_NAME).apply {
            if (!exists()) mkdirs()
        }
    }

    /**
     * Récupère un picto depuis le cache (mémoire ou disque).
     *
     * @param climbId ID du climb
     * @return Bitmap ou null si pas en cache
     */
    suspend fun getPicto(climbId: String): Bitmap? = withContext(Dispatchers.IO) {
        // D'abord vérifier le cache mémoire
        memoryCache.get(climbId)?.let { return@withContext it }

        // Sinon charger depuis le disque
        val file = getPictoFile(climbId)
        if (file.exists()) {
            val bitmap = BitmapFactory.decodeFile(file.absolutePath)
            if (bitmap != null) {
                // Ajouter au cache mémoire
                memoryCache.put(climbId, bitmap)
            }
            return@withContext bitmap
        }

        null
    }

    /**
     * Sauvegarde un picto dans le cache.
     *
     * @param climbId ID du climb
     * @param bitmap Bitmap du picto
     */
    suspend fun savePicto(climbId: String, bitmap: Bitmap) = withContext(Dispatchers.IO) {
        // Sauvegarder en mémoire
        memoryCache.put(climbId, bitmap)

        // Sauvegarder sur disque
        val file = getPictoFile(climbId)
        try {
            FileOutputStream(file).use { out ->
                bitmap.compress(Bitmap.CompressFormat.PNG, PNG_QUALITY, out)
            }
        } catch (e: Exception) {
            // Ignorer les erreurs d'écriture
        }
    }

    /**
     * Vérifie si un picto est en cache.
     */
    fun hasPicto(climbId: String): Boolean {
        // Vérifier mémoire puis disque
        return memoryCache.get(climbId) != null || getPictoFile(climbId).exists()
    }

    /**
     * Supprime un picto du cache.
     */
    suspend fun removePicto(climbId: String) = withContext(Dispatchers.IO) {
        memoryCache.remove(climbId)
        getPictoFile(climbId).delete()
    }

    /**
     * Vide tout le cache (mémoire et disque).
     */
    suspend fun clearAll() = withContext(Dispatchers.IO) {
        memoryCache.evictAll()
        cacheDir.listFiles()?.forEach { it.delete() }
    }

    /**
     * Invalide les pictos qui pourraient être obsolètes.
     * Appelé quand les holds changent (après sync).
     */
    suspend fun invalidateForFace(faceId: String) = withContext(Dispatchers.IO) {
        // Pour l'instant, on invalide tout le cache quand une face change
        // On pourrait améliorer en gardant une trace des faces par climb
        clearAll()
    }

    /**
     * Retourne la taille du cache disque en bytes.
     */
    fun getDiskCacheSize(): Long {
        return cacheDir.listFiles()?.sumOf { it.length() } ?: 0L
    }

    /**
     * Retourne le nombre de pictos en cache mémoire.
     */
    fun getMemoryCacheCount(): Int {
        return memoryCache.size()
    }

    /**
     * Retourne le nombre de pictos en cache disque.
     */
    fun getDiskCacheCount(): Int {
        return cacheDir.listFiles()?.size ?: 0
    }

    /**
     * Fichier cache pour un climb donné.
     */
    private fun getPictoFile(climbId: String): File {
        // Nettoyer l'ID pour en faire un nom de fichier valide
        val safeId = climbId.replace(Regex("[^a-zA-Z0-9_-]"), "_")
        return File(cacheDir, "$safeId.png")
    }
}
