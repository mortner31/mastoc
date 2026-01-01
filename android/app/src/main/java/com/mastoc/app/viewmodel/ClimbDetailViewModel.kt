package com.mastoc.app.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.mastoc.app.data.local.MastocDatabase
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.Face
import com.mastoc.app.data.model.Hold
import com.mastoc.app.data.repository.ClimbRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * État UI pour le détail d'un climb.
 */
data class ClimbDetailUiState(
    val climb: Climb? = null,
    val face: Face? = null,
    val allHolds: List<Hold> = emptyList(),
    val climbHolds: List<Hold> = emptyList(),
    val holdsMap: Map<Int, Hold> = emptyMap(),
    val isLoading: Boolean = false,
    val error: String? = null
)

/**
 * ViewModel pour l'écran détail climb.
 */
class ClimbDetailViewModel(
    application: Application,
    private val climbId: String
) : AndroidViewModel(application) {

    private val database = MastocDatabase.getInstance(application)
    private val repository = ClimbRepository(
        climbDao = database.climbDao(),
        holdDao = database.holdDao(),
        faceDao = database.faceDao()
    )

    private val _uiState = MutableStateFlow(ClimbDetailUiState())
    val uiState: StateFlow<ClimbDetailUiState> = _uiState.asStateFlow()

    init {
        loadClimb()
    }

    private fun loadClimb() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            try {
                // Charger le climb
                val climb = repository.getClimb(climbId)
                if (climb == null) {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = "Climb introuvable"
                    )
                    return@launch
                }

                _uiState.value = _uiState.value.copy(climb = climb)

                // Charger la face et les holds
                val faceId = climb.faceId
                val face = repository.getFace(faceId)

                // Si pas de face en cache, essayer de la charger
                if (face == null) {
                    val result = repository.refreshFaceSetup(faceId)
                    if (result.isSuccess) {
                        val faceWithHolds = result.getOrNull()!!
                        updateWithFaceData(climb, faceWithHolds.face, faceWithHolds.holds)
                    } else {
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            error = result.exceptionOrNull()?.message
                        )
                    }
                } else {
                    // Face en cache, charger les holds
                    val holds = repository.getHoldsByFace(faceId)
                    updateWithFaceData(climb, face, holds)
                }
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }

    private fun updateWithFaceData(climb: Climb, face: Face, allHolds: List<Hold>) {
        // Créer une map des holds par ID (id et stoktId)
        val holdsMap = mutableMapOf<Int, Hold>()
        allHolds.forEach { hold ->
            holdsMap[hold.id] = hold
            hold.stoktId?.let { holdsMap[it] = hold }
        }

        // Filtrer les holds utilisés par ce climb
        val holdIds = climb.getHoldIds().toSet()
        val climbHolds = allHolds.filter { it.id in holdIds || it.stoktId in holdIds }

        _uiState.value = _uiState.value.copy(
            face = face,
            allHolds = allHolds,
            climbHolds = climbHolds,
            holdsMap = holdsMap,
            isLoading = false
        )
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)

            val climb = _uiState.value.climb ?: return@launch
            val result = repository.refreshFaceSetup(climb.faceId)

            if (result.isSuccess) {
                val faceWithHolds = result.getOrNull()!!
                updateWithFaceData(climb, faceWithHolds.face, faceWithHolds.holds)
            } else {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = result.exceptionOrNull()?.message
                )
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
