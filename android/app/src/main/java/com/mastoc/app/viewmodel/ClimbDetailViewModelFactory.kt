package com.mastoc.app.viewmodel

import android.app.Application
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider

/**
 * Factory pour créer ClimbDetailViewModel avec un climbId.
 */
class ClimbDetailViewModelFactory(
    private val application: Application,
    private val climbId: String
) : ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(ClimbDetailViewModel::class.java)) {
            return ClimbDetailViewModel(application, climbId) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
