# Timeline du Projet mastoc

Ce fichier trace l'historique chronologique des TODOs et jalons du projet.

## Format
`YYYY-MM-DD | TODO XX - Description | Statut`

---

## 2026-01-01

- **TODO 16 complété** - Tableau de Bord Sync
  - Endpoint `/api/sync/stats` enrichi (climbs_synced, climbs_local)
  - Paramètre `local_only` sur `/api/climbs`
  - Module `mastoc/core/sync_stats.py`
  - CLI `python -m mastoc.tools.sync_status`
  - Dialog `SyncStatusDialog` (menu Outils > État synchronisation)

- **TODO 15 archivé** - Sync Incrémentale (100%)

- **TODO 17 archivé** - Authentification et Utilisateurs mastoc
  - Menu Compte ajouté dans app.py (connexion/profil/déconnexion)
  - Fix bug passlib/bcrypt : utilisation directe de bcrypt
  - 15 tests JWT automatisés (test_jwt_auth.py)
  - Déployé sur Railway

## 2025-12-31

- **TODO 17 complété à 100%** - Système d'Authentification et Utilisateurs mastoc
  - **Phase 1** : Extension Modèle User (email, password_hash, role, etc.)
  - **Phase 2** : Endpoints Auth (register, login, refresh, logout, reset-password)
  - **Phase 3** : Endpoints Users (profil, avatar, liste admin)
  - **Phase 4** : Middleware JWT (security.py, dependencies.py, coexistence API Key)
  - **Phase 5** : Client AuthManager (core/auth.py, intégration MastocAPI)
  - **Phase 6** : Client UI (MastocLoginDialog, ProfileDialog, PasswordResetDialog)
  - **Phase 7** : Traçabilité (created_by_id, updated_by_id sur Climb)
  - Fichiers serveur : security.py, dependencies.py, routers/auth.py, routers/users.py
  - Fichiers client : core/auth.py, gui/dialogs/mastoc_auth.py
  - Script migration : scripts/migrate_user_auth.py

- **TODO 18 créé** - Synchronisation Données Sociales
  - Extrait de TODO 16 (ancienne Phase 2c)
  - Refresh compteurs : climbed_by, total_likes, total_comments
  - Approche légère (compteurs) vs complète (tables dédiées)
  - Prérequis : TODO 15, TODO 16

- **TODO 16 simplifié** - Tableau de Bord Sync
  - Renommé de "Outil de Synchronisation Bidirectionnelle"
  - Scope réduit : dashboard stats + liste climbs locaux
  - Retiré : push Stokt, import, Diff Engine, tables sends/comments, conflits
  - 2 phases au lieu de 5 (analyse critique : sur-ingénierie)

- **TODO 15 avancé à 90%** - Sync Incrémentale (Phases 1-4 complétées)
  - Phase 4 : UI et Feedback (100%)
    - `SyncDialog` : Dialog avec choix full/incremental
    - Statistiques affichées : climbs téléchargés, ajoutés, mis à jour, total
    - Mode incrémental désactivé si première sync
  - **ADR-007 créé** : Synchronisation Incrémentale
  - 300 tests passent

- **TODO 15 avancé à 60%** - Sync Incrémentale (Phases 1-3 complétées)
  - Phase 1 : Stokt `max_age` dynamique basé sur `last_sync`
  - Phase 2 : Railway serveur `since_created_at` + `since_synced_at`
  - Phase 3 : Client Railway `sync_incremental()` + `needs_sync()`
  - 300 tests au total (+4 nouveaux)
  - Rapport : `docs/reports/SESSION_2025-12-31_sync_incrementale.md`

- **TODO 16 enrichi** - Stratégie sync sociale documentée
  - Limitation TODO 15 : sync incrémentale ne détecte pas sends/comments/likes
  - Solution Phase 2c : sync sociale dédiée avec 3 modes

- **TODO 14 archivé** - Portage Client Railway (100%)
  - 7 phases complétées : Client API, Backend Switch, Migration GUI, Endpoints, Sync, Validation, Assets
  - 296 tests au total
  - Archivé dans `/archive/TODOS/`

- **TODO 17 créé** - Système d'Authentification et Utilisateurs mastoc
  - Authentification native mastoc : email/password + JWT
  - Rôles : User + Admin
  - Reset password par email
  - Endpoints : `/api/auth/*` (register, login, refresh, reset)
  - Endpoints : `/api/users/*` (me, profil, avatar)
  - Client : AuthManager + dialogs PyQt6
  - Traçabilité : `created_by_id` sur les climbs
  - Liaison Stokt reportée (optionnel v2)

- **TODO 15 créé** - Synchronisation Incrémentale (Optimisation Téléchargement)
  - Analyse complète des capacités de filtrage Stokt vs Railway
  - **Stokt** : paramètre `max_age` disponible mais non utilisé (hardcodé 9999)
  - **Railway** : champs `created_at`/`synced_at` en DB mais non exposés via API
  - **Gain potentiel** : ~99% de données en moins pour sync quotidienne
  - Plan en 5 phases : Quick Win Stokt → Serveur Railway → Client Railway → UI → Tests
  - Prérequis : TODO 14 (MastocAPI)

- **TODO 15 (sync_tool) renommé en TODO 16**
  - L'outil de synchronisation bidirectionnelle devient TODO 16
  - Permet d'insérer le TODO 15 sur l'optimisation des téléchargements

- **TODO 14 avancé à 90%** - Portage Client Python vers Railway
  - **Session 2** : Config persistante + fix sync holds
    - Module `core/config.py` créé : sauvegarde API key + source dans `~/.mastoc/config.json`
    - Méthode `save_hold()` ajoutée à `HoldRepository` (manquait)
    - `RailwaySyncManager` refactorisé : climbs → extraction face_ids → prises
    - Synchronisation Railway testée : **1012 climbs, 776 prises**
    - 10 tests config + 277 tests totaux
    - Rapport : `docs/reports/SESSION_2025-12-31_config_persistance_sync_holds.md`

- **TODO 14 session précédente (85%)**
  - **Phase 1-4 (100%)** : Complétées (session précédente)
  - **Phase 5 (50%)** : Sync et Données
    - **ADR-006 créé** : Deux bases SQLite séparées
      - `~/.mastoc/stokt.db` : données Stokt
      - `~/.mastoc/railway.db` : données Railway
      - Basculement automatique selon `BackendSource`
    - `RailwaySyncManager` créé pour sync Railway → SQLite
    - `MastocAPI.get_faces()` ajouté pour lister les faces
    - Sync automatique des holds via `/api/faces/{id}/setup`
    - **Reste à faire** : images, avatars, users

- **TODO 16 mis à jour** - Nouvelle architecture avec ADR-006 (ex-TODO 15)
  - Sync en 3 temps : Stokt→stokt.db, Railway→railway.db, analyse diff
  - DiffEngine compare les deux bases locales (offline, rapide)
  - Actions Push/Import avec mise à jour des APIs

- **TODO 14 avancé à 80%** - Portage Client Python vers Railway
  - **Phase 1 (100%)** : Client `MastocAPI` créé
    - `mastoc/api/railway_client.py` (400+ lignes)
    - Endpoints : GET/POST/PATCH/DELETE climbs, GET holds, GET faces/setup
    - 16 tests unitaires
  - **Phase 2 (100%)** : `BackendSwitch` créé
    - `mastoc/core/backend.py` (580 lignes)
    - Interface commune `BackendInterface`
    - Adapters `RailwayBackend` et `StoktBackend`
    - Fallback automatique si Railway indisponible
    - 27 tests unitaires
  - **Phase 3 (100%)** : Migration GUI
    - `app.py` : menu "Source de données" (Stokt/Railway)
    - `hold_selector.py`, `creation_app.py` adaptés
  - **Phase 4 (100%)** : Endpoints Railway
    - `server/routers/faces.py` : GET /api/faces/{id}/setup
    - Tests serveur `test_faces.py`
  - **Reste Phase 5** : Sync bidirectionnelle

- **TODO 16 créé** - Outil de Synchronisation Bidirectionnelle mastoc <-> Stokt (ex-TODO 15)
  - Interface PyQtGraph avec 3 onglets : Climbs, Users, Social
  - Diff Engine pour Climbs : local_only, stokt_only, synced, conflicts
  - Diff Engine pour Users : nouveaux setters, modifiés, à jour
  - Sync données sociales : sends (réalisations), comments, likes
  - Actions : Push vers Stokt, Import depuis Stokt, Ignorer
  - Gestion des conflits avec résolution côte-à-côte
  - Prérequis : TODO 14 (MastocAPI)

- **TODO 14 créé** - Portage Client Python vers Railway
  - Migration du client de Stokt (`sostokt.com`) vers Railway (`mastoc-api`)
  - 5 phases : Client API, Backend Switch, Migration GUI, Endpoints, Sync
  - 18 fichiers à adapter
  - Objectif : indépendance complète de Stokt

## 2025-12-30

- **TODO 13 complété à 100%** - Serveur Railway mastoc-api
  - **Import complet des données Stokt réussi**
    - 1 gym, 1 face, 776 holds, ~1000 climbs, ~50 users
  - **Endpoints batch** pour import optimisé (10x plus rapide)
    - `POST /api/sync/import/holds/batch`
    - `POST /api/sync/import/users/batch`
    - `POST /api/sync/import/climbs/batch`
  - **ADRs créés** dans `docs/adr/` :
    - 001: Architecture Railway-First avec Mapping d'IDs
    - 002: Authentification par API Key
    - 003: Stack serveur (FastAPI + PostgreSQL)
    - 004: Client PyQtGraph + SQLite
    - 005: Batch Import pour Holds, Users et Climbs
  - **Script d'import amélioré** :
    - `--use-cache` : utilise cache local (évite appels Stokt)
    - `--save-cache` : sauvegarde les données en cache
    - `--climbs-only` : skip gym/faces/holds
    - `--batch-size N` : taille des lots (défaut: 50)
  - URL production : https://mastoc-production.up.railway.app
  - API Key configurée sur Railway

- **TODO 10 archivé** - Interface de Création de Blocs (97% → Terminé)
  - Premier bloc créé avec succès via mastoc
  - API création fonctionnelle (POST /api/faces/{faceId}/climbs)
  - Wizard complet : sélection prises → formulaire → soumission
  - 3 tâches polish reportées (erreurs par champ, timeout, sauvegarde locale)
  - Archivé dans `/archive/TODOS/`

- **Architecture Railway-First avec Mapping**
  - Refonte stratégie d'indépendance (v3.0)
  - Single-source sélectionnable (Railway par défaut)
  - Mapping `stokt_id` nullable pour sync bidirectionnelle
  - BackendSwitch remplace DataSourceManager
  - Plan de dev mis à jour pour cohérence

- **TODO 13 avancé à 95%** - Serveur Railway (mastoc-api)
  - Structure FastAPI créée dans `server/`
  - Modèles SQLAlchemy : Gym, Face, Hold, Climb, User, IdMapping
  - Routers : health, climbs, holds, sync
  - Endpoints CRUD + import Stokt
  - **Déploiement Railway réussi** :
    - URL : https://mastoc-production.up.railway.app
    - PostgreSQL connecté et fonctionnel
    - Endpoints /health, /docs, /redoc opérationnels
  - **Authentification API Key** :
    - Header `X-API-Key` requis sur `/api/*`
    - `/health`, `/docs`, `/redoc` restent publics
    - Mode dev (sans API_KEY = pas d'auth)
  - **Script d'import Stokt** :
    - `scripts/init_from_stokt.py` : import gym/faces/holds/climbs
    - Support `--api-key` pour authentification
  - **Suite de tests** :
    - 28 tests (health, sync, climbs, auth)
    - Fixtures SQLite en mémoire
  - Problèmes résolus :
    - `uvicorn: command not found` → ajout requirements.txt
    - Module non trouvé → PYTHONPATH=src dans Procfile
    - 404 sur import/gym → JSON body au lieu de query params
    - Double prefix `/api/api` → correction routers
    - API publique → authentification API Key
  - Rapport complet : `docs/reports/SESSION_2025-12-30_serveur_railway_complet.md`

## 2025-12-23

- **Plan de développement créé** - `/docs/devplan/`
  - Analyse complète du projet (10 000 lignes code, 225 tests)
  - 6 documents structurés :
    - `00_OVERVIEW.md` : Vision et synthèse
    - `01_CURRENT_STATE.md` : État actuel détaillé
    - `02_SHORT_TERM.md` : Plan 1-3 mois (Railway, Hold Annotations)
    - `03_MEDIUM_TERM.md` : Plan 3-6 mois (Android MVP, Sync)
    - `04_LONG_TERM.md` : Plan 6-12 mois (Multi-users, Stats, V1.0)
    - `05_ARCHITECTURE.md` : 11 décisions architecturales (ADR)
  - Jalons définis : Android MVP (Mai 2026), V1.0 (Déc 2026)

- **TODO 12 créé** - Hold Annotations (Annotations de prises)
  - Système de tags crowd-sourcés pour les prises (type, état, difficulté)
  - Multi-utilisateurs avec serveur personnel Railway + PostgreSQL
  - Tags : grip_type (12 types), condition (6 états), difficulty (3 niveaux)
  - Consensus communautaire (mode statistique + seuil de votes)
  - Intégration prévue : filtres, ColorModes, panel d'annotation
  - Prérequis : déploiement serveur Railway
  - Statut : Documentation (0%)

- **TODO 10 avancé à 97%** - Interface de Création de Blocs **FONCTIONNEL**
  - **Premier bloc créé via mastoc** : `509345cb-8c01-477d-bfba-dd4d55ee4ddd`
  - **Bugs critiques corrigés** :
    - Boucle infinie signaux (`_load_state()` freeze)
    - Bouton "Suivant" jamais activé
    - Style CSS désactivé invisible
    - Face ID incorrect
  - **Corrections API découvertes** (analyse code décompilé) :
    - `gradingSystem` : minuscule (`"font"`, `"hueco"`, `"dankyu"`)
    - Grades Font : majuscule (`"6A+"`, pas `"6a+"`)
    - `attemptsNumber` : champ requis (peut être `null`)
  - User-Agent "Stokt/6.1.13 (Android)" ajouté
  - **Tests** : 43 tests création passent

- **Documentation stratégique créée** - Indépendance Stokt
  - `docs/backend_spec.md` : Spécification API backend indépendant (780 lignes)
    - Schéma PostgreSQL complet (12 tables)
    - 20+ endpoints documentés (format requête/réponse)
    - Gestion images, authentification, interactions sociales
  - `docs/04_strategie_independance.md` : Stratégie de migration
    - Architecture multi-murs (Montoboard Stokt + pan personnel)
    - Mode hybride recommandé (Stokt + serveur Railway)
    - Plan de sync silencieuse
    - Coûts estimés (~$5-10/mois)

## 2025-12-22 (nuit 6)

- **TODO 10 avancé à 55%** - Interface de Création de Blocs
  - **Phase 0.5 complète** : Infrastructure Navigation
    - `QStackedWidget` pour navigation wizard multi-écrans
    - `WizardController` : gère état et transitions
    - `ClimbCreationState` dataclass partagée entre écrans
  - **Phase 1 complète** : Sélection de Prises
    - `SelectHoldsScreen` avec overlay spécialisé
    - Boutons radio pour type (START, OTHER, FEET, TOP)
    - Couleurs distinctes par type de prise
    - Validation temps réel (min 2 START, 1 TOP)
  - **Phase 2 partielle** : Formulaire (6/9 tâches)
    - `ClimbInfoScreen` avec formulaire complet
    - Champs : nom, grade, description, règle pieds, privé/public
    - Reste : méthodes API (create/update/delete)
  - **Fichiers créés** :
    - `gui/creation/` - Module complet (6 fichiers)
    - `tests/test_creation.py` - 43 nouveaux tests
  - **Tests** : 213 passent (170 + 43 nouveaux)

## 2025-12-22 (nuit 5)

- **TODO 07 archivé** - Interactions avec les Blocs (100%)
  - 10 méthodes API sociales (sends, comments, likes, bookmarks)
  - Modèles : `UserRef`, `Effort`, `Comment`, `Like`
  - `SocialLoader` : chargement async avec cache TTL 5min
  - `SocialPanel` intégré dans hold_selector.py (mode parcours)
  - **Bug fix** : API utilise `effortBy`/`effortDate` (pas `user`/`date`)
  - 33 tests unitaires, 170 tests totaux
  - Rapport : `docs/reports/SESSION_2025-12-22_todo07_social.md`

## 2025-12-22 (nuit 4)

- **TODO 11 cree** - Principes d'Ergonomie UI/UX
  - Document de reference Material Design 3 mobile-first
  - 6 modes principaux : Connexion, Sync, Recherche Simple, Recherche Avancee, Creer, Moi
  - Navigation par gestes : swipe haut/bas (blocs), swipe droite (like)
  - Aspects sociaux caches par defaut (tap pour reveler)
  - Options depliables (Progressive Disclosure)
  - Wireframes ASCII pour tous les modes
  - Heuristiques Nielsen, Loi de Fitts, norme ISO 9241
  - Statut : Documentation complete (100%)

## 2025-12-22 (nuit 3)

- **TODO 10 révisé** - Analyse critique et restructuration
  - Analyse multi-agents : code décompilé + architecture mastoc
  - **Risques identifiés** :
    - GAP Architectural : UI splitter incompatible avec wizard multi-écrans
    - API Client incomplet : manquent POST/PATCH/DELETE
    - HoldSelectorApp : standalone, pas réutilisable comme widget
  - **Décisions** :
    - Phase 0.5 ajoutée : Infrastructure Navigation (prérequis)
    - Extension API intégrée à Phase 2
    - Phases 4-5 (Édition/Circuit) → reportées TODO 11/12
  - Progression corrigée : 17% (5/29 tâches)

- **TODO 10 créé** - Interface de Création de Blocs
  - Analyse complète par 5 agents parallèles
  - Endpoints : POST/PATCH/DELETE climbs documentés
  - Structure données : holdsList, grade, isPrivate, etc.
  - Validations : min 2 prises START, nom min 3 caractères
  - Workflow UI : SelectHolds → ClimbInfo → POST
  - Permissions : canEditHolds, canSetPrivate, canSetPublic
  - Lignes code : 415263-467019 (endpoints), 903059-960320 (UI)
  - Statut : Investigation (10%)

- **TODO 09 créé** - Listes Personnalisées (Collections)
  - 25 endpoints découverts par analyse code décompilé
  - CRUD listes utilisateur et gym
  - Gestion items (ajout/retrait/réordonnancement)
  - Système de suivi/followers
  - Endpoints "my-*" non documentés dans TODO 07
  - Statut : Investigation (5%)

- **Vérification conformité TODO 07** - Analyse agents parallèles
  - 15/15 endpoints confirmés dans le code décompilé
  - Likes (4/4), Comments (3/3), Bookmarks (2/2), Efforts (4/4), Ratings (2/2)
  - Bodies POST/PATCH validés (structure exacte)
  - Endpoints bonus découverts : feed likes, user bookmarks

## 2025-12-22 (soir)

- **TODO 08 complété à 100%** - Modes de Coloration et Heatmaps
  - Quatre modes : Min, Max, Fréquence (quantiles), Rareté (5 niveaux)
  - 7 palettes heatmap (viridis, plasma, inferno, magma, cividis, turbo, coolwarm)
  - Filtre par ouvreur (Tous/Inclure/Exclure) avec top 20 setters
  - Panel ouvreurs rétractable (caché par défaut)
  - UI : comboboxes mode/palette + checkboxes setters
  - Quantiles recalculés à chaque filtrage
  - 137 tests au total

## 2025-12-22 (après-midi)

- **Refactoring TODO 06** - Architecture deux modes + renderer commun
  - **Mode Sélection** : Overlay pyqtgraph avec couleurs par niveau (vert→rouge)
  - **Mode Parcours** : Rendu PIL identique à `app.py`
  - Création `climb_renderer.py` : renderer commun pour les deux applications
  - Bouton Undo pour annuler la dernière sélection
  - Slider de luminosité pour ajuster le fond
  - Suppression du panneau de détail (double-click)
  - 111 tests passent

## 2025-12-22 (matin)

- **Debug TODO 06** - Corrections et nouvelles fonctionnalites
  - Bug IRCRA corrige : 4=12.0 (pas 10.0), 133 blocs 4-5+ (vs 13 avant)
  - Bug click prises : conversion coordonnees scene→plot + point-dans-polygone
  - Image fond grisee 85% + luminosite 50%
  - Optimisation : items selection crees a la demande (lazy)
  - Double filtre : couleurs basees sur blocs filtres (grade + prises)
  - **Deux modes** : Exploration (toutes prises) / Parcours (bloc courant)
    - Boutons Prec/Suiv/Retour selection
  - 21 tests passent
  - Rapport : `docs/reports/SESSION_2025-12-22_debug_todo06.md`

## 2025-12-22 (nuit 2)

- **TODO 07 créé** - Interactions avec les Blocs
  - Objectif : Récupérer ascensions, commentaires, gérer favoris
  - Réflexion : API officielle vs stockage local vs hybride
  - Endpoints à investiguer : ascents, comments, bookmarks
  - Statut : À faire (0%)

- **Marquage prises de départ - vraies données tape**
  - Analyse code décompilé Stokt (lignes 922271-922322)
  - Découverte format tape : `centerTapeStr`, `leftTapeStr`, `rightTapeStr`
  - Logique : 1 prise → 2 lignes (V), 2+ prises → 1 ligne centrale
  - Remplacement trait artisanal 45° dans 5 fichiers
  - Rapport : `docs/reports/SESSION_2025-12-22_start_tapes.md`

- **Contour NEON_BLUE pour prises FEET**
  - Couleur `#31DAFF` (RGB 49, 218, 255) pour pieds obligatoires
  - Ajouté dans : `app.py`, `climb_viewer.py`, `picto.py`
  - Déjà configuré dans : `climb_detail.py`, `hold_overlay.py`
  - 108 tests passent

## 2025-12-22 (soir)

- **Améliorations UI mastoc**
  - Filtrage par grade min/max (deux sliders Fontainebleau)
  - Contrôle luminosité fond (slider 10-100%)
  - Navigation clavier avec mise à jour auto du viewer
  - Système de logs de débugage
  - Génération de pictos (miniatures) pour les blocs
    - Cercles colorés proportionnels aux prises
    - Top 20 prises en gris (contexte)
    - Marqueurs START et TOP (double cercle)
  - Cache persistant des pictos sur disque (`~/.mastoc/pictos/`)
  - Menu "Outils > Régénérer pictos"
  - Marqueurs dans viewer : START (lignes tape), TOP (double polygone écarté 135%)
  - Documentation créée : `01_architecture.md`, `02_design_decisions.md`
  - 108 tests passent

## 2025-12-22 (nuit)

- **TODO 06 complété à 100%** - Interface de Filtrage et Sélection de Blocs
  - Double slider de niveau (4 → 8A)
  - Coloration dynamique des prises (vert→rouge selon grade)
  - Sélection multi-prises avec logique ET
  - Liste des blocs filtrés avec vue détaillée
  - Navigation Previous/Next
  - 108 tests passent au total
  - Usage : `python -m mastoc.gui.hold_selector`

## 2025-12-21 (nuit)

- **TODO 05 archivé** - Package Python mastoc (100%)
  - Phase 1-5 toutes complétées
  - 90 tests unitaires et d'intégration passent
  - Modules créés : `core/sync.py`, `core/filters.py`, `gui/app.py`, `gui/widgets/climb_list.py`, `gui/dialogs/login.py`
  - Application principale fonctionnelle avec liste de climbs, filtres et visualisation
  - Archivé dans `/archive/TODOS/`

## 2025-12-21 (soir)

- **TODO 06 créé** - Interface de Filtrage et Sélection de Blocs
  - Objectif : Retrouver un bloc à partir des prises de façon interactive
  - Double slider de niveau (4+ → 8A)
  - Coloration des prises selon le grade du bloc le plus facile (dégradé vert→rouge)
  - Sélection multi-prises (logique ET)
  - Liste des blocs filtrés (nom, auteur, grade)
  - Vue détaillée avec navigation Previous/Next
  - Complète le TODO 05
  - Statut : À faire (0%)

- **TODO 05 avancé à 50%** - Package Python mastoc fonctionnel
  - Phase 1 (100%) : Structure package avec `pyproject.toml`
  - Phase 2 (100%) : Base SQLite avec 1017 climbs et 776 prises importés
  - Phase 4 (50%) : Viewer PyQtGraph avec rendu avancé
    - Image haute résolution avec effet gris/couleur
    - Détection automatique couleur des prises
    - 3 sliders interactifs (fond, contour, épaisseur)
  - 39 tests unitaires passent
  - Usage : `python3 -m mastoc.gui.climb_viewer --name "Nia" --setter "Mathias" --image`

## 2025-12-21

- **TODO 05 créé** - Structure Package Python mastoc
  - Objectif : Restructurer le code en package installable (`pip install -e .`)
  - Stack : PyQtGraph + PyQt6 pour GUI, SQLite pour stockage local
  - Fonctionnalités : stockage BD, sync, filtres climbs, visualisation prises
  - Servira de prototype avant l'application mobile
  - Statut : À faire (0%)

- **TODO 04 complété à 100%** - Extraction données Montoboard
  - Endpoint `/api/faces/{faceId}/setup` découvert et testé
  - 776 prises avec polygones récupérées
  - Image haute résolution téléchargée (2263x3000)
  - Documentation mise à jour

## 2025-12-20 (nuit)

- **TODO 04 avancé à 25%** - Tests d'extraction
  - Authentification réussie (token valide)
  - Tests des endpoints : plusieurs retournent 404
  - Endpoints OK : `api/token-auth`, `api/users/me`, `api/version`, `api/my-notifications`
  - Endpoints 404 : `api/gyms/{id}/climbs`, `api/gyms/{id}/faces`, `api/users/{id}/sent-climbs`
  - **Découverte** : L'API a peut-être changé, ou il manque des headers
  - **Prochaine étape** : Analyser `fetchMySentClimbs` pour comprendre la construction des requêtes

- **TODO 03 avancé à 95%** - Endpoints supplémentaires découverts
  - Endpoint climbs récents : `api/gyms/{gymId}/climbs?max_age=60`
  - Endpoint sent-climbs : `api/users/{userId}/sent-climbs?limit=X`
  - Endpoint my-sent-climbs : `api/gyms/{gymId}/my-sent-climbs`
  - Paramètres filtrage complets documentés
  - HomeScreen analysé (flux de chargement)

## 2025-12-20 (soir)

- **TODO 04 créé** - Test extraction données Montoboard
  - Objectif : Tester les endpoints découverts
  - Récupérer gym, faces, climbs, images
  - Analyser le format holdsList
  - Exporter en JSON
  - Statut : À faire (0%)

- **TODO 03 avancé à 85%** - Analyse Hermes réussie
  - Installation de hermes-dec (décompileur Hermes v96)
  - Désassemblage complet du bundle (95 Mo)
  - Configuration app extraite (`baseURL`, `appVersion`, etc.)
  - Flux authentification documenté (`Token <value>`)
  - 40+ endpoints API identifiés et documentés
  - 100+ actions Redux cataloguées
  - Structures de données Climb/Face extraites
  - **Création base documentaire** : `/docs/reverse_engineering/`
  - Rapport : `/docs/reports/SESSION_2025-12-20_analyse_hermes.md`

## 2025-12-20 (après-midi)

- **Test d'extraction API directe**
  - Authentification réussie sur `sostokt.com` (pas getstokt.com)
  - Token DRF obtenu via `/api/token-auth`
  - Salle Montoboard identifiée (ID: `be149ef2-317d-4c73-8d7d-50074577d2fa`)
  - Endpoints `/api/faces`, `/api/climbs` : erreurs/timeout
  - **Décision** : Analyse statique approfondie avant nouvelles requêtes
  - Rapport : `/docs/reports/SESSION_2025-12-20_api_extraction.md`

- **TODO 03 créé** - Analyse approfondie du bundle Hermes via agents
  - Objectif : Comprendre exactement les flux API de l'app
  - Stratégie : Décompilation Hermes + analyse Redux
  - Contrainte : Pas de requêtes exploratoires (risque bannissement)
  - Statut : À faire (0%)

- **TODO 01 mis à jour** - Analyse complète refaite depuis zéro
  - Re-analyse de l'APK et du bundle JavaScript
  - 40+ endpoints API identifiés
  - Architecture Redux documentée (150+ actions)
  - Système de prises (holds) analysé
  - Problème offline confirmé (pas de persistance locale)
  - Statut : En cours (70%)
  - Rapport : `/docs/reports/SESSION_2025-12-20_analyse_complete_stokt.md`

- **Tentative de patch APK pour interception HTTPS**
  - Utilisation de apk-mitm pour patcher le certificate pinning
  - Split APKs re-signés avec clé commune
  - **Échec** : Bug `@null` dans le manifest empêche l'installation
  - Guide créé : `/docs/02_guide_interception_https.md`
  - Rapport : `/docs/reports/SESSION_2025-12-20_patch_apk_mitm.md`
  - Statut : Bloqué - alternatives à explorer

- **TODO 02 créé** - Conception du schéma SQLite pour mastoc
  - Basé sur l'analyse statique de Stōkt
  - Architecture offline-first
  - Statut : À faire (0%)

## 2025-11-10

- **TODO 01 créé** - Analyse et décompilation de l'application d'escalade
  - Objectif : Comprendre le fonctionnement de l'app existante
  - Focus : Système d'images interactives et problèmes offline
  - Statut : En cours (0%)
