# Architecture mastoc - Application d'Escalade Offline-First

**Version** : 1.0
**Date** : 2025-11-10
**Statut** : Proposition d'architecture

---

## 📋 Table des Matières

1. [Vision et Objectifs](#vision-et-objectifs)
2. [Principes de Conception](#principes-de-conception)
3. [Architecture Technique](#architecture-technique)
4. [Modèle de Données](#modèle-de-données)
5. [Système d'Images Interactives](#système-dimages-interactives)
6. [Synchronisation Stōkt (Optionnelle)](#synchronisation-stōkt-optionnelle)
7. [Stack Technique](#stack-technique)
8. [Roadmap de Développement](#roadmap-de-développement)

---

## 🎯 Vision et Objectifs

### Vision
Créer une application mobile d'escalade **offline-first**, simple et efficace, permettant de visualiser et gérer des blocs d'escalade sur des images de murs, avec un fonctionnement **100% local** et une synchronisation **optionnelle** avec Stōkt.

### Objectifs Principaux

1. **Fonctionnement 100% Offline**
   - L'application doit être pleinement fonctionnelle sans connexion réseau
   - Toutes les données stockées localement (SQLite + fichiers)
   - Aucune dépendance critique à un service externe

2. **Simplicité d'Usage**
   - Interface intuitive
   - Création rapide de problèmes
   - Visualisation claire des voies sur images

3. **Performance**
   - Chargement instantané des données
   - Pas de latence réseau
   - Fluidité maximale

4. **Indépendance**
   - Ne pas dépendre de Stōkt pour le fonctionnement de base
   - Import optionnel de données Stōkt (bonus)
   - Possibilité de continuer sans Stōkt

### Problème Résolu

L'application Stōkt actuelle présente des limitations en mode offline :
- Dépendance forte au réseau (Firebase + API REST)
- Pas de persistance locale robuste
- Images non mises en cache
- Interface inutilisable sans connexion

**mastoc** résout ces problèmes en inversant la logique :
- **Base locale d'abord** (offline-first)
- Synchronisation optionnelle (bonus)
- Tout fonctionne localement

---

## 🏛️ Principes de Conception

### 1. Offline-First

**Principe** : L'application doit fonctionner parfaitement sans jamais se connecter à Internet.

**Implémentation** :
- Base de données SQLite locale
- Images stockées dans le système de fichiers local
- Pas de requête réseau obligatoire
- UI réactive basée sur les données locales uniquement

### 2. Simplicité

**Principe** : Fonctionnalités essentielles uniquement, pas de sur-engineering.

**Implémentation** :
- Pas de compte utilisateur (local uniquement)
- Pas de synchronisation cloud complexe
- Interface minimaliste et efficace
- Flux utilisateur direct

### 3. Performance

**Principe** : Réactivité maximale, pas de latence perceptible.

**Implémentation** :
- Données en mémoire (cache)
- Images optimisées et compressées
- Pas d'attente réseau
- Rendu graphique optimisé (Compose + Canvas)

### 4. Extensibilité

**Principe** : Architecture modulaire permettant d'ajouter des fonctionnalités.

**Implémentation** :
- Modules indépendants
- Interfaces claires
- Sync Stōkt comme module optionnel
- Possibilité d'ajouter d'autres sources de données

---

## 🏗️ Architecture Technique

### Vue d'Ensemble

```
┌─────────────────────────────────────────────────────┐
│                  Interface Utilisateur               │
│              (Jetpack Compose / Kotlin)              │
├─────────────────────────────────────────────────────┤
│                   Couche Métier                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Gestion     │  │  Visualisation│  │  Stats &  │ │
│  │  Problèmes   │  │  Images       │  │  Analyse  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
├─────────────────────────────────────────────────────┤
│                   Couche Données                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Repository  │  │  Cache       │  │  Sync     │ │
│  │  Local       │  │  Images      │  │  Stōkt    │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
├─────────────────────────────────────────────────────┤
│                 Stockage Persistant                  │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │  SQLite DB   │  │  File System │                 │
│  │  (Room)      │  │  (Images)    │                 │
│  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────┘
```

### Architecture en Couches

#### 1. **Couche UI (Présentation)**

**Technologies** :
- Jetpack Compose
- Material Design 3
- Navigation Compose
- ViewModel (MVVM)

**Responsabilités** :
- Affichage des écrans
- Gestion des interactions utilisateur
- Navigation entre écrans
- Animations et transitions

**Écrans Principaux** :
```
┌─ Navigation ─────────────────────────────┐
│                                          │
│  📱 Accueil                              │
│      └─ Liste des salles                │
│                                          │
│  🏢 Salle                                │
│      └─ Liste des murs                  │
│                                          │
│  🧗 Mur                                  │
│      ├─ Image du mur                    │
│      ├─ Liste des problèmes             │
│      └─ Filtres (grade, statut)         │
│                                          │
│  🎯 Détails Problème                    │
│      ├─ Image avec prises marquées      │
│      ├─ Informations (grade, ouvreur)   │
│      ├─ Mes tentatives                  │
│      └─ Notes personnelles              │
│                                          │
│  ➕ Créer Problème                      │
│      ├─ Sélection du mur                │
│      ├─ Photo/Image existante           │
│      ├─ Marquage des prises             │
│      └─ Métadonnées (nom, grade, etc.)  │
│                                          │
│  📊 Statistiques                         │
│      ├─ Mes réussites                   │
│      ├─ Progression par grade           │
│      └─ Analyse des prises (usage)      │
│                                          │
│  ⚙️  Paramètres                         │
│      ├─ Import/Export données           │
│      └─ Sync Stōkt (optionnel)          │
│                                          │
└──────────────────────────────────────────┘
```

#### 2. **Couche Métier (Business Logic)**

**Use Cases** :
```kotlin
// Gestion des problèmes
interface ProblemUseCases {
    suspend fun createProblem(problem: Problem, holds: List<Hold>): Result<Long>
    suspend fun updateProblem(problem: Problem): Result<Unit>
    suspend fun deleteProblem(problemId: Long): Result<Unit>
    suspend fun getProblemsForWall(wallId: Long): Flow<List<Problem>>
    suspend fun searchProblems(query: String): List<Problem>
}

// Gestion des tentatives
interface AttemptUseCases {
    suspend fun logAttempt(problemId: Long, status: AttemptStatus): Result<Long>
    suspend fun getAttemptsForProblem(problemId: Long): Flow<List<Attempt>>
    suspend fun updateAttempt(attempt: Attempt): Result<Unit>
}

// Statistiques
interface StatsUseCases {
    suspend fun getMyStats(): UserStats
    suspend fun getHoldUsageStats(wallId: Long): Map<Long, Int>
    suspend fun getProgressionByGrade(): Map<Grade, Int>
}

// Import/Export
interface DataSyncUseCases {
    suspend fun exportToJson(): Result<File>
    suspend fun importFromJson(file: File): Result<ImportStats>
    suspend fun syncFromStokt(token: String): Result<SyncStats>  // Optionnel
}
```

#### 3. **Couche Données (Data Layer)**

**Repository Pattern** :
```kotlin
interface ProblemRepository {
    suspend fun insert(problem: Problem): Long
    suspend fun update(problem: Problem)
    suspend fun delete(problemId: Long)
    fun getAll(): Flow<List<Problem>>
    fun getById(id: Long): Flow<Problem?>
    fun getByWallId(wallId: Long): Flow<List<Problem>>
}

interface WallRepository {
    suspend fun insert(wall: Wall): Long
    suspend fun update(wall: Wall)
    fun getAll(): Flow<List<Wall>>
    fun getById(id: Long): Flow<Wall?>
    fun getByGymId(gymId: Long): Flow<List<Wall>>
}

interface ImageRepository {
    suspend fun saveImage(bitmap: Bitmap, name: String): String  // Retourne le path
    suspend fun getImage(path: String): Bitmap?
    suspend fun deleteImage(path: String)
}
```

**Sources de Données** :
```
Local Data Source (Principal)
├─ SQLite via Room
├─ File System (images)
└─ Shared Preferences (config)

Remote Data Source (Optionnel)
└─ Stōkt API (sync uniquement)
```

#### 4. **Couche Stockage**

**SQLite avec Room** :
- Base de données relationnelle locale
- Queries type-safe avec Room
- Migrations gérées
- Transactions ACID

**File System** :
- Images des murs stockées localement
- Format JPEG/PNG compressé
- Organisation par salle/mur

---

## 📊 Modèle de Données

### Schéma SQLite

```sql
-- Salles d'escalade
CREATE TABLE gyms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

-- Murs (faces)
CREATE TABLE walls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gym_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    image_path TEXT NOT NULL,           -- Chemin vers l'image locale
    image_width INTEGER NOT NULL,       -- Largeur de l'image en pixels
    image_height INTEGER NOT NULL,      -- Hauteur de l'image en pixels
    angle INTEGER,                      -- Angle du mur (optionnel)
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (gym_id) REFERENCES gyms(id) ON DELETE CASCADE
);

-- Problèmes (voies d'escalade)
CREATE TABLE problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wall_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    setter TEXT,                        -- Nom de l'ouvreur
    grade TEXT NOT NULL,                -- Cotation (V0, V1, 6A, etc.)
    color TEXT,                         -- Couleur des prises
    description TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    stokt_id TEXT,                      -- ID Stōkt si importé (nullable)
    FOREIGN KEY (wall_id) REFERENCES walls(id) ON DELETE CASCADE
);

-- Prises (holds) - Coordonnées sur l'image
CREATE TABLE holds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL,
    x REAL NOT NULL,                    -- Position X (0.0 - 1.0 relatif)
    y REAL NOT NULL,                    -- Position Y (0.0 - 1.0 relatif)
    type TEXT NOT NULL,                 -- 'start', 'hand', 'foot', 'top'
    order_index INTEGER NOT NULL,       -- Ordre dans la séquence
    is_optional INTEGER DEFAULT 0,      -- Prise optionnelle
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
);

-- Tentatives (efforts)
CREATE TABLE attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL,
    status TEXT NOT NULL,               -- 'attempted', 'sent', 'flashed'
    attempts_count INTEGER DEFAULT 1,   -- Nombre de tentatives
    rating INTEGER,                     -- Note 1-5 étoiles
    notes TEXT,                         -- Notes personnelles
    created_at INTEGER NOT NULL,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
);

-- Métadonnées de synchronisation (optionnel)
CREATE TABLE sync_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,          -- 'problem', 'wall', etc.
    entity_id INTEGER NOT NULL,
    stokt_id TEXT,
    last_sync INTEGER,
    sync_status TEXT                    -- 'synced', 'modified', 'new'
);

-- Index pour les performances
CREATE INDEX idx_problems_wall ON problems(wall_id);
CREATE INDEX idx_holds_problem ON holds(problem_id);
CREATE INDEX idx_attempts_problem ON attempts(problem_id);
CREATE INDEX idx_walls_gym ON walls(gym_id);
```

### Entités Kotlin (Room)

```kotlin
@Entity(tableName = "gyms")
data class Gym(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val name: String,
    val location: String? = null,
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis(),
    @ColumnInfo(name = "updated_at")
    val updatedAt: Long = System.currentTimeMillis()
)

@Entity(
    tableName = "walls",
    foreignKeys = [ForeignKey(
        entity = Gym::class,
        parentColumns = ["id"],
        childColumns = ["gym_id"],
        onDelete = ForeignKey.CASCADE
    )]
)
data class Wall(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    @ColumnInfo(name = "gym_id")
    val gymId: Long,
    val name: String,
    @ColumnInfo(name = "image_path")
    val imagePath: String,
    @ColumnInfo(name = "image_width")
    val imageWidth: Int,
    @ColumnInfo(name = "image_height")
    val imageHeight: Int,
    val angle: Int? = null,
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis(),
    @ColumnInfo(name = "updated_at")
    val updatedAt: Long = System.currentTimeMillis()
)

@Entity(
    tableName = "problems",
    foreignKeys = [ForeignKey(
        entity = Wall::class,
        parentColumns = ["id"],
        childColumns = ["wall_id"],
        onDelete = ForeignKey.CASCADE
    )]
)
data class Problem(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    @ColumnInfo(name = "wall_id")
    val wallId: Long,
    val name: String,
    val setter: String? = null,
    val grade: String,
    val color: String? = null,
    val description: String? = null,
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis(),
    @ColumnInfo(name = "updated_at")
    val updatedAt: Long = System.currentTimeMillis(),
    @ColumnInfo(name = "stokt_id")
    val stoktId: String? = null
)

@Entity(
    tableName = "holds",
    foreignKeys = [ForeignKey(
        entity = Problem::class,
        parentColumns = ["id"],
        childColumns = ["problem_id"],
        onDelete = ForeignKey.CASCADE
    )]
)
data class Hold(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    @ColumnInfo(name = "problem_id")
    val problemId: Long,
    val x: Float,  // Position relative 0.0 - 1.0
    val y: Float,  // Position relative 0.0 - 1.0
    val type: HoldType,
    @ColumnInfo(name = "order_index")
    val orderIndex: Int,
    @ColumnInfo(name = "is_optional")
    val isOptional: Boolean = false
)

enum class HoldType {
    START,   // Prise(s) de départ
    HAND,    // Prise main
    FOOT,    // Prise pied
    TOP      // Prise finale
}

@Entity(
    tableName = "attempts",
    foreignKeys = [ForeignKey(
        entity = Problem::class,
        parentColumns = ["id"],
        childColumns = ["problem_id"],
        onDelete = ForeignKey.CASCADE
    )]
)
data class Attempt(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    @ColumnInfo(name = "problem_id")
    val problemId: Long,
    val status: AttemptStatus,
    @ColumnInfo(name = "attempts_count")
    val attemptsCount: Int = 1,
    val rating: Int? = null,  // 1-5
    val notes: String? = null,
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis()
)

enum class AttemptStatus {
    ATTEMPTED,  // Tenté mais pas réussi
    SENT,       // Réussi (plusieurs tentatives)
    FLASHED     // Réussi du premier coup
}
```

### Relations et DTO

```kotlin
// Problème avec ses prises
data class ProblemWithHolds(
    @Embedded val problem: Problem,
    @Relation(
        parentColumn = "id",
        entityColumn = "problem_id"
    )
    val holds: List<Hold>,
    @Relation(
        parentColumn = "id",
        entityColumn = "problem_id"
    )
    val attempts: List<Attempt>
)

// Mur avec ses problèmes
data class WallWithProblems(
    @Embedded val wall: Wall,
    @Relation(
        parentColumn = "id",
        entityColumn = "wall_id"
    )
    val problems: List<Problem>
)

// Salle complète
data class GymComplete(
    @Embedded val gym: Gym,
    @Relation(
        parentColumn = "id",
        entityColumn = "gym_id"
    )
    val walls: List<Wall>
)
```

---

## 🎨 Système d'Images Interactives

### Principe

Basé sur l'analyse de Stōkt, le système utilise des **coordonnées relatives** (0.0 à 1.0) sur une image de référence.

### Format de Stockage

**Coordonnées relatives** :
```kotlin
// Prise à 30% de la largeur, 45% de la hauteur
Hold(
    x = 0.30f,  // 30% de la largeur totale
    y = 0.45f,  // 45% de la hauteur totale
    type = HoldType.HAND
)
```

**Avantages** :
- ✅ Indépendant de la résolution d'affichage
- ✅ Fonctionne sur tous les écrans
- ✅ Zoom sans perte de précision
- ✅ Compatible avec différentes tailles d'images

### Rendu avec Jetpack Compose

```kotlin
@Composable
fun WallImageWithHolds(
    imagePath: String,
    holds: List<Hold>,
    selectedHold: Hold? = null,
    onHoldClick: (Hold) -> Unit = {}
) {
    val image = rememberImageBitmap(imagePath)

    Canvas(modifier = Modifier.fillMaxSize()) {
        // Dessiner l'image de fond
        drawImage(
            image = image,
            dstSize = IntSize(size.width.toInt(), size.height.toInt())
        )

        // Dessiner les prises
        holds.forEach { hold ->
            val absoluteX = hold.x * size.width
            val absoluteY = hold.y * size.height

            drawCircle(
                color = getColorForHoldType(hold.type),
                radius = if (hold == selectedHold) 30f else 20f,
                center = Offset(absoluteX, absoluteY),
                style = Stroke(width = 3f)
            )

            // Numéro de séquence
            drawText(
                textMeasurer = textMeasurer,
                text = hold.orderIndex.toString(),
                topLeft = Offset(absoluteX - 10, absoluteY - 10)
            )
        }
    }
}

private fun getColorForHoldType(type: HoldType): Color = when (type) {
    HoldType.START -> Color.Green
    HoldType.HAND -> Color.Blue
    HoldType.FOOT -> Color.Yellow
    HoldType.TOP -> Color.Red
}
```

### Mode Création - Marquage des Prises

```kotlin
@Composable
fun CreateProblemScreen(viewModel: CreateProblemViewModel) {
    var selectedHoldType by remember { mutableStateOf(HoldType.START) }

    Column {
        // Sélection du type de prise
        HoldTypeSelector(
            selected = selectedHoldType,
            onSelect = { selectedHoldType = it }
        )

        // Image interactive
        WallImageInteractive(
            imagePath = viewModel.wallImagePath,
            holds = viewModel.currentHolds,
            onImageClick = { offset ->
                // Convertir en coordonnées relatives
                val relativeX = offset.x / imageWidth
                val relativeY = offset.y / imageHeight

                viewModel.addHold(
                    Hold(
                        x = relativeX,
                        y = relativeY,
                        type = selectedHoldType,
                        orderIndex = viewModel.currentHolds.size
                    )
                )
            },
            onHoldLongPress = { hold ->
                // Supprimer la prise
                viewModel.removeHold(hold)
            }
        )

        // Bouton de sauvegarde
        Button(onClick = { viewModel.saveProblem() }) {
            Text("Créer le problème")
        }
    }
}
```

### Gestion des Images

```kotlin
class ImageRepository(private val context: Context) {
    private val imagesDir = File(context.filesDir, "wall_images")

    init {
        if (!imagesDir.exists()) {
            imagesDir.mkdirs()
        }
    }

    suspend fun saveImage(bitmap: Bitmap, name: String): String = withContext(Dispatchers.IO) {
        val filename = "${System.currentTimeMillis()}_$name.jpg"
        val file = File(imagesDir, filename)

        FileOutputStream(file).use { out ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 85, out)
        }

        file.absolutePath
    }

    suspend fun loadImage(path: String): Bitmap? = withContext(Dispatchers.IO) {
        try {
            BitmapFactory.decodeFile(path)
        } catch (e: Exception) {
            null
        }
    }

    suspend fun deleteImage(path: String) = withContext(Dispatchers.IO) {
        File(path).delete()
    }
}
```

---

## 🔄 Synchronisation Stōkt (Optionnelle)

### Principe

Module **complètement optionnel** permettant d'importer des données depuis Stōkt. Si ce module cesse de fonctionner, l'application reste fonctionnelle.

### Architecture du Module

```
Module Sync Stōkt (Optionnel)
├─ Masquage du client (User-Agent navigateur)
├─ Authentification (token)
├─ Récupération des données via API
├─ Conversion au format local
└─ Import dans la base SQLite
```

### Implémentation

```kotlin
class StoktSyncService(
    private val httpClient: OkHttpClient,
    private val problemRepository: ProblemRepository,
    private val wallRepository: WallRepository
) {

    // Client HTTP masqué
    private val client = httpClient.newBuilder()
        .addInterceptor { chain ->
            val request = chain.request().newBuilder()
                // Se faire passer pour un navigateur mobile
                .header("User-Agent", "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0")
                .removeHeader("X-Requested-With")  // Enlever le package name
                .build()
            chain.proceed(request)
        }
        .build()

    suspend fun syncMyProblems(token: String): Result<SyncStats> = withContext(Dispatchers.IO) {
        try {
            // 1. Récupérer les données de Stōkt
            val response = client.newCall(
                Request.Builder()
                    .url("https://www.getstokt.com/api/my-bookmarked-climbs")
                    .header("Authorization", "Token $token")
                    .build()
            ).execute()

            if (!response.isSuccessful) {
                return@withContext Result.failure(Exception("HTTP ${response.code}"))
            }

            val json = response.body?.string() ?: return@withContext Result.failure(Exception("Empty response"))
            val stoktProblems = Json.decodeFromString<List<StoktProblem>>(json)

            // 2. Convertir au format local
            var imported = 0
            var updated = 0

            stoktProblems.forEach { stoktProblem ->
                // Vérifier si déjà importé
                val existing = problemRepository.getByStoktId(stoktProblem.id)

                if (existing == null) {
                    // Nouveau problème
                    val localProblem = convertStoktToLocal(stoktProblem)
                    problemRepository.insert(localProblem)
                    imported++
                } else {
                    // Mise à jour
                    val updated = existing.copy(
                        name = stoktProblem.name,
                        grade = stoktProblem.grade,
                        updatedAt = System.currentTimeMillis()
                    )
                    problemRepository.update(updated)
                    updated++
                }
            }

            Result.success(SyncStats(imported, updated))

        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun convertStoktToLocal(stoktProblem: StoktProblem): Problem {
        // Conversion des données Stōkt vers format local
        return Problem(
            name = stoktProblem.name,
            grade = stoktProblem.grade,
            setter = stoktProblem.setter,
            wallId = findOrCreateWall(stoktProblem.wall),
            stoktId = stoktProblem.id,
            // ... autres champs
        )
    }
}

data class SyncStats(
    val imported: Int,
    val updated: Int
)

// Modèle de données Stōkt (basé sur notre analyse)
@Serializable
data class StoktProblem(
    val id: String,
    val name: String,
    val grade: String,
    val setter: String?,
    val wall: StoktWall,
    val holds: List<StoktHold>
)

@Serializable
data class StoktHold(
    val x: Float,
    val y: Float,
    val type: String
)
```

### UI de Synchronisation (Sans PC Requis)

```kotlin
@Composable
fun SyncSettingsScreen(viewModel: SyncViewModel) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var syncing by remember { mutableStateOf(false) }
    var lastSyncStats by remember { mutableStateOf<SyncStats?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            "Synchronisation Stōkt (optionnel)",
            style = MaterialTheme.typography.headlineMedium
        )

        Text(
            "mastoc fonctionne 100% sans connexion. Cette fonctionnalité " +
            "permet d'importer vos données depuis Stōkt si vous le souhaitez.",
            style = MaterialTheme.typography.bodyMedium,
            color = Color.Gray
        )

        Spacer(Modifier.height(24.dp))

        // Formulaire de connexion Stōkt
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email Stōkt") },
            placeholder = { Text("votre@email.com") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
            singleLine = true
        )

        Spacer(Modifier.height(8.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Mot de passe Stōkt") },
            placeholder = { Text("Votre mot de passe") },
            modifier = Modifier.fillMaxWidth(),
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
            singleLine = true
        )

        Spacer(Modifier.height(16.dp))

        Button(
            onClick = {
                syncing = true
                viewModel.syncFromStokt(email, password) { result ->
                    syncing = false
                    result.onSuccess { stats ->
                        lastSyncStats = stats
                    }.onFailure { error ->
                        // Afficher l'erreur
                    }
                }
            },
            enabled = email.isNotEmpty() && password.isNotEmpty() && !syncing,
            modifier = Modifier.fillMaxWidth()
        ) {
            if (syncing) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = Color.White
                )
                Spacer(Modifier.width(8.dp))
                Text("Synchronisation...")
            } else {
                Icon(Icons.Default.CloudDownload, null)
                Spacer(Modifier.width(8.dp))
                Text("Se connecter et synchroniser")
            }
        }

        // Afficher les résultats
        lastSyncStats?.let { stats ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF4CAF50).copy(alpha = 0.1f)
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("✅ Synchronisation réussie", fontWeight = FontWeight.Bold)
                    Text("${stats.imported} problèmes importés")
                    Text("${stats.updated} problèmes mis à jour")
                }
            }
        }

        Spacer(Modifier.height(16.dp))

        // Note de sécurité
        Card(
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFFE3F2FD)
            )
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Default.Lock,
                    contentDescription = null,
                    tint = Color(0xFF2196F3)
                )
                Spacer(Modifier.width(8.dp))
                Column {
                    Text("🔒 Sécurité", fontWeight = FontWeight.Bold)
                    Text(
                        "Vos identifiants ne sont jamais stockés. " +
                        "Seul un token temporaire est sauvegardé de manière chiffrée dans l'app.",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }

        Spacer(Modifier.height(8.dp))

        // Avertissement
        Card(
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFFFFC107).copy(alpha = 0.1f)
            )
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Default.Warning,
                    contentDescription = null,
                    tint = Color(0xFFFFC107)
                )
                Spacer(Modifier.width(8.dp))
                Column {
                    Text("Note importante", fontWeight = FontWeight.Bold)
                    Text(
                        "Cette fonctionnalité n'est pas supportée officiellement par Stōkt. " +
                        "Elle peut cesser de fonctionner à tout moment. " +
                        "L'application continuera de fonctionner normalement en mode local.",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }
    }
}
```

### Authentification Simplifiée (Pas de PC Requis)

```kotlin
class StoktSyncService(
    private val httpClient: HttpClient,
    private val secureStorage: SecureStorage
) {

    /**
     * Authentification directe auprès de Stōkt
     * Pas besoin de PC ou mitmproxy
     */
    suspend fun authenticate(email: String, password: String): Result<String> {
        return try {
            val response = httpClient.post("https://www.getstokt.com/api/token-auth") {
                headers {
                    // Se faire passer pour un navigateur mobile
                    append("User-Agent", "Mozilla/5.0 (Linux; Android 14) Chrome/120.0")
                    contentType(ContentType.Application.Json)
                }
                setBody(mapOf(
                    "username" to email,
                    "password" to password
                ))
            }

            if (response.status.isSuccess()) {
                val tokenData = response.body<TokenResponse>()

                // Sauvegarder le token de manière sécurisée
                secureStorage.saveToken(tokenData.token)

                Result.success(tokenData.token)
            } else {
                Result.failure(Exception("Authentification échouée: ${response.status}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Synchronisation complète des données
     */
    suspend fun syncAllData(token: String): Result<SyncStats> {
        return try {
            // Récupérer les problèmes
            val problems = fetchMyProblems(token)

            // Récupérer les murs
            val walls = fetchMyWalls(token)

            // Importer dans la base locale
            val imported = importToLocalDatabase(problems, walls)

            Result.success(SyncStats(
                imported = imported,
                updated = 0
            ))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

@Serializable
data class TokenResponse(
    val token: String,
    @SerialName("user_id")
    val userId: String? = null
)
```

### Gestion des Échecs

**Principe** : Si la sync échoue, l'application continue de fonctionner normalement.

```kotlin
sealed class SyncResult {
    data class Success(val stats: SyncStats) : SyncResult()
    data class NetworkError(val message: String) : SyncResult()
    data class AuthError(val message: String) : SyncResult()
    data class ApiChanged(val message: String) : SyncResult()
}

fun handleSyncResult(result: SyncResult) {
    when (result) {
        is SyncResult.Success -> {
            showToast("✅ ${result.stats.imported} problèmes importés")
        }
        is SyncResult.NetworkError -> {
            showToast("❌ Erreur réseau - mode local maintenu")
        }
        is SyncResult.AuthError -> {
            showToast("❌ Token invalide - vérifiez votre token")
        }
        is SyncResult.ApiChanged -> {
            showToast("⚠️ API Stōkt a changé - sync désactivée temporairement")
            // L'app fonctionne toujours en local
        }
    }
}
```

---

## 🛠️ Stack Technique

### Frontend (Android)

**Langage** : Kotlin

**UI** :
- Jetpack Compose (UI déclarative)
- Material Design 3
- Compose Navigation
- Accompanist (compléments Compose)

**Architecture** :
- MVVM (Model-View-ViewModel)
- Clean Architecture (UseCase, Repository)
- Dependency Injection : Hilt/Koin

**Base de Données** :
- Room (SQLite ORM)
- Flow (reactive streams)
- Coroutines (async)

**Images** :
- Coil (chargement d'images)
- Compose Canvas (dessin des prises)

**Optionnel** :
- OkHttp (requêtes HTTP pour sync Stōkt)
- Kotlinx Serialization (JSON)

### Outils de Développement

**Build** :
- Gradle Kotlin DSL
- Version Catalogs

**Tests** :
- JUnit 5
- Mockk (mocking)
- Turbine (testing Flow)
- Compose UI Testing

**Qualité** :
- Ktlint (formatting)
- Detekt (static analysis)

---

## 🗺️ Roadmap de Développement

### Phase 1 : MVP Offline (4-6 semaines)

**Objectif** : Application fonctionnelle 100% locale

**Fonctionnalités** :
- ✅ Modèle de données SQLite complet
- ✅ Création manuelle de salles/murs
- ✅ Import d'images de murs
- ✅ Création de problèmes avec marquage de prises
- ✅ Visualisation des problèmes sur images
- ✅ Logger des tentatives
- ✅ Interface basique mais fonctionnelle

**Livrables** :
- App Android fonctionnelle en local
- Base de données SQLite opérationnelle
- Système d'images avec prises fonctionnel

### Phase 2 : Amélioration UX (2-3 semaines)

**Objectif** : Interface polie et agréable

**Fonctionnalités** :
- ✅ Interface Material Design 3
- ✅ Animations et transitions
- ✅ Filtres et recherche
- ✅ Tri des problèmes (grade, date, etc.)
- ✅ Statistiques de base

**Livrables** :
- UI/UX professionnelle
- Navigation fluide
- Expérience utilisateur optimisée

### Phase 3 : Statistiques Avancées (2 semaines)

**Objectif** : Analyse des données

**Fonctionnalités** :
- ✅ Graphiques de progression
- ✅ Analyse de l'usage des prises
- ✅ Stats par grade
- ✅ Export PDF de statistiques

**Livrables** :
- Module de statistiques complet
- Visualisations graphiques

### Phase 4 : Import/Export (1-2 semaines)

**Objectif** : Portabilité des données

**Fonctionnalités** :
- ✅ Export JSON complet
- ✅ Import JSON
- ✅ Backup/Restore
- ✅ Partage de problèmes

**Livrables** :
- Système d'import/export robuste
- Format JSON documenté

### Phase 5 : Sync Stōkt (Optionnel) (2-3 semaines)

**Objectif** : Import des données Stōkt

**Fonctionnalités** :
- ✅ Authentification masquée
- ✅ Import de données Stōkt
- ✅ Conversion de format
- ✅ Gestion des erreurs

**Livrables** :
- Module de sync optionnel
- Documentation utilisateur

### Phase 6 : Optimisations et Tests (1-2 semaines)

**Objectif** : Stabilité et performance

**Tâches** :
- Tests unitaires complets
- Tests d'intégration
- Optimisation des performances
- Gestion de la mémoire
- Tests sur différents appareils

**Livrables** :
- App stable et testée
- Documentation technique complète

---

## 📝 Considérations Techniques

### Performance

**Objectifs** :
- Temps de démarrage < 2 secondes
- Affichage d'un mur < 500ms
- Pas de latence perceptible dans l'UI
- Gestion fluide de 1000+ problèmes

**Optimisations** :
- Pagination des listes
- Cache des images en mémoire
- Queries SQL optimisées avec index
- Lazy loading des données

### Sécurité

**Token Stōkt** :
- Stockage dans EncryptedSharedPreferences
- Jamais loggé
- Effacement possible

**Données Locales** :
- Pas de données sensibles
- SQLite non chiffré (pas nécessaire)
- Images locales non sensibles

### Compatibilité

**Android** :
- Min SDK : 24 (Android 7.0)
- Target SDK : 34 (Android 14)
- Support des différentes tailles d'écran
- Support du mode sombre

---

## 🎓 Apprentissages de l'Analyse Stōkt

### Ce qui Fonctionne Bien

1. **Système de coordonnées relatives** (0.0 - 1.0)
   - ✅ À reproduire dans mastoc

2. **Structure modulaire Redux**
   - ✅ S'inspirer pour l'architecture ViewModels

3. **React Native Skia pour le rendu**
   - ✅ Équivalent : Jetpack Compose Canvas

### Ce qui Pose Problème

1. **Dépendance forte au réseau**
   - ❌ À éviter absolument dans mastoc

2. **Pas de persistance locale**
   - ❌ mastoc sera 100% local

3. **API non documentée**
   - ⚠️ Risque pour le module de sync (acceptable car optionnel)

---

## 📚 Annexes

### Ressources Techniques

**Documentation** :
- [Jetpack Compose](https://developer.android.com/jetpack/compose)
- [Room Database](https://developer.android.com/training/data-storage/room)
- [Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)

**Inspirations** :
- Stōkt (système d'images)
- Kilter Board (marquage de prises)
- MoonBoard (grading system)

### Glossaire

- **Offline-first** : Architecture où l'application fonctionne d'abord localement
- **Hold** : Prise d'escalade
- **Problem** : Voie ou bloc d'escalade
- **Wall/Face** : Mur d'escalade
- **Grade** : Cotation de difficulté (V0-V17, 3-9c)
- **Flash** : Réussir du premier coup
- **Send** : Réussir une voie
- **Setter** : Ouvreur de bloc

---

**Document préparé par l'analyse de Stōkt et les discussions sur l'architecture**
**Date** : 2025-11-10
**Version** : 1.0
