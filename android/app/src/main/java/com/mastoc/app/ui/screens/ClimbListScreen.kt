package com.mastoc.app.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RangeSlider
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.Surface
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.mastoc.app.ui.components.ClimbCard
import com.mastoc.app.ui.components.GRADE_COUNT
import com.mastoc.app.ui.components.indexToFont
import com.mastoc.app.viewmodel.ClimbListViewModel
import com.mastoc.app.viewmodel.SetterFilterMode
import com.mastoc.app.viewmodel.SetterInfo
import com.mastoc.app.viewmodel.SortOption

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ClimbListScreen(
    onClimbClick: (climbIds: List<String>, index: Int) -> Unit,
    onSettingsClick: () -> Unit = {},
    viewModel: ClimbListViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    // Afficher les erreurs
    LaunchedEffect(uiState.error) {
        uiState.error?.let { error ->
            snackbarHostState.showSnackbar(error)
            viewModel.clearError()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Montoboard") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary
                ),
                actions = {
                    // Bouton filtres
                    IconButton(onClick = viewModel::toggleFilters) {
                        Icon(
                            imageVector = Icons.Default.Menu,
                            contentDescription = "Filtres",
                            tint = MaterialTheme.colorScheme.onPrimary
                        )
                    }
                    // Bouton refresh
                    IconButton(
                        onClick = viewModel::refresh,
                        enabled = !uiState.isRefreshing
                    ) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Rafraîchir",
                            tint = MaterialTheme.colorScheme.onPrimary
                        )
                    }
                    // Bouton settings
                    IconButton(onClick = onSettingsClick) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = "Paramètres",
                            tint = MaterialTheme.colorScheme.onPrimary
                        )
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Cartouche résumé des filtres (cliquable)
            FilterSummaryChip(
                searchQuery = uiState.searchQuery,
                minGradeIndex = uiState.minGradeIndex,
                maxGradeIndex = uiState.maxGradeIndex,
                setterFilterMode = uiState.setterFilterMode,
                selectedSetters = uiState.selectedSetters,
                sortOption = uiState.sortOption,
                onClick = viewModel::toggleFilters,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            )

            // Panneau de filtres (animé)
            AnimatedVisibility(visible = uiState.showFilters) {
                FilterPanel(
                    searchQuery = uiState.searchQuery,
                    onSearchChange = viewModel::updateSearch,
                    minGradeIndex = uiState.minGradeIndex,
                    maxGradeIndex = uiState.maxGradeIndex,
                    onGradeRangeChange = viewModel::updateGradeRange,
                    setterFilterMode = uiState.setterFilterMode,
                    selectedSetters = uiState.selectedSetters,
                    availableSetters = uiState.availableSetters,
                    onSetterFilterModeChange = viewModel::updateSetterFilterMode,
                    onSetterToggle = viewModel::toggleSetterSelection,
                    onSelectAllSetters = viewModel::selectAllSetters,
                    onClearSetterSelection = viewModel::clearSetterSelection,
                    sortOption = uiState.sortOption,
                    onSortChange = viewModel::updateSort,
                    onReset = viewModel::resetFilters,
                    onApply = viewModel::toggleFilters,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp)
                )
            }

            // Compteur résultats (affichés / total serveur)
            val countText = if (uiState.totalCount > 0 && uiState.filteredClimbs.size < uiState.totalCount) {
                "${uiState.filteredClimbs.size} / ${uiState.totalCount} blocs"
            } else {
                "${uiState.filteredClimbs.size} bloc(s)"
            }
            Text(
                text = countText,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)
            )

            // Liste des climbs
            val listState = rememberLazyListState()

            // Détecter quand on approche de la fin pour charger plus
            val shouldLoadMore by remember {
                derivedStateOf {
                    val layoutInfo = listState.layoutInfo
                    val totalItems = layoutInfo.totalItemsCount
                    val lastVisibleIndex = layoutInfo.visibleItemsInfo.lastOrNull()?.index ?: 0
                    // Charger quand on est à 5 items de la fin
                    lastVisibleIndex >= totalItems - 5 && totalItems > 0
                }
            }

            LaunchedEffect(shouldLoadMore) {
                if (shouldLoadMore && uiState.hasMore && !uiState.isLoadingMore && !uiState.isRefreshing) {
                    viewModel.loadMore()
                }
            }

            Box(modifier = Modifier.fillMaxSize()) {
                if (uiState.filteredClimbs.isEmpty() && !uiState.isRefreshing) {
                    // État vide
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator()
                        } else {
                            Text(
                                text = "Aucun bloc trouvé",
                                style = MaterialTheme.typography.bodyLarge,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                } else {
                    LazyColumn(
                        state = listState,
                        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        val climbIds = uiState.filteredClimbs.map { it.id }
                        items(
                            items = uiState.filteredClimbs,
                            key = { it.id }
                        ) { climb ->
                            val index = climbIds.indexOf(climb.id)
                            ClimbCard(
                                climb = climb,
                                onClick = { onClimbClick(climbIds, index) }
                            )
                        }

                        // Indicateur de chargement en bas
                        if (uiState.isLoadingMore) {
                            item {
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(16.dp),
                                    contentAlignment = Alignment.Center
                                ) {
                                    CircularProgressIndicator(
                                        modifier = Modifier.size(24.dp),
                                        strokeWidth = 2.dp
                                    )
                                }
                            }
                        }

                        // Espace en bas
                        item {
                            Spacer(modifier = Modifier.height(16.dp))
                        }
                    }
                }

                // Indicateur de chargement superposé (refresh)
                if (uiState.isRefreshing) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
            }
        }
    }
}

/**
 * Cartouche cliquable affichant un résumé des filtres actifs.
 */
@Composable
private fun FilterSummaryChip(
    searchQuery: String,
    minGradeIndex: Int,
    maxGradeIndex: Int,
    setterFilterMode: SetterFilterMode,
    selectedSetters: Set<String>,
    sortOption: SortOption,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    // Construire le texte du résumé
    val summaryParts = mutableListOf<String>()

    // Recherche textuelle
    if (searchQuery.isNotBlank()) {
        summaryParts.add("\"${searchQuery}\"")
    }

    // Grade (seulement si différent des valeurs par défaut)
    val gradeChanged = minGradeIndex > 0 || maxGradeIndex < GRADE_COUNT - 1
    if (gradeChanged) {
        summaryParts.add("${indexToFont(minGradeIndex)} → ${indexToFont(maxGradeIndex)}")
    }

    // Setter (mode include/exclude)
    if (setterFilterMode != SetterFilterMode.NONE && selectedSetters.isNotEmpty()) {
        val prefix = if (setterFilterMode == SetterFilterMode.INCLUDE) "+" else "-"
        val setterText = if (selectedSetters.size <= 2) {
            selectedSetters.joinToString(", ") { "$prefix$it" }
        } else {
            "$prefix${selectedSetters.size} setters"
        }
        summaryParts.add(setterText)
    }

    // Tri (seulement si différent du défaut)
    if (sortOption != SortOption.DATE_DESC) {
        summaryParts.add(sortOption.displayName)
    }

    val summaryText = if (summaryParts.isEmpty()) {
        "Tous les blocs"
    } else {
        summaryParts.joinToString(" • ")
    }

    Surface(
        modifier = modifier.clickable(onClick = onClick),
        shape = RoundedCornerShape(8.dp),
        color = MaterialTheme.colorScheme.surfaceVariant,
        tonalElevation = 2.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Search,
                contentDescription = null,
                modifier = Modifier.size(20.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.width(12.dp))
            Text(
                text = summaryText,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.weight(1f)
            )
            Icon(
                imageVector = Icons.Default.Menu,
                contentDescription = "Filtres",
                modifier = Modifier.size(20.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
private fun FilterPanel(
    searchQuery: String,
    onSearchChange: (String) -> Unit,
    minGradeIndex: Int,
    maxGradeIndex: Int,
    onGradeRangeChange: (Int, Int) -> Unit,
    setterFilterMode: SetterFilterMode,
    selectedSetters: Set<String>,
    availableSetters: List<SetterInfo>,
    onSetterFilterModeChange: (SetterFilterMode) -> Unit,
    onSetterToggle: (String) -> Unit,
    onSelectAllSetters: () -> Unit,
    onClearSetterSelection: () -> Unit,
    sortOption: SortOption,
    onSortChange: (SortOption) -> Unit,
    onReset: () -> Unit,
    onApply: () -> Unit,
    modifier: Modifier = Modifier
) {
    val scrollState = rememberScrollState()

    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier
                .heightIn(max = 400.dp)
                .padding(12.dp)
        ) {
            // Header avec bouton reset (fixe en haut)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Filtres",
                    style = MaterialTheme.typography.titleSmall
                )
                TextButton(
                    onClick = onReset,
                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 0.dp)
                ) {
                    Text("Réinitialiser", style = MaterialTheme.typography.bodySmall)
                }
            }

            // Contenu scrollable
            Column(
                modifier = Modifier
                    .weight(1f)
                    .verticalScroll(scrollState)
            ) {
                Spacer(modifier = Modifier.height(4.dp))

                // Recherche textuelle (plus compact)
                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = onSearchChange,
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("Rechercher...", style = MaterialTheme.typography.bodySmall) },
                    leadingIcon = {
                        Icon(
                            imageVector = Icons.Default.Search,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp)
                        )
                    },
                    trailingIcon = {
                        if (searchQuery.isNotEmpty()) {
                            IconButton(onClick = { onSearchChange("") }) {
                                Icon(
                                    imageVector = Icons.Default.Clear,
                                    contentDescription = "Effacer",
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                        }
                    },
                    singleLine = true,
                    textStyle = MaterialTheme.typography.bodySmall
                )

                Spacer(modifier = Modifier.height(8.dp))

                // Slider grade
                Text(
                    text = "Grade: ${indexToFont(minGradeIndex)} - ${indexToFont(maxGradeIndex)}",
                    style = MaterialTheme.typography.bodySmall
                )
                RangeSlider(
                    value = minGradeIndex.toFloat()..maxGradeIndex.toFloat(),
                    onValueChange = { range ->
                        onGradeRangeChange(range.start.toInt(), range.endInclusive.toInt())
                    },
                    valueRange = 0f..(GRADE_COUNT - 1).toFloat(),
                    steps = GRADE_COUNT - 2,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(4.dp))

                // Section setter avancée
                SetterFilterSection(
                    filterMode = setterFilterMode,
                    selectedSetters = selectedSetters,
                    availableSetters = availableSetters,
                    onFilterModeChange = onSetterFilterModeChange,
                    onSetterToggle = onSetterToggle,
                    onSelectAll = onSelectAllSetters,
                    onClearSelection = onClearSetterSelection
                )

                Spacer(modifier = Modifier.height(8.dp))

                // Chips de tri
                Text(
                    text = "Trier par",
                    style = MaterialTheme.typography.bodySmall
                )
                Spacer(modifier = Modifier.height(2.dp))
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                    verticalArrangement = Arrangement.spacedBy(2.dp)
                ) {
                    SortOption.entries.forEach { option ->
                        FilterChip(
                            selected = sortOption == option,
                            onClick = { onSortChange(option) },
                            label = { Text(option.displayName, style = MaterialTheme.typography.labelSmall) }
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Bouton Appliquer (fixe en bas)
            Button(
                onClick = onApply,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Appliquer")
            }
        }
    }
}

/**
 * Section de filtrage avancé des setters avec mode Include/Exclude.
 */
@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
private fun SetterFilterSection(
    filterMode: SetterFilterMode,
    selectedSetters: Set<String>,
    availableSetters: List<SetterInfo>,
    onFilterModeChange: (SetterFilterMode) -> Unit,
    onSetterToggle: (String) -> Unit,
    onSelectAll: () -> Unit,
    onClearSelection: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        // Titre + Chips de mode sur la même ligne
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Setters",
                style = MaterialTheme.typography.bodySmall
            )
            SetterFilterMode.entries.forEach { mode ->
                FilterChip(
                    selected = filterMode == mode,
                    onClick = { onFilterModeChange(mode) },
                    label = { Text(mode.displayName, style = MaterialTheme.typography.labelSmall) }
                )
            }
        }

        // Liste des setters (seulement si mode != NONE)
        if (filterMode != SetterFilterMode.NONE) {
            Spacer(modifier = Modifier.height(4.dp))

            // Boutons Tout / Aucun (compact)
            Row(
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                TextButton(
                    onClick = onSelectAll,
                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 0.dp)
                ) {
                    Text("Tout", style = MaterialTheme.typography.labelSmall)
                }
                TextButton(
                    onClick = onClearSelection,
                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 0.dp)
                ) {
                    Text("Aucun", style = MaterialTheme.typography.labelSmall)
                }
                Text(
                    text = "(${selectedSetters.size} sélectionné${if (selectedSetters.size > 1) "s" else ""})",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.align(Alignment.CenterVertically)
                )
            }

            // Liste des setters (compact)
            availableSetters.take(15).forEach { setterInfo ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onSetterToggle(setterInfo.name) }
                        .padding(vertical = 2.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = setterInfo.name in selectedSetters,
                        onCheckedChange = { onSetterToggle(setterInfo.name) },
                        modifier = Modifier.size(32.dp)
                    )
                    Text(
                        text = "${setterInfo.name} (${setterInfo.climbCount})",
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
}

