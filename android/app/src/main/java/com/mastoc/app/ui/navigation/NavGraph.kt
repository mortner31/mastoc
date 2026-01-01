package com.mastoc.app.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.navArgument
import com.mastoc.app.ui.screens.AdvancedSearchScreen
import com.mastoc.app.ui.screens.ClimbDetailScreen
import com.mastoc.app.ui.screens.ClimbListScreen
import com.mastoc.app.ui.screens.CreateScreen
import com.mastoc.app.ui.screens.ProfileScreen
import com.mastoc.app.ui.screens.SettingsScreen
import com.mastoc.app.ui.screens.SyncScreen

/**
 * Navigation principale de l'application avec Bottom Navigation Bar.
 */
@Composable
fun MastocNavGraph(navController: NavHostController) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    // Routes qui affichent la bottom nav
    val bottomNavRoutes = BottomNavDestination.entries.map { it.route }
    val showBottomNav = currentDestination?.route in bottomNavRoutes

    Scaffold(
        bottomBar = {
            if (showBottomNav) {
                NavigationBar {
                    BottomNavDestination.entries.forEach { destination ->
                        val selected = currentDestination?.hierarchy?.any {
                            it.route == destination.route
                        } == true

                        NavigationBarItem(
                            icon = {
                                Icon(
                                    imageVector = destination.icon,
                                    contentDescription = destination.label
                                )
                            },
                            label = { Text(destination.label) },
                            selected = selected,
                            onClick = {
                                navController.navigate(destination.route) {
                                    // Pop up to the start destination to avoid building up a large stack
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    // Avoid multiple copies of the same destination
                                    launchSingleTop = true
                                    // Restore state when reselecting a previously selected item
                                    restoreState = true
                                }
                            }
                        )
                    }
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Simple.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            // Bottom Nav destinations
            composable(Screen.Sync.route) {
                SyncScreen()
            }

            composable(Screen.Simple.route) {
                ClimbListScreen(
                    onClimbClick = { climbIds, index ->
                        navController.navigate(Screen.ClimbDetail.createRoute(climbIds, index))
                    },
                    onSettingsClick = {
                        navController.navigate(Screen.Settings.route)
                    }
                )
            }

            composable(Screen.Advanced.route) {
                AdvancedSearchScreen(
                    onClimbClick = { climbId ->
                        navController.navigate(Screen.ClimbDetail.createRoute(climbId))
                    }
                )
            }

            composable(Screen.Create.route) {
                CreateScreen()
            }

            composable(Screen.Profile.route) {
                ProfileScreen()
            }

            // Sub-routes (not in bottom nav)
            composable(
                route = Screen.ClimbDetail.route,
                arguments = listOf(
                    navArgument("climbIds") { type = NavType.StringType },
                    navArgument("initialIndex") { type = NavType.IntType }
                )
            ) { backStackEntry ->
                val climbIdsStr = backStackEntry.arguments?.getString("climbIds") ?: return@composable
                val initialIndex = backStackEntry.arguments?.getInt("initialIndex") ?: 0
                val climbIds = climbIdsStr.split(",")
                ClimbDetailScreen(
                    climbIds = climbIds,
                    initialIndex = initialIndex,
                    onNavigateBack = { navController.popBackStack() }
                )
            }

            composable(Screen.Settings.route) {
                SettingsScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }

            // Legacy routes for compatibility
            composable(Screen.ClimbList.route) {
                ClimbListScreen(
                    onClimbClick = { climbIds, index ->
                        navController.navigate(Screen.ClimbDetail.createRoute(climbIds, index))
                    },
                    onSettingsClick = {
                        navController.navigate(Screen.Settings.route)
                    }
                )
            }

            composable(
                route = Screen.HoldSelector.route,
                arguments = listOf(
                    navArgument("faceId") { type = NavType.StringType }
                )
            ) { backStackEntry ->
                val faceId = backStackEntry.arguments?.getString("faceId") ?: return@composable
                com.mastoc.app.ui.screens.HoldSelectorScreen(
                    faceId = faceId,
                    onNavigateBack = { navController.popBackStack() },
                    onClimbClick = { climbId ->
                        navController.navigate(Screen.ClimbDetail.createRoute(climbId))
                    }
                )
            }
        }
    }
}
