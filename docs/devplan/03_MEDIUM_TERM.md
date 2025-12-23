# Plan Moyen Terme (3-6 mois)

**Période** : Mars - Juin 2026

---

## Objectifs principaux

1. **Application Android MVP**
2. **Synchronisation bi-directionnelle**
3. **Support du pan personnel**
4. **Listes personnalisées**

---

## Phase 5 : Application Android MVP (Mois 3-4)

### Stack technique

| Composant | Technologie |
|-----------|-------------|
| Langage | Kotlin |
| UI | Jetpack Compose |
| Architecture | MVVM + Clean Architecture |
| Base de données | Room (SQLite) |
| Réseau | Retrofit + OkHttp |
| DI | Hilt |
| Images | Coil |
| Dessin | Compose Canvas |

### Architecture de l'application

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Screens   │  │ ViewModels  │  │    Theme    │          │
│  │  (Compose)  │  │   (State)   │  │    (M3)     │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  UseCases   │  │   Models    │  │ Repository  │          │
│  │             │  │ (Domain)    │  │ Interfaces  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                       Data Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │    Room     │  │  Retrofit   │  │   DataStore │          │
│  │   (Local)   │  │  (Remote)   │  │   (Prefs)   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Écrans à implémenter

| Écran | Priorité | Complexité |
|-------|----------|------------|
| Splash + Sync initial | Haute | Faible |
| Liste des blocs | Haute | Moyenne |
| Détail bloc (visualisation) | Haute | Élevée |
| Filtres (grade, setter) | Haute | Faible |
| Recherche par prises | Haute | Élevée |
| Création de bloc (wizard) | Moyenne | Élevée |
| Profil / Paramètres | Basse | Faible |

### Tâches détaillées

#### Semaine 9-10 : Setup projet

| Tâche | Effort |
|-------|--------|
| Créer projet Android Studio | 2h |
| Configurer Gradle (version catalogs) | 4h |
| Setup Hilt (DI) | 4h |
| Setup Room (database) | 4h |
| Setup Retrofit (network) | 4h |
| Setup Navigation Compose | 4h |
| Définir le thème M3 | 4h |

#### Semaine 11-12 : Core features

| Tâche | Effort |
|-------|--------|
| Écran liste des blocs | 8h |
| Intégration API (fetch climbs) | 8h |
| Persistance Room | 8h |
| Filtres par grade | 4h |
| Navigation entre écrans | 4h |

#### Semaine 13-14 : Visualisation

| Tâche | Effort |
|-------|--------|
| Compose Canvas - rendu image mur | 12h |
| Dessin des prises (polygones) | 8h |
| Marqueurs START/TOP/FEET | 4h |
| Zoom/Pan sur image | 8h |
| Détail bloc avec prises | 8h |

#### Semaine 15-16 : Recherche avancée

| Tâche | Effort |
|-------|--------|
| Écran recherche par prises | 12h |
| Sélection tap sur prises | 8h |
| Filtrage par prises sélectionnées | 8h |
| Modes de coloration (heatmaps) | 8h |

### Livrables MVP

- [ ] App Android installable
- [ ] Liste des blocs avec filtres
- [ ] Visualisation des blocs
- [ ] Recherche par prises
- [ ] Synchronisation API

---

## Phase 6 : Synchronisation Bi-directionnelle (Mois 4-5)

### Objectif

Permettre la modification des données depuis Android avec sync vers le serveur.

### Flux de données

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Android    │────▶│   Railway    │────▶│    Stokt     │
│   (Room)     │◀────│  (PostgreSQL)│◀────│   (API)      │
└──────────────┘     └──────────────┘     └──────────────┘
     Local             Serveur perso         Source vérité
```

### Stratégie de synchronisation

| Scénario | Comportement |
|----------|--------------|
| Online | Sync immédiate vers serveur |
| Offline | Queue locale, sync au retour |
| Conflit | Priorité serveur (timestamp) |
| Création bloc | Dual-write Stokt + serveur perso |

### Tâches

| Tâche | Effort |
|-------|--------|
| WorkManager pour sync background | 8h |
| Queue offline (Room) | 8h |
| Résolution de conflits | 8h |
| Indicateurs sync UI | 4h |
| Tests sync | 8h |

---

## Phase 7 : Pan Personnel (Mois 5-6)

### Objectif

Supporter un mur personnel (pan maison) en plus de Montoboard.

### Workflow

1. **Capture photo** : Prendre photo du pan
2. **Upload** : Envoyer au serveur
3. **Mapping prises** : Dessiner les polygones (web ou app)
4. **Création blocs** : Comme pour Montoboard

### Outil de mapping des prises

Options :
- **Option A** : Interface web simple (Canvas HTML5)
- **Option B** : Dans l'app Android (Compose Canvas)
- **Option C** : Outil Python standalone

**Recommandation** : Option A (web) - plus facile à développer, usage ponctuel.

### Interface web de mapping

```html
<!-- Pseudo-code interface mapping -->
<canvas id="wall-image">
  <!-- Affiche l'image du pan -->
  <!-- Click pour ajouter des points -->
  <!-- Double-click pour fermer le polygone -->
</canvas>
<button onclick="savePolygons()">Sauvegarder</button>
```

### Tâches

| Tâche | Effort |
|-------|--------|
| Upload image pan (API) | 4h |
| Interface web mapping | 16h |
| Calcul centroïdes automatique | 4h |
| Import polygones dans DB | 4h |
| Support multi-faces dans app | 8h |
| Tests intégration | 4h |

---

## Phase 8 : Listes Personnalisées (Mois 6)

### Objectif

Implémenter TODO 09 : gérer des collections de blocs.

### Fonctionnalités

- Créer/modifier/supprimer des listes
- Ajouter/retirer des blocs d'une liste
- Consulter les listes populaires du gym
- Partager une liste

### Tâches

| Tâche | Effort |
|-------|--------|
| API listes sur serveur perso | 8h |
| Écran "Mes listes" | 8h |
| Création/édition liste | 8h |
| Ajout/retrait blocs | 4h |
| Listes populaires | 4h |
| Tests | 4h |

---

## Calendrier prévisionnel

```
Mois 3 (Mars)
├── Semaine 9-10  : Setup projet Android
├── Semaine 11-12 : Core features
Mois 4 (Avril)
├── Semaine 13-14 : Visualisation Canvas
├── Semaine 15-16 : Recherche avancée
├── Semaine 17    : Polish + Tests
Mois 5 (Mai)
├── Semaine 18-19 : Sync bi-directionnelle
├── Semaine 20-21 : Pan personnel (mapping)
Mois 6 (Juin)
├── Semaine 22-23 : Pan personnel (app)
├── Semaine 24-25 : Listes personnalisées
├── Semaine 26    : Polish + Release beta
```

---

## Critères de succès Phase Moyen Terme

### Application Android

- [ ] App fonctionnelle sur Play Store (beta interne)
- [ ] Toutes les features du prototype Python
- [ ] Performance < 500ms pour afficher un bloc
- [ ] Taille APK < 30 MB
- [ ] Support Android 7.0+ (API 24)

### Infrastructure

- [ ] Sync bi-directionnelle fiable
- [ ] Support mode offline complet
- [ ] Pan personnel fonctionnel

### Tests

- [ ] Tests unitaires Kotlin (~100)
- [ ] Tests UI instrumentés (~20)
- [ ] Tests d'intégration API

---

## Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| Complexité Compose Canvas | POC validé en phase précédente |
| Performance rendu prises | Optimisation lazy loading |
| Mapping prises complexe | Interface web simple, pas parfaite |
| Scope creep | MVP strict, features supplémentaires en V2 |

---

## Technologies à maîtriser

| Technologie | Ressource |
|-------------|-----------|
| Jetpack Compose | Android Developers / Codelabs |
| Compose Canvas | [Official docs](https://developer.android.com/jetpack/compose/graphics/draw/overview) |
| Room | Android Developers |
| WorkManager | Android Developers |
| Hilt | Android Developers |

---

*Plan moyen terme créé le 2025-12-23*
