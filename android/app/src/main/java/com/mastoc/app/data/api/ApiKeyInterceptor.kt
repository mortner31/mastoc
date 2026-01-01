package com.mastoc.app.data.api

import okhttp3.Interceptor
import okhttp3.Response

/**
 * Interceptor OkHttp pour ajouter le header X-API-Key à toutes les requêtes.
 */
class ApiKeyInterceptor(private val apiKey: String) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val requestWithApiKey = originalRequest.newBuilder()
            .header("X-API-Key", apiKey)
            .build()
        return chain.proceed(requestWithApiKey)
    }

    companion object {
        const val DEFAULT_API_KEY = "mastoc-2025-1213-brosse-lesprises-secret"
    }
}
