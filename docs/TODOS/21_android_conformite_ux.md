# TODO 21 - Conformité UX/Design Android

## Objectif

Corriger les écarts entre l'implémentation Android actuelle et les spécifications définies dans :
- `/docs/03_ergonomie_ui_ux.md` (v2.2)
- `/docs/05_theme_design_system.md` (v1.0)

---

## Analyse Approfondie des Écarts

### 1. Navigation - Écart CRITIQUE

**Spec 03_ergonomie section 4.1** :
```
5 modes : Sync | Simple | Avancée | Créer | Profil
Navigation Bar en bas de l'écran
```

**État actuel** :
- UNE SEULE PAGE (ClimbListScreen)
- Pas de Bottom Navigation Bar
- Pas d'accès au mode Sync, Créer, Profil
- HoldSelectorScreen existe mais INACCESSIBLE depuis l'UI

**Impact** : L'utilisateur ne peut accéder qu'à la liste des blocs.

---

### 2. Pictos (Miniatures) - Écart MAJEUR

**Spec 03_ergonomie section 5.2** :
```
| [Picto]  Bloc "Nia"              |
|         6a+ - Mathias           |
```

**Spec 05_theme section 4.2** :
```
Les pictos conservent un fond blanc invariant
```

**État actuel** :
- ClimbCard N'AFFICHE PAS de picto
- Aucune génération de miniature côté Android
- Espace pour l'info inutile "12 prises" à la place

**Impact** : L'utilisateur ne peut pas identifier visuellement un bloc dans la liste.

---

### 3. Ligne de synthèse - Écart MINEUR

**Spec 03_ergonomie section 5.2** :
```
[heart] 12   [comment] 3   [bm]
```

**État actuel** (ClimbCard.kt:200-206) :
```kotlin
Text(
    text = "${climbHolds.size} prises",
    ...
)
```

**Problème** : Le nombre de prises n'est pas une info utile pour l'utilisateur.
Les stats sociales (likes, commentaires) sont affichées mais pas le nombre de commentaires.

---

### 4. Recherche par Prises - Écart CRITIQUE

**Spec 03_ergonomie section 4.1** :
```
Mode "Recherche Avancée" : Recherche par prises (sélection sur mur)
```

**État actuel** :
- `HoldSelectorScreen.kt` existe et fonctionne
- Route définie dans `NavGraph.kt:43-57`
- **AUCUN BOUTON** pour y accéder depuis l'UI

**Impact** : Fonctionnalité développée mais invisible.

---

### 5. Authentification - REPORTÉ

**Spec 03_ergonomie section 4.2** :
```
Mode Profil : Login/Logout, email, avatar
```

**État actuel** (ApiClient.kt) :
```kotlin
private const val API_KEY = "mastoc-2025-1213-brosse-lesprises-secret"
```

**Décision** : Garder l'API Key hardcodée pour l'instant.
L'authentification utilisateur sera implémentée dans un TODO ultérieur.

---

### 6. Image dans Détail Bloc - Écart FONCTIONNEL

**Analyse code** (ClimbDetailScreen.kt:126-146) :
```kotlin
if (uiState.face != null && uiState.climb != null) {
    WallImageWithClimbOverlay(
        pictureUrl = uiState.face!!.pictureUrl,
        ...
    )
}
```

**Problème potentiel** :
- L'image est bien chargée via Coil
- Mais si `face` est null (pas encore chargée), l'image n'apparaît pas
- Possible problème de timing ou d'URL

**Vérification requise** : Tester le chargement de `face.pictureUrl`.

---

### 7. Paramètres d'Affichage - Écart MAJEUR

**Spec 03_ergonomie section 8.1-8.2** :
```
Contrôles dans Bottom Sheet :
- Luminosité (Slider 10-100%)
- Mode coloration (Min, Max, Fréquence, Rareté)
- Palette (viridis, plasma, inferno, magma, cividis, turbo, coolwarm)
- Épaisseur contour (Slider 1-5px)

Persistance via SharedPreferences/DataStore
```

**État actuel** :
- `ColorMode.kt` définit les modes et palettes
- **AUCUNE UI** pour modifier ces paramètres
- Pas de Bottom Sheet contrôles
- Pas de persistance

**Impact** : L'utilisateur ne peut pas personnaliser l'affichage.

---

### 8. Rotation X/Y des Blocs - Écart CRITIQUE

**Analyse code** (HoldOverlay.kt:137-139) :
```kotlin
val scaledPoints = points.map { point ->
    Offset(point.x * scaleX, point.y * scaleY)
}
```

**Problème potentiel** :
- L'image du mur Montoboard est en portrait (2263x3000)
- Les coordonnées des polygones sont stockées en référence image originale
- Possible inversion si l'image est affichée en mode `ContentScale.Fit`

**Hypothèse** : Le scaling `scaleX/scaleY` pourrait être inversé si l'image est plus large que haute à l'écran mais les coords sont pour une image plus haute que large.

**Solution possible** : Vérifier le ratio de l'image vs le ratio du container.

---

### 9. Palette de Couleurs - DÉCISION PRISE

**Spec 05_theme section 1.1** :
```
primary = #1976D2 (Bleu)
secondary = #00897B (Teal)
```

**État actuel** : Thème "Coloré" (Rouge #D32F2F, Vert #388E3C, Jaune #FBC02D)

**Décision** : Créer un écran Paramètres avec choix de thème :

| Thème | Primary | Secondary | Description |
|-------|---------|-----------|-------------|
| **Coloré** | Rouge #D32F2F | Vert #388E3C | Actuel (couleurs icône) |
| **Bleu** | Bleu #1976D2 | Teal #00897B | Conforme aux specs |
| **Gris** | Gris #616161 | Gris #9E9E9E | Neutre/minimaliste |

**Implémentation** :
- Écran `SettingsScreen` accessible depuis TopAppBar (icône engrenage)
- Choix de thème via RadioButtons
- Persistance via DataStore

---

## Tâches par Priorité

### P0 - Critique (Fonctionnalité cassée)

- [ ] **NAV-01** : Implémenter Bottom Navigation Bar (5 destinations)
- [ ] **NAV-02** : Ajouter accès au mode Recherche Avancée (HoldSelector)
- [ ] **IMG-01** : Investiguer et corriger le problème de rotation X/Y
- [ ] **IMG-02** : Vérifier le chargement de l'image dans ClimbDetail

### P1 - Majeur (Fonctionnalité manquante)

- [ ] **PICTO-01** : Implémenter génération/affichage des pictos dans ClimbCard
- [ ] **SETTINGS-01** : Créer écran SettingsScreen
- [ ] **SETTINGS-02** : Implémenter choix de thème (Coloré/Bleu/Gris)
- [ ] **SETTINGS-03** : Créer les 3 ColorSchemes (Colorful, Blue, Gray)
- [ ] **SETTINGS-04** : Persistance du thème via DataStore
- [ ] **SETTINGS-05** : Bouton engrenage dans TopAppBar → SettingsScreen

### P2 - Mineur (Amélioration UX)

- [ ] **CARD-01** : Supprimer "X prises" de ClimbCard
- [ ] **CARD-02** : Ajouter compteur commentaires si disponible
- [ ] **SYNC-01** : Ajouter indicateur mode offline

### P3 - Cosmétique

- [ ] **STYLE-01** : Affiner les espacements M3 (multiples de 4dp)
- [ ] **STYLE-02** : Ajouter animations transitions

### REPORTÉ

- [ ] **AUTH-01** : Créer écran de login (mode Profil) - API Key hardcodée pour l'instant

---

## Références

- `/docs/03_ergonomie_ui_ux.md` - Guide UX complet (v2.2)
- `/docs/05_theme_design_system.md` - Design System (v1.0)
- `/docs/TODOS/20_android_kotlin_readonly_STATUS.md` - État actuel

---

**Créé** : 2026-01-01
**Version** : 1.0
