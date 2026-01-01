package com.mastoc.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.navigation.compose.rememberNavController
import com.mastoc.app.data.settings.AppTheme
import com.mastoc.app.data.settings.SettingsDataStore
import com.mastoc.app.ui.navigation.MastocNavGraph
import com.mastoc.app.ui.theme.MastocTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Splash screen (doit être appelé AVANT super.onCreate)
        installSplashScreen()

        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val settingsDataStore = SettingsDataStore(this)

        setContent {
            val appTheme by settingsDataStore.appTheme.collectAsState(initial = AppTheme.COLORFUL)

            MastocTheme(appTheme = appTheme) {
                Surface(modifier = Modifier.fillMaxSize()) {
                    val navController = rememberNavController()
                    MastocNavGraph(navController = navController)
                }
            }
        }
    }
}
