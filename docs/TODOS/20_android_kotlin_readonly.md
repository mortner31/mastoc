# TODO 20 - Application Android Kotlin (Lecture Seule)

## Objectif

Créer une première version de l'application Android en **lecture seule**, connectée au backend Railway.

### Scope

| Inclus | Exclus |
|--------|--------|
| Liste des climbs avec filtres | Création/édition de blocs |
| Visualisation sur image du mur | Authentification utilisateur |
| Recherche par prises (tap) | Sync bidirectionnelle |
| Modes de coloration (heatmaps) | Mode offline complet |
| Sync depuis Railway API | Hold Annotations |

---

## Icône et Thème

### Icône Application

**Source** : `/docs/images/Gemini_Generated_Image_m1l3sum1l3sum1l3.png`

![Icône mastoc](../images/Gemini_Generated_Image_m1l3sum1l3sum1l3.png)

Style : Bras de pierre/roche avec prises d'escalade colorées (rouge, vert, jaune)

### Palette de Couleurs (Material 3)

Couleurs extraites de l'icône :

```kotlin
// Primary - Rouge (prises rouges dominantes)
val PrimaryLight = Color(0xFFD32F2F)
val PrimaryDark = Color(0xFFEF5350)

// Secondary - Vert (prises vertes)
val SecondaryLight = Color(0xFF388E3C)
val SecondaryDark = Color(0xFF66BB6A)

// Tertiary - Jaune/Or (prises jaunes)
val TertiaryLight = Color(0xFFFBC02D)
val TertiaryDark = Color(0xFFFFD54F)

// Surface - Gris pierre (bras)
val SurfaceLight = Color(0xFFF5F0E8)
val SurfaceDark = Color(0xFF2D2418)

// Background - Sombre (fond icône)
val BackgroundLight = Color(0xFFFFFBFE)
val BackgroundDark = Color(0xFF1C1B1F)
```

---

## Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Langage | **Kotlin** | 2.0.0 |
| UI | **Jetpack Compose** | BOM 2023.10.01 |
| Architecture | MVVM | - |
| Base de données | Room | 2.6.1 |
| Réseau | Retrofit + OkHttp | 2.9.0 |
| DI | Manual (ViewModel Factory) | - |
| Images | Coil | 2.5.0 |
| Dessin prises | Compose Canvas | - |

### Versions SDK

| SDK | Version |
|-----|---------|
| Min SDK | **31** (Android 12) |
| Target SDK | **34** (Android 14) |
| Compile SDK | **34** |
| JDK | **17** |

---

## Configuration Machine

| Propriété | Valeur |
|-----------|--------|
| SDK Path | `/home/mortner/Android` |
| Templates | `/home/mortner/Repositories/templates/android/` |

---

## Structure Projet

```
android/
├── app/
│   ├── src/main/
│   │   ├── java/com/mastoc/app/
│   │   │   ├── MainActivity.kt
│   │   │   ├── MastocApplication.kt
│   │   │   ├── data/
│   │   │   │   ├── api/           # Retrofit service, DTOs
│   │   │   │   │   ├── MastocApiService.kt
│   │   │   │   │   └── dto/       # ClimbDto, HoldDto, etc.
│   │   │   │   ├── local/         # Room entities, DAOs
│   │   │   │   │   ├── AppDatabase.kt
│   │   │   │   │   ├── ClimbEntity.kt
│   │   │   │   │   └── ClimbDao.kt
│   │   │   │   ├── model/         # Domain models
│   │   │   │   │   ├── Climb.kt
│   │   │   │   │   └── Hold.kt
│   │   │   │   └── repository/
│   │   │   │       └── ClimbRepository.kt
│   │   │   ├── ui/
│   │   │   │   ├── theme/         # Material 3 theme
│   │   │   │   │   ├── Color.kt
│   │   │   │   │   ├── Theme.kt
│   │   │   │   │   └── Type.kt
│   │   │   │   ├── navigation/
│   │   │   │   │   ├── Screen.kt
│   │   │   │   │   └── NavGraph.kt
│   │   │   │   ├── screens/
│   │   │   │   │   ├── ClimbListScreen.kt
│   │   │   │   │   ├── ClimbDetailScreen.kt
│   │   │   │   │   └── HoldSelectorScreen.kt
│   │   │   │   └── components/
│   │   │   │       ├── ClimbCard.kt
│   │   │   │       └── HoldOverlay.kt
│   │   │   └── viewmodel/
│   │   │       ├── ClimbListViewModel.kt
│   │   │       └── ClimbDetailViewModel.kt
│   │   └── res/
│   │       ├── drawable/
│   │       ├── mipmap-*/          # Icônes app
│   │       ├── values/
│   │       │   ├── strings.xml
│   │       │   ├── colors.xml
│   │       │   └── themes.xml
│   │       └── xml/
│   └── build.gradle.kts
├── gradle/
│   └── wrapper/
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── local.properties
├── gradlew
└── gradlew.bat
```

---

## Tâches

### Phase 1 : Setup Projet (Foundation)

- [ ] Copier configs depuis templates
- [ ] Créer structure dossiers
- [ ] Configurer `build.gradle.kts` (namespace: `com.mastoc.app`)
- [ ] Configurer `settings.gradle.kts` (rootProject.name: `mastoc`)
- [ ] Créer `AndroidManifest.xml`
- [ ] Créer `MainActivity.kt`
- [ ] Définir thème Material 3 (couleurs icône)
- [ ] Ajouter Retrofit + OkHttp
- [ ] Setup Room
- [ ] Setup Navigation Compose
- [ ] Copier icône dans `mipmap-*/`
- [ ] Vérifier build : `./gradlew build`

### Phase 2 : Data Layer

- [ ] DTOs : `ClimbDto`, `HoldDto`, `FaceDto`, `UserDto`
- [ ] Entities Room : `ClimbEntity`, `HoldEntity`
- [ ] DAOs : `ClimbDao`, `HoldDao`
- [ ] `AppDatabase` (Room)
- [ ] `MastocApiService` (Retrofit)
- [ ] `ClimbRepository` (API + Room)
- [ ] Interceptor API Key (`X-API-Key`)

### Phase 3 : Écran Liste des Climbs

- [ ] `ClimbListViewModel` (StateFlow)
- [ ] `ClimbListScreen` (Composable)
- [ ] `ClimbCard` (item de liste avec picto, grade, setter, stats)
- [ ] Filtres (fidèle à l'app Python) :
  - [ ] Recherche texte (nom du bloc)
  - [ ] Grade min/max (sliders avec grades Fontainebleau)
  - [ ] Filtre par setter (dropdown)
  - [ ] Tri : Date, Grade, Nom, Popularité (ascending/descending)
- [ ] Pull-to-refresh (sync)
- [ ] Loading/Error states
- [ ] Navigation vers détail

### Phase 4 : Écran Détail Climb (Visualisation)

- [ ] `ClimbDetailViewModel`
- [ ] `ClimbDetailScreen` (Composable)
- [ ] Affichage infos (nom, grade, setter, stats)
- [ ] **Canvas** : rendu image mur + polygones prises
- [ ] Marqueurs visuels (fidèle à l'app Python) :
  - [ ] **START** : Lignes de tape blanches
    - 1 prise de départ → 2 lignes formant un "V" (leftTapeStr + rightTapeStr)
    - 2+ prises de départ → 1 ligne centrale par prise (centerTapeStr)
  - [ ] **TOP** : Double contour écarté (dilatation depuis centroïde, +15px)
  - [ ] **FEET** : Contour bleu néon (#31DAFF)
  - [ ] Autres prises : Contour blanc épais (8px)
- [ ] Zoom/Pan sur l'image (transformations)

### Phase 5 : Recherche par Prises

- [ ] `HoldSelectorViewModel`
- [ ] `HoldSelectorScreen` (Composable)
- [ ] Tap sur prise → sélection/désélection
- [ ] Filtrage climbs par prises sélectionnées (logique ET)
- [ ] Affichage liste climbs filtrés
- [ ] Navigation vers détail

### Phase 6 : Modes de Coloration (Heatmaps)

- [ ] Enum `ColorMode` (fidèle à l'app Python) :
  - [ ] `NONE` : Pas de coloration (gris uniforme)
  - [ ] `MIN_GRADE` : Grade du bloc le plus facile utilisant la prise
  - [ ] `MAX_GRADE` : Grade du bloc le plus difficile utilisant la prise
  - [ ] `FREQUENCY` : Fréquence d'utilisation (quantiles pour distribution équitable)
  - [ ] `RARE` : Prises rares mises en valeur (0 usage=1.0, 1=0.75, 2=0.5, 3=0.25, 4+=0.0)
- [ ] 7 Palettes (identiques à Python) :
  - [ ] VIRIDIS (recommandé, perceptuellement uniforme)
  - [ ] PLASMA
  - [ ] INFERNO
  - [ ] MAGMA
  - [ ] CIVIDIS (optimisé daltoniens)
  - [ ] TURBO (arc-en-ciel amélioré)
  - [ ] COOLWARM (divergent : bleu → blanc → rouge)
- [ ] LUT pré-calculées (256 couleurs par palette)
- [ ] UI : sélecteur mode + palette avec aperçu visuel
- [ ] Mise à jour Canvas en temps réel

### Phase 7 : Polish & Tests

- [ ] Tests unitaires ViewModels
- [ ] Tests Repository (mock API)
- [ ] Tests UI instrumentés (Compose)
- [ ] Gestion erreurs réseau
- [ ] Splash screen
- [ ] Build release signé

---

## Endpoints Railway Utilisés

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/health` | GET | Vérification connexion |
| `/api/climbs` | GET | Liste climbs (filtres: grade, search) |
| `/api/climbs/{id}` | GET | Détail climb |
| `/api/holds` | GET | Liste holds |
| `/api/faces/{id}/setup` | GET | Face + tous ses holds |

**Auth** : Header `X-API-Key: mastoc-2025-1213-brosse-lesprises-secret`

**Base URL** : `https://mastoc-production.up.railway.app`

---

## Dépendances (app/build.gradle.kts)

```kotlin
dependencies {
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
    implementation("androidx.activity:activity-compose:1.8.1")

    // Compose BOM
    implementation(platform("androidx.compose:compose-bom:2023.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")

    // Navigation Compose
    implementation("androidx.navigation:navigation-compose:2.7.5")

    // ViewModel Compose
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")

    // Room Database
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")

    // Retrofit + OkHttp
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Coil (images)
    implementation("io.coil-kt:coil-compose:2.5.0")

    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation(platform("androidx.compose:compose-bom:2023.10.01"))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}
```

---

## Critères de Complétion

- [ ] App installable sur Android 12+ (API 31)
- [ ] Liste climbs avec filtres fonctionnelle
- [ ] Visualisation bloc avec polygones prises
- [ ] Recherche par prises (tap sur image)
- [ ] Au moins 1 mode de coloration
- [ ] Sync depuis Railway opérationnelle
- [ ] 20+ tests unitaires
- [ ] APK < 30 MB

---

## Références

- `/home/mortner/Repositories/templates/android/` - Templates Android
- `/docs/devplan/03_MEDIUM_TERM.md` - Plan moyen terme Android
- `/docs/03_ergonomie_ui_ux.md` - Guide ergonomie Material Design 3
- `/server/` - API Railway (endpoints)
- `/mastoc/src/mastoc/` - Implémentation Python de référence
