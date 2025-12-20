# TODO 04 - Test Extraction Données Montoboard

## 🎯 Objectif

Tester les endpoints API découverts pour récupérer toutes les données de la salle Montoboard et valider le flux d'extraction.

## 🔑 Données Connues

| Information | Valeur |
|-------------|--------|
| Base URL | `https://www.sostokt.com/` |
| Gym ID | `be149ef2-317d-4c73-8d7d-50074577d2fa` |
| Auth Header | `Authorization: Token <token>` |
| Content-Type | `application/x-www-form-urlencoded` |

## 📋 Tâches

### Phase 1 : Authentification

- [ ] Récupérer un nouveau token via `api/token-auth`
- [ ] Valider le token avec `api/users/me`
- [ ] Stocker le token pour les requêtes suivantes

### Phase 2 : Récupération Gym

- [ ] GET `api/gyms/{gym_id}/` - Détails du gym Montoboard
- [ ] Documenter la structure de réponse
- [ ] Identifier les IDs des faces/walls

### Phase 3 : Récupération Faces/Walls

- [ ] GET `api/faces/?gym={gym_id}` ou équivalent
- [ ] Lister toutes les faces de Montoboard
- [ ] Récupérer les URLs des images de chaque face
- [ ] Documenter la structure Face

### Phase 4 : Récupération Climbs

- [ ] GET `api/faces/{face_id}/climbs` pour chaque face
- [ ] Ou GET `api/climbs/?gym={gym_id}` avec pagination
- [ ] Récupérer tous les climbs avec `page_size=1000`
- [ ] Documenter la structure Climb complète

### Phase 5 : Analyse HoldsList

- [ ] Extraire le champ `holdsList` d'un climb
- [ ] Analyser le format (JSON ? coordonnées X/Y ?)
- [ ] Comprendre le lien avec les images de face

### Phase 6 : Export des Données

- [ ] Sauvegarder les données en JSON
- [ ] Télécharger les images des faces/walls
- [ ] Créer une structure de données exploitable

## 🔧 Script de Test

```bash
# Variables
BASE_URL="https://www.sostokt.com"
GYM_ID="be149ef2-317d-4c73-8d7d-50074577d2fa"

# 1. Auth
TOKEN=$(curl -s -X POST "$BASE_URL/api/token-auth" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=EMAIL&password=PASSWORD" | jq -r '.token')

# 2. Test token
curl -s "$BASE_URL/api/users/me" \
  -H "Authorization: Token $TOKEN"

# 3. Get gym
curl -s "$BASE_URL/api/gyms/$GYM_ID/" \
  -H "Authorization: Token $TOKEN"

# 4. Get faces
curl -s "$BASE_URL/api/faces/?gym=$GYM_ID" \
  -H "Authorization: Token $TOKEN"

# 5. Get climbs (avec pagination)
curl -s "$BASE_URL/api/climbs/?gym=$GYM_ID&page_size=100" \
  -H "Authorization: Token $TOKEN"
```

## ⚠️ Précautions

1. **Pas de requêtes en boucle** - Tester manuellement d'abord
2. **Respecter les rate limits** - Attendre entre les requêtes
3. **Sauvegarder les réponses** - Pour analyse offline
4. **Documenter les erreurs** - Pour ajuster les endpoints

## 📚 Références

- `/docs/reverse_engineering/02_AUTHENTIFICATION.md` - Format auth
- `/docs/reverse_engineering/03_ENDPOINTS.md` - Liste endpoints
- `/docs/reverse_engineering/04_STRUCTURES.md` - Structures attendues

## 🎯 Résultats Attendus

1. **Fichier JSON** avec tous les climbs de Montoboard
2. **Images** des faces/walls téléchargées
3. **Documentation** du format holdsList
4. **Validation** que l'extraction fonctionne

---

**Créé** : 2025-12-20
**Statut** : À faire
