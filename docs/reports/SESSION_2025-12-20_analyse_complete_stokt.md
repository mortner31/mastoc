# Rapport de Session - Analyse Complète de l'Application Stōkt

**Date** : 2025-12-20

## 🎯 Objectifs Atteints

- ✅ Re-analyse complète de l'APK depuis le début
- ✅ Identification de l'architecture technique
- ✅ Extraction des endpoints API
- ✅ Analyse du système de gestion des prises (holds)
- ✅ Identification des actions Redux
- ✅ Confirmation du problème offline

---

## 📱 Informations de l'Application

| Élément | Valeur |
|---------|--------|
| **Nom** | Stōkt |
| **Package** | `com.getstokt.stokt` |
| **Version** | 6.1.13 (versionCode 689) |
| **Taille totale** | ~87 MB (4 APKs split) |
| **SDK minimum** | 24 (Android 7.0) |
| **SDK cible** | 35 (Android 15) |

---

## 🏗️ Architecture Technique

### Framework Principal
- **React Native** avec **Expo SDK 53**
- Bundle JavaScript en format **Hermes** (binaire optimisé, 7.6 MB)

### Bibliothèques Identifiées
| Catégorie | Bibliothèque |
|-----------|--------------|
| Animations | React Native Reanimated |
| Graphiques/Canvas | React Native Skia |
| Navigation | React Navigation |
| State Management | Redux |
| Authentification | Firebase Auth, Facebook SDK, Apple Sign-In, Google Sign-In |
| Notifications | Expo Notifications, Firebase Messaging |
| Achats In-App | react-native-iap |
| Monitoring | Sentry |

### Services Backend
| Service | Détails |
|---------|---------|
| **API REST** | `https://www.getstokt.com/api/` |
| **Firebase** | Messaging, Analytics |
| **Expo Updates** | `https://u.expo.dev/d010a830-bcc2-11e8-b18f-bf35f14ebd8d` |
| **Facebook SDK** | App ID: 472291919004573 |

---

## 🔌 Endpoints API Identifiés

### Authentification
- `POST /api/token-auth/` - Connexion par email/password
- `POST /api/signup/` - Inscription
- `POST /api/social-auth/facebook/` - Auth Facebook
- `POST /api/social-auth/google/` - Auth Google
- `POST /api/social-auth/apple/` - Auth Apple
- `POST /api/password/reset/` - Reset mot de passe
- `POST /api/logout/` - Déconnexion

### Salles et Murs
- `GET /api/gyms/paginated` - Liste des salles paginée
- `GET /api/favorite-gyms/` - Salles favorites
- `GET /api/walls/` - Murs d'escalade
- `GET /api/faces/` - Faces de murs (images des murs)

### Blocs/Problèmes
- `GET /api/climbs/` - Liste des blocs
- `GET /api/climbs/comments/` - Commentaires
- `GET /api/climb-lists/` - Listes de blocs
- `GET /api/ratings/` - Notes des blocs

### Activité Utilisateur
- `GET /api/user/` - Profil utilisateur
- `GET /api/user/history` - Historique
- `GET /api/efforts/` - Tentatives/envois
- `GET /api/efforts/comments/` - Commentaires sur efforts
- `GET /api/feeds/` - Flux d'activité

### Listes et Social
- `GET /api/lists/` - Listes personnalisées
- `GET /api/search/climbers` - Recherche de grimpeurs
- `GET /api/search/following/` - Recherche dans les suivis
- `GET /api/follow/` - Suivre un utilisateur
- `GET /api/unfollow/` - Ne plus suivre

### Système LED (Prises Connectées)
- `GET /api/led-kit/` - Kits LED
- `GET /api/led-kits/` - Liste des kits

### Autres
- `GET /api/stokt-sessions/` - Sessions d'escalade
- `GET /api/videos/` - Vidéos
- `GET /api/version` - Version API

---

## 🧩 Modules Redux (State Management)

L'application utilise Redux avec des actions préfixées par `stokt-app/`. Modules identifiés :

### `stokt-app/myGym/`
Gestion de la salle active :
- `CHANGE_GYM` - Changer de salle
- `CLIMBS_PENDING/SUCCESS/ERROR` - Chargement des blocs
- `FILTER_CLIMBS_SUCCESS` - Filtrage
- `GET_PAIRED_HOLDS_*` - Prises appairées (LED)
- `PAIR_HOLD_*` / `UNPAIR_HOLD_*` - Appairage prises
- `TOGGLE_LED_HOLD` - Toggle LED
- `SETUP_*` - Configuration du mur
- `GYM_SUMMARY_*` - Résumé de la salle

### `stokt-app/problem/`
Gestion des problèmes/blocs :
- `CLIMB_PENDING/SUCCESS/ERROR` - Chargement d'un bloc
- `BOOKMARK_*` - Favoris
- `POST_LIKE_*` / `DELETE_LIKE_*` - Likes
- `CREATE_EFFORT_*` - Enregistrer une tentative
- `DELETE_EFFORT_*` - Supprimer une tentative
- `FETCH_LIKES_*` - Récupérer les likes

### `stokt-app/problemCreation/`
Création de nouveaux blocs :
- `TOGGLE_START_HOLD` - Sélectionner prise de départ
- `TOGGLE_FINISH_HOLD` - Sélectionner prise d'arrivée
- `TOGGLE_FOOT_HOLD` - Sélectionner prise de pied
- `TOGGLE_OTHER_HOLD` - Autres prises
- `TOGGLE_CIRCUIT_HOLD` - Circuit
- `UPDATE_GRADE` - Modifier la cotation
- `UPDATE_NAME` - Modifier le nom
- `UPDATE_DESCRIPTION` - Modifier la description
- `POST_CLIMB_*` - Publier le bloc
- `CLEAR_HOLDS` - Effacer la sélection

### `stokt-app/lists/`
Gestion des listes :
- `FETCH_LISTS_*` - Charger les listes
- `ADD_LIST_*` - Créer une liste
- `DELETE_LIST_*` - Supprimer une liste
- `ADD_CLIMB_TO_LIST_*` - Ajouter un bloc à une liste
- `FOLLOW_LIST_*` / `UNFOLLOW_LIST_*` - Suivre/ne plus suivre

### `stokt-app/faces/`
Gestion des images de murs :
- `FETCH_FACES_*` - Charger les faces
- `FETCH_GYMS_*` - Charger les salles
- `FETCH_WALLS_*` - Charger les murs
- `ADD_GYM_PIC_*` - Ajouter photo de salle
- `GET_GYM_ADMINS_*` - Admins de la salle

### `stokt-app/filterAndSort/`
Filtres et tri :
- `UPDATE_SORT_OPTIONS` - Options de tri
- `UPDATE_TAGS` - Filtrer par tags
- `RESET_FILTERS` - Réinitialiser
- `CIRCUITS_ONLY` - Circuits uniquement
- `EXCLUDE_SENDS` - Exclure les envois
- `INCLUDE_PROBLEMS` - Inclure les problèmes

### `stokt-app/user/`
Profil utilisateur :
- `GET_USER_BOOKMARKS_*` - Favoris
- `UPDATE_USER_SUCCESS` - Mise à jour profil
- `FACEBOOK_AUTH_SUCCESS` / `APPLE_AUTH_SUCCESS` - Auth sociale
- `PAYMENT_*` - Paiements (Stōkt Premium)

---

## 🧗 Système de Gestion des Prises (Holds)

### Principe
Les prises sont positionnées sur une image du mur via des **coordonnées X/Y absolues**.

### Types de Prises
| Type | Description |
|------|-------------|
| `start` | Prise(s) de départ |
| `finish` | Prise(s) d'arrivée |
| `foot` | Prises de pieds uniquement |
| `other` | Autres prises intermédiaires |
| `circuit` | Prises d'un circuit |

### Limitations
- Maximum **1500 prises** par mur (message d'alerte au-delà)
- Maximum **600 prises** sélectionnables pour un bloc

### Système LED
- Support de prises connectées via kits LED
- Appairage prises physiques ↔ LEDs virtuelles
- Actions : `PAIR_HOLD`, `UNPAIR_HOLD`, `TOGGLE_LED_HOLD`

### Règles de Pieds (Feet Rules)
- Configuration personnalisable des règles de pieds
- Limite sur le nombre de règles (avec message d'alerte)

---

## ⚠️ Problème Offline Confirmé

### Constat
Aucun système de **persistance locale** détecté dans le bundle :
- Pas de SQLite
- Pas d'AsyncStorage pour les données de blocs
- Toutes les données sont chargées via API REST

### Conséquence
L'application ne peut pas fonctionner sans connexion internet car :
1. Les images des murs sont chargées à la demande
2. Les données des blocs ne sont pas mises en cache
3. Les coordonnées des prises ne sont pas stockées localement

### Solution pour mastock
Créer une architecture **offline-first** avec :
- Base SQLite locale pour stocker les blocs, murs, coordonnées
- Cache d'images local
- Synchronisation périodique avec possibilité de sync manuelle

---

## 📊 Statistiques du Bundle

| Métrique | Valeur |
|----------|--------|
| Taille bundle JS | 7.6 MB |
| Lignes (estimé) | ~61,000 |
| Format | Hermes bytecode |
| Actions Redux | 150+ |
| Endpoints API | 40+ |

---

## 🚀 Prochaines Étapes Recommandées

1. **Capture réseau avec mitmproxy**
   - Observer les vraies requêtes/réponses JSON
   - Documenter la structure exacte des données

2. **Extraire des exemples de données**
   - Structure JSON d'un bloc
   - Structure JSON des coordonnées de prises
   - Structure d'une image de mur (face)

3. **Concevoir le schéma SQLite pour mastock**
   - Tables : gyms, walls, faces, climbs, holds, attempts
   - Relations et index

4. **Prototyper l'interface de visualisation**
   - Affichage image + overlay des prises
   - Interaction tactile pour sélection

---

## 📚 Fichiers de Référence

- APK décompilé : `/extracted/stockt_decompiled/`
- Bundle JS : `/extracted/stockt_decompiled/assets/index.android.bundle`
- Config Expo : `/extracted/stockt_decompiled/assets/app.config`
- Manifest : `/extracted/stockt_decompiled/AndroidManifest.xml`

---

**Session effectuée par** : Claude (Opus 4.5)
