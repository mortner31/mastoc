# STATUS - TODO 20 : Application Android Kotlin (Lecture Seule)

**Progression** : 100% ✅ COMPLET

## Phase 1 : Setup Projet (100%) ✅

- [x] Copier configs depuis templates
- [x] Créer structure dossiers
- [x] Configurer `build.gradle.kts` (com.mastoc.app)
- [x] Configurer `settings.gradle.kts` (mastoc)
- [x] Créer `AndroidManifest.xml`
- [x] Créer `MainActivity.kt`
- [x] Définir thème Material 3 (couleurs icône)
- [x] Ajouter Retrofit + OkHttp
- [x] Setup Room
- [x] Setup Navigation Compose
- [x] Copier icône dans `mipmap-*/`
- [x] Vérifier build : `./gradlew build` ✅ BUILD SUCCESSFUL

## Phase 2 : Data Layer (100%) ✅

- [x] DTOs : ClimbDto, HoldDto, FaceDto, FaceSetupDto, PictureDto
- [x] Entities Room : ClimbEntity, HoldEntity, FaceEntity
- [x] DAOs : ClimbDao, HoldDao, FaceDao
- [x] MastocDatabase (Room)
- [x] MastocApiService (Retrofit)
- [x] ApiKeyInterceptor + ApiClient
- [x] Domain Models : Climb, Hold, Face, FaceWithHolds
- [x] Mappers (DTO → Entity → Domain)
- [x] ClimbRepository
- [x] Vérifier build : `./gradlew build` ✅ BUILD SUCCESSFUL

## Phase 3 : Écran Liste Climbs (100%) ✅

- [x] ClimbListViewModel (StateFlow, refresh, search)
- [x] ClimbListScreen (Scaffold, TopAppBar, LazyColumn)
- [x] ClimbCard (nom, grade, setter, stats)
- [x] SearchBar (recherche par nom)
- [x] Bouton refresh dans TopAppBar
- [x] Navigation vers détail
- [x] Filtre grade min/max (RangeSlider IRCRA → Fontainebleau)
- [x] Filtre par setter (ExposedDropdownMenuBox)
- [x] Tri : Date, Grade, Nom, Popularité (FilterChips)
- [x] SortOption enum avec 7 options
- [x] Panneau filtres animé (AnimatedVisibility)
- [x] Compteur résultats
- [x] HoldTypeIndicators dans ClimbCard (S/O/F/T avec pastilles colorées)
- [x] Vérifier build : `./gradlew build` ✅ BUILD SUCCESSFUL

## Phase 4 : Écran Détail Climb (100%) ✅

- [x] ClimbDetailViewModel + Factory
- [x] ClimbDetailScreen (Scaffold, TopAppBar, navigation)
- [x] WallImageWithOverlay (Coil + Canvas)
- [x] HoldOverlay (polygones des prises)
- [x] Zoom/Pan avec detectTransformGestures
- [x] Mise en surbrillance des prises du climb
- [x] **START** : Lignes de tape (1 prise = V, 2+ = centrale)
- [x] **TOP** : Double contour écarté (+15px dilatation)
- [x] **FEET** : Contour bleu néon (#31DAFF)
- [x] Contour blanc épais (8px) pour autres prises
- [x] HoldType enum (S/O/F/T) + ClimbHold data class
- [x] ClimbHoldOverlay composable avec rendu fidèle Python
- [x] Tapes stockées dans HoldEntity (center/left/right)
- [x] Vérifier build : `./gradlew build` ✅ BUILD SUCCESSFUL

## Phase 5 : Recherche par Prises (100%) ✅

- [x] HoldSelectorViewModel + Factory
- [x] HoldSelectorScreen (image + liste résultats)
- [x] Tap sélection avec détection polygone (ray casting)
- [x] Filtrage par prises (logique ET)
- [x] Navigation + routes
- [x] Vérifier build : `./gradlew build` ✅ BUILD SUCCESSFUL

## Phase 6 : Heatmaps (100%) ✅

- [x] ColorMode enum (NONE, MIN_GRADE, MAX_GRADE, FREQUENCY, RARE)
- [x] ColorPalette enum (VIRIDIS, PLASMA, INFERNO, MAGMA, CIVIDIS, TURBO, COOLWARM)
- [x] Mode **RARE** avec getRareValue() (0=1.0, 1=0.75, 2=0.5, 3=0.25, 4+=0.0)
- [x] LUT pré-calculées (256 niveaux) via ColorLut object
- [x] Polynômes fidèles au Python pour toutes les palettes
- [x] PalettePreview composable pour aperçu visuel
- [x] applyColormap() helper function
- [x] Vérifier build : `./gradlew build` ✅ BUILD SUCCESSFUL

## Phase 7 : Polish & Tests (100%) ✅

- [x] Tests unitaires modèles (ClimbTest, HoldTest)
- [x] Tests ColorMode/ColorPalette
- [x] Tests SortOption
- [x] Splash screen (androidx.core.splashscreen)
- [x] Theme.Mastoc.Splash avec icône
- [x] Build release : `./gradlew assembleRelease`
- [x] Vérifier build : `./gradlew build` ✅ BUILD SUCCESSFUL

---

## Icône et Thème

**Source icône** : `/docs/images/Gemini_Generated_Image_m1l3sum1l3sum1l3.png`

**Palette** :
- Primary : Rouge `#D32F2F`
- Secondary : Vert `#388E3C`
- Tertiary : Jaune `#FBC02D`
