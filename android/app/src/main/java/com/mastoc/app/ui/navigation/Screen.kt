package com.mastoc.app.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Search
import androidx.compose.ui.graphics.vector.ImageVector

/**
 * Routes de navigation de l'application.
 */
sealed class Screen(val route: String) {
    // Bottom Navigation destinations (5 modes)
    data object Sync : Screen("sync")
    data object Simple : Screen("simple")
    data object Advanced : Screen("advanced")
    data object Create : Screen("create")
    data object Profile : Screen("profile")

    // Sub-routes (not in bottom nav)
    data object ClimbDetail : Screen("climb_detail/{climbId}") {
        fun createRoute(climbId: String) = "climb_detail/$climbId"
    }

    data object Settings : Screen("settings")

    // Legacy route redirect
    data object ClimbList : Screen("climb_list")
    data object HoldSelector : Screen("hold_selector/{faceId}") {
        fun createRoute(faceId: String) = "hold_selector/$faceId"
    }
}

/**
 * Destinations de la Bottom Navigation Bar.
 */
enum class BottomNavDestination(
    val route: String,
    val icon: ImageVector,
    val label: String
) {
    SYNC(Screen.Sync.route, Icons.Default.Refresh, "Sync"),
    SIMPLE(Screen.Simple.route, Icons.Default.List, "Simple"),
    ADVANCED(Screen.Advanced.route, Icons.Default.Search, "Avancée"),
    CREATE(Screen.Create.route, Icons.Default.Add, "Créer"),
    PROFILE(Screen.Profile.route, Icons.Default.Person, "Profil")
}
