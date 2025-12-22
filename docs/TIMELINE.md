# Timeline du Projet mastock

Ce fichier trace l'historique chronologique des TODOs et jalons du projet.

## Format
`YYYY-MM-DD | TODO XX - Description | Statut`

---

## 2025-12-22 (soir)

- **TODO 08 complété à 100%** - Modes de Coloration et Heatmaps
  - Trois modes : Min, Max, Fréquence (quantiles)
  - 7 palettes heatmap (viridis, plasma, inferno, magma, cividis, turbo, coolwarm)
  - Filtre par ouvreur (Tous/Inclure/Exclure) avec top 20 setters
  - UI : comboboxes mode/palette + checkboxes setters
  - Quantiles recalculés à chaque filtrage
  - 23 nouveaux tests, 134 tests au total

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

- **Améliorations UI mastock**
  - Filtrage par grade min/max (deux sliders Fontainebleau)
  - Contrôle luminosité fond (slider 10-100%)
  - Navigation clavier avec mise à jour auto du viewer
  - Système de logs de débugage
  - Génération de pictos (miniatures) pour les blocs
    - Cercles colorés proportionnels aux prises
    - Top 20 prises en gris (contexte)
    - Marqueurs START et TOP (double cercle)
  - Cache persistant des pictos sur disque (`~/.mastock/pictos/`)
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
  - Usage : `python -m mastock.gui.hold_selector`

## 2025-12-21 (nuit)

- **TODO 05 archivé** - Package Python mastock (100%)
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

- **TODO 05 avancé à 50%** - Package Python mastock fonctionnel
  - Phase 1 (100%) : Structure package avec `pyproject.toml`
  - Phase 2 (100%) : Base SQLite avec 1017 climbs et 776 prises importés
  - Phase 4 (50%) : Viewer PyQtGraph avec rendu avancé
    - Image haute résolution avec effet gris/couleur
    - Détection automatique couleur des prises
    - 3 sliders interactifs (fond, contour, épaisseur)
  - 39 tests unitaires passent
  - Usage : `python3 -m mastock.gui.climb_viewer --name "Nia" --setter "Mathias" --image`

## 2025-12-21

- **TODO 05 créé** - Structure Package Python mastock
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

- **TODO 02 créé** - Conception du schéma SQLite pour mastock
  - Basé sur l'analyse statique de Stōkt
  - Architecture offline-first
  - Statut : À faire (0%)

## 2025-11-10

- **TODO 01 créé** - Analyse et décompilation de l'application d'escalade
  - Objectif : Comprendre le fonctionnement de l'app existante
  - Focus : Système d'images interactives et problèmes offline
  - Statut : En cours (0%)
