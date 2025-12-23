# Rapport de Session - Extraction APK Stockt

**Date** : 2025-11-10

## 🎯 Objectifs Atteints

- ✅ Identification de l'application sur le téléphone
- ✅ Extraction complète des APK (base + splits)
- ✅ Récupération des informations de version et permissions

## 📊 Informations de l'Application

### Identification
- **Nom** : stockt (Stokt)
- **Package** : `com.getstokt.stokt`
- **Version** : 6.1.13 (versionCode 689)

### Configuration
- **minSdk** : 24 (Android 7.0+)
- **targetSdk** : 35 (Android 15)
- **Taille totale** : ~87 MB
  - base.apk : 59 MB
  - split_config.arm64_v8a.apk : 25 MB
  - split_config.fr.apk : 49 KB
  - split_config.xxhdpi.apk : 3.3 MB

### Permissions Principales

#### Permissions Critiques
- `ACCESS_FINE_LOCATION` - Localisation précise
- `ACCESS_COARSE_LOCATION` - Localisation approximative
- `CAMERA` - Accès à la caméra
- `RECORD_AUDIO` - Enregistrement audio
- `INTERNET` - Accès réseau

#### Permissions de Stockage
- `READ_EXTERNAL_STORAGE` - Lecture stockage externe
- `WRITE_EXTERNAL_STORAGE` - Écriture stockage externe

#### Permissions Système
- `ACCESS_NETWORK_STATE` - État du réseau
- `ACCESS_WIFI_STATE` - État du WiFi
- `FOREGROUND_SERVICE` - Services en avant-plan
- `POST_NOTIFICATIONS` - Notifications
- `WAKE_LOCK` - Maintenir l'appareil éveillé
- `VIBRATE` - Vibration

#### Permissions Commerciales
- `com.android.vending.BILLING` - Achats intégrés
- `ACCESS_ADSERVICES_*` - Services publicitaires Google
- `com.google.android.gms.permission.AD_ID` - ID publicitaire

#### Permissions de Badges (divers launchers)
- Permissions pour afficher des badges sur différents launchers Android (Samsung, Huawei, Oppo, Sony, HTC)

## 📁 Fichiers Extraits

Les fichiers APK sont situés dans :
```
/media/veracrypt1/Repositories/mastoc/extracted/stockt_apk/
├── base.apk
├── split_config.arm64_v8a.apk
├── split_config.fr.apk
└── split_config.xxhdpi.apk
```

## 🔍 Observations Initiales

1. **Application moderne** : targetSdk 35 (Android 15), indiquant une maintenance active
2. **Services de localisation** : Permissions de géolocalisation (attendu pour une app d'escalade)
3. **Caméra et Audio** : Suggère des fonctionnalités multimédia (photos de blocs, vidéos?)
4. **Services commerciaux** : Billing et Ad services indiquent un modèle freemium/avec publicités
5. **Fonctionnalités réseau** : INTERNET + état réseau pour synchronisation
6. **Architecture native** : Split ARM64-v8a indique du code natif optimisé

## 🏗️ Architecture Découverte

### Stack Technique
- **Framework** : React Native + Expo SDK 53.0.0
- **Runtime Version** : 1.1.3
- **Backend** : Firebase (Realtime Database + Storage)
- **Authentification** : Facebook SDK + Login natif
- **Paiements** : Google Play Billing (react-native-iap)
- **Monitoring** : Sentry
- **Analytics** : Firebase Analytics + Google Analytics

### Composants Clés
- **Activité principale** : `com.getstokt.stokt.MainActivity` (portrait uniquement)
- **Application** : `com.getstokt.stokt.MainApplication`
- **Bundle JavaScript** : `/assets/index.android.bundle` (7.3 MB minifié)

### Infrastructure Firebase
- **Database URL** : https://stokt-app-6342d.firebaseio.com
- **Storage Bucket** : stokt-app-6342d.appspot.com
- **Project ID** : stokt-app-6342d
- **Google API Key** : AIzaSyAfkG2P7rHVghXfepBf6NX2L01-0qcR330

### Configuration Facebook
- **App ID** : 472291919004573
- **Client Token** : 5b0ab36941c474395b4a720ac51ba24c

### Modules Expo Utilisés
- expo-notifications (notifications push)
- expo-localization (i18n)
- expo-font (polices personnalisées)
- expo-asset (gestion des assets)
- expo-mail-composer (envoi d'emails)
- expo-web-browser (navigation web)

## 📱 Fonctionnalités Identifiées

D'après la description et les ressources :

1. **Gestion des problèmes d'escalade**
   - Création et publication de problèmes sur murs d'entraînement
   - Visualisation de listes de problèmes
   - Système d'images interactives pour marquer les prises

2. **Recherche et filtrage**
   - Recherche par nom de problème
   - Recherche par ouvreur ("setter")
   - Filtrage par cotation/grade

3. **Suivi des performances**
   - Logger les réussites ("sends")
   - Statuts : "sent", "flashed", "compended"
   - Système de notation (étoiles)

4. **Fonctionnalités sociales**
   - Profils utilisateurs (Facebook)
   - Partage de problèmes
   - "My Gym" (salle personnelle)

5. **Modèle économique**
   - Version gratuite avec essai ("free_trial_banner")
   - Achats in-app
   - Publicités (Google AdServices)

## 🗄️ Structure de Données

### Stockage
- **Base de données** : Firebase Realtime Database (cloud)
- **Cache local** : Probablement AsyncStorage ou SQLite (expo-sqlite)
- **Fichiers** : Firebase Storage (images des murs, photos de profil)

### Types de données attendus
- Problèmes (problems)
  - ID, nom, ouvreur, cotation, date
  - Référence image du mur
  - Coordonnées des prises
- Salles (gyms)
  - ID, nom, localisation
  - Liste de murs
- Utilisateurs (users)
  - Profil, statistiques
  - Problèmes créés/résolus
- Sessions (sends)
  - Tentatives, réussites
  - Notes, commentaires

## 🖼️ Ressources Visuelles

### Icônes découvertes
- `images_mygym_sent.png` - Problème réussi
- `images_mygym_flashed.png` - Problème flashé (réussi du premier coup)
- `images_mygym_compended.png` - Statut "compended"
- `images_mygym_star.png` - Notation
- `images_mygym_banner.png` - Bannière My Gym
- `images_mygym_free_trial_banner.png` - Bannière essai gratuit
- `images_problem_addtolisticon.png` - Ajouter à une liste

### Assets
- Images de splash screen
- Logo Stōkt
- Icônes de navigation (flèches, retour, recherche, etc.)

## 🔍 Observations sur le Mode Offline

### Problème identifié (à confirmer)
L'application utilise Firebase Realtime Database qui nécessite une connexion réseau. Possibles causes des problèmes offline :
1. Cache Firebase mal configuré
2. Pas de persistance locale activée
3. Images non mises en cache
4. Dépendance aux requêtes réseau pour l'UI

### Points à investiguer
- Configuration de la persistance Firebase (`setPersistenceEnabled`)
- Stratégie de cache des images
- Gestion des états offline dans le code JavaScript
- Utilisation éventuelle d'une base SQLite locale

## 🚀 Prochaines Étapes

1. **Analyse du bundle JavaScript**
   - Déminifier le bundle (si possible)
   - Identifier les composants React
   - Analyser la logique de gestion des données offline

2. **Reverse engineering du système d'images interactives**
   - Comprendre comment les coordonnées des prises sont stockées
   - Identifier le format de données (JSON, coordonnées x/y)
   - Analyser la bibliothèque utilisée (SVG, Canvas, React Native Gesture Handler)

3. **Extraction de données via Firebase**
   - Tenter de lire la structure Firebase (si règles publiques)
   - Examiner les données en cache sur le téléphone
   - Identifier le schéma de données

4. **Tests de l'application**
   - Tester le comportement offline
   - Observer les appels réseau (mitmproxy)
   - Capturer la structure des requêtes API

5. **Conception de la solution mastoc**
   - Base de données locale SQLite offline-first
   - Système de synchronisation optionnelle
   - Cache agressif des images
   - UI fonctionnelle sans réseau
