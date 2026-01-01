package com.mastoc.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.HoldType
import com.mastoc.app.ui.theme.MastocTheme

/**
 * Carte affichant un climb dans la liste.
 */
@OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)
@Composable
fun ClimbCard(
    climb: Climb,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onClick,
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Première ligne : Nom + Grade
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = climb.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f)
                )
                Spacer(modifier = Modifier.width(8.dp))
                GradeBadge(grade = climb.displayGrade)
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Pictos des prises
            HoldTypeIndicators(climb = climb)

            Spacer(modifier = Modifier.height(8.dp))

            // Deuxième ligne : Setter + Stats
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Setter
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = climb.setterName ?: "Inconnu",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                // Stats
                Row(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Climbed by
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Person,
                            contentDescription = null,
                            modifier = Modifier.size(14.dp),
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(2.dp))
                        Text(
                            text = "${climb.climbedBy}",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }

                    // Likes
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Favorite,
                            contentDescription = null,
                            modifier = Modifier.size(14.dp),
                            tint = MaterialTheme.colorScheme.error
                        )
                        Spacer(modifier = Modifier.width(2.dp))
                        Text(
                            text = "${climb.totalLikes}",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.error
                        )
                    }
                }
            }
        }
    }
}

/**
 * Indicateurs visuels des types de prises dans le climb.
 */
@Composable
private fun HoldTypeIndicators(climb: Climb) {
    val climbHolds = climb.getClimbHolds()
    if (climbHolds.isEmpty()) return

    val startCount = climbHolds.count { it.holdType == HoldType.START }
    val otherCount = climbHolds.count { it.holdType == HoldType.OTHER }
    val feetCount = climbHolds.count { it.holdType == HoldType.FEET }
    val topCount = climbHolds.count { it.holdType == HoldType.TOP }

    Row(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // START (vert)
        if (startCount > 0) {
            HoldTypePill(
                count = startCount,
                label = "S",
                color = Color(0xFF4CAF50) // Vert
            )
        }

        // OTHER (blanc/gris)
        if (otherCount > 0) {
            HoldTypePill(
                count = otherCount,
                label = "O",
                color = Color(0xFF9E9E9E) // Gris
            )
        }

        // FEET (bleu néon)
        if (feetCount > 0) {
            HoldTypePill(
                count = feetCount,
                label = "F",
                color = Color(0xFF31DAFF) // Bleu néon
            )
        }

        // TOP (rouge)
        if (topCount > 0) {
            HoldTypePill(
                count = topCount,
                label = "T",
                color = Color(0xFFF44336) // Rouge
            )
        }
    }
}

/**
 * Petit badge coloré indiquant le type et le nombre de prises.
 */
@Composable
private fun HoldTypePill(
    count: Int,
    label: String,
    color: Color
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(2.dp)
    ) {
        Box(
            modifier = Modifier
                .size(12.dp)
                .background(color, CircleShape)
        )
        Text(
            text = "$count",
            style = MaterialTheme.typography.labelSmall,
            color = color
        )
    }
}

/**
 * Badge affichant le grade du climb.
 */
@Composable
fun GradeBadge(
    grade: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Text(
            text = grade,
            style = MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onPrimaryContainer,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

@Preview(showBackground = true)
@Composable
fun ClimbCardPreview() {
    MastocTheme {
        ClimbCard(
            climb = Climb(
                id = "1",
                faceId = "face1",
                name = "Super Bloc Rouge",
                holdsList = "S123 S124 O125 O126 O127 F128 T129",
                gradeFont = "6a+",
                setterName = "Jean Dupont",
                climbedBy = 42,
                totalLikes = 15,
                source = "stokt"
            ),
            onClick = {}
        )
    }
}
