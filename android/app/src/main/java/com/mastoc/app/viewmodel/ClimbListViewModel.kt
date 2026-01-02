package com.mastoc.app.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.mastoc.app.data.local.MastocDatabase
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.repository.ClimbRepository
import com.mastoc.app.ui.components.GRADE_COUNT
import com.mastoc.app.ui.components.getMinIrcraForIndex
import com.mastoc.app.ui.components.getMaxIrcraForIndex
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
 * Mode de filtrage des setters.
 */
enum class SetterFilterMode(val displayName: String) {
    NONE("Tous"),
    INCLUDE("Inclure"),
    EXCLUDE("Exclure")
}

/**
 * Informations sur un setter avec son nombre de climbs.
 */
data class SetterInfo(
    val name: String,
    val climbCount: Int
)

/**
 * État UI pour la liste des climbs.
 */
data class ClimbListUiState(
    val climbs: List<Climb> = emptyList(),
    val filteredClimbs: List<Climb> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val isLoadingMore: Boolean = false,
    val error: String? = null,
    val searchQuery: String = "",
    // Filtres grade (indices 0 à GRADE_COUNT-1)
    val minGradeIndex: Int = 0,
    val maxGradeIndex: Int = GRADE_COUNT - 1,
    // Filtre setter avancé
    val setterFilterMode: SetterFilterMode = SetterFilterMode.NONE,
    val selectedSetters: Set<String> = emptySet(),
    val availableSetters: List<SetterInfo> = emptyList(),
    // Tri
    val sortOption: SortOption = SortOption.DATE_DESC,
    // Panneau filtres visible
    val showFilters: Boolean = false,
    // Pagination
    val currentPage: Int = 1,
    val hasMore: Boolean = true,
    val totalCount: Int = 0
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
     * Met à jour les états dérivés (setters disponibles avec compteur).
     */
    private fun updateDerivedState(climbs: List<Climb>) {
        // Compter les climbs par setter et trier par nombre décroissant
        val setterCounts = climbs
            .mapNotNull { it.setterName }
            .groupingBy { it }
            .eachCount()
            .map { (name, count) -> SetterInfo(name, count) }
            .sortedByDescending { it.climbCount }

        _uiState.value = _uiState.value.copy(
            climbs = climbs,
            availableSetters = setterCounts
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

        // Filtre par grade (utilise les indices avec logique epsilon)
        val minIrcra = getMinIrcraForIndex(state.minGradeIndex)
        val maxIrcra = getMaxIrcraForIndex(state.maxGradeIndex)
        filtered = filtered.filter { climb ->
            val grade = climb.gradeIrcra ?: return@filter true
            grade >= minIrcra && grade <= maxIrcra
        }

        // Filtre par setter (include/exclude)
        if (state.selectedSetters.isNotEmpty()) {
            when (state.setterFilterMode) {
                SetterFilterMode.INCLUDE -> {
                    // Ne garder QUE les climbs des setters sélectionnés
                    filtered = filtered.filter { climb ->
                        climb.setterName in state.selectedSetters
                    }
                }
                SetterFilterMode.EXCLUDE -> {
                    // Exclure les climbs des setters sélectionnés
                    filtered = filtered.filter { climb ->
                        climb.setterName == null || climb.setterName !in state.selectedSetters
                    }
                }
                SetterFilterMode.NONE -> {
                    // Pas de filtre
                }
            }
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

    companion object {
        private const val PAGE_SIZE = 100
    }

    /**
     * Rafraîchit les données depuis l'API (première page).
     */
    fun refresh() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isRefreshing = true,
                error = null,
                currentPage = 1,
                hasMore = true
            )

            val result = repository.refreshClimbs(page = 1, pageSize = PAGE_SIZE)

            result.onSuccess { paginated ->
                _uiState.value = _uiState.value.copy(
                    isRefreshing = false,
                    currentPage = paginated.page,
                    hasMore = paginated.hasMore,
                    totalCount = paginated.totalCount
                )
            }.onFailure { e ->
                _uiState.value = _uiState.value.copy(
                    isRefreshing = false,
                    error = e.message
                )
            }
        }
    }

    /**
     * Charge la page suivante (pagination infinie).
     */
    fun loadMore() {
        val state = _uiState.value
        // Ne pas charger si déjà en cours ou si pas de page suivante
        if (state.isLoadingMore || state.isRefreshing || !state.hasMore) return

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoadingMore = true)

            val nextPage = state.currentPage + 1
            val result = repository.refreshClimbs(page = nextPage, pageSize = PAGE_SIZE)

            result.onSuccess { paginated ->
                _uiState.value = _uiState.value.copy(
                    isLoadingMore = false,
                    currentPage = paginated.page,
                    hasMore = paginated.hasMore,
                    totalCount = paginated.totalCount
                )
            }.onFailure { e ->
                _uiState.value = _uiState.value.copy(
                    isLoadingMore = false,
                    error = e.message
                )
            }
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
     * Met à jour la plage de grades (pour RangeSlider avec indices).
     */
    fun updateGradeRange(minIndex: Int, maxIndex: Int) {
        _uiState.value = _uiState.value.copy(
            minGradeIndex = minIndex.coerceIn(0, GRADE_COUNT - 1),
            maxGradeIndex = maxIndex.coerceIn(0, GRADE_COUNT - 1)
        )
        applyFiltersAndSort()
    }

    /**
     * Met à jour le mode de filtrage des setters.
     */
    fun updateSetterFilterMode(mode: SetterFilterMode) {
        _uiState.value = _uiState.value.copy(setterFilterMode = mode)
        applyFiltersAndSort()
    }

    /**
     * Toggle la sélection d'un setter.
     */
    fun toggleSetterSelection(setterName: String) {
        val current = _uiState.value.selectedSetters
        val updated = if (setterName in current) {
            current - setterName
        } else {
            current + setterName
        }
        _uiState.value = _uiState.value.copy(selectedSetters = updated)
        applyFiltersAndSort()
    }

    /**
     * Sélectionne tous les setters.
     */
    fun selectAllSetters() {
        val allNames = _uiState.value.availableSetters.map { it.name }.toSet()
        _uiState.value = _uiState.value.copy(selectedSetters = allNames)
        applyFiltersAndSort()
    }

    /**
     * Désélectionne tous les setters.
     */
    fun clearSetterSelection() {
        _uiState.value = _uiState.value.copy(selectedSetters = emptySet())
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
        _uiState.value = _uiState.value.copy(
            searchQuery = "",
            minGradeIndex = 0,
            maxGradeIndex = GRADE_COUNT - 1,
            setterFilterMode = SetterFilterMode.NONE,
            selectedSetters = emptySet(),
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
