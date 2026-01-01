# Rapport de Session - TODO 21 : Conformité UX/Design Android

**Date** : 2026-01-01

## Objectifs Atteints

- P0 - Critique (100%)
- P1 - Majeur (100%)
- P2 - Mineur (33%)

**Progression globale** : 80%

---

## P0 - Navigation et Images

### NAV-01 : Bottom Navigation Bar
- Implémentation de 5 destinations : Sync | Simple | Avancée | Créer | Profil
- Enum `BottomNavDestination` avec icônes Material Icons
- Scaffold global dans `NavGraph.kt` avec `NavigationBar`
- Bottom nav masquée sur les écrans de détail (ClimbDetail, Settings)

### NAV-02 : Accès Recherche Avancée
- Nouvel écran `AdvancedSearchScreen.kt` autonome
- Charge automatiquement la première face disponible
- ViewModel intégré avec même logique que `HoldSelectorScreen`

### IMG-01/02 : Correction Alignement Overlay
- **Problème identifié** : L'overlay Canvas utilisait `fillMaxSize()` alors que l'image avec `ContentScale.Fit` ne remplit pas forcément tout le container
- **Solution** : Calcul de la taille réelle de l'image affichée basé sur le ratio d'aspect, puis dimensionnement du Box parent à cette taille exacte
- Appliqué à : `ClimbDetailScreen`, `HoldSelectorScreen`, `AdvancedSearchScreen`

---

## P1 - Système de Thèmes

### Architecture
```
data/settings/
└── SettingsDataStore.kt    # Enum AppTheme + DataStore Preferences

ui/theme/
├── Color.kt                # 3 palettes (Colorful, Blue, Gray)
└── Theme.kt                # 6 ColorSchemes + getColorScheme()

ui/screens/
└── SettingsScreen.kt       # UI choix thème avec RadioButtons
```

### 3 Thèmes Implémentés

| Thème | Primary | Secondary | Tertiary |
|-------|---------|-----------|----------|
| Coloré | Rouge #D32F2F | Vert #388E3C | Jaune #FBC02D |
| Bleu | Bleu #1976D2 | Teal #00897B | Light Blue #03A9F4 |
| Gris | Gris #616161 | Gris #757575 | Gris #9E9E9E |

### Persistance
- Utilisation de `DataStore Preferences`
- Clé : `app_theme` (String)
- Chargement au démarrage dans `MainActivity`
- Changement instantané via `collectAsState`

### Accès
- Bouton engrenage (Settings) dans TopAppBar de `ClimbListScreen`
- Route `/settings` avec navigation back

---

## P2 - Améliorations ClimbCard

### CARD-01 : Suppression "X prises"
- Retrait du texte redondant dans `HoldTypeIndicators`
- Les pictos colorés (S/O/F/T) suffisent

---

## Fichiers Créés (7)

| Fichier | Description |
|---------|-------------|
| `ui/screens/SyncScreen.kt` | Placeholder synchronisation |
| `ui/screens/CreateScreen.kt` | Placeholder création bloc |
| `ui/screens/ProfileScreen.kt` | Placeholder profil utilisateur |
| `ui/screens/AdvancedSearchScreen.kt` | Recherche par prises (autonome) |
| `ui/screens/SettingsScreen.kt` | Écran paramètres avec thèmes |
| `data/settings/SettingsDataStore.kt` | DataStore + enum AppTheme |

## Fichiers Modifiés (10)

| Fichier | Modifications |
|---------|---------------|
| `ui/navigation/Screen.kt` | +Settings route, +BottomNavDestination enum |
| `ui/navigation/NavGraph.kt` | Scaffold avec BottomNavigationBar |
| `ui/screens/ClimbDetailScreen.kt` | Fix alignement overlay |
| `ui/screens/HoldSelectorScreen.kt` | Fix alignement overlay |
| `ui/screens/ClimbListScreen.kt` | +onSettingsClick, +bouton engrenage |
| `ui/components/ClimbCard.kt` | Suppression "X prises" |
| `ui/theme/Color.kt` | 3 palettes complètes |
| `ui/theme/Theme.kt` | 6 ColorSchemes, getColorScheme() |
| `MainActivity.kt` | Intégration DataStore thème |
| `build.gradle.kts` | +DataStore Preferences dependency |

---

## Reste à Faire

### P2 - Mineur
- [ ] SYNC-01 : Indicateur offline
- [ ] CARD-02 : Compteur commentaires (nécessite modification modèle)

### P3 - Cosmétique
- [ ] STYLE-01 : Espacements Material 3
- [ ] STYLE-02 : Animations de transition

### Reporté
- [ ] AUTH-01 : Écran login (API Key hardcodée)

---

## Tests Recommandés

1. **Navigation** : Vérifier les 5 onglets bottom nav
2. **Thèmes** : Changer de thème dans Settings, vérifier persistance après redémarrage
3. **Recherche Avancée** : Sélectionner des prises, vérifier résultats
4. **Overlay** : Vérifier alignement des polygones sur l'image (portrait et paysage)

---

## Dépendances Ajoutées

```kotlin
implementation("androidx.datastore:datastore-preferences:1.0.0")
```

---

**Build** : `./gradlew assembleDebug` - SUCCESS
**Installation** : `adb install` - SUCCESS
