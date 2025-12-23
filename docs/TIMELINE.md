# Timeline du Projet mastoc

Ce fichier trace l'historique chronologique des TODOs et jalons du projet.

## Format
`YYYY-MM-DD | TODO XX - Description | Statut`

---

## 2025-12-23

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
