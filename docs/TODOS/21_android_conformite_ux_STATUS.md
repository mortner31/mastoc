# STATUS - TODO 21 : Conformité UX/Design Android

**Progression** : 80%

## Décisions Prises

- **Auth** : REPORTÉ - Garder API Key hardcodée pour l'instant
- **Thème** : 3 choix implémentés (Coloré/Bleu/Gris) avec persistance DataStore

---

## P0 - Critique (100%)

- [x] NAV-01 : Bottom Navigation Bar (5 destinations)
- [x] NAV-02 : Accès Recherche Avancée (intégré dans nav)
- [x] IMG-01 : Correction alignement overlay/image (ContentScale.Fit pris en compte)
- [x] IMG-02 : Chargement image vérifié

## P1 - Majeur (100%)

- [x] SETTINGS-01 : Écran SettingsScreen
- [x] SETTINGS-02 : Choix thème (Coloré/Bleu/Gris) avec RadioButtons
- [x] SETTINGS-03 : 3 ColorSchemes complets (light/dark)
- [x] SETTINGS-04 : Persistance DataStore
- [x] SETTINGS-05 : Bouton engrenage TopAppBar
- [x] PICTO-01 : Pictos dans ClimbCard (HoldTypeIndicators déjà implémenté)

## P2 - Mineur (33%)

- [x] CARD-01 : Supprimer "X prises"
- [ ] CARD-02 : Compteur commentaires (REPORTÉ - champ absent du modèle)
- [ ] SYNC-01 : Indicateur offline

## P3 - Cosmétique (0%)

- [ ] STYLE-01 : Espacements M3
- [ ] STYLE-02 : Animations

## REPORTÉ

- [ ] AUTH-01 : Écran login (API Key hardcodée pour l'instant)
- [ ] CARD-02 : Compteur commentaires (nécessite ajout champ au modèle Climb)

---

## Fichiers Créés/Modifiés

### Créés
- `ui/screens/SyncScreen.kt` - Écran placeholder Sync
- `ui/screens/CreateScreen.kt` - Écran placeholder Créer
- `ui/screens/ProfileScreen.kt` - Écran placeholder Profil
- `ui/screens/AdvancedSearchScreen.kt` - Recherche par prises (autonome)
- `ui/screens/SettingsScreen.kt` - Écran Paramètres avec choix thème
- `data/settings/SettingsDataStore.kt` - Persistance préférences (AppTheme enum)

### Modifiés
- `ui/navigation/Screen.kt` - 5 destinations bottom nav + Settings + enum BottomNavDestination
- `ui/navigation/NavGraph.kt` - Scaffold avec BottomNavigationBar + route Settings
- `ui/screens/ClimbDetailScreen.kt` - Correction alignement overlay/image
- `ui/screens/HoldSelectorScreen.kt` - Correction alignement overlay/image
- `ui/screens/ClimbListScreen.kt` - Bouton engrenage + callback onSettingsClick
- `ui/components/ClimbCard.kt` - Suppression "X prises"
- `ui/theme/Color.kt` - 3 palettes complètes (Colorful, Blue, Gray)
- `ui/theme/Theme.kt` - 6 ColorSchemes + fonction getColorScheme()
- `MainActivity.kt` - Intégration DataStore pour thème dynamique
- `build.gradle.kts` - Ajout dépendance DataStore

---

## Thèmes Implémentés

| Thème | Primary | Secondary | Tertiary |
|-------|---------|-----------|----------|
| **Coloré** | Rouge #D32F2F | Vert #388E3C | Jaune #FBC02D |
| **Bleu** | Bleu #1976D2 | Teal #00897B | Bleu clair #03A9F4 |
| **Gris** | Gris #616161 | Gris #757575 | Gris #9E9E9E |

---

**Dernière mise à jour** : 2026-01-01
