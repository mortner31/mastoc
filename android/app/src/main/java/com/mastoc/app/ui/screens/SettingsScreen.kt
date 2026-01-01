package com.mastoc.app.ui.screens

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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.mastoc.app.data.settings.AppTheme
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

/**
 * Écran des paramètres.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onNavigateBack: () -> Unit
) {
    val context = LocalContext.current
    val settingsDataStore = SettingsDataStore(context)
    val currentTheme by settingsDataStore.appTheme.collectAsState(initial = AppTheme.COLORFUL)
    val coroutineScope = rememberCoroutineScope()

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
                .padding(16.dp)
        ) {
            Text(
                text = "Apparence",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Thème de couleurs",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Options de thème
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
                Spacer(modifier = Modifier.height(8.dp))
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Info version
            Text(
                text = "À propos",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "mastoc Android v1.0",
                style = MaterialTheme.typography.bodyMedium
            )
            Text(
                text = "Application de gestion de blocs d'escalade",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
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
                MaterialTheme.colorScheme.surface
            }
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isSelected) 4.dp else 1.dp
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            RadioButton(
                selected = isSelected,
                onClick = onClick
            )

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = theme.displayName,
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(4.dp))

                // Aperçu des couleurs
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    ColorPreviewDot(color = primary, label = "Primary")
                    ColorPreviewDot(color = secondary, label = "Secondary")
                    ColorPreviewDot(color = tertiary, label = "Tertiary")
                }
            }

            if (isSelected) {
                Icon(
                    imageVector = Icons.Default.Check,
                    contentDescription = "Sélectionné",
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

@Composable
private fun ColorPreviewDot(
    color: Color,
    label: String
) {
    Box(
        modifier = Modifier
            .size(24.dp)
            .clip(CircleShape)
            .background(color)
    )
}

private fun getThemeColors(theme: AppTheme): Triple<Color, Color, Color> {
    return when (theme) {
        AppTheme.COLORFUL -> Triple(ColorfulPrimaryLight, ColorfulSecondaryLight, ColorfulTertiaryLight)
        AppTheme.BLUE -> Triple(BluePrimaryLight, BlueSecondaryLight, BlueTertiaryLight)
        AppTheme.GRAY -> Triple(GrayPrimaryLight, GraySecondaryLight, GrayTertiaryLight)
    }
}
