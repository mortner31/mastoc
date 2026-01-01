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
 * État UI pour la sélection de prises.
 */
data class HoldSelectorUiState(
    val face: Face? = null,
    val holds: List<Hold> = emptyList(),
    val selectedHoldIds: Set<Int> = emptySet(),
    val matchingClimbs: List<Climb> = emptyList(),
    val allClimbs: List<Climb> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

/**
 * ViewModel pour la sélection de prises et recherche de climbs.
 */
class HoldSelectorViewModel(
    application: Application,
    private val faceId: String
) : AndroidViewModel(application) {

    private val database = MastocDatabase.getInstance(application)
    private val repository = ClimbRepository(
        climbDao = database.climbDao(),
        holdDao = database.holdDao(),
        faceDao = database.faceDao()
    )

    private val _uiState = MutableStateFlow(HoldSelectorUiState())
    val uiState: StateFlow<HoldSelectorUiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            try {
                // Charger face et holds
                val result = repository.refreshFaceSetup(faceId)
                if (result.isSuccess) {
                    val faceWithHolds = result.getOrNull()!!
                    _uiState.value = _uiState.value.copy(
                        face = faceWithHolds.face,
                        holds = faceWithHolds.holds
                    )
                }

                // Charger tous les climbs de cette face
                repository.refreshClimbs(faceId = faceId)
                repository.observeClimbsByFace(faceId).collect { climbs ->
                    _uiState.value = _uiState.value.copy(
                        allClimbs = climbs,
                        isLoading = false
                    )
                    // Recalculer les climbs correspondants
                    updateMatchingClimbs()
                }
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }

    /**
     * Toggle la sélection d'une prise.
     */
    fun toggleHoldSelection(holdId: Int) {
        val currentSelected = _uiState.value.selectedHoldIds
        val newSelected = if (holdId in currentSelected) {
            currentSelected - holdId
        } else {
            currentSelected + holdId
        }

        _uiState.value = _uiState.value.copy(selectedHoldIds = newSelected)
        updateMatchingClimbs()
    }

    /**
     * Efface toutes les sélections.
     */
    fun clearSelection() {
        _uiState.value = _uiState.value.copy(
            selectedHoldIds = emptySet(),
            matchingClimbs = emptyList()
        )
    }

    /**
     * Met à jour la liste des climbs correspondants aux prises sélectionnées.
     */
    private fun updateMatchingClimbs() {
        val selectedIds = _uiState.value.selectedHoldIds
        if (selectedIds.isEmpty()) {
            _uiState.value = _uiState.value.copy(matchingClimbs = emptyList())
            return
        }

        // Trouver les climbs qui contiennent TOUTES les prises sélectionnées
        val matching = _uiState.value.allClimbs.filter { climb ->
            val climbHoldIds = climb.getHoldIds().toSet()
            selectedIds.all { it in climbHoldIds }
        }

        _uiState.value = _uiState.value.copy(matchingClimbs = matching)
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}

/**
 * Factory pour HoldSelectorViewModel.
 */
class HoldSelectorViewModelFactory(
    private val application: Application,
    private val faceId: String
) : androidx.lifecycle.ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(HoldSelectorViewModel::class.java)) {
            return HoldSelectorViewModel(application, faceId) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
