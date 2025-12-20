# STATUS - TODO 03 : Analyse Approfondie du Bundle Hermes via Agents

**Progression** : 95%

## ✅ Complété

### Session 2025-12-20 (soir) : Analyse approfondie des requêtes
- [x] Flux complet : Gym → Face → Climb
- [x] Endpoint faces : `api/gyms/{gymId}/faces`
- [x] Endpoint climbs : `api/faces/{faceId}/latest-climbs/paginated`
- [x] **Endpoint climbs récents** : `api/gyms/{gymId}/climbs?max_age=60`
- [x] **Endpoint sent-climbs** : `api/users/{userId}/sent-climbs?limit=X`
- [x] **Endpoint my-sent-climbs** : `api/gyms/{gymId}/my-sent-climbs` (à analyser)
- [x] Paramètres filtrage : grade_from/to, ordering, search, tags, exclude_mine, show_circuit_only, angle
- [x] Structure Climb complète avec holdsList
- [x] Documentation mise à jour dans `/docs/reverse_engineering/03_ENDPOINTS.md`
- [x] Test authentification OK (`api/token-auth`, `api/users/me`, `api/version`)
- [x] Découverte : endpoints gym retournent 404 → API peut avoir changé

### Session 2025-12-20 (après-midi) : Premiers endpoints

### Phase 1 : Installation des outils
- [x] Rechercher et installer un décompileur Hermes (hermes-dec)
- [x] Tester la décompilation sur le bundle (disasm OK, decompile partiel)
- [x] Valider que le code est lisible (strings et objets extraits)

### Phase 2 : Analyse du flux d'authentification
- [x] Identifier la fonction/module d'authentification
- [x] Documenter le format exact de la requête (`api/token-auth`)
- [x] Comprendre le format du token (`Token <value>`)
- [x] Documenter dans `/docs/reverse_engineering/02_AUTHENTIFICATION.md`

### Phase 3 : Analyse du flux "My Gym"
- [x] Trouver le code myGym (actions Redux `stokt-app/myGym/*`)
- [x] Identifier la séquence de requêtes (FACE, CLIMBS, etc.)
- [x] Documenter les paramètres pagination (`offset`, `page_size`, `ordering`)

### Phase 4 : Analyse du flux "Climbs"
- [x] Trouver le code problem/climbs (actions Redux)
- [x] Identifier la récupération des blocs
- [x] Documenter la structure de base d'un Climb

### Phase 5 : Analyse du flux "Faces/Walls"
- [x] Trouver les endpoints faces/walls
- [x] Comprendre le lien face/climb (`api/faces/{id}/climbs`)
- [x] Documenter les structures

### Phase 6 : Synthèse
- [x] Créer base documentaire pyramidale `/docs/reverse_engineering/`
- [x] Documenter configuration, endpoints, structures, actions Redux

## ⏳ En cours / À faire

### À compléter
- [ ] Analyser les coordonnées des prises (format exact)
- [ ] Créer diagramme de séquence complet
- [ ] Tester l'extraction réelle avec les endpoints découverts
- [ ] Documenter les images des murs/faces

## 📁 Documentation Créée

| Fichier | Description |
|---------|-------------|
| `/docs/reverse_engineering/INDEX.md` | Index racine |
| `/docs/reverse_engineering/01_CONFIGURATION.md` | Configuration app |
| `/docs/reverse_engineering/02_AUTHENTIFICATION.md` | Flux auth |
| `/docs/reverse_engineering/03_ENDPOINTS.md` | Liste endpoints |
| `/docs/reverse_engineering/04_STRUCTURES.md` | Structures données |
| `/docs/reverse_engineering/05_REDUX_ACTIONS.md` | Actions Redux |

## 🛠️ Outils Installés

- **hermes-dec** v0.0.1 : Désassembleur Hermes (pip)
- **Fichiers générés** :
  - `stokt_disasm.hasm` (95 Mo)
  - `stokt_decompiled.js` (40 Mo, partiel)
