package com.mastoc.app.ui.components

import android.graphics.Bitmap
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.mastoc.app.data.model.Climb
import com.mastoc.app.data.model.HoldType
import com.mastoc.app.ui.theme.MastocTheme
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

/**
 * Carte affichant un climb dans la liste avec picto.
 *
 * Layout 25% | 50% | 25% :
 * - Gauche : Picto carré du bloc
 * - Centre : Titre, auteur, date
 * - Droite : Grade, stats (likes, croix)
 */
@OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)
@Composable
fun ClimbCard(
    climb: Climb,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    picto: Bitmap? = null
) {
    Card(
        onClick = onClick,
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(80.dp)
                .padding(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Zone gauche (25%) : Picto
            PictoZone(
                picto = picto,
                modifier = Modifier.weight(0.25f)
            )

            Spacer(modifier = Modifier.width(8.dp))

            // Zone centre (50%) : Infos
            InfoZone(
                climb = climb,
                modifier = Modifier.weight(0.50f)
            )

            Spacer(modifier = Modifier.width(8.dp))

            // Zone droite (25%) : Grade + Stats
            StatsZone(
                climb = climb,
                modifier = Modifier.weight(0.25f)
            )
        }
    }
}

/**
 * Zone gauche : affiche le picto du bloc.
 */
@Composable
private fun PictoZone(
    picto: Bitmap?,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .aspectRatio(1f)
            .clip(RoundedCornerShape(8.dp))
            .border(
                width = 1.dp,
                color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                shape = RoundedCornerShape(8.dp)
            ),
        contentAlignment = Alignment.Center
    ) {
        if (picto != null) {
            Image(
                bitmap = picto.asImageBitmap(),
                contentDescription = "Picto du bloc",
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.FillBounds
            )
        } else {
            // Placeholder quand pas de picto
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .aspectRatio(1f)
                    .background(MaterialTheme.colorScheme.surfaceVariant),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "...",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

/**
 * Zone centre : titre, auteur, date.
 */
@Composable
private fun InfoZone(
    climb: Climb,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxHeight(),
        verticalArrangement = Arrangement.SpaceEvenly
    ) {
        // Titre
        Text(
            text = climb.name,
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis
        )

        // Auteur
        Text(
            text = "par ${climb.setterName ?: "Inconnu"}",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis
        )

        // Date
        val formattedDate = remember(climb.createdAt) {
            formatDate(climb.createdAt)
        }
        Text(
            text = formattedDate,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

/**
 * Zone droite : grade et statistiques.
 */
@Composable
private fun StatsZone(
    climb: Climb,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxHeight(),
        horizontalAlignment = Alignment.End,
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        // Grade (en haut)
        GradeBadge(grade = climb.displayGrade)

        // Stats (en bas)
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Likes
            StatChip(
                icon = Icons.Default.Favorite,
                value = climb.totalLikes,
                tint = MaterialTheme.colorScheme.error
            )

            // Croix (climbed by)
            StatChip(
                icon = Icons.Default.Close,
                value = climb.climbedBy,
                tint = MaterialTheme.colorScheme.primary
            )
        }
    }
}

/**
 * Petit indicateur de stat (icône + valeur).
 */
@Composable
private fun StatChip(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    value: Int,
    tint: Color
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(2.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(12.dp),
            tint = tint
        )
        Text(
            text = "$value",
            style = MaterialTheme.typography.labelSmall,
            color = tint
        )
    }
}

/**
 * Formate une date ISO en format lisible (ex: "15 déc. 2025").
 */
private fun formatDate(isoDate: String?): String {
    if (isoDate.isNullOrBlank()) return ""

    return try {
        // Parse différents formats possibles
        val date = when {
            isoDate.contains("T") -> LocalDate.parse(isoDate.substringBefore("T"))
            else -> LocalDate.parse(isoDate.take(10))
        }

        val formatter = DateTimeFormatter.ofPattern("d MMM yyyy", Locale.FRENCH)
        date.format(formatter)
    } catch (e: Exception) {
        isoDate.take(10) // Fallback
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

// --- Legacy components for backward compatibility ---

/**
 * Indicateurs visuels des types de prises dans le climb.
 * (Conservé pour compatibilité avec d'autres écrans)
 */
@Composable
fun HoldTypeIndicators(climb: Climb) {
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
        if (startCount > 0) {
            HoldTypePill(count = startCount, label = "S", color = Color(0xFF4CAF50))
        }
        if (otherCount > 0) {
            HoldTypePill(count = otherCount, label = "O", color = Color(0xFF9E9E9E))
        }
        if (feetCount > 0) {
            HoldTypePill(count = feetCount, label = "F", color = Color(0xFF31DAFF))
        }
        if (topCount > 0) {
            HoldTypePill(count = topCount, label = "T", color = Color(0xFFF44336))
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
                source = "stokt",
                createdAt = "2025-12-15T10:30:00"
            ),
            onClick = {},
            picto = null
        )
    }
}

@Preview(showBackground = true)
@Composable
fun ClimbCardWithoutPictoPreview() {
    MastocTheme {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            ClimbCard(
                climb = Climb(
                    id = "1",
                    faceId = "face1",
                    name = "Bloc avec un nom très long qui dépasse",
                    holdsList = "S123 T129",
                    gradeFont = "7c+",
                    setterName = "Marie Martin",
                    climbedBy = 156,
                    totalLikes = 89,
                    source = "stokt",
                    createdAt = "2025-01-02"
                ),
                onClick = {}
            )
            ClimbCard(
                climb = Climb(
                    id = "2",
                    faceId = "face1",
                    name = "Petit",
                    holdsList = "S1 O2 T3",
                    gradeFont = "4a",
                    setterName = null,
                    climbedBy = 3,
                    totalLikes = 0,
                    source = "stokt"
                ),
                onClick = {}
            )
        }
    }
}
