package com.mastoc.app.ui.screens

import androidx.compose.animation.AnimatedVisibility
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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Card
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
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.mastoc.app.ui.components.ClimbCard
import com.mastoc.app.viewmodel.ClimbListViewModel
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
                title = { Text("mastoc") },
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
            // Barre de recherche
            SearchBar(
                query = uiState.searchQuery,
                onQueryChange = viewModel::updateSearch,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            )

            // Panneau de filtres (animé)
            AnimatedVisibility(visible = uiState.showFilters) {
                FilterPanel(
                    minGrade = uiState.minGrade,
                    maxGrade = uiState.maxGrade,
                    gradeRange = uiState.gradeRange,
                    onGradeRangeChange = viewModel::updateGradeRange,
                    selectedSetter = uiState.selectedSetter,
                    availableSetters = uiState.availableSetters,
                    onSetterChange = viewModel::updateSetter,
                    sortOption = uiState.sortOption,
                    onSortChange = viewModel::updateSort,
                    onReset = viewModel::resetFilters,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp)
                )
            }

            // Compteur résultats
            Text(
                text = "${uiState.filteredClimbs.size} bloc(s)",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)
            )

            // Liste des climbs
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
                        // Espace en bas
                        item {
                            Spacer(modifier = Modifier.height(16.dp))
                        }
                    }
                }

                // Indicateur de chargement superposé
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

@Composable
private fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = query,
        onValueChange = onQueryChange,
        modifier = modifier,
        placeholder = { Text("Rechercher un bloc...") },
        leadingIcon = {
            Icon(
                imageVector = Icons.Default.Search,
                contentDescription = null
            )
        },
        trailingIcon = {
            if (query.isNotEmpty()) {
                IconButton(onClick = { onQueryChange("") }) {
                    Icon(
                        imageVector = Icons.Default.Clear,
                        contentDescription = "Effacer"
                    )
                }
            }
        },
        singleLine = true
    )
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
private fun FilterPanel(
    minGrade: Float,
    maxGrade: Float,
    gradeRange: ClosedFloatingPointRange<Float>,
    onGradeRangeChange: (Float, Float) -> Unit,
    selectedSetter: String?,
    availableSetters: List<String>,
    onSetterChange: (String?) -> Unit,
    sortOption: SortOption,
    onSortChange: (SortOption) -> Unit,
    onReset: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Header avec bouton reset
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Filtres",
                    style = MaterialTheme.typography.titleMedium
                )
                TextButton(onClick = onReset) {
                    Text("Réinitialiser")
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Slider grade
            Text(
                text = "Grade: ${ircraToFont(minGrade)} - ${ircraToFont(maxGrade)}",
                style = MaterialTheme.typography.bodyMedium
            )
            RangeSlider(
                value = minGrade..maxGrade,
                onValueChange = { range ->
                    onGradeRangeChange(range.start, range.endInclusive)
                },
                valueRange = gradeRange,
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Dropdown setter
            SetterDropdown(
                selectedSetter = selectedSetter,
                availableSetters = availableSetters,
                onSetterChange = onSetterChange,
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Chips de tri
            Text(
                text = "Trier par",
                style = MaterialTheme.typography.bodyMedium
            )
            Spacer(modifier = Modifier.height(4.dp))
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                SortOption.entries.forEach { option ->
                    FilterChip(
                        selected = sortOption == option,
                        onClick = { onSortChange(option) },
                        label = { Text(option.displayName) }
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SetterDropdown(
    selectedSetter: String?,
    availableSetters: List<String>,
    onSetterChange: (String?) -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }

    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = it },
        modifier = modifier
    ) {
        OutlinedTextField(
            value = selectedSetter ?: "Tous les setters",
            onValueChange = {},
            readOnly = true,
            label = { Text("Setter") },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier = Modifier
                .menuAnchor()
                .fillMaxWidth()
        )

        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            // Option "Tous"
            DropdownMenuItem(
                text = { Text("Tous les setters") },
                onClick = {
                    onSetterChange(null)
                    expanded = false
                }
            )
            // Setters disponibles
            availableSetters.forEach { setter ->
                DropdownMenuItem(
                    text = { Text(setter) },
                    onClick = {
                        onSetterChange(setter)
                        expanded = false
                    }
                )
            }
        }
    }
}

/**
 * Convertit un grade IRCRA en notation Fontainebleau approximative.
 */
private fun ircraToFont(ircra: Float): String {
    return when {
        ircra < 10 -> "3"
        ircra < 15 -> "4"
        ircra < 20 -> "5"
        ircra < 23 -> "5+"
        ircra < 26 -> "6A"
        ircra < 29 -> "6A+"
        ircra < 32 -> "6B"
        ircra < 35 -> "6B+"
        ircra < 38 -> "6C"
        ircra < 41 -> "6C+"
        ircra < 44 -> "7A"
        ircra < 47 -> "7A+"
        ircra < 50 -> "7B"
        ircra < 53 -> "7B+"
        ircra < 56 -> "7C"
        ircra < 59 -> "7C+"
        ircra < 62 -> "8A"
        ircra < 65 -> "8A+"
        ircra < 68 -> "8B"
        ircra < 71 -> "8B+"
        ircra < 74 -> "8C"
        else -> "8C+"
    }
}
