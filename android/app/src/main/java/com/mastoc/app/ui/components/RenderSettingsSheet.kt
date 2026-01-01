package com.mastoc.app.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.SheetState
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.mastoc.app.data.settings.RenderSettings
import kotlin.math.roundToInt

/**
 * BottomSheet pour les paramètres de rendu (fidélité Python climb_renderer.py).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RenderSettingsSheet(
    sheetState: SheetState,
    settings: RenderSettings,
    onSettingsChange: (RenderSettings) -> Unit,
    onDismiss: () -> Unit
) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp, vertical = 16.dp)
        ) {
            Text(
                text = "Paramètres de rendu",
                style = MaterialTheme.typography.titleLarge
            )

            Spacer(modifier = Modifier.height(24.dp))

            // Switch : Afficher l'image
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Afficher l'image",
                    modifier = Modifier.weight(1f)
                )
                Switch(
                    checked = settings.showImage,
                    onCheckedChange = { onSettingsChange(settings.copy(showImage = it)) }
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

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
                    checked = settings.holdsInColor,
                    onCheckedChange = { onSettingsChange(settings.copy(holdsInColor = it)) }
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Slider : Niveau de gris du fond
            SliderWithLabel(
                label = "Saturation fond",
                value = 1f - settings.grayLevel,
                valueLabel = "${((1f - settings.grayLevel) * 100).roundToInt()}%",
                onValueChange = { onSettingsChange(settings.copy(grayLevel = 1f - it)) }
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Slider : Luminosité du fond
            SliderWithLabel(
                label = "Luminosité fond",
                value = settings.brightness,
                valueLabel = "${(settings.brightness * 100).roundToInt()}%",
                onValueChange = { onSettingsChange(settings.copy(brightness = it)) }
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Slider : Épaisseur contour
            SliderWithLabel(
                label = "Épaisseur contour",
                value = settings.contourWidth.toFloat(),
                valueRange = 1f..20f,
                steps = 18,
                valueLabel = "${settings.contourWidth}px",
                onValueChange = { onSettingsChange(settings.copy(contourWidth = it.roundToInt())) }
            )

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
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
