# Analyse de la Structure Firebase et API - Stōkt

**Date** : 2025-11-10
**Application** : Stōkt (com.getstokt.stokt)
**Version** : 6.1.13

## 🌐 Infrastructure Backend

### URLs de Base
- **Backend principal** : https://www.getstokt.com
- **Backend secondaire** : https://www.sostokt.com
- **Firebase Database** : https://stokt-app-6342d.firebaseio.com
- **Firebase Storage** : stokt-app-6342d.appspot.com

### Architecture
L'application utilise une architecture hybride :
- **Firebase Realtime Database** pour certaines données en temps réel
- **API REST personnalisée** (`www.getstokt.com/api/`) pour la logique métier
- **Firebase Storage** pour les images/médias

## 📊 Structure de l'État Redux

L'analyse du bundle JavaScript révèle l'utilisation intensive de Redux pour la gestion d'état. Voici les modules principaux :

### 1. Module `problem` (Problèmes/Voies d'escalade)

**Actions identifiées** :
- `stokt-app/problem/FETCH_LIKES_SUCCESS`
- `stokt-app/problem/POST_LIKE_ERROR`
- `stokt-app/problem/DELETE_EFFORT_RESE[T]`
- `stokt-app/problem/USER_GRADE_ERROR`
- `stokt-app/problem/CLOSE_MODAL`
- `stokt-app/problem/FETCH_GRADE_DETAILS_RESE[T]`

**Données gérées** :
- Détails des problèmes (voies)
- Likes/favoris
- Efforts (tentatives)
- Cotations (grades)

### 2. Module `user` (Utilisateurs)

**Actions identifiées** :
- `stokt-app/user/ATTEMPT_NAVIGATION`
- `stokt-app/user/GET_USER_BOOKMARKS_SUCCESS`
- `stokt-app/user/SEARCH_CLIMBERS_SUCCESS`
- `stokt-app/user/GET_FOLLOWING_PENDING`
- `stokt-app/user/GYM_EVENTS_REQUES[T]`

**Données gérées** :
- Profils utilisateurs
- Bookmarks (blocs sauvegardés)
- Abonnements (following)
- Événements de salle

### 3. Module `myGym` (Salle personnelle)

**Actions identifiées** :
- `stokt-app/myGym/SETUP_SUCCESS`
- `stokt-app/myGym/CHANGE_GYM`
- `stokt-app/myGym/CLEAR_CLIMBS_ERROR`
- `stokt-app/myGym/UPDATE_FILTER_APPLIED`
- `stokt-app/myGym/UNPAIR_HOLD_PENDING`
- `stokt-app/myGym/RESET_RULES_IMAGE[T]`
- `stokt-app/myGym/DESCRIPTION_SUCCESS`

**Données gérées** :
- Configuration de la salle
- Filtres actifs
- Gestion des prises (holds) et leur appariement (pairing)
- Images de référence (rules image)

### 4. Module `lists` (Listes de problèmes)

**Actions identifiées** :
- `stokt-app/lists/DELETE_LIST_SUCCESS`
- `stokt-app/lists/UPDATE_LISTS_ON_SEARCH`
- `stokt-app/lists/ARCHIVED`

**Données gérées** :
- Listes personnalisées de blocs
- Recherche dans les listes
- Archivage

### 5. Module `problemCreation` (Création de problèmes)

**Actions identifiées** :
- `stokt-app/problemCreation/UPDATE_FEET_SELECTION`

**Données gérées** :
- Sélection de prises (pieds/mains)
- Processus de création de voies

### 6. Module `faces` (Murs/Faces d'escalade)

**Actions identifiées** :
- `stokt-app/faces/GET_POPULAR_CLIMBS_LIST_ERROR`
- `stokt-app/faces/NOTIFICATION_COMMUNICATION_REQUES[T]`
- `stokt-app/faces/GET_FEED_ITEM_SUCCESS`

**Données gérées** :
- Liste des murs disponibles
- Problèmes populaires par mur
- Flux d'activité (feed)

## 🔌 Endpoints API Identifiés

### Authentification
- `/api/token-auth` - Authentification par token
- `/api/logout` - Déconnexion

### Gestion des Utilisateurs
- `/api/my-avatar` - Avatar de l'utilisateur
- `/api/user/history?start_date=` - Historique utilisateur
- `/api/search/climbers?search=` - Recherche de grimpeurs
- `/api/search/following` - Abonnements
- `/api/follow` - Suivre un utilisateur
- `/api/unfollow` - Ne plus suivre

### Problèmes (Climbs/Problems)
- `/api/climbs/comments` - Commentaires
- `/api/climbs?max_age=` - Liste des problèmes avec filtrage par âge
- `/api/grade-details?angle=` - Détails de cotation par angle
- `/api/climb-lists` - Listes de problèmes
- `/api/items?page_size=1000` - Items (probable endpoint générique paginé)
- `/api/lists?kind=` - Listes filtrées par type
- `/api/lists?ordering=` - Listes triées
- `/api/lists?page_size=` - Listes paginées

### Efforts (Tentatives)
- `/api/efforts/comments?limit=` - Commentaires sur les tentatives
- `/api/attempts/log()` - Log des tentatives

### Faces/Murs
- `/api/faces/competitions` - Compétitions
- `/api/feeds/crowd-grades` - Notes communautaires

### Favoris et Bookmarks
- `/api/favorite-gyms` - Salles favorites
- `/api/bookmarked-climbs` - Blocs sauvegardés
- `/api/liked-climbs` - Blocs likés
- `/api/my-bookmarked-climbs` - Mes blocs sauvegardés
- `/api/my-liked-climbs` - Mes blocs likés
- `/api/my-sent-climbs` - Mes blocs réussis
- `/api/my-set-climbs` - Mes blocs créés

### Sessions
- `/api/stokt-sessions` - Sessions d'escalade

### Autres
- `/api/password/reset` - Réinitialisation de mot de passe
- `/api/purchases` - Achats in-app
- `/api/tokens` - Gestion des tokens
- `/api/notifications` - Notifications
- `/api/payments` - Paiements
- `/api/permissions-to-modify` - Permissions

### Formats de Données
- `/api/latest-climbs/paginated` - Derniers blocs (paginés)
- `/api/latest-sends` - Dernières réussites
- `/api/pop-up-summary` - Résumé popup
- `/api/personal?ordering=` - Données personnelles triées

## 🗺️ Structure de Données Inférée

### Problem (Voie d'escalade)
```typescript
interface Problem {
  id: string;
  name: string;
  setter: string;          // Ouvreur
  grade: string;           // Cotation (ex: "V4", "6B")
  angle?: number;          // Angle du mur
  date_created: Date;
  date_modified: Date;
  date_updated: Date;
  face_id: string;         // ID du mur
  holds: Hold[];           // Liste des prises
  likes_count: number;
  comments_count: number;
  sends_count: number;     // Nombre de réussites
  status?: 'new' | 'sent' | 'flashed' | 'compended';
  bookmarked: boolean;
  liked: boolean;
}
```

### Hold (Prise)
```typescript
interface Hold {
  id: string;
  coordinates: {
    x: number;             // Position X sur l'image
    y: number;             // Position Y sur l'image
  };
  type: 'hand' | 'foot' | 'both';
  paired?: boolean;        // Si la prise est appairée
  paired_hold_id?: string;
}
```

### Face (Mur)
```typescript
interface Face {
  id: string;
  name: string;
  gym_id: string;
  angle?: number;
  image_url: string;       // Image de référence du mur
  rules_image_url?: string;
  width: number;           // Dimensions de l'image
  height: number;
  problems_count: number;
}
```

### Gym (Salle)
```typescript
interface Gym {
  id: string;
  name: string;
  location?: {
    lat: number;
    lng: number;
  };
  faces: Face[];
  is_favorite: boolean;
}
```

### User
```typescript
interface User {
  id: string;
  username: string;
  avatar_url: string;
  email?: string;
  stats: {
    sends_count: number;
    problems_created: number;
    following_count: number;
    followers_count: number;
  };
  bookmarks: string[];     // IDs des problèmes sauvegardés
  liked_climbs: string[];
  sent_climbs: string[];
  set_climbs: string[];    // Problèmes créés
}
```

### Effort (Tentative)
```typescript
interface Effort {
  id: string;
  problem_id: string;
  user_id: string;
  status: 'sent' | 'flashed' | 'attempted';
  attempts_count: number;
  date: Date;
  comment?: string;
  rating?: number;         // Note (1-5 étoiles)
}
```

### List (Liste de problèmes)
```typescript
interface List {
  id: string;
  name: string;
  user_id: string;
  problems: string[];      // IDs des problèmes
  kind?: string;           // Type de liste
  is_archived: boolean;
}
```

## 🎨 Système d'Images Interactives

### Mécanisme Identifié
L'application utilise un système de **coordonnées absolues** sur une image de référence du mur :

1. **Image de base** : Photo haute résolution du mur d'escalade
2. **Marqueurs de prises** : Coordonnées X/Y enregistrées pour chaque prise
3. **Rendu** : Superposition graphique (probablement SVG ou Canvas) sur l'image
4. **Interaction** : Tap/Click sur l'image pour ajouter/sélectionner des prises

### Technologies Utilisées
D'après le bundle :
- **React Native Skia** (`@shopify/react-native-skia`) - Rendu graphique performant
- **React Native Gesture Handler** - Gestion des interactions tactiles
- **React Native Reanimated** - Animations fluides

### Format de Stockage (Hypothèse)
```json
{
  "problem_id": "abc123",
  "face_image": "https://storage.googleapis.com/.../wall_image.jpg",
  "holds": [
    {
      "id": "hold1",
      "x": 150,
      "y": 300,
      "type": "hand",
      "color": "#FF1031"
    },
    {
      "id": "hold2",
      "x": 200,
      "y": 250,
      "type": "foot",
      "paired_with": "hold1"
    }
  ]
}
```

## 🔄 Gestion Offline

### Problème Actuel
L'application utilise Firebase Realtime Database sans persistance locale robuste.

### Cause Probable des Problèmes Offline
1. **Pas de cache Firebase activé** : `setPersistenceEnabled(false)` ou non configuré
2. **Dépendance à l'API REST** : Les endpoints `/api/` nécessitent une connexion réseau
3. **Images non mises en cache** : Les images des murs ne sont probablement pas stockées localement
4. **État Redux non persisté** : Pas de middleware de persistance (ex: redux-persist)

### Flux de Données
```
Utilisateur → Action Redux → API REST / Firebase → Mise à jour État → UI
                                    ↓
                              Nécessite réseau
```

### Solution Proposée pour mastoc
```
Utilisateur → Action Redux → SQLite Local → Mise à jour État → UI
                                    ↓
                          Synchronisation optionnelle
                                    ↓
                              API/Firebase (quand réseau disponible)
```

## 🔐 Authentification

### Mécanisme
- **Token-based auth** (`/api/token-auth`)
- **Facebook SDK** intégré (OAuth optionnel)
- **Apple Sign In** (iOS uniquement)

### Stockage des Tokens
Probablement dans **AsyncStorage** (React Native) ou **SecureStore** (Expo)

## 📸 Médias et Assets

### Images Statiques
- **Avatar par défaut** : `https://www.sostokt.com/static/main/img/hand_avatar_small.jpg`
- **Assets packagés** : `/assets/images/` (inclus dans l'APK)

### Images Dynamiques
- **Firebase Storage** : `stokt-app-6342d.appspot.com`
- **Format** : Probablement JPEG/PNG optimisés
- **Tailles multiples** : Thumbnails + haute résolution

## 📊 Observations Clés

### Points Forts de l'Architecture
1. Architecture modulaire (Redux bien organisé)
2. Séparation claire entre API et Firebase
3. Système d'images interactives sophistiqué

### Faiblesses Identifiées (Causes du problème offline)
1. **Aucune persistance locale des données** (ou mal configurée)
2. **Dépendance forte au réseau** pour chaque requête
3. **Pas de stratégie de cache claire**
4. **Images non stockées localement**

### Recommandations pour mastoc
1. **Base SQLite locale** avec schéma complet
2. **Cache agressif des images** (file system local)
3. **Synchronisation optionnelle** en arrière-plan
4. **UI offline-first** : tout doit fonctionner sans réseau
5. **Système de coordonnées identique** pour compatibilité

## 🚀 Prochaines Étapes

1. **Capture réseau** : Utiliser mitmproxy pour observer les requêtes réelles
2. **Extraction d'exemples de données** : Capturer des JSON réels de l'API
3. **Test du système de coordonnées** : Créer un problème et analyser le format exact
4. **Conception du schéma SQLite** : Modéliser les tables pour mastoc
5. **POC du système d'images** : Reproduire le système de marquage des prises

## 📝 Notes Techniques

### Versions des Dépendances Clés
- React Native : ~0.74.x (Expo SDK 53)
- Firebase : v9+
- Redux : Probablement RTK (Redux Toolkit)

### Format des Dates
- Utilisation de **ISO 8601** (ex: `2025-11-10T14:30:00Z`)
- Timestamps Unix pour certaines données

### Pagination
- **Page size** par défaut : 1000 items (`?page_size=1000`)
- **Ordering** : `-date_created`, `-date_modified`, `-date_updated`

---

**Document généré par l'analyse du bundle JavaScript décompilé**
**Source** : `/media/veracrypt1/Repositories/mastoc/extracted/stockt_decompiled/assets/index.android.bundle`
