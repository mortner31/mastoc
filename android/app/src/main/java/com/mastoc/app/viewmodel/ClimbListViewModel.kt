package com.mastoc.app.viewmodel

import android.app.Application
import android.graphics.Bitmap
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.mastoc.app.core.PictoManager
import com.mastoc.app.data.local.MastocDatabase
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.Hold
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
        context = application.applicationContext,
        climbDao = database.climbDao(),
        holdDao = database.holdDao(),
        faceDao = database.faceDao()
    )

    // Gestionnaire de pictos
    val pictoManager = PictoManager(application.applicationContext)

    private val _uiState = MutableStateFlow(ClimbListUiState())
    val uiState: StateFlow<ClimbListUiState> = _uiState.asStateFlow()

    // Cache de tous les climbs non filtrés
    private var allClimbs: List<Climb> = emptyList()

    // Cache des holds par face (pour générer les pictos)
    private val _holdsMap = MutableStateFlow<Map<Int, Hold>>(emptyMap())
    val holdsMap: StateFlow<Map<Int, Hold>> = _holdsMap.asStateFlow()

    // Cache des pictos générés
    private val _pictosCache = MutableStateFlow<Map<String, Bitmap>>(emptyMap())
    val pictosCache: StateFlow<Map<String, Bitmap>> = _pictosCache.asStateFlow()

    // Cache des top holds par face (prises les plus fréquentes pour le fond gris des pictos)
    private val _topHoldsByFace = MutableStateFlow<Map<String, Set<Int>>>(emptyMap())

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
     * Rafraîchit les données depuis l'API (charge TOUTES les pages pour sync complète).
     * Le cache local doit être une copie complète du serveur pour le filtrage client.
     */
    fun refresh() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isRefreshing = true,
                error = null,
                currentPage = 1,
                hasMore = true
            )

            var page = 1
            var hasMore = true

            // Charger toutes les pages jusqu'à la fin
            while (hasMore) {
                val result = repository.refreshClimbs(page = page, pageSize = PAGE_SIZE)

                result.onSuccess { paginated ->
                    _uiState.value = _uiState.value.copy(
                        currentPage = paginated.page,
                        hasMore = paginated.hasMore,
                        totalCount = paginated.totalCount
                    )
                    hasMore = paginated.hasMore
                    page++
                }.onFailure { e ->
                    _uiState.value = _uiState.value.copy(
                        isRefreshing = false,
                        error = e.message
                    )
                    return@launch
                }
            }

            _uiState.value = _uiState.value.copy(
                isRefreshing = false,
                hasMore = false
            )
        }
    }

    /**
     * Charge la page suivante (plus utilisé car refresh charge tout).
     */
    fun loadMore() {
        // Plus nécessaire car refresh() charge toutes les pages
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

    /**
     * Charge les holds d'une face si pas encore en cache (suspend).
     * Extrait les couleurs depuis l'image du mur si nécessaire.
     * Retourne la map des holds pour cette face.
     */
    private suspend fun loadHoldsForFaceAsync(faceId: String): Map<Int, Hold> {
        // Vérifier si déjà chargé avec couleurs
        val currentHolds = _holdsMap.value
        val existingHolds = currentHolds.values.filter { it.faceId == faceId }
        if (existingHolds.isNotEmpty() && existingHolds.all { it.colorRgb != null }) {
            return currentHolds
        }

        // Charger depuis le cache local ou l'API
        var holds = repository.getHoldsByFace(faceId)
        if (holds.isEmpty()) {
            // Pas en cache, charger depuis l'API
            val result = repository.refreshFaceSetup(faceId)
            holds = result.getOrNull()?.holds ?: emptyList()
        }

        // Extraire les couleurs si nécessaire
        if (repository.needsColorExtraction(faceId)) {
            repository.extractHoldColors(faceId)
            // Recharger les holds avec les couleurs
            holds = repository.getHoldsByFace(faceId)
        }

        // Ajouter au cache
        val newMap = currentHolds.toMutableMap()
        holds.forEach { hold ->
            newMap[hold.id] = hold
            hold.stoktId?.let { newMap[it] = hold }
        }
        _holdsMap.value = newMap

        return newMap
    }

    /**
     * Charge les holds d'une face (version publique non-suspend).
     */
    fun loadHoldsForFace(faceId: String) {
        viewModelScope.launch {
            loadHoldsForFaceAsync(faceId)
        }
    }

    /**
     * Calcule les top N prises les plus utilisées pour une face.
     * Ces prises sont affichées en gris sur les pictos pour donner du contexte.
     */
    private fun computeTopHoldsForFace(faceId: String, topN: Int = 20): Set<Int> {
        // Compter l'utilisation de chaque prise dans les climbs de cette face
        val holdCounts = mutableMapOf<Int, Int>()

        allClimbs
            .filter { it.faceId == faceId }
            .forEach { climb ->
                climb.getClimbHolds().forEach { climbHold ->
                    holdCounts[climbHold.holdId] = (holdCounts[climbHold.holdId] ?: 0) + 1
                }
            }

        // Retourner les top N
        return holdCounts.entries
            .sortedByDescending { it.value }
            .take(topN)
            .map { it.key }
            .toSet()
    }

    /**
     * Obtient les top holds pour une face, les calcule si nécessaire.
     */
    private fun getTopHoldsForFace(faceId: String): Set<Int> {
        _topHoldsByFace.value[faceId]?.let { return it }

        val topHolds = computeTopHoldsForFace(faceId)
        _topHoldsByFace.value = _topHoldsByFace.value + (faceId to topHolds)
        return topHolds
    }

    /**
     * Génère le picto pour un climb (lazy, appelé au scroll).
     */
    fun loadPictoForClimb(climb: Climb) {
        // Déjà en cache ?
        if (_pictosCache.value.containsKey(climb.id)) return

        viewModelScope.launch {
            // Charger les holds et attendre qu'ils soient disponibles
            val holdsMap = loadHoldsForFaceAsync(climb.faceId)
            if (holdsMap.isEmpty()) return@launch

            // Obtenir les top holds pour cette face (pour le fond gris)
            val topHolds = getTopHoldsForFace(climb.faceId)

            // Générer le picto
            val picto = pictoManager.getPicto(
                climb = climb,
                holdsMap = holdsMap,
                topHoldIds = topHolds,
                size = 128 // Taille du picto
            )

            if (picto != null) {
                _pictosCache.value = _pictosCache.value + (climb.id to picto)
            }
        }
    }

    /**
     * Pré-charge les pictos pour les climbs visibles.
     */
    fun preloadPictosForVisibleClimbs(climbs: List<Climb>) {
        climbs.forEach { loadPictoForClimb(it) }
    }

    /**
     * Regénère le picto d'un climb spécifique (force la recréation).
     */
    fun regeneratePicto(climb: Climb) {
        viewModelScope.launch {
            // Charger les holds et attendre
            val holdsMap = loadHoldsForFaceAsync(climb.faceId)
            if (holdsMap.isEmpty()) return@launch

            val topHolds = getTopHoldsForFace(climb.faceId)

            // Regénérer le picto
            val picto = pictoManager.regeneratePicto(
                climb = climb,
                holdsMap = holdsMap,
                topHoldIds = topHolds,
                size = 128
            )

            if (picto != null) {
                _pictosCache.value = _pictosCache.value + (climb.id to picto)
            }
        }
    }

    /**
     * Regénère tous les pictos (vide le cache et régénère).
     */
    fun regenerateAllPictos() {
        viewModelScope.launch {
            // Vider le cache mémoire local
            _pictosCache.value = emptyMap()
            _topHoldsByFace.value = emptyMap()

            // Invalider le cache du PictoManager (mémoire + disque)
            pictoManager.invalidateCache()
        }
    }
}
