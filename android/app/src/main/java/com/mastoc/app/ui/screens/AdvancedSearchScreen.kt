package com.mastoc.app.ui.screens

import android.app.Application
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material3.Badge
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.mastoc.app.data.local.MastocDatabase
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.Face
import com.mastoc.app.data.model.Hold
import com.mastoc.app.data.repository.ClimbRepository
import com.mastoc.app.ui.components.ClimbCard
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

/**
 * État UI pour la recherche avancée.
 */
data class AdvancedSearchUiState(
    val face: Face? = null,
    val holds: List<Hold> = emptyList(),
    val selectedHoldIds: Set<Int> = emptySet(),
    val matchingClimbs: List<Climb> = emptyList(),
    val allClimbs: List<Climb> = emptyList(),
    val isLoading: Boolean = true,
    val error: String? = null
)

/**
 * ViewModel pour la recherche avancée.
 * Charge automatiquement la première face disponible.
 */
class AdvancedSearchViewModel(application: Application) : AndroidViewModel(application) {

    private val database = MastocDatabase.getInstance(application)
    private val repository = ClimbRepository(
        context = application.applicationContext,
        climbDao = database.climbDao(),
        holdDao = database.holdDao(),
        faceDao = database.faceDao()
    )

    private val _uiState = MutableStateFlow(AdvancedSearchUiState())
    val uiState: StateFlow<AdvancedSearchUiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            try {
                // Charger la liste des faces
                repository.refreshFaces()
                val faces = repository.observeFaces().first()

                if (faces.isEmpty()) {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = "Aucun mur disponible"
                    )
                    return@launch
                }

                // Utiliser la première face
                val faceId = faces.first().id

                // Charger face setup (avec holds)
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

    fun clearSelection() {
        _uiState.value = _uiState.value.copy(
            selectedHoldIds = emptySet(),
            matchingClimbs = emptyList()
        )
    }

    private fun updateMatchingClimbs() {
        val selectedIds = _uiState.value.selectedHoldIds
        if (selectedIds.isEmpty()) {
            _uiState.value = _uiState.value.copy(matchingClimbs = emptyList())
            return
        }

        val matching = _uiState.value.allClimbs.filter { climb ->
            val climbHoldIds = climb.getHoldIds().toSet()
            selectedIds.all { it in climbHoldIds }
        }

        _uiState.value = _uiState.value.copy(matchingClimbs = matching)
    }
}

/**
 * Écran de recherche avancée par sélection de prises.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdvancedSearchScreen(
    onClimbClick: (String) -> Unit
) {
    val context = LocalContext.current
    val viewModel: AdvancedSearchViewModel = viewModel(
        factory = object : androidx.lifecycle.ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T {
                return AdvancedSearchViewModel(context.applicationContext as Application) as T
            }
        }
    )

    val uiState by viewModel.uiState.collectAsState()

    if (uiState.isLoading) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            CircularProgressIndicator()
        }
        return
    }

    if (uiState.error != null) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = uiState.error ?: "Erreur inconnue",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.error
            )
        }
        return
    }

    Column(modifier = Modifier.fillMaxSize()) {
        // Header avec badge sélection
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .padding(horizontal = 16.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "Recherche par prises",
                    style = MaterialTheme.typography.titleMedium
                )
                if (uiState.selectedHoldIds.isNotEmpty()) {
                    Badge(modifier = Modifier.padding(start = 8.dp)) {
                        Text("${uiState.selectedHoldIds.size}")
                    }
                }
            }
            if (uiState.selectedHoldIds.isNotEmpty()) {
                IconButton(onClick = viewModel::clearSelection) {
                    Icon(
                        imageVector = Icons.Default.Clear,
                        contentDescription = "Effacer"
                    )
                }
            }
        }

        // Image avec prises sélectionnables (50% de l'écran)
        if (uiState.face != null) {
            SelectableWallImageAdvanced(
                pictureUrl = uiState.face!!.pictureUrl,
                imageWidth = uiState.face!!.pictureWidth?.toFloat() ?: 1000f,
                imageHeight = uiState.face!!.pictureHeight?.toFloat() ?: 1500f,
                holds = uiState.holds,
                selectedHoldIds = uiState.selectedHoldIds,
                onHoldTap = viewModel::toggleHoldSelection,
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            )
        }

        // Liste des climbs correspondants (50% de l'écran)
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .background(MaterialTheme.colorScheme.surface)
        ) {
            Text(
                text = if (uiState.matchingClimbs.isEmpty()) {
                    if (uiState.selectedHoldIds.isEmpty()) {
                        "Tapez sur des prises pour rechercher"
                    } else {
                        "Aucun bloc trouvé"
                    }
                } else {
                    "${uiState.matchingClimbs.size} bloc(s) trouvé(s)"
                },
                style = MaterialTheme.typography.titleSmall,
                modifier = Modifier.padding(16.dp)
            )

            LazyColumn(
                contentPadding = PaddingValues(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(
                    items = uiState.matchingClimbs,
                    key = { it.id }
                ) { climb ->
                    ClimbCard(
                        climb = climb,
                        onClick = { onClimbClick(climb.id) }
                    )
                }
                item {
                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
        }
    }
}

@Composable
private fun SelectableWallImageAdvanced(
    pictureUrl: String,
    imageWidth: Float,
    imageHeight: Float,
    holds: List<Hold>,
    selectedHoldIds: Set<Int>,
    onHoldTap: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    var containerSize by remember { mutableStateOf(IntSize.Zero) }
    val density = LocalContext.current.resources.displayMetrics.density

    Box(
        modifier = modifier
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .onSizeChanged { containerSize = it },
        contentAlignment = Alignment.Center
    ) {
        // Calculer la taille réelle de l'image avec ContentScale.Fit
        val imageAspectRatio = imageWidth / imageHeight
        val containerAspectRatio = if (containerSize.height > 0) {
            containerSize.width.toFloat() / containerSize.height.toFloat()
        } else imageAspectRatio

        val (displayWidth, displayHeight) = if (imageAspectRatio > containerAspectRatio) {
            containerSize.width.toFloat() to (containerSize.width.toFloat() / imageAspectRatio)
        } else {
            (containerSize.height.toFloat() * imageAspectRatio) to containerSize.height.toFloat()
        }

        Box(
            modifier = Modifier
                .width((displayWidth / density).dp)
                .height((displayHeight / density).dp)
        ) {
            AsyncImage(
                model = ImageRequest.Builder(LocalContext.current)
                    .data(pictureUrl)
                    .crossfade(true)
                    .build(),
                contentDescription = "Photo du mur",
                contentScale = ContentScale.Fit,
                modifier = Modifier.fillMaxSize()
            )

            if (displayWidth > 0 && displayHeight > 0) {
                val scaleX = displayWidth / imageWidth
                val scaleY = displayHeight / imageHeight

                Canvas(
                    modifier = Modifier
                        .fillMaxSize()
                        .pointerInput(holds) {
                            detectTapGestures { tapOffset ->
                                val tappedHold = holds.find { hold ->
                                    isPointInPolygonAdvanced(
                                        tapOffset,
                                        hold.getPolygonPoints().map { p ->
                                            Offset(p.x * scaleX, p.y * scaleY)
                                        }
                                    )
                                }
                                tappedHold?.let { onHoldTap(it.id) }
                            }
                        }
                ) {
                    holds.forEach { hold ->
                        val isSelected = hold.id in selectedHoldIds
                        val points = hold.getPolygonPoints().map { p ->
                            Offset(p.x * scaleX, p.y * scaleY)
                        }

                        if (points.isNotEmpty()) {
                            val path = Path().apply {
                                moveTo(points.first().x, points.first().y)
                                for (i in 1 until points.size) {
                                    lineTo(points[i].x, points[i].y)
                                }
                                close()
                            }

                            drawPath(
                                path,
                                color = if (isSelected) {
                                    Color(0xFF4CAF50).copy(alpha = 0.5f)
                                } else {
                                    Color.Gray.copy(alpha = 0.2f)
                                }
                            )

                            drawPath(
                                path,
                                color = if (isSelected) Color(0xFF4CAF50) else Color.Gray,
                                style = Stroke(width = if (isSelected) 4f else 2f)
                            )
                        }
                    }
                }
            }
        }
    }
}

private fun isPointInPolygonAdvanced(point: Offset, polygon: List<Offset>): Boolean {
    if (polygon.size < 3) return false

    var inside = false
    var j = polygon.size - 1

    for (i in polygon.indices) {
        val xi = polygon[i].x
        val yi = polygon[i].y
        val xj = polygon[j].x
        val yj = polygon[j].y

        if ((yi > point.y) != (yj > point.y) &&
            point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi
        ) {
            inside = !inside
        }
        j = i
    }

    return inside
}
