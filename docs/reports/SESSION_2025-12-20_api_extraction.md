# Rapport de Session - Extraction de Données via API Stōkt

**Date** : 2025-12-20

---

## 🎯 Objectif

Tenter de requêter directement l'API de l'application Stōkt pour extraire les données de la salle Montoboard, après l'échec du patch APK pour interception HTTPS.

---

## ✅ Ce qui a fonctionné

### 1. Authentification réussie

**Endpoint** : `POST https://www.sostokt.com/api/token-auth`

**Format de requête** :
```bash
curl -X POST "https://www.sostokt.com/api/token-auth" \
  -H "Content-Type: application/json" \
  -d '{"username": "EMAIL", "password": "MOT_DE_PASSE"}'
```

**Réponse** :
```json
{"token":"dba723cbee34ff3cf049b12150a21dc8919c3cf8"}
```

**Points clés** :
- Le champ est `username` (pas `email`)
- Le token est au format DRF (Django REST Framework)
- L'URL backend est `sostokt.com` (pas `getstokt.com` qui est devenu un site Squarespace)

### 2. Liste des gyms accessible

**Endpoint** : `GET https://www.sostokt.com/api/gyms`

**Header d'authentification** :
```
Authorization: Token <TOKEN>
```

**Réponse** : Liste complète de toutes les salles (plusieurs centaines)

**Structure d'un gym** :
```json
{
  "id": "be149ef2-317d-4c73-8d7d-50074577d2fa",
  "displayName": "Montoboard",
  "logo": "CACHE/images/gyms/logos/logo_q9kVBl3/62457c4805e0011d6d2c74d02b2c0dd1.jpg",
  "locationString": "Caraman, France",
  "gradesDisabled": false
}
```

### 3. Salle Montoboard identifiée

| Champ | Valeur |
|-------|--------|
| ID | `be149ef2-317d-4c73-8d7d-50074577d2fa` |
| Nom | Montoboard |
| Localisation | Caraman, France |

---

## ❌ Ce qui n'a pas fonctionné

### 1. Endpoints non trouvés (404)

Les endpoints suivants n'existent pas sur l'API `sostokt.com` :
- `/api/gyms/{id}` - Détails d'un gym spécifique
- `/api/gyms/{id}/faces` - Murs d'un gym
- `/api/my-bookmarked-climbs`
- `/api/my-sent-climbs`
- `/api/my-liked-climbs`
- `/api/walls`

### 2. Endpoints en erreur (500)

- `/api/faces` - Erreur serveur
- `/api/faces?gym={id}` - Erreur serveur

### 3. Endpoints avec timeout

- `/api/climbs?gym={id}` - Requête très longue, interrompue

### 4. Problèmes de format

L'URL `getstokt.com` n'est plus l'API backend (redirige vers Squarespace).

---

## 📊 Analyse du Bundle Hermes

Le bundle JavaScript est compilé en **bytecode Hermes** (version 96), ce qui empêche une lecture directe du code.

### Endpoints identifiés via `strings`

```
api/climb
api/climb-lists
api/climbs
api/efforts
api/faces
api/favorite-gyms
api/feeds
api/follow
api/gyms
api/led-kit
api/led-kits
api/lists
api/logout
api/my-avatar
api/password
api/search
api/signup
api/social-auth
api/stokt-sessions
api/token-auth
api/unfollow
api/user
api/user-reports
api/users
api/version
api/videos
api/walls
```

### Actions Redux identifiées

- `stokt-app/myGym/FILTER_CLIMBS_SUCCESS`
- `stokt-app/faces/FETCH_WALLS_SUCCESS`
- `stokt-app/problem/SAVE_CLIMB`
- `stokt-app/myGym/GET_PAIRED_HOLDS_SUCCESS`
- `stokt-app/user/SWITCH_GYM`

---

## ⚠️ Risques identifiés

### Rate limiting / Bannissement

L'API peut détecter :
1. **Requêtes inhabituelles** : endpoints non utilisés par l'app officielle
2. **Volume de requêtes** : trop de requêtes en peu de temps
3. **User-Agent suspect** : curl vs app mobile
4. **Patterns d'accès** : accès à des endpoints dans un ordre non naturel

### Recommandations

1. **Ne pas tester à l'aveugle** les endpoints
2. **Analyser le code** avant de faire des requêtes
3. **Espacer les requêtes** si nécessaire
4. **Utiliser un User-Agent mobile** si on continue

---

## 🔧 Stratégie recommandée

### Phase 1 : Analyse statique approfondie

Utiliser des agents pour :
1. **Décompiler le bytecode Hermes** avec `hermes-dec` ou équivalent
2. **Analyser le flux de données** : comment l'app récupère les climbs d'un gym
3. **Identifier les paramètres exacts** de chaque requête
4. **Comprendre le système de cache** de l'app

### Phase 2 : Extraction ciblée

Une fois le flux compris :
1. Reproduire exactement les requêtes de l'app
2. Se limiter aux données de Montoboard
3. Sauvegarder les données localement

### Phase 3 : App offline

Créer une app locale qui :
1. Utilise les données exportées
2. Fonctionne 100% offline
3. Affiche les blocs avec le système de coordonnées identifié

---

## 📁 Données récupérées

| Type | Statut | Fichier |
|------|--------|---------|
| Token d'auth | ✅ Obtenu | (ne pas stocker en clair) |
| ID Montoboard | ✅ Obtenu | `be149ef2-317d-4c73-8d7d-50074577d2fa` |
| Liste gyms | ✅ Accessible | Non sauvegardée |
| Faces/Murs | ❌ Non accessible | - |
| Climbs | ❌ Non accessible | - |

---

## 🚀 Prochaines étapes

1. **Installer un décompileur Hermes** pour analyser le bundle
2. **Mapper le flux exact** de récupération des données dans l'app
3. **Identifier les bons endpoints** avec leurs paramètres
4. **Tester de manière ciblée** uniquement les requêtes validées

---

**Temps passé** : ~30 min
**Bloqueur principal** : API différente de ce qui était documenté dans l'analyse statique initiale
