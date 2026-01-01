package com.mastoc.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.pager.VerticalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.rememberModalBottomSheetState
import kotlinx.coroutines.launch
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.ColorMatrix
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.mastoc.app.data.settings.RenderSettings
import com.mastoc.app.data.settings.SettingsDataStore
import com.mastoc.app.ui.components.ClimbHoldOverlay
import com.mastoc.app.ui.components.GradeBadge
import com.mastoc.app.ui.components.RenderSettingsSheet
import com.mastoc.app.viewmodel.ClimbDetailViewModel
import com.mastoc.app.viewmodel.ClimbDetailViewModelFactory

/**
 * Écran de détail avec navigation swipe vertical entre les blocs.
 * Le swipe est désactivé quand l'image est zoomée (scale > 1).
 */
@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
@Composable
fun ClimbDetailScreen(
    climbIds: List<String>,
    initialIndex: Int,
    onNavigateBack: () -> Unit
) {
    val context = LocalContext.current
    val pagerState = rememberPagerState(
        initialPage = initialIndex.coerceIn(0, (climbIds.size - 1).coerceAtLeast(0)),
        pageCount = { climbIds.size }
    )

    // État du zoom partagé pour désactiver le swipe
    var currentZoom by remember { mutableFloatStateOf(1f) }

    // Paramètres de rendu partagés
    val settingsDataStore = remember { SettingsDataStore(context) }
    val renderSettings by settingsDataStore.renderSettings.collectAsState(initial = RenderSettings.DEFAULT)
    var showRenderSettings by remember { mutableStateOf(false) }
    val sheetState = rememberModalBottomSheetState()
    val scope = rememberCoroutineScope()

    // Titre dynamique selon la page courante
    val currentClimbId = climbIds.getOrNull(pagerState.currentPage)

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "${pagerState.currentPage + 1}/${climbIds.size}",
                        maxLines = 1
                    )
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
                    IconButton(onClick = { showRenderSettings = true }) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = "Paramètres de rendu"
                        )
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
        VerticalPager(
            state = pagerState,
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            // Désactiver le swipe si zoomé
            userScrollEnabled = currentZoom <= 1.01f,
            // Éviter le préchargement excessif
            beyondBoundsPageCount = 1
        ) { pageIndex ->
            val climbId = climbIds[pageIndex]

            ClimbDetailPage(
                climbId = climbId,
                renderSettings = renderSettings,
                onZoomChanged = { zoom ->
                    if (pageIndex == pagerState.currentPage) {
                        currentZoom = zoom
                    }
                }
            )
        }
    }

    // BottomSheet paramètres de rendu
    if (showRenderSettings) {
        RenderSettingsSheet(
            sheetState = sheetState,
            settings = renderSettings,
            onSettingsChange = { newSettings ->
                scope.launch {
                    settingsDataStore.setRenderSettings(newSettings)
                }
            },
            onDismiss = { showRenderSettings = false }
        )
    }
}

/**
 * Contenu d'une page de détail (un bloc).
 */
@Composable
private fun ClimbDetailPage(
    climbId: String,
    renderSettings: RenderSettings,
    onZoomChanged: (Float) -> Unit
) {
    val context = LocalContext.current
    val viewModel: ClimbDetailViewModel = viewModel(
        key = climbId,  // Clé unique pour chaque bloc
        factory = ClimbDetailViewModelFactory(
            application = context.applicationContext as android.app.Application,
            climbId = climbId
        )
    )

    val uiState by viewModel.uiState.collectAsState()

    Box(modifier = Modifier.fillMaxSize()) {
        if (uiState.isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.align(Alignment.Center)
            )
        } else if (uiState.climb != null) {
            Column(modifier = Modifier.fillMaxSize()) {
                // Info climb
                ClimbInfoHeader(
                    climb = uiState.climb!!,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                )

                // Image avec overlay
                if (uiState.face != null) {
                    WallImageWithClimbOverlay(
                        pictureUrl = uiState.face!!.pictureUrl,
                        imageWidth = uiState.face!!.pictureWidth?.toFloat() ?: 1000f,
                        imageHeight = uiState.face!!.pictureHeight?.toFloat() ?: 1500f,
                        climb = uiState.climb!!,
                        holdsMap = uiState.holdsMap,
                        renderSettings = renderSettings,
                        onZoomChanged = onZoomChanged,
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f)
                    )
                } else {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("Chargement de l'image...")
                    }
                }
            }
        }
    }
}

@Composable
private fun ClimbInfoHeader(
    climb: com.mastoc.app.data.model.Climb,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        // Nom + Grade
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = climb.name,
                style = MaterialTheme.typography.headlineSmall,
                modifier = Modifier.weight(1f)
            )
            GradeBadge(grade = climb.displayGrade)
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Setter + Date
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = climb.setterName ?: "Inconnu",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            // Date de création
            climb.createdAt?.let { dateStr ->
                Spacer(modifier = Modifier.width(16.dp))
                Icon(
                    imageVector = Icons.Default.DateRange,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = formatDate(dateStr),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }

        Spacer(modifier = Modifier.height(4.dp))

        // Stats (likes + grimpeurs)
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Favorite,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.error
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = "${climb.totalLikes}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.error
            )

            Spacer(modifier = Modifier.width(16.dp))

            Text(
                text = "${climb.climbedBy} grimpeurs",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        // Description
        if (!climb.description.isNullOrBlank()) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = climb.description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Formate une date ISO en format lisible (ex: "15 janv. 2025").
 */
private fun formatDate(isoDate: String): String {
    return try {
        // Format ISO: "2025-01-15T10:30:00Z" ou "2025-01-15"
        val datePart = isoDate.substringBefore("T")
        val parts = datePart.split("-")
        if (parts.size == 3) {
            val day = parts[2].toInt()
            val month = when (parts[1]) {
                "01" -> "janv."
                "02" -> "févr."
                "03" -> "mars"
                "04" -> "avr."
                "05" -> "mai"
                "06" -> "juin"
                "07" -> "juil."
                "08" -> "août"
                "09" -> "sept."
                "10" -> "oct."
                "11" -> "nov."
                "12" -> "déc."
                else -> parts[1]
            }
            val year = parts[0]
            "$day $month $year"
        } else {
            isoDate
        }
    } catch (e: Exception) {
        isoDate
    }
}

/**
 * Composable qui affiche l'image du mur avec l'overlay du climb.
 * Implémente le rendu fidèle au Python climb_renderer.py :
 * - Fond grisé + assombri
 * - Prises du bloc en couleur originale (via masque)
 * - Contours blancs
 */
@Composable
private fun WallImageWithClimbOverlay(
    pictureUrl: String,
    imageWidth: Float,
    imageHeight: Float,
    climb: com.mastoc.app.data.model.Climb,
    holdsMap: Map<Int, com.mastoc.app.data.model.Hold>,
    renderSettings: RenderSettings,
    onZoomChanged: (Float) -> Unit = {},
    modifier: Modifier = Modifier
) {
    var scale by remember { mutableFloatStateOf(1f) }
    var offset by remember { mutableStateOf(Offset.Zero) }
    var containerSize by remember { mutableStateOf(IntSize.Zero) }
    val context = LocalContext.current
    val density = context.resources.displayMetrics.density

    // Notifier le parent du changement de zoom
    LaunchedEffect(scale) {
        onZoomChanged(scale)
    }

    Box(
        modifier = modifier
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .clipToBounds()
            .onSizeChanged { containerSize = it }
            .pointerInput(Unit) {
                detectTransformGestures { _, pan, zoom, _ ->
                    scale = (scale * zoom).coerceIn(1f, 4f)
                    val maxOffsetX = (containerSize.width * (scale - 1) / 2).coerceAtLeast(0f)
                    val maxOffsetY = (containerSize.height * (scale - 1) / 2).coerceAtLeast(0f)
                    offset = Offset(
                        x = (offset.x + pan.x).coerceIn(-maxOffsetX, maxOffsetX),
                        y = (offset.y + pan.y).coerceIn(-maxOffsetY, maxOffsetY)
                    )
                }
            },
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

        // Créer le ColorFilter combiné (saturation + luminosité)
        val backgroundColorFilter = remember(renderSettings.grayLevel, renderSettings.brightness) {
            createBackgroundColorFilter(renderSettings.grayLevel, renderSettings.brightness)
        }

        // Créer le Path pour clipper les prises
        val scaleX = displayWidth / imageWidth
        val scaleY = displayHeight / imageHeight
        val holdsClipPath = remember(climb, holdsMap, scaleX, scaleY) {
            createHoldsClipPath(climb, holdsMap, scaleX, scaleY)
        }

        Box(
            modifier = Modifier
                .width((displayWidth / density).dp)
                .height((displayHeight / density).dp)
                .graphicsLayer(
                    scaleX = scale,
                    scaleY = scale,
                    translationX = offset.x,
                    translationY = offset.y
                )
        ) {
            if (renderSettings.showImage) {
                // Couche 1 : Image de fond (grisée + assombrie)
                AsyncImage(
                    model = ImageRequest.Builder(context)
                        .data(pictureUrl)
                        .crossfade(true)
                        .build(),
                    contentDescription = "Photo du mur",
                    contentScale = ContentScale.Fit,
                    modifier = Modifier.fillMaxSize(),
                    colorFilter = backgroundColorFilter
                )

                // Couche 2 : Prises en couleur originale (clippées aux polygones)
                if (renderSettings.holdsInColor && holdsClipPath != null) {
                    AsyncImage(
                        model = ImageRequest.Builder(context)
                            .data(pictureUrl)
                            .crossfade(false)
                            .build(),
                        contentDescription = null,
                        contentScale = ContentScale.Fit,
                        modifier = Modifier
                            .fillMaxSize()
                            .clipToHoldsPath(holdsClipPath)
                    )
                }
            }

            // Couche 3 : Contours des prises
            ClimbHoldOverlay(
                climb = climb,
                holdsMap = holdsMap,
                imageWidth = imageWidth,
                imageHeight = imageHeight,
                contourWidth = renderSettings.contourWidth.toFloat(),
                modifier = Modifier.fillMaxSize()
            )
        }
    }
}

/**
 * Crée un ColorFilter combinant désaturation et assombrissement.
 * Équivalent Python: Image.blend(img, gray, grayLevel) + Brightness.enhance(brightness)
 */
private fun createBackgroundColorFilter(
    grayLevel: Float,
    brightness: Float
): androidx.compose.ui.graphics.ColorFilter {
    // Matrice de saturation (1.0 = couleur, 0.0 = gris)
    val saturationMatrix = ColorMatrix().apply {
        setToSaturation(1f - grayLevel)
    }

    // Matrice de luminosité (scale RGB)
    val brightnessMatrix = ColorMatrix(floatArrayOf(
        brightness, 0f, 0f, 0f, 0f,
        0f, brightness, 0f, 0f, 0f,
        0f, 0f, brightness, 0f, 0f,
        0f, 0f, 0f, 1f, 0f
    ))

    // Combiner les deux matrices
    saturationMatrix.timesAssign(brightnessMatrix)

    return androidx.compose.ui.graphics.ColorFilter.colorMatrix(saturationMatrix)
}

/**
 * Crée un Path contenant tous les polygones des prises du climb.
 */
private fun createHoldsClipPath(
    climb: com.mastoc.app.data.model.Climb,
    holdsMap: Map<Int, com.mastoc.app.data.model.Hold>,
    scaleX: Float,
    scaleY: Float
): Path? {
    val climbHolds = climb.getClimbHolds()
    if (climbHolds.isEmpty()) return null

    val path = Path()

    climbHolds.forEach { climbHold ->
        val hold = holdsMap[climbHold.holdId] ?: return@forEach
        val points = hold.getPolygonPoints()
        if (points.isEmpty()) return@forEach

        // Ajouter le polygone au path
        path.moveTo(points.first().x * scaleX, points.first().y * scaleY)
        for (i in 1 until points.size) {
            path.lineTo(points[i].x * scaleX, points[i].y * scaleY)
        }
        path.close()
    }

    return path
}

/**
 * Modifier qui clippe le contenu à un Path donné.
 */
private fun Modifier.clipToHoldsPath(path: Path?): Modifier {
    if (path == null) return this
    return this.then(
        Modifier.graphicsLayer {
            clip = true
            shape = object : androidx.compose.ui.graphics.Shape {
                override fun createOutline(
                    size: Size,
                    layoutDirection: androidx.compose.ui.unit.LayoutDirection,
                    density: androidx.compose.ui.unit.Density
                ): androidx.compose.ui.graphics.Outline {
                    return androidx.compose.ui.graphics.Outline.Generic(path)
                }
            }
        }
    )
}
