# Guide d'Ergonomie UI/UX - mastock Android

**Document de reference pour le developpement de l'application Android mastock.**

Design System : **Material Design 3**
Approche : **Mobile-first, Offline-first**
Stack technique : **Jetpack Compose** (recommande)

## References externes

- [Nielsen Norman Group - 10 Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
- [Material Design 3](https://m3.material.io/)
- [M3 Navigation Bar](https://m3.material.io/components/navigation-bar/guidelines)
- [Smashing Magazine - Fitts' Law](https://www.smashingmagazine.com/2022/02/fitts-law-touch-era/)
- [NN/G - Wizards](https://www.nngroup.com/articles/wizards/)

---

## 1. Fondamentaux

### 1.1 Les 10 Heuristiques de Nielsen

| # | Heuristique | Application mastock |
|---|-------------|---------------------|
| 1 | **Visibilite du statut** | Feedback sync API, loading states, progression wizard, badge offline |
| 2 | **Correspondance systeme/monde reel** | Terminologie escalade (grade, setter, TOP, FEET, START) |
| 3 | **Controle utilisateur** | Undo, navigation back, annuler creation, dialog confirmation |
| 4 | **Coherence et standards** | Material Design 3 partout, patterns familiers |
| 5 | **Prevention des erreurs** | Validation avant POST, confirmations actions destructives, autosave brouillon |
| 6 | **Reconnaissance > Rappel** | Chips filtres visibles, options affichees, pictos, stats sociales visibles |
| 7 | **Flexibilite et efficacite** | Boutons d'action rapides, FAB action principale, raccourcis |
| 8 | **Design minimaliste** | Focus sur le mur et les prises, pas de surcharge |
| 9 | **Aide a la recuperation d'erreurs** | Messages clairs, solutions proposees, retry auto, queue offline |
| 10 | **Aide et documentation** | Onboarding, tooltips, aide contextuelle |

### 1.2 Norme ISO 9241 (Utilisabilite)

| Critere | Definition | Objectif mastock |
|---------|------------|------------------|
| **Efficacite** | L'utilisateur atteint son but | Trouver un bloc en < 3 taps |
| **Efficience** | Chemin optimise | Filtrer -> Selectionner -> Voir en 10 secondes |
| **Satisfaction** | Experience agreable | Animations fluides, feedback haptique |

---

## 2. Ergonomie Tactile

### 2.1 Loi de Fitts

> Plus une cible est **grande** et **proche**, plus elle est facile a atteindre.

**Implications :**
- Boutons d'action principaux : grands et accessibles
- Actions secondaires : peuvent etre plus petites
- Actions destructives : petites et eloignees (eviter erreurs)

### 2.2 Zones de Pouce (Thumb Zones)

```
+-------------------------------+
|     Zone rouge (difficile)    |  Eviter actions frequentes
|  Coins superieurs, haut ecran |
+-------------------------------+
|     Zone jaune (etirement)    |  Actions secondaires
|  Bords lateraux, milieu-haut  |
+-------------------------------+
|     Zone verte (naturelle)    |  Actions principales
|  Centre-bas, accessible pouce |  Navigation, FAB, filtres
+-------------------------------+
```

**Regles :**
- Bottom navigation : zone verte (toujours accessible)
- FAB : coin inferieur droit (zone verte)
- Filtres : haut mais accessibles par scroll
- Actions destructives : zone rouge (protection erreurs)

### 2.3 Tailles Minimum Material Design 3

| Element | Taille minimum | Notes |
|---------|---------------|-------|
| Touch target | **48 x 48 dp** | Zone cliquable, pas visuelle |
| Espacement elements | **8 dp** | Entre boutons adjacents |
| FAB standard | **56 dp** | Action principale |
| FAB small | **40 dp** | Actions secondaires |
| Bottom nav height | **80 dp** | Avec labels |
| Bottom nav item width | **80-168 dp** | Min 80dp par item |
| Chips | **32 dp** hauteur | Filtres |

### 2.4 Consideration Doigts Magnesie

> Les grimpeurs ont souvent les doigts pleins de magnesie, ce qui peut causer des taps imprecis.

**Regles specifiques escalade :**
- Eviter les swipes horizontaux pour actions critiques (like)
- Preferer les boutons explicites aux gestes
- Touch targets genereux (56dp+ pour actions importantes)
- Double-tap pour actions irreversibles

---

## 3. Material Design 3

### 3.1 Palette de Composants

| Composant M3 | Usage mastock | Notes |
|--------------|---------------|-------|
| **Navigation Bar** | 5 destinations | Sync, Simple, Avance, Creer, Profil |
| **FAB** | Action principale contextuelle | Creer bloc (modes recherche) |
| **Cards** | Liste des blocs | Elevation, picto, infos |
| **Chips** | Filtres | Grade, setter, selection |
| **Bottom Sheet** | Detail bloc, controles apparence | Drag handle, expandable |
| **Snackbar** | Feedback actions | Like, bookmark, erreurs |
| **Progress Indicator** | Sync, wizard | Linear ou circular |
| **Dialogs** | Confirmations | Actions destructives, interruption wizard |
| **Text Fields** | Formulaires | Nom bloc, commentaires |
| **Badges** | Indicateurs | Mode offline, notifications |

### 3.2 Typographie M3

| Style | Usage | Taille |
|-------|-------|--------|
| Display | Non utilise | - |
| Headline Large | Titre ecran | 32sp |
| Headline Medium | Nom bloc (detail) | 28sp |
| Title Large | Sections | 22sp |
| Title Medium | Nom bloc (liste) | 16sp |
| Body Large | Description, commentaires | 16sp |
| Body Medium | Texte standard | 14sp |
| Label Large | Boutons | 14sp |
| Label Medium | Chips, badges | 12sp |

### 3.3 Espacement

**Regle : multiples de 4dp**

| Usage | Espacement |
|-------|------------|
| Padding cards | 16 dp |
| Marge ecran | 16 dp |
| Entre cards | 8 dp |
| Entre elements dans card | 8 dp |
| Padding boutons | 16 dp horizontal, 8 dp vertical |

### 3.4 Dynamic Color

- Palette adaptative selon theme systeme
- Couleurs primaires derivees du wallpaper (Android 12+)
- Fallback : palette mastock definie (bleu escalade)
- Mode sombre : inversions automatiques

---

## 4. Navigation

### 4.1 Les 5 Modes Principaux

L'application s'organise autour de **5 modes distincts** (conforme M3 : 3-5 destinations max) :

```
+---------------------------------------+
|                                       |
|            [Ecran actif]              |
|                                       |
+---------------------------------------+
|   Sync   Simple  Avance  Creer Profil |
+---------------------------------------+
```

| Mode | Icone | Description |
|------|-------|-------------|
| **Synchronisation** | sync | Recuperation donnees API + generation pictos |
| **Recherche Simple** | list | Parcours des blocs par niveau (scroll vertical) |
| **Recherche Avancee** | search | Recherche par prises (selection sur mur) |
| **Creer** | add | Creation d'un nouveau bloc (wizard) |
| **Profil** | person | Compte, mes blocs, mes likes, mes favoris, parametres |

### 4.2 Comportement par Mode

#### Mode Synchronisation
- Telechargement donnees depuis API
- Generation/regeneration des pictos
- Indicateur progression
- Statut derniere sync
- **Badge offline** si pas de connexion
- Queue des actions en attente

#### Mode Recherche Simple
- **Scroll vertical** pour parcourir les blocs
- Filtrage par niveau (chips ou slider) - **visible par defaut**
- Affichage : Picto + Nom + Grade + Setter + Stats sociales
- **Boutons explicites** pour liker/bookmark (pas de swipe)
- **Stats sociales visibles** par defaut (configurable)
- **Filtres avances depliables** (voir section 4.5)

#### Mode Recherche Avancee
- Affichage mur complet avec prises
- Selection de prises (tap)
- Filtrage resultats par prises selectionnees
- Double slider niveau - **visible par defaut**
- **Modes de coloration** : Min, Max, Frequence, Rarete
- **Filtres avances depliables** (voir section 4.5)
- Basculement vers visualisation bloc
- Bouton **Undo** pour annuler derniere selection

#### Mode Creer
- Wizard 3 etapes (voir section 4.6)
- Etape 1 : Selection des prises
- Etape 2 : Informations bloc (nom, grade, regle pieds)
- Etape 3 : Confirmation et publication
- **Autosave brouillon** entre etapes
- **Dialog confirmation** si interruption

#### Mode Profil
- **Section Compte** : Login/Logout, email, avatar
- **Section Mes donnees** : Mes blocs crees, mes likes, mes favoris, mes ascensions
- **Section Statistiques** : Stats personnelles
- **Section Parametres** : Apparence (social visible/cache), notifications

### 4.3 Navigation dans les Blocs

**Principe : simplicite et precision (doigts magnesie)**

| Geste/Action | Resultat |
|--------------|----------|
| Scroll vertical | Parcourir la liste |
| Tap card | Ouvrir detail bloc |
| Tap bouton coeur | Like/Unlike |
| Tap bouton bookmark | Ajouter/Retirer favoris |
| Tap bouton stats | Afficher panel social complet |
| Bouton Undo (detail) | Annuler derniere action |

**Note :** Les swipes horizontaux sont **evites** pour prevenir les conflits avec la navigation systeme Android et les erreurs de tap avec doigts magnesie.

### 4.4 Aspects Sociaux (Configurable)

**Principe : equilibre entre information et focus**

Par defaut, les stats de base sont **visibles** :
- Nombre de likes (icone + compteur)
- Nombre de commentaires (icone + compteur)

**Panel social complet** (tap sur bouton stats) :
- Ascensions recentes
- Liste des commentaires
- Notes communaute
- Ajouter un commentaire

**Option dans Parametres :**
- "Mode Focus" : cache les stats sociales par defaut

### 4.5 Options Depliables (Progressive Disclosure)

**Principe : montrer l'essentiel, cacher le secondaire**

Les options sont organisees en deux niveaux :
- **Niveau 1 (visible)** : Options principales, toujours affichees
- **Niveau 2 (depliable)** : Options avancees, accessibles via un bouton "Plus"

**Regles de conception :**

| Regle | Description |
|-------|-------------|
| **Icone claire** | v (deplier) / ^ (replier) ou chevron |
| **Animation fluide** | Transition douce (200-300ms) |
| **Etat memorise** | Se souvient si deplie ou non |
| **Accessibilite** | Zone tactile 48dp minimum |
| **Feedback visuel** | Highlight du bouton au tap |

**Options par mode :**

| Mode | Niveau 1 (visible) | Niveau 2 (depliable) |
|------|-------------------|----------------------|
| Recherche Simple | Filtrage niveau | Ouvreur, periode, tri |
| Recherche Avancee | Slider niveau, selection prises, mode coloration | Ouvreur, colormap, luminosite |
| Profil | Tabs (blocs/likes/favoris) | Tri, periode |

### 4.6 Wizard Pattern (Creation bloc)

```
Etape 1/3          Etape 2/3          Etape 3/3
Selection prises   Informations       Confirmation
[*oo]              [**o]              [***]
     ------->           ------->
     <-------           <-------
```

#### Regles fondamentales

| Regle | Implementation |
|-------|----------------|
| Indicateur progression | Barre + etape X/3 toujours visible |
| Retour arriere | Bouton "<- Retour" preserve l'etat |
| Annuler | Dialog "Sauvegarder brouillon ?" |
| Autosave | Brouillon sauvegarde apres chaque etape |
| Validation | Par etape, avant passage suivant |

#### Gestion des interruptions

| Scenario | Comportement |
|----------|--------------|
| **Tap "Annuler"** | Dialog : "Sauvegarder comme brouillon ?" [Oui] [Non] [Annuler] |
| **Back systeme** | Meme dialog que "Annuler" |
| **Home / App switch** | Autosave silencieux du brouillon |
| **Rotation ecran** | Etat preserve via SavedStateHandle |
| **Kill process** | Brouillon recuperable au retour |

#### Validation par etape

| Etape | Validations | Erreur si... |
|-------|-------------|--------------|
| **1 - Prises** | Min 2 START, Min 1 TOP | "Selectionnez au moins 2 prises START" |
| **2 - Infos** | Nom 3-50 chars, Grade selectionne | "Le nom doit contenir 3-50 caracteres" |
| **3 - Confirm** | Aucune (recapitulatif) | - |

#### Gestion des erreurs reseau (etape 3)

| Scenario | Comportement |
|----------|--------------|
| **Erreur POST** | Snackbar "Erreur de publication. [Reessayer]" |
| **Timeout** | Retry automatique (3 tentatives, backoff exponentiel) |
| **Offline** | "Vous etes hors ligne. Le bloc sera publie a la reconnexion." |
| **Succes** | Snackbar "Bloc publie !" + navigation vers detail |

#### Brouillons

- Stockes localement (Room)
- Visibles dans Profil > Mes brouillons
- Expiration : 30 jours
- Suppression : swipe ou bouton

### 4.7 Extensibilite : Navigation Drawer

**Principe : preparer l'ajout de modes supplementaires sans casser la bottom nav**

Material Design 3 limite la bottom navigation a **5 destinations maximum**. Pour ajouter des fonctionnalites futures (jeux, defis, classements, etc.), mastock utilise un **Navigation Drawer** accessible via un menu hamburger.

#### Architecture hybride

```
+---------------------------------------+
| [=] Recherche Simple            [cog] |  <- Hamburger menu
+---------------------------------------+
|                                       |
|            [Contenu principal]        |
|                                       |
+---------------------------------------+
|  Sync  Simple  Avance  Creer  Profil  |  <- 5 modes principaux (bottom nav)
+---------------------------------------+
```

#### Navigation Drawer (modes secondaires)

```
+--------------------+------------------+
| [X] Menu           |                  |
|                    |                  |
| --- PRINCIPAL ---  |                  |
| [sync] Sync        |   [Contenu       |
| [list] Simple      |    principal     |
| [search] Avance    |    grise]        |
| [add] Creer        |                  |
| [person] Profil    |                  |
|                    |                  |
| --- EXTRAS ---     |                  |
| [brush] Brossage   |  <- Modes        |
| [trophy] Defis     |     additionnels |
| [leaderboard] Classement |            |
|                    |                  |
| --- SYSTEME ---    |                  |
| [settings] Parametres |               |
| [help] Aide        |                  |
| [info] A propos    |                  |
+--------------------+------------------+
```

#### Regles de conception

| Regle | Implementation |
|-------|----------------|
| **Acces** | Hamburger [=] en haut a gauche (toutes les pages) |
| **Geste** | Swipe depuis bord gauche (optionnel, peut confliter) |
| **Fermeture** | Tap hors drawer, tap [X], ou back systeme |
| **Largeur** | 80% de l'ecran (max 320dp) |
| **Overlay** | Fond grise a 50% opacite |

#### Hierarchie des destinations

| Niveau | Emplacement | Exemples |
|--------|-------------|----------|
| **Principal** | Bottom Nav (5 max) | Sync, Simple, Avance, Creer, Profil |
| **Secondaire** | Drawer > Extras | Jeux, Defis, Classements |
| **Systeme** | Drawer > Systeme | Parametres, Aide, A propos |

#### Exemple : Mode "Brossage de Prises"

**Concept :** Jeu de gamification ou l'utilisateur gagne des points en brossant les prises sales dans la salle.

**Acces :**
1. Drawer > Extras > Brossage
2. Notification push "Nouvelles prises a brosser !"
3. Badge sur hamburger menu si points a reclamer

**Ecran Brossage :**

```
+---------------------------------------+
| <- Retour       Brossage        [?]   |
+---------------------------------------+
|                                       |
|     [Trophy] Niveau 12                |
|     1250 points                       |
|                                       |
| +-----------------------------------+ |
| | Prises a brosser aujourd'hui : 5  | |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| |      [Image mur]                  | |
| |      Prises sales highlighted     | |
| |      Tap = marquer comme brosse   | |
| +-----------------------------------+ |
|                                       |
| Historique                            |
| - Prise #234 brossee il y a 2h (+10)  |
| - Prise #567 brossee hier (+10)       |
|                                       |
+---------------------------------------+
```

#### Quand promouvoir un mode secondaire ?

| Critere | Action |
|---------|--------|
| Usage > 30% des sessions | Considerer promotion en bottom nav |
| Feature temporaire (event) | Garder dans drawer + banner promo |
| Feature niche | Drawer permanent |
| Feature critique | Bottom nav obligatoire |

**Note :** Si un mode secondaire devient tres populaire, on peut reorganiser la bottom nav (ex: fusionner Simple+Avance) pour lui faire de la place.

---

## 5. Wireframes

### 5.1 Mode Synchronisation

```
+---------------------------------------+
|            Synchronisation            |
+---------------------------------------+
|                                       |
| Derniere sync : il y a 2 heures       |
|                                       |
| +-----------------------------------+ |
| | Donnees locales                   | |
| | - 1017 blocs                      | |
| | - 776 prises                      | |
| | - 892 pictos generes              | |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| | Actions en attente : 3            | |  <- Queue offline
| | - 2 likes                         | |
| | - 1 commentaire                   | |
| +-----------------------------------+ |
|                                       |
|         [Synchroniser]                |
|                                       |
| ------------------------------------- |
|                                       |
| [Regenerer tous les pictos]           |
| (peut prendre plusieurs minutes)      |
|                                       |
| ------------------------------------- |
|                                       |
| Progression sync :                    |
| [============........] 60%            |
| Telechargement blocs...               |
|                                       |
+---------------------------------------+
|  Sync  Simple  Avance  Creer  Profil  |
+---------------------------------------+
```

### 5.2 Mode Recherche Simple

**Vue liste (scroll vertical) :**

```
+---------------------------------------+
| Recherche Simple              [cog]   |
+---------------------------------------+
| Niveau : [4+] [5] [6a] [6b+] [7a] [>] |
+---------------------------------------+
|                                       |
| +-----------------------------------+ |
| |  [Picto]  Bloc "Nia"              | |
| |           6a+ - Mathias           | |
| |                                   | |
| |  [heart] 12   [comment] 3   [bm]  | |  <- Stats visibles
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| |  [Picto]  Bloc "Sunrise"          | |
| |           5+ - Alex               | |
| |                                   | |
| |  [heart] 8    [comment] 1   [bm]  | |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| |  [Picto]  Bloc "Moonlight"        | |
| |           6b+ - Thomas            | |
| |                                   | |
| |  [heart] 24   [comment] 5   [bm]  | |
| +-----------------------------------+ |
|                                       |
| [v Plus de filtres]                   |  <- Depliable
|                                       |
+---------------------------------------+
|  Sync  Simple  Avance  Creer  Profil  |
+---------------------------------------+
```

### 5.3 Mode Recherche Avancee

```
+---------------------------------------+
| Recherche Avancee             [cog]   |
+---------------------------------------+
| Niveau : [4+]----*----*----[8A]       |
| Mode : [Min] [Max] [Freq] [Rare]      |
+---------------------------------------+
|                                       |
| +-----------------------------------+ |
| |                                   | |
| |      [Image mur avec prises]      | |
| |      Prises colorees par mode     | |
| |      Tap = selectionner           | |
| |                                   | |
| |      * Prise selectionnee         | |
| |      o Prise non selectionnee     | |
| |                                   | |
| +-----------------------------------+ |
|                                       |
| Prises selectionnees : 3              |
| Blocs correspondants : 7              |
|                                       |
| [Undo] [Clear]        [Voir blocs ->] |
|                                       |
| [v Plus d'options]                    |  <- Depliable
|                                       |
+---------------------------------------+
|  Sync  Simple  Avance  Creer  Profil  |
+---------------------------------------+
```

### 5.4 Mode Creer - Wizard

**Etape 1/3 : Selection des prises**

```
+---------------------------------------+
| <- Annuler      Creation    Suivant ->|
+---------------------------------------+
| [*oo-----------------------] 1/3      |
|                                       |
| Selectionnez les prises du bloc       |
|                                       |
| +-----------------------------------+ |
| |                                   | |
| |      [Image mur interactive]      | |
| |      Tap = selectionner prise     | |
| |                                   | |
| +-----------------------------------+ |
|                                       |
| Type actif :                          |
| [START] [OTHER] [FEET] [TOP]          |
|                                       |
| Selection : 5 prises                  |
| - 2 START ok  - 2 OTHER  - 1 TOP ok   |
|                                       |
| [Undo]                                |
|                                       |
|           [Suivant ->]                |
+---------------------------------------+
```

**Etape 2/3 : Informations**

```
+---------------------------------------+
| <- Retour       Creation    Suivant ->|
+---------------------------------------+
| [**o-----------------------] 2/3      |
|                                       |
| Informations du bloc                  |
|                                       |
| Nom du bloc *                         |
| +-----------------------------------+ |
| | Ex: "Moonlight"                   | |
| +-----------------------------------+ |
| ! Le nom doit contenir 3-50 car.      |  <- Validation inline
|                                       |
| Grade *                               |
| [4] [5] [5+] [6a] [6a+] [6b] [6b+]...|
|                                       |
| Regle pieds                           |
| ( ) Pieds libres (defaut)             |
| ( ) Pieds sur prises uniquement       |
| ( ) Pieds marques obligatoires        |
|                                       |
| Visibilite                            |
| [Prive] [Public]                      |
|                                       |
|           [Suivant ->]                |
+---------------------------------------+
```

**Etape 3/3 : Confirmation**

```
+---------------------------------------+
| <- Retour       Creation      Publier |
+---------------------------------------+
| [***-----------------------] 3/3      |
|                                       |
| Verifiez votre bloc                   |
|                                       |
| +-----------------------------------+ |
| |       [Apercu du bloc]            | |
| |       Miniature avec prises       | |
| +-----------------------------------+ |
|                                       |
| Nom : Moonlight                       |
| Grade : 6b+                           |
| Pieds : Libres                        |
| Visibilite : Public                   |
|                                       |
| Prises : 7                            |
| - 2 START - 4 OTHER - 1 TOP           |
|                                       |
|    [<- Modifier]     [Publier ->]     |
|                                       |
+---------------------------------------+
```

**Dialog interruption (Annuler / Back) :**

```
+---------------------------------------+
|                                       |
|     Quitter la creation ?             |
|                                       |
|     Votre progression sera perdue     |
|     sauf si vous sauvegardez.         |
|                                       |
| +-----------------------------------+ |
| |        [Sauvegarder brouillon]    | |
| +-----------------------------------+ |
| |        [Quitter sans sauvegarder] | |
| +-----------------------------------+ |
| |        [Continuer]                | |
| +-----------------------------------+ |
|                                       |
+---------------------------------------+
```

### 5.5 Mode Profil

```
+---------------------------------------+
| Profil                          [cog] |
+---------------------------------------+
|                                       |
|           [Avatar]                    |
|         Pierre Martin                 |
|         @pierre_climb                 |
|                                       |
|     [Se deconnecter]                  |
|                                       |
| ------------------------------------- |
|                                       |
| [Mes blocs] [Likes] [Favoris] [Stats] |
|                                       |
| ------------------------------------- |
|                                       |
| Onglet "Mes blocs" (12) :             |
|                                       |
| +-----------------------------------+ |
| | [Picto] Moonlight - 6b+ - 15 dec  | |
| | [heart] 24  [comment] 5           | |
| +-----------------------------------+ |
| +-----------------------------------+ |
| | [Picto] Sunrise - 5+ - 10 dec     | |
| | [heart] 8   [comment] 1           | |
| +-----------------------------------+ |
|                                       |
| Brouillons (1)                        |
| +-----------------------------------+ |
| | [draft] Sans nom - 6a - En cours  | |
| +-----------------------------------+ |
|                                       |
+---------------------------------------+
|  Sync  Simple  Avance  Creer  Profil  |
+---------------------------------------+
```

### 5.6 Detail Bloc

**Etat par defaut (stats visibles) :**

```
+---------------------------------------+
| <- Retour                       [cog] |
+---------------------------------------+
|                                       |
|         [Image mur + prises]          |
|         Zoom/pan enabled              |
|                                       |
+---------------------------------------+
|                                       |
| Bloc "Nia"                            |
| 6a+ - Mathias - 15 decembre 2025      |
|                                       |
| [heart] 12  [bookmark]  [share]       |
|                                       |
| [v Voir ascensions et commentaires]   |
|                                       |
+---------------------------------------+
```

**Panel social deploye :**

```
+---------------------------------------+
| <- Retour                       [cog] |
+---------------------------------------+
|         [Image mur + prises]          |
|         (reduite)                     |
+---------------------------------------+
| ------------------------------------- |  <- Drag handle
|                                       |
| [^ Masquer]                           |
|                                       |
| Ascensions recentes                   |
|                                       |
| Pierre - Flash - il y a 2h            |
| Marie - 3 essais - hier               |
| Thomas - 5 essais - il y a 3j         |
|                                       |
| ------------------------------------- |
| Commentaires (3)                      |
|                                       |
| Alex : "Super bloc !"                 |
| Julie : "Attention au devers"         |
|                                       |
| +-----------------------------------+ |
| | Ajouter un commentaire...         | |
| +-----------------------------------+ |
|                                       |
+---------------------------------------+
```

### 5.7 Bottom Sheet Controles Apparence

```
+---------------------------------------+
| ------------------------------------- |  <- Drag handle
|                                       |
| Apparence                    [Reset]  |
|                                       |
| Luminosite                            |
| [----*-----------------------] 85%    |
|                                       |
| Mode coloration                       |
| [Min] [Max] [Frequence] [Rarete]      |
|                                       |
| Palette                               |
| [viridis v]                           |
| [apercu gradient colormap]            |
|                                       |
| Epaisseur contour                     |
| [--*---------] 2px                    |
|                                       |
+---------------------------------------+
```

---

## 6. Etats et Feedback

### 6.1 Loading States

| Situation | Pattern | Implementation |
|-----------|---------|----------------|
| Chargement liste | Skeleton cards | 3-5 placeholders animes |
| Chargement image | Shimmer | Effet brillance |
| Sync en cours | Progress linear | En haut de l'ecran |
| Action en cours | Circular progress | Sur le bouton |
| Chargement mur | Placeholder + progress | Image basse resolution puis HD |

### 6.2 Etats Vides

```
+-------------------------------+
|                               |
|         [Illustration]        |
|                               |
|      Aucun bloc trouve        |
|                               |
|  Essayez d'autres filtres ou  |
|  creez votre premier bloc !   |
|                               |
|      [Creer un bloc]          |
|                               |
+-------------------------------+
```

### 6.3 Messages d'Erreur

| Type | Pattern | Exemple |
|------|---------|---------|
| Erreur reseau | Snackbar + retry | "Connexion perdue. [Reessayer]" |
| Erreur validation | Inline sous champ | "Nom trop court (min 3 car.)" |
| Erreur serveur | Dialog | "Erreur serveur. Reessayez plus tard." |
| Erreur auth | Redirect | Retour ecran login |
| Mode offline | Banner persistent | "Mode hors ligne - Actions en attente : 3" |

### 6.4 Snackbars (Feedback Actions)

| Action | Message | Duree |
|--------|---------|-------|
| Like | "Bloc aime" | 2s |
| Unlike | "Like retire" | 2s |
| Bookmark | "Ajoute aux favoris" | 2s + [Voir] |
| Comment | "Commentaire publie" | 2s |
| Sync OK | "Synchronisation terminee" | 2s |
| Bloc cree | "Bloc publie !" | 3s + [Voir] |
| Brouillon sauve | "Brouillon sauvegarde" | 2s |
| Action queued | "Action enregistree (hors ligne)" | 3s |

---

## 7. Accessibilite

### 7.1 Contraste WCAG AA

| Element | Ratio minimum |
|---------|---------------|
| Texte normal | 4.5:1 |
| Texte large (>18sp) | 3:1 |
| Composants UI | 3:1 |
| Icones informatives | 3:1 |

### 7.2 Touch Targets

- **Minimum 48x48 dp** pour tous elements interactifs
- **56x56 dp** recommande pour actions principales (like, bookmark)
- Espacement 8dp minimum entre cibles adjacentes
- Zone de tap peut depasser la zone visuelle

### 7.3 Labels et Descriptions

| Element | Requirement |
|---------|-------------|
| Boutons icone | contentDescription obligatoire |
| Images | alt text si informatif |
| Formulaires | labels visibles + hints |
| Etats | annonces vocales (TalkBack) |
| Mode offline | Annonce "Mode hors ligne actif" |

### 7.4 Navigation

- Focus order logique (haut -> bas, gauche -> droite)
- Skip links pour contenu principal
- Actions accessibles sans gestes complexes
- Boutons explicites plutot que swipes

---

## 8. Persistance et Controles d'Apparence

### 8.1 Principe : Coherence des Controles

Tous les controles de modification d'apparence doivent avoir un **look & feel homogene** :

| Controle | Type | Valeurs |
|----------|------|---------|
| Luminosite | Slider horizontal | 10% - 100% |
| Colormap | Dropdown/Picker | viridis, plasma, inferno, magma, cividis, turbo, coolwarm |
| Epaisseur contour | Slider horizontal | 1 - 5 px |
| Mode coloration | Chips/Segmented | Min, Max, Frequence, Rarete |

### 8.2 Persistance des Settings

**Principe : les preferences utilisateur sont sauvegardees entre sessions**

| Categorie | Settings persistes | Stockage |
|-----------|-------------------|----------|
| **Apparence** | Luminosite, colormap, epaisseur, mode | SharedPreferences |
| **Filtres** | Dernier niveau selectionne, ouvreur | SharedPreferences |
| **Selection** | Prises selectionnees (recherche avancee) | Session uniquement |
| **Navigation** | Dernier mode actif, position scroll | SharedPreferences |
| **Preferences** | Mode focus (social cache), notifications | SharedPreferences |
| **Brouillons** | Blocs en cours de creation | Room (SQLite) |
| **Queue offline** | Actions en attente | Room (SQLite) |

**Implementation Android :**
- `SharedPreferences` / `DataStore` pour settings simples
- Room/SQLite pour donnees complexes et queue offline

### 8.3 Reset Independant

**Principe : pouvoir reinitialiser chaque categorie separement**

| Bouton | Action | Confirmation |
|--------|--------|--------------|
| Reset Apparence | Luminosite=85%, colormap=viridis, mode=Min | Non |
| Reset Selection | Vider les prises selectionnees | Non |
| Reset Filtres | Tous niveaux, tous ouvreurs, tout temps | Non |
| Tout reinitialiser | Tous les settings par defaut | Oui (dialog) |

### 8.4 Valeurs par Defaut

| Setting | Valeur par defaut |
|---------|-------------------|
| Luminosite | 85% |
| Colormap | viridis |
| Mode coloration | Min |
| Epaisseur contour | 2 px |
| Niveau min | 4 |
| Niveau max | 8A |
| Ouvreur | Tous |
| Periode | Tout |
| Mode focus | Desactive (social visible) |

### 8.5 Acces aux Controles d'Apparence

Depuis n'importe quel mode avec visualisation du mur :
- Icone [cog] en haut a droite
- Tap -> Bottom Sheet avec controles
- Bouton Reset dans le sheet

---

## 9. Comportement Offline

### 9.1 Principe : Offline-First

> mastock est concu pour fonctionner **sans connexion** dans la salle d'escalade.

**Donnees disponibles offline :**
- Tous les blocs synchronises
- Toutes les prises et coordonnees
- Tous les pictos generes
- Filtres et recherche
- Brouillons de creation

### 9.2 Actions Offline vs Online

| Action | Offline | Online |
|--------|---------|--------|
| Parcourir blocs | OK | OK |
| Filtrer par niveau | OK | OK |
| Recherche par prises | OK | OK |
| Voir detail bloc | OK | OK |
| Like/Unlike | **Queued** | OK |
| Bookmark | **Queued** | OK |
| Commenter | **Queued** | OK |
| Creer bloc | **Queued** | OK |
| Synchroniser | NON | OK |
| Voir stats temps reel | NON | OK |

### 9.3 Queue d'Actions Offline

| Element | Comportement |
|---------|--------------|
| Stockage | Room (SQLite), persiste redemarrage |
| Indicateur | Badge sur icone Sync + compteur |
| Retry | Automatique a la reconnexion |
| Conflits | Last-write-wins (timestamp) |
| Expiration | 7 jours, puis warning |

### 9.4 Indicateurs Visuels Offline

```
+---------------------------------------+
| [!] Mode hors ligne                   |  <- Banner persistent
+---------------------------------------+
|  Sync(3) Simple  Avance  Creer Profil |  <- Badge sur Sync
+---------------------------------------+
```

**Regles d'affichage :**
- Banner jaune en haut si offline
- Badge numerique sur icone Sync (actions en attente)
- Snackbar a chaque action queued

### 9.5 Synchronisation

| Declencheur | Comportement |
|-------------|--------------|
| Retour online | Sync auto des actions queued |
| Tap "Synchroniser" | Sync complete (blocs + actions) |
| Pull-to-refresh | Sync incrementale |
| Background | Sync periodique si WiFi (WorkManager) |

---

## 10. Performance

### 10.1 Donnees a Gerer

| Element | Volume | Strategie |
|---------|--------|-----------|
| Blocs | 1017+ | LazyColumn avec pagination |
| Prises | 776 polygones | Canvas optimise, pas de recomposition |
| Image mur | 2263x3000 (~500KB) | Coil + cache disque + thumbnails |
| Pictos | 1017 miniatures | Cache LRU memoire + disque |

### 10.2 Strategies de Chargement

| Ecran | Strategie |
|-------|-----------|
| Liste blocs | LazyColumn, prefetch 10 items, skeleton loading |
| Image mur | Thumbnail d'abord, puis HD progressive |
| Pictos | Cache memoire (50 items), puis disque |
| Polygones | Pre-calcul au sync, stockage SQLite |

### 10.3 Optimisations Compose

| Technique | Application |
|-----------|-------------|
| `remember` | Calculs couteux (filtres, colormaps) |
| `derivedStateOf` | Compteurs derives (blocs filtres) |
| `LazyColumn` | Listes longues |
| `key()` | Items de liste (ID bloc) |
| Stable classes | Data classes immutables |

### 10.4 Seuils de Performance

| Metrique | Objectif |
|----------|----------|
| Temps demarrage froid | < 2s |
| Scroll 60fps | Pas de jank |
| Tap-to-response | < 100ms |
| Chargement image mur | < 500ms (cache), < 2s (reseau) |
| Sync complete | < 30s pour 1000 blocs |

---

## 11. Gestion Multi-Murs

### 11.1 Concept

> mastock peut gérer **plusieurs murs** (salles d'escalade différentes ou faces distinctes d'une même salle).

**Terminologie :**
- **Mur** : Une face d'escalade avec son image, ses prises et ses blocs
- **Salle** : Un lieu physique pouvant contenir plusieurs murs
- **Mur actif** : Le mur actuellement sélectionné dans l'application

### 11.2 Architecture de Données

```
Salle (Gym)
├── Mur 1 (Face Nord)
│   ├── Image fond
│   ├── Prises (coordonnées)
│   └── Blocs
├── Mur 2 (Face Sud)
│   ├── Image fond
│   ├── Prises
│   └── Blocs
└── Mur 3 (Dévers)
    ├── Image fond
    ├── Prises
    └── Blocs
```

**Isolation des données :**

| Donnée | Scope | Notes |
|--------|-------|-------|
| Prises | Par mur | Coordonnées spécifiques à l'image |
| Blocs | Par mur | Référencent les prises du mur |
| Pictos | Par bloc (donc par mur) | Générés à partir de l'image du mur |
| Likes/Favoris | Par utilisateur, globaux | Peuvent traverser les murs |
| Brouillons | Par mur | Liés aux prises du mur |
| Settings apparence | Globaux | Même config sur tous les murs |

### 11.3 Sélection du Mur

#### Option A : Sélecteur dans la Top Bar (Recommandé)

```
+---------------------------------------+
| [=] [v Arkose Nation ▼]         [cog] |  <- Dropdown sélecteur mur
+---------------------------------------+
|                                       |
|            [Contenu actif]            |
|                                       |
+---------------------------------------+
|  Sync  Simple  Avance  Creer  Profil  |
+---------------------------------------+
```

**Comportement dropdown :**
- Tap -> Liste des murs disponibles
- Mur actif coché
- Indicateur sync (badge si données obsolètes)
- Option "Gérer mes murs" en bas

#### Option B : Dans le Navigation Drawer

```
+--------------------+------------------+
| [X] Menu           |                  |
|                    |                  |
| --- MUR ACTIF ---  |                  |
| [v] Arkose Nation  |                  |
|     Face Nord      |                  |
|                    |                  |
| [ ] Arkose Nation  |                  |
|     Face Sud       |                  |
| [ ] Climb Up       |   [Contenu       |
|     Mur Principal  |    principal     |
|                    |    grisé]        |
| [+ Ajouter un mur] |                  |
|                    |                  |
| --- PRINCIPAL ---  |                  |
| ...                |                  |
+--------------------+------------------+
```

#### Option C : Écran dédié au démarrage

```
+---------------------------------------+
|           Choisir un mur              |
+---------------------------------------+
|                                       |
| +-----------------------------------+ |
| | [Thumbnail]                       | |
| | Arkose Nation - Face Nord         | |
| | 324 blocs · Sync il y a 2h        | |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| | [Thumbnail]                       | |
| | Arkose Nation - Face Sud          | |
| | 156 blocs · Sync il y a 1j        | |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| | [+] Ajouter un nouveau mur        | |
| +-----------------------------------+ |
|                                       |
| [v] Toujours démarrer sur ce mur     |
|                                       |
+---------------------------------------+
```

### 11.4 Ajout d'un Nouveau Mur

**Wizard d'ajout (3 étapes) :**

```
Étape 1/3          Étape 2/3          Étape 3/3
Identifier salle   Choisir face       Synchroniser
[*oo]              [**o]              [***]
```

**Étape 1 : Identifier la salle**
```
+---------------------------------------+
| <- Annuler    Nouveau mur   Suivant ->|
+---------------------------------------+
| [*oo-----------------------] 1/3      |
|                                       |
| Comment voulez-vous ajouter ce mur ?  |
|                                       |
| +-----------------------------------+ |
| | [QR] Scanner le QR code           | |
| |     (affiché dans la salle)       | |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| | [search] Rechercher une salle     | |
| |          Par nom ou ville         | |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| | [link] Entrer un code d'accès     | |
| |        (fourni par la salle)      | |
| +-----------------------------------+ |
|                                       |
+---------------------------------------+
```

**Étape 2 : Choisir la face**
```
+---------------------------------------+
| <- Retour     Nouveau mur   Suivant ->|
+---------------------------------------+
| [**o-----------------------] 2/3      |
|                                       |
| Arkose Nation - Paris 15              |
| 3 faces disponibles                   |
|                                       |
| +-----------------------------------+ |
| | [Thumbnail] Face Nord             | |
| | 324 blocs · 245 prises            | |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| | [Thumbnail] Face Sud              | |
| | 156 blocs · 180 prises            | |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| | [Thumbnail] Dévers                | |
| | 89 blocs · 120 prises             | |
| +-----------------------------------+ |
|                                       |
|           [Tout sélectionner]         |
|                                       |
+---------------------------------------+
```

**Étape 3 : Synchronisation initiale**
```
+---------------------------------------+
| <- Retour     Nouveau mur    Terminer |
+---------------------------------------+
| [***-----------------------] 3/3      |
|                                       |
| Synchronisation en cours...           |
|                                       |
| Face Nord                             |
| [============........] 60%            |
| Téléchargement des prises...          |
|                                       |
| Face Sud                              |
| [....................] En attente     |
|                                       |
| Estimation : 2 min restantes          |
|                                       |
| +-----------------------------------+ |
| | [i] La synchronisation peut       | |
| |     continuer en arrière-plan     | |
| +-----------------------------------+ |
|                                       |
|      [Continuer en arrière-plan]      |
|                                       |
+---------------------------------------+
```

### 11.5 Indicateur Mur Actif

**Règle : l'utilisateur doit toujours savoir sur quel mur il travaille**

| Élément | Emplacement | Information |
|---------|-------------|-------------|
| **Nom du mur** | Top bar (centre ou dropdown) | "Arkose Nation - Nord" |
| **Badge sync** | À côté du nom | Point orange si données > 24h |
| **Thumbnail** | Drawer / Sélecteur | Miniature du mur |

### 11.6 Synchronisation Multi-Murs

#### Stratégies

| Stratégie | Description | Recommandation |
|-----------|-------------|----------------|
| **Sync mur actif uniquement** | Économise data/batterie | Par défaut |
| **Sync tous les murs** | Toutes données à jour | Option manuelle |
| **Sync intelligente** | Murs visités < 7j | Background WiFi |

#### Écran Sync mis à jour

```
+---------------------------------------+
|            Synchronisation            |
+---------------------------------------+
|                                       |
| Mur actif : Arkose Nation - Nord      |
| Dernière sync : il y a 2 heures       |
|                                       |
|         [Synchroniser ce mur]         |
|                                       |
| ------------------------------------- |
|                                       |
| Autres murs :                         |
|                                       |
| +-----------------------------------+ |
| | Arkose Nation - Sud               | |
| | Sync : il y a 3 jours    [Sync]   | |
| +-----------------------------------+ |
| +-----------------------------------+ |
| | Climb Up - Principal              | |
| | Sync : il y a 1 semaine  [Sync]   | |
| +-----------------------------------+ |
|                                       |
| ------------------------------------- |
|                                       |
| [Synchroniser tous les murs]          |
| (WiFi recommandé)                     |
|                                       |
| Espace utilisé : 156 MB               |
| [Gérer le stockage]                   |
|                                       |
+---------------------------------------+
|  Sync  Simple  Avance  Creer  Profil  |
+---------------------------------------+
```

### 11.7 Gestion du Stockage

```
+---------------------------------------+
|         Gestion du stockage           |
+---------------------------------------+
|                                       |
| Espace total : 156 MB                 |
|                                       |
| +-----------------------------------+ |
| | Arkose Nation - Nord              | |
| | 45 MB · 324 blocs · 892 pictos    | |
| |            [Supprimer les données]| |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| | Arkose Nation - Sud               | |
| | 28 MB · 156 blocs · 456 pictos    | |
| |            [Supprimer les données]| |
| +-----------------------------------+ |
|                                       |
| +-----------------------------------+ |
| | Climb Up - Principal              | |
| | 83 MB · 537 blocs · 1200 pictos   | |
| |            [Supprimer les données]| |
| +-----------------------------------+ |
|                                       |
| Options :                             |
| [ ] Supprimer les pictos > 30 jours   |
| [ ] Garder uniquement le mur actif    |
|                                       |
+---------------------------------------+
```

### 11.8 Comportement Offline Multi-Murs

| Scénario | Comportement |
|----------|--------------|
| Mur actif non synchronisé | Banner "Aucune donnée. Connectez-vous pour synchroniser." |
| Changement de mur offline | OK si données locales existent |
| Action sur autre mur offline | Queue spécifique au mur |
| Sync au retour online | Prioriser le mur actif |

### 11.9 Profil Multi-Murs

Le profil affiche les données **agrégées** ou **filtrées par mur** :

```
+---------------------------------------+
| Profil                          [cog] |
+---------------------------------------+
|           [Avatar]                    |
|         Pierre Martin                 |
|                                       |
| Filtrer par mur :                     |
| [Tous] [Arkose Nord] [Arkose Sud] ... |
|                                       |
| ------------------------------------- |
|                                       |
| [Mes blocs] [Likes] [Favoris] [Stats] |
|                                       |
| Mes blocs (47 au total) :             |
|                                       |
| -- Arkose Nation - Nord (32) --       |
| +-----------------------------------+ |
| | [Picto] Moonlight - 6b+           | |
| +-----------------------------------+ |
|                                       |
| -- Arkose Nation - Sud (15) --        |
| +-----------------------------------+ |
| | [Picto] Sunset - 6a               | |
| +-----------------------------------+ |
|                                       |
+---------------------------------------+
```

### 11.10 Considérations Techniques

| Aspect | Implémentation |
|--------|----------------|
| **Base de données** | Une DB Room avec tables préfixées par gym_id + wall_id |
| **API** | Endpoints paramétrés par wall_id |
| **Cache images** | Dossiers séparés par mur |
| **Pictos** | Générés et stockés par mur |
| **Migration** | Script pour ajouter wall_id aux tables existantes |

### 11.11 Cas Particuliers

| Cas | Gestion |
|-----|---------|
| **Salle avec 1 seul mur** | Pas de sélecteur visible, comportement actuel |
| **Mur supprimé côté serveur** | Notification + option archiver local ou supprimer |
| **Nouveau mur ajouté à une salle** | Notification + option sync |
| **Transfert de bloc entre murs** | Non supporté (prises différentes) |
| **Fusion de murs** | Admin seulement, migration côté serveur |

---

## 12. Roadmap des Features

### Phase 0 (MVP)

- [ ] Navigation 5 tabs
- [ ] Recherche Simple (liste + filtres niveau)
- [ ] Recherche Avancee (selection prises, mode Min)
- [ ] Detail bloc
- [ ] Sync basique
- [ ] Profil (login, mes blocs)
- [ ] Mode offline (consultation)

### Phase 1

- [ ] Wizard creation bloc complet
- [ ] Like/Bookmark avec queue offline
- [ ] 4 modes coloration (Min, Max, Freq, Rarete)
- [ ] 7 colormaps
- [ ] Panel social complet

### Phase 2

- [ ] Commentaires
- [ ] Statistiques personnelles
- [ ] Filtres avances (ouvreur, periode)
- [ ] Brouillons
- [ ] Notifications

---

## 13. Checklist Pre-Implementation

Avant chaque nouvel ecran, verifier :

- [ ] Respect zones de pouce (actions principales en bas)
- [ ] Touch targets >= 48dp (56dp pour actions principales)
- [ ] Espacement multiples de 4dp
- [ ] Composants M3 standards utilises
- [ ] Loading state defini
- [ ] Etat vide defini
- [ ] Etat offline defini
- [ ] Messages erreur prevus
- [ ] Feedback actions (snackbars)
- [ ] Contraste WCAG AA
- [ ] Labels accessibilite
- [ ] Settings persistables identifies
- [ ] Boutons Reset disponibles si applicable
- [ ] Controles d'apparence homogenes
- [ ] Performance : pas de jank au scroll

---

**Version** : 2.2
**Date** : 2025-12-23
**Changelog** :
- v2.2 : Gestion Multi-Murs
  - Section 11 : Architecture multi-murs complete
  - Hierarchie Salle > Mur > Blocs
  - 3 options de selection du mur (top bar, drawer, ecran dedie)
  - Wizard d'ajout de mur (QR code, recherche, code acces)
  - Synchronisation par mur avec strategies
  - Gestion du stockage multi-murs
  - Comportement offline adapte
  - Profil avec filtrage par mur
  - Considerations techniques (DB, API, cache)
- v2.1 : Extensibilite navigation
  - Section 4.7 : Navigation Drawer pour modes supplementaires (6+ destinations)
  - Architecture hybride bottom nav + drawer
  - Exemple mode "Brossage de Prises" (gamification)
  - Regles de promotion modes secondaires -> principaux
- v2.0 : Corrections suite analyse critique
  - Navigation reduite de 6 a 5 destinations (fusion Compte+Moi -> Profil)
  - Wizard detaille (interruptions, erreurs, autosave, brouillons)
  - Social configurable (visible par defaut, option Mode Focus)
  - Swipes horizontaux remplaces par boutons explicites
  - Section Offline complete (queue, indicateurs, sync)
  - Section Performance ajoutee
  - Roadmap features (Phase 0/1/2)
  - Stack technique specifie (Jetpack Compose)
