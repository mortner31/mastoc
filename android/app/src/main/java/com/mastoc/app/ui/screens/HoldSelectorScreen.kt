package com.mastoc.app.ui.screens

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
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material3.Badge
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
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
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.mastoc.app.data.model.Hold
import com.mastoc.app.ui.components.ClimbCard
import com.mastoc.app.viewmodel.HoldSelectorViewModel
import com.mastoc.app.viewmodel.HoldSelectorViewModelFactory

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HoldSelectorScreen(
    faceId: String,
    onNavigateBack: () -> Unit,
    onClimbClick: (String) -> Unit
) {
    val context = LocalContext.current
    val viewModel: HoldSelectorViewModel = viewModel(
        factory = HoldSelectorViewModelFactory(
            application = context.applicationContext as android.app.Application,
            faceId = faceId
        )
    )

    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("Recherche par prises")
                        if (uiState.selectedHoldIds.isNotEmpty()) {
                            Badge(
                                modifier = Modifier.padding(start = 8.dp)
                            ) {
                                Text("${uiState.selectedHoldIds.size}")
                            }
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Retour"
                        )
                    }
                },
                actions = {
                    if (uiState.selectedHoldIds.isNotEmpty()) {
                        IconButton(onClick = viewModel::clearSelection) {
                            Icon(
                                imageVector = Icons.Default.Clear,
                                contentDescription = "Effacer"
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimary,
                    actionIconContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        }
    ) { paddingValues ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                // Image avec prises sélectionnables (50% de l'écran)
                if (uiState.face != null) {
                    SelectableWallImage(
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
    }
}

@Composable
private fun SelectableWallImage(
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
            // Image du mur
            AsyncImage(
                model = ImageRequest.Builder(LocalContext.current)
                    .data(pictureUrl)
                    .crossfade(true)
                    .build(),
                contentDescription = "Photo du mur",
                contentScale = ContentScale.Fit,
                modifier = Modifier.fillMaxSize()
            )

            // Overlay des prises avec détection de tap
            if (displayWidth > 0 && displayHeight > 0) {
                val scaleX = displayWidth / imageWidth
                val scaleY = displayHeight / imageHeight

                Canvas(
                    modifier = Modifier
                        .fillMaxSize()
                        .pointerInput(holds) {
                            detectTapGestures { tapOffset ->
                                // Trouver la prise tapée
                                val tappedHold = holds.find { hold ->
                                    isPointInPolygon(
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

                            // Remplissage
                            drawPath(
                                path,
                                color = if (isSelected) {
                                    Color(0xFF4CAF50).copy(alpha = 0.5f)
                                } else {
                                    Color.Gray.copy(alpha = 0.2f)
                                }
                            )

                            // Contour
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

/**
 * Vérifie si un point est à l'intérieur d'un polygone (ray casting algorithm).
 */
private fun isPointInPolygon(point: Offset, polygon: List<Offset>): Boolean {
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
