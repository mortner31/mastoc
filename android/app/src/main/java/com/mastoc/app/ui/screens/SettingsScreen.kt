package com.mastoc.app.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.mastoc.app.core.PictoManager
import com.mastoc.app.data.settings.AppTheme
import com.mastoc.app.data.settings.RenderSettings
import com.mastoc.app.data.settings.SettingsDataStore
import com.mastoc.app.ui.theme.BluePrimaryLight
import com.mastoc.app.ui.theme.BlueSecondaryLight
import com.mastoc.app.ui.theme.BlueTertiaryLight
import com.mastoc.app.ui.theme.ColorfulPrimaryLight
import com.mastoc.app.ui.theme.ColorfulSecondaryLight
import com.mastoc.app.ui.theme.ColorfulTertiaryLight
import com.mastoc.app.ui.theme.GrayPrimaryLight
import com.mastoc.app.ui.theme.GraySecondaryLight
import com.mastoc.app.ui.theme.GrayTertiaryLight
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

/**
 * Écran des paramètres avec sections dépliables :
 * 1. Thème de couleurs
 * 2. Cache et pictos
 * 3. Apparence des blocs (rendu)
 * 4. À propos
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onNavigateBack: () -> Unit
) {
    val context = LocalContext.current
    val settingsDataStore = remember { SettingsDataStore(context) }
    val pictoManager = remember { PictoManager(context) }

    val currentTheme by settingsDataStore.appTheme.collectAsState(initial = AppTheme.GRAY)
    val renderSettings by settingsDataStore.renderSettings.collectAsState(initial = RenderSettings.DEFAULT)
    val coroutineScope = rememberCoroutineScope()

    var isRegenerating by remember { mutableStateOf(false) }
    val scrollState = rememberScrollState()

    // États d'expansion des sections
    var themeExpanded by remember { mutableStateOf(false) }
    var pictosExpanded by remember { mutableStateOf(false) }
    var renderExpanded by remember { mutableStateOf(false) }
    var aboutExpanded by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Paramètres") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Retour"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(scrollState)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // ==================== SECTION 1: THÈME ====================
            ExpandableSection(
                title = "Thème de couleurs",
                subtitle = currentTheme.displayName,
                expanded = themeExpanded,
                onToggle = { themeExpanded = !themeExpanded }
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    AppTheme.entries.forEach { theme ->
                        ThemeOptionCard(
                            theme = theme,
                            isSelected = currentTheme == theme,
                            onClick = {
                                coroutineScope.launch {
                                    settingsDataStore.setAppTheme(theme)
                                }
                            }
                        )
                    }
                }
            }

            // ==================== SECTION 2: CACHE ET PICTOS ====================
            ExpandableSection(
                title = "Cache et pictos",
                subtitle = "Miniatures des blocs",
                expanded = pictosExpanded,
                onToggle = { pictosExpanded = !pictosExpanded }
            ) {
                Column {
                    Text(
                        text = "Les pictos sont des miniatures générées pour chaque bloc.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    // Stats du cache
                    val cacheStats = remember { pictoManager.getCacheStats() }
                    Text(
                        text = "En mémoire: ${cacheStats.memoryCount} pictos",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = "Sur disque: ${cacheStats.diskCount} pictos (${formatBytes(cacheStats.diskSizeBytes)})",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Button(
                        onClick = {
                            isRegenerating = true
                            coroutineScope.launch {
                                pictoManager.invalidateCache()
                                isRegenerating = false
                            }
                        },
                        enabled = !isRegenerating,
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.secondaryContainer,
                            contentColor = MaterialTheme.colorScheme.onSecondaryContainer
                        )
                    ) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(if (isRegenerating) "Suppression..." else "Regénérer les pictos")
                    }

                    Text(
                        text = "Supprime le cache et régénère les pictos au prochain affichage.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }
            }

            // ==================== SECTION 3: APPARENCE DES BLOCS ====================
            ExpandableSection(
                title = "Apparence des blocs",
                subtitle = "Rendu dans l'écran de détail",
                expanded = renderExpanded,
                onToggle = { renderExpanded = !renderExpanded }
            ) {
                Column {
                    // Switch : Afficher l'image
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Afficher l'image du mur",
                            modifier = Modifier.weight(1f)
                        )
                        Switch(
                            checked = renderSettings.showImage,
                            onCheckedChange = {
                                coroutineScope.launch {
                                    settingsDataStore.setRenderSettings(renderSettings.copy(showImage = it))
                                }
                            }
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    // Switch : Prises en couleur
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(text = "Prises en couleur")
                            Text(
                                text = "Les prises gardent leur couleur originale",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Switch(
                            checked = renderSettings.holdsInColor,
                            onCheckedChange = {
                                coroutineScope.launch {
                                    settingsDataStore.setRenderSettings(renderSettings.copy(holdsInColor = it))
                                }
                            }
                        )
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Slider : Saturation du fond
                    SliderWithLabel(
                        label = "Saturation du fond",
                        value = 1f - renderSettings.grayLevel,
                        valueLabel = "${((1f - renderSettings.grayLevel) * 100).roundToInt()}%",
                        onValueChange = {
                            coroutineScope.launch {
                                settingsDataStore.setRenderSettings(renderSettings.copy(grayLevel = 1f - it))
                            }
                        }
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    // Slider : Luminosité du fond
                    SliderWithLabel(
                        label = "Luminosité du fond",
                        value = renderSettings.brightness,
                        valueLabel = "${(renderSettings.brightness * 100).roundToInt()}%",
                        onValueChange = {
                            coroutineScope.launch {
                                settingsDataStore.setRenderSettings(renderSettings.copy(brightness = it))
                            }
                        }
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    // Slider : Épaisseur contour
                    SliderWithLabel(
                        label = "Épaisseur du contour",
                        value = renderSettings.contourWidth.toFloat(),
                        valueRange = 1f..20f,
                        steps = 18,
                        valueLabel = "${renderSettings.contourWidth}px",
                        onValueChange = {
                            coroutineScope.launch {
                                settingsDataStore.setRenderSettings(renderSettings.copy(contourWidth = it.roundToInt()))
                            }
                        }
                    )
                }
            }

            // ==================== SECTION 4: À PROPOS ====================
            ExpandableSection(
                title = "À propos",
                subtitle = "mastoc Android v1.0",
                expanded = aboutExpanded,
                onToggle = { aboutExpanded = !aboutExpanded }
            ) {
                Column {
                    Text(
                        text = "mastoc Android v1.0",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = "Application de gestion de blocs d'escalade",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Compatible avec Stokt et mastoc server",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

/**
 * Section dépliable avec titre et contenu.
 */
@Composable
private fun ExpandableSection(
    title: String,
    subtitle: String,
    expanded: Boolean,
    onToggle: () -> Unit,
    content: @Composable () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column {
            // Header cliquable
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable(onClick = onToggle)
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Text(
                        text = subtitle,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Icon(
                    imageVector = if (expanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                    contentDescription = if (expanded) "Replier" else "Déplier",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            // Contenu animé
            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically(),
                exit = shrinkVertically()
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(start = 16.dp, end = 16.dp, bottom = 16.dp)
                ) {
                    content()
                }
            }
        }
    }
}

@Composable
private fun ThemeOptionCard(
    theme: AppTheme,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    val (primary, secondary, tertiary) = getThemeColors(theme)

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) {
                MaterialTheme.colorScheme.primaryContainer
            } else {
                MaterialTheme.colorScheme.surfaceVariant
            }
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isSelected) 2.dp else 0.dp
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            RadioButton(
                selected = isSelected,
                onClick = onClick
            )

            Spacer(modifier = Modifier.width(8.dp))

            Text(
                text = theme.displayName,
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.weight(1f)
            )

            // Aperçu des couleurs
            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                ColorPreviewDot(color = primary)
                ColorPreviewDot(color = secondary)
                ColorPreviewDot(color = tertiary)
            }

            if (isSelected) {
                Spacer(modifier = Modifier.width(8.dp))
                Icon(
                    imageVector = Icons.Default.Check,
                    contentDescription = "Sélectionné",
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp)
                )
            }
        }
    }
}

@Composable
private fun ColorPreviewDot(color: Color) {
    Box(
        modifier = Modifier
            .size(20.dp)
            .clip(CircleShape)
            .background(color)
    )
}

@Composable
private fun SliderWithLabel(
    label: String,
    value: Float,
    valueLabel: String,
    onValueChange: (Float) -> Unit,
    valueRange: ClosedFloatingPointRange<Float> = 0f..1f,
    steps: Int = 0
) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = label,
                modifier = Modifier.weight(1f),
                style = MaterialTheme.typography.bodyMedium
            )
            Text(
                text = valueLabel,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary
            )
        }
        Slider(
            value = value,
            onValueChange = onValueChange,
            valueRange = valueRange,
            steps = steps,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

private fun getThemeColors(theme: AppTheme): Triple<Color, Color, Color> {
    return when (theme) {
        AppTheme.COLORFUL -> Triple(ColorfulPrimaryLight, ColorfulSecondaryLight, ColorfulTertiaryLight)
        AppTheme.BLUE -> Triple(BluePrimaryLight, BlueSecondaryLight, BlueTertiaryLight)
        AppTheme.GRAY -> Triple(GrayPrimaryLight, GraySecondaryLight, GrayTertiaryLight)
    }
}

private fun formatBytes(bytes: Long): String {
    return when {
        bytes < 1024 -> "$bytes B"
        bytes < 1024 * 1024 -> "${bytes / 1024} KB"
        else -> "${bytes / (1024 * 1024)} MB"
    }
}
