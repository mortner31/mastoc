# Rapport de Session - Setup Android Kotlin

**Date** : 2026-01-01

## Objectifs Atteints

- ✅ Mise à jour plan de développement (TODO 12, 18, 19 complétés)
- ✅ Création TODO 20 - App Android Kotlin (Lecture Seule)
- ✅ **Phase 1 complétée** : Setup projet Android avec build fonctionnel

## TODO 20 - Phase 1 : Setup Projet

### Configuration

| Paramètre | Valeur |
|-----------|--------|
| Package | `com.mastoc.app` |
| Min SDK | 31 (Android 12) |
| Target SDK | 34 (Android 14) |
| Kotlin | 2.0.0 |
| Compose BOM | 2023.10.01 |

### Dépendances ajoutées

- Room 2.6.1 (base de données locale)
- Retrofit 2.9.0 + Gson (API Railway)
- OkHttp Logging Interceptor 4.12.0
- Coil 2.5.0 (chargement images)
- Navigation Compose 2.7.5

### Thème Material 3

Palette extraite de l'icône (`docs/images/Gemini_Generated_Image_m1l3sum1l3sum1l3.png`) :

| Rôle | Light | Dark |
|------|-------|------|
| Primary (Rouge) | `#D32F2F` | `#EF5350` |
| Secondary (Vert) | `#388E3C` | `#66BB6A` |
| Tertiary (Jaune) | `#FBC02D` | `#FFD54F` |
| Surface (Pierre) | `#F5F0E8` | `#2D2418` |

### Fichiers créés

```
android/
├── app/
│   ├── build.gradle.kts
│   ├── proguard-rules.pro
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/com/mastoc/app/
│       │   ├── MainActivity.kt
│       │   └── ui/theme/
│       │       ├── Color.kt
│       │       ├── Theme.kt
│       │       └── Type.kt
│       └── res/
│           ├── mipmap-*/ic_launcher.png
│           ├── mipmap-*/ic_launcher_round.png
│           ├── values/strings.xml
│           ├── values/colors.xml
│           ├── values/themes.xml
│           ├── xml/backup_rules.xml
│           └── xml/data_extraction_rules.xml
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── local.properties
├── gradlew
├── gradlew.bat
└── gradle/wrapper/
```

### Build

```bash
cd /media/veracrypt1/Repositories/mastock/android
./gradlew build
# BUILD SUCCESSFUL in 51s
# APK: app/build/outputs/apk/debug/app-debug.apk (38 MB)
```

## Prochaines Étapes (Phase 2 - Data Layer)

### À implémenter

1. **DTOs** (Data Transfer Objects) :
   - `ClimbDto.kt` - réponse API climbs
   - `HoldDto.kt` - réponse API holds
   - `FaceDto.kt` - réponse API faces
   - `FaceSetupDto.kt` - réponse `/api/faces/{id}/setup`

2. **Entities Room** :
   - `ClimbEntity.kt`
   - `HoldEntity.kt`

3. **DAOs** :
   - `ClimbDao.kt`
   - `HoldDao.kt`

4. **Database** :
   - `MastocDatabase.kt`

5. **API Service** :
   - `MastocApiService.kt` (interface Retrofit)
   - `ApiKeyInterceptor.kt` (header X-API-Key)

6. **Repository** :
   - `ClimbRepository.kt`

### Endpoints Railway à utiliser

| Endpoint | Usage |
|----------|-------|
| `GET /api/climbs` | Liste climbs avec filtres |
| `GET /api/climbs/{id}` | Détail climb |
| `GET /api/holds` | Liste holds |
| `GET /api/faces/{id}/setup` | Face + tous ses holds |

**Base URL** : `https://mastoc-production.up.railway.app`
**Auth** : `X-API-Key: mastoc-2025-1213-brosse-lesprises-secret`

## Commandes utiles

```bash
# Build
cd /media/veracrypt1/Repositories/mastock/android
./gradlew build

# Clean + Build
./gradlew clean build

# Install sur device
./gradlew installDebug

# Lancer l'app
adb shell am start -n com.mastoc.app/.MainActivity
```

## Références

- TODO 20 : `/docs/TODOS/20_android_kotlin_readonly.md`
- STATUS : `/docs/TODOS/20_android_kotlin_readonly_STATUS.md`
- Templates : `/home/mortner/Repositories/templates/android/`
- API Railway : `https://mastoc-production.up.railway.app/docs`

## État du Projet

| Composant | Statut |
|-----------|--------|
| Client Python | ✅ Complet (375+ tests) |
| Serveur Railway | ✅ Déployé |
| App Android | 🔄 Phase 1/7 complétée |
