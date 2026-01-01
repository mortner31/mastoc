package com.mastoc.app.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.mastoc.app.data.local.MastocDatabase
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.repository.ClimbRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * Options de tri pour la liste des climbs.
 */
enum class SortOption(val displayName: String) {
    DATE_DESC("Date (récent)"),
    DATE_ASC("Date (ancien)"),
    GRADE_ASC("Grade (facile)"),
    GRADE_DESC("Grade (difficile)"),
    NAME_ASC("Nom (A-Z)"),
    NAME_DESC("Nom (Z-A)"),
    POPULARITY("Popularité")
}

/**
 * État UI pour la liste des climbs.
 */
data class ClimbListUiState(
    val climbs: List<Climb> = emptyList(),
    val filteredClimbs: List<Climb> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val error: String? = null,
    val searchQuery: String = "",
    // Filtres grade (IRCRA)
    val minGrade: Float = 0f,
    val maxGrade: Float = 100f,
    val gradeRange: ClosedFloatingPointRange<Float> = 0f..100f,
    // Filtre setter
    val selectedSetter: String? = null,
    val availableSetters: List<String> = emptyList(),
    // Tri
    val sortOption: SortOption = SortOption.DATE_DESC,
    // Panneau filtres visible
    val showFilters: Boolean = false
)

/**
 * ViewModel pour l'écran liste des climbs.
 */
class ClimbListViewModel(application: Application) : AndroidViewModel(application) {

    private val database = MastocDatabase.getInstance(application)
    private val repository = ClimbRepository(
        climbDao = database.climbDao(),
        holdDao = database.holdDao(),
        faceDao = database.faceDao()
    )

    private val _uiState = MutableStateFlow(ClimbListUiState())
    val uiState: StateFlow<ClimbListUiState> = _uiState.asStateFlow()

    // Cache de tous les climbs non filtrés
    private var allClimbs: List<Climb> = emptyList()

    init {
        // Observer les climbs depuis le cache
        viewModelScope.launch {
            repository.observeClimbs().collect { climbs ->
                allClimbs = climbs
                updateDerivedState(climbs)
                applyFiltersAndSort()
            }
        }
        // Charger les données initiales
        refresh()
    }

    /**
     * Met à jour les états dérivés (setters disponibles, plage de grades).
     */
    private fun updateDerivedState(climbs: List<Climb>) {
        // Extraire les setters uniques
        val setters = climbs
            .mapNotNull { it.setterName }
            .distinct()
            .sorted()

        // Calculer la plage de grades
        val grades = climbs.mapNotNull { it.gradeIrcra }
        val minAvailable = grades.minOrNull() ?: 0f
        val maxAvailable = grades.maxOrNull() ?: 100f

        _uiState.value = _uiState.value.copy(
            climbs = climbs,
            availableSetters = setters,
            gradeRange = minAvailable..maxAvailable
        )
    }

    /**
     * Applique les filtres et le tri.
     */
    private fun applyFiltersAndSort() {
        val state = _uiState.value
        var filtered = allClimbs

        // Filtre par recherche texte
        if (state.searchQuery.isNotBlank()) {
            filtered = filtered.filter {
                it.name.contains(state.searchQuery, ignoreCase = true)
            }
        }

        // Filtre par grade
        filtered = filtered.filter { climb ->
            val grade = climb.gradeIrcra ?: return@filter true
            grade >= state.minGrade && grade <= state.maxGrade
        }

        // Filtre par setter
        if (state.selectedSetter != null) {
            filtered = filtered.filter { it.setterName == state.selectedSetter }
        }

        // Tri
        filtered = when (state.sortOption) {
            SortOption.DATE_DESC -> filtered.sortedByDescending { it.createdAt ?: "" }
            SortOption.DATE_ASC -> filtered.sortedBy { it.createdAt ?: "" }
            SortOption.GRADE_ASC -> filtered.sortedBy { it.gradeIrcra ?: 0f }
            SortOption.GRADE_DESC -> filtered.sortedByDescending { it.gradeIrcra ?: 0f }
            SortOption.NAME_ASC -> filtered.sortedBy { it.name.lowercase() }
            SortOption.NAME_DESC -> filtered.sortedByDescending { it.name.lowercase() }
            SortOption.POPULARITY -> filtered.sortedByDescending { it.climbedBy }
        }

        _uiState.value = _uiState.value.copy(filteredClimbs = filtered)
    }

    /**
     * Rafraîchit les données depuis l'API.
     */
    fun refresh() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isRefreshing = true, error = null)

            val result = repository.refreshClimbs()

            _uiState.value = _uiState.value.copy(
                isRefreshing = false,
                error = result.exceptionOrNull()?.message
            )
        }
    }

    /**
     * Met à jour la recherche.
     */
    fun updateSearch(query: String) {
        _uiState.value = _uiState.value.copy(searchQuery = query)
        applyFiltersAndSort()
    }

    /**
     * Met à jour le filtre de grade minimum.
     */
    fun updateMinGrade(grade: Float) {
        _uiState.value = _uiState.value.copy(minGrade = grade)
        applyFiltersAndSort()
    }

    /**
     * Met à jour le filtre de grade maximum.
     */
    fun updateMaxGrade(grade: Float) {
        _uiState.value = _uiState.value.copy(maxGrade = grade)
        applyFiltersAndSort()
    }

    /**
     * Met à jour la plage de grades (pour RangeSlider).
     */
    fun updateGradeRange(min: Float, max: Float) {
        _uiState.value = _uiState.value.copy(minGrade = min, maxGrade = max)
        applyFiltersAndSort()
    }

    /**
     * Met à jour le setter sélectionné.
     */
    fun updateSetter(setter: String?) {
        _uiState.value = _uiState.value.copy(selectedSetter = setter)
        applyFiltersAndSort()
    }

    /**
     * Met à jour l'option de tri.
     */
    fun updateSort(option: SortOption) {
        _uiState.value = _uiState.value.copy(sortOption = option)
        applyFiltersAndSort()
    }

    /**
     * Toggle l'affichage du panneau de filtres.
     */
    fun toggleFilters() {
        _uiState.value = _uiState.value.copy(showFilters = !_uiState.value.showFilters)
    }

    /**
     * Réinitialise tous les filtres.
     */
    fun resetFilters() {
        val range = _uiState.value.gradeRange
        _uiState.value = _uiState.value.copy(
            searchQuery = "",
            minGrade = range.start,
            maxGrade = range.endInclusive,
            selectedSetter = null,
            sortOption = SortOption.DATE_DESC
        )
        applyFiltersAndSort()
    }

    /**
     * Efface l'erreur affichée.
     */
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
