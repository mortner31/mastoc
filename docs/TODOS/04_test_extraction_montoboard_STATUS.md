# STATUS - TODO 04 : Test Extraction Données Montoboard

**Progression** : 100%

## ✅ Complété

### Phase 1 : Authentification
- [x] Récupérer token (`api/token-auth`) ✅
- [x] Valider avec `/api/users/me` ✅
- [x] Token valide : `dba723cbee34ff3cf049b12150a21dc8919c3cf8`

### Phase 2 : Analyse du code décompilé
- [x] Analyser `fetchMySentClimbs` (ligne 442389)
- [x] Comprendre la construction des URLs : `'api/gyms/' + gymId + '/my-sent-climbs'`
- [x] Identifier le mécanisme d'authentification (header `Authorization: Token xxx`)
- [x] Analyser `fetchGymRecentClimbs` (ligne 458971) : `api/gyms/{gymId}/climbs?max_age={days}`
- [x] Analyser `getWalls` (ligne 440447) : `api/gyms/{gymId}/walls`
- [x] Analyser `fetchGymSummary` (ligne 440848) : `api/gyms/{gymId}/summary`

### Phase 3 : Test des endpoints corrigés
- [x] Test `api/gyms/{gymId}/my-sent-climbs` → **200 OK** ✅
- [x] Test `api/gyms/{gymId}/climbs?max_age=60` → **200 OK** ✅ (63 climbs)
- [x] Test `api/gyms/{gymId}/walls` → **200 OK** ✅ (1 wall, 1 face)
- [x] Test `api/gyms/{gymId}/summary` → **200 OK** ✅

## 📊 Endpoints Fonctionnels

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `api/token-auth` | POST | Authentification (form: username, password) |
| `api/users/me` | GET | Profil utilisateur |
| `api/version` | GET | Version API |
| `api/my-notifications` | GET | Notifications |
| `api/gyms/{id}/summary` | GET | Résumé gym (walls, stats, managers) |
| `api/gyms/{id}/walls` | GET | Liste des murs avec faces |
| `api/gyms/{id}/climbs?max_age={days}` | GET | Climbs récents (paginé) |
| `api/gyms/{id}/my-sent-climbs` | GET | Climbs validés par l'utilisateur |

## 📊 Endpoints NON Fonctionnels

| Endpoint | Statut | Note |
|----------|--------|------|
| `api/gyms/{id}/` | 404 | Utiliser `/summary` à la place |
| `api/gyms/{id}/faces` | 404 | Utiliser `/walls` qui inclut les faces |
| `api/faces/{faceId}` | 403/404 | Permission refusée |
| `api/efforts` | 403 | Permission refusée |

## 📋 Structure Climb (holdsList)

Format découvert : `S829279 S829528 O828906 O828964 O828985 O829120 O829377 O829459 T829009`
- **S** = Start (prise de départ)
- **O** = Other (prise normale)
- **F** = Feet (pied obligatoire - pieds des mains)
- **T** = Top (prise finale)
- Le nombre = ID de la prise sur la face

## 📊 Données découvertes

| Information | Valeur |
|-------------|--------|
| Base URL | `https://www.sostokt.com/` |
| Gym ID | `be149ef2-317d-4c73-8d7d-50074577d2fa` |
| Gym Name | Montoboard |
| Wall ID | `1ab81c9a-ecfa-4a1a-b56e-1490f3445d99` |
| Wall Name | Stōkt board |
| Face ID | `61b42d14-c629-434a-8827-801512151a18` |
| Total Climbs | 1174 |
| Image Face | `media/CACHE/images/walls/.../ref_pic_qMsRutJ_small.jpg` |
| User ID | `35722f7d-79d2-4688-a856-9d9caf34be7b` |
| Token | `dba723cbee34ff3cf049b12150a21dc8919c3cf8` |
| API Version | 1.3.0 |

## ⏳ En cours / À faire

### Phase 4 : Outil Python
- [x] Image de face téléchargée (`/extracted/images/face_small.jpg`)
- [x] Créer script Python d'extraction (`mastock/src/stokt_api.py`)
- [x] Créer script d'extraction complète (`mastock/src/extract_all_climbs.py`)
- [x] Récupérer tous les climbs avec pagination (459 climbs extraits)
- [x] Exporter en JSON (`extracted/data/montoboard_20251220.json`)

### Phase 5 : Analyse holdsList
- [x] Format holdsList décodé (S/O/F/T + ID)
- [x] 738 prises uniques identifiées
- [x] Prise la plus utilisée : 829098 (78 fois)
- [ ] Récupérer `api/faces/{faceId}/setup` pour les coordonnées
- [ ] Mapper les IDs vers positions (x, y) sur l'image

## 📁 Fichiers de référence

- Code décompilé : `/extracted/stockt_decompiled/decompiled/stokt_decompiled.js`
- Image face small : `/extracted/images/face_small.jpg` (339x450)
- Image face full : `/extracted/images/face_full.jpg` (905x1200)
- API Client : `/mastock/src/stokt_api.py`
- Script extraction : `/mastack/src/extract_all_climbs.py`
- Données (459 climbs/365j) : `/extracted/data/montoboard_20251220.json`
- Données (1017 climbs/ALL) : `/extracted/data/montoboard_ALL_climbs.json`

## 📊 Résultats d'extraction

- **459 climbs** extraits sur 365 jours
- Répartition : 4 (1), 4+ (25), 5 (12), 5+ (15), 6A (31), 6A+ (45), 6B (51), 6B+ (48), 6C (63), 6C+ (38), 7A (60), 7A+ (28), 7B (18), 7B+ (2), 7C (1), 8A (2)
- Top setters : Alex Le Deun (76), Ilian Audoin (76), Thomas Pamies (44)
