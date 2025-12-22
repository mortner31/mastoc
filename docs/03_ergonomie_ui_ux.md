# Guide d'Ergonomie UI/UX - mastock Android

**Document de reference pour le developpement de l'application Android mastock.**

Design System : **Material Design 3**
Approche : **Mobile-first**

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
| 1 | **Visibilite du statut** | Feedback sync API, loading states, progression wizard |
| 2 | **Correspondance systeme/monde reel** | Terminologie escalade (grade, setter, TOP, FEET, START) |
| 3 | **Controle utilisateur** | Undo, navigation back, annuler creation, swipe dismiss |
| 4 | **Coherence et standards** | Material Design 3 partout, patterns familiers |
| 5 | **Prevention des erreurs** | Validation avant POST, confirmations actions destructives |
| 6 | **Reconnaissance > Rappel** | Chips filtres visibles, options affichees, pictos |
| 7 | **Flexibilite et efficacite** | Gestes rapides, FAB action principale, raccourcis |
| 8 | **Design minimaliste** | Focus sur le mur et les prises, pas de surcharge |
| 9 | **Aide a la recuperation d'erreurs** | Messages clairs, solutions proposees, retry auto |
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
| Chips | **32 dp** hauteur | Filtres |

---

## 3. Material Design 3

### 3.1 Palette de Composants

| Composant M3 | Usage mastock | Notes |
|--------------|---------------|-------|
| **Navigation Bar** | 6 destinations | Compte, Sync, Simple, Avance, Creer, Moi |
| **FAB** | Action principale | Creer bloc, Sync |
| **Cards** | Liste des blocs | Elevation, picto, infos |
| **Chips** | Filtres | Grade, setter, selection |
| **Bottom Sheet** | Detail bloc | Drag handle, expandable |
| **Snackbar** | Feedback actions | Like, bookmark, erreurs |
| **Progress Indicator** | Sync, wizard | Linear ou circular |
| **Dialogs** | Confirmations | Actions destructives |
| **Text Fields** | Formulaires | Nom bloc, commentaires |

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

### 4.1 Les 6 Modes Principaux

L'application s'organise autour de **6 modes distincts** :

```
+---------------------------------------+
|                                       |
|            [Ecran actif]              |
|                                       |
+---------------------------------------+
|  U+1F510  U+1F504  U+1F4CA  U+1F50D  +  U+1F464       |
| Compte Sync Simple Avance Creer Moi   |
+---------------------------------------+
```

| Mode | Icone | Description |
|------|-------|-------------|
| **Connexion** | U+1F510 | Gestion du compte (login, logout, profil) |
| **Synchronisation** | U+1F504 | Recuperation donnees API + generation pictos |
| **Recherche Simple** | U+1F4CA | Parcours des blocs par niveau (scroll vertical) |
| **Recherche Avancee** | U+1F50D | Recherche par prises (selection sur mur) |
| **Creer** | + | Creation d'un nouveau bloc (wizard) |
| **Moi** | U+1F464 | Mes blocs crees, mes likes, mes favoris |

### 4.2 Comportement par Mode

#### Mode Connexion
- Login / Logout
- Affichage profil utilisateur
- Parametres compte

#### Mode Synchronisation
- Telechargement donnees depuis API
- Generation/regeneration des pictos
- Indicateur progression
- Statut derniere sync

#### Mode Recherche Simple
- **Scroll vertical** pour parcourir les blocs
- Filtrage par niveau (chips ou slider) - **visible par defaut**
- Affichage : Picto + Nom + Grade + Setter
- **Swipe lateral** ou tap pour liker
- **Aspects sociaux caches** par defaut (tap pour reveler)
- **Filtres avances depliables** (voir section 4.6)

#### Mode Recherche Avancee
- Affichage mur complet avec prises
- Selection de prises (tap)
- Filtrage resultats par prises selectionnees
- Double slider niveau - **visible par defaut**
- **Filtres avances depliables** (voir section 4.6)
- Basculement vers visualisation bloc

#### Mode Creer
- Wizard 3 etapes (voir section 4.7)
- Etape 1 : Selection des prises
- Etape 2 : Informations bloc (nom, grade, regle pieds)
- Etape 3 : Confirmation et publication

#### Mode Moi
- Mes blocs crees
- Mes blocs likes
- Mes favoris (bookmarks)
- Mes ascensions
- Statistiques personnelles

### 4.3 Navigation dans les Blocs

**Principe : simplicite et fluidite**

| Geste | Action |
|-------|--------|
| Swipe haut | Bloc suivant |
| Swipe bas | Bloc precedent |
| Swipe droite | Like (avec animation coeur) |
| Swipe gauche | Passer / Ignorer |
| Tap image | Zoom/details |
| Tap icone social | Reveler infos sociales |

### 4.4 Aspects Sociaux (Caches par Defaut)

**Principe : focus sur l'escalade, pas le social**

Les informations sociales sont **cachees par defaut** :
- Nombre de likes
- Nombre de commentaires
- Ascensions recentes
- Notes communaute

**Pour les reveler :**
- Tap sur une icone discrete (i)
- Le panel social apparait en overlay ou bottom sheet
- Se ferme automatiquement ou par swipe down

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
| Recherche Avancee | Slider niveau, selection prises | Ouvreur, couleur prises |
| Moi | Tabs (blocs/likes/favoris) | Tri, periode |

### 4.6 Wizard Pattern (Creation bloc)

```
Etape 1/3          Etape 2/3          Etape 3/3
Selection prises   Informations       Confirmation
[*oo]              [**o]              [***]
     ------->           ------->
     <-------           <-------
```

**Regles wizard :**
- Indicateur progression visible
- Retour arriere possible
- Validation par etape
- Bouton "Annuler" toujours accessible
- Sauvegarde brouillon optionnelle

---

## 5. Wireframes

### 5.1 Mode Connexion

```
+---------------------------------------+
|                                       |
|              mastock                  |
|                                       |
|         [Logo Montoboard]             |
|                                       |
| +-----------------------------------+ |
| | Email                             | |
| +-----------------------------------+ |
| +-----------------------------------+ |
| | Mot de passe                      | |
| +-----------------------------------+ |
|                                       |
|         [Se connecter]                |
|                                       |
| ------------------------------------- |
|                                       |
| Connecte en tant que :                |
| Pierre Martin (@pierre_climb)         |
|                                       |
| [Deconnexion]      [Parametres]       |
|                                       |
+---------------------------------------+
| Compte Sync Simple Avance Creer Moi   |
+---------------------------------------+
```

### 5.2 Mode Synchronisation

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
| ------------------------------------- |
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
| Compte Sync Simple Avance Creer Moi   |
+---------------------------------------+
```

### 5.3 Mode Recherche Simple

**Vue liste (scroll vertical) :**

```
+---------------------------------------+
| Recherche Simple                      |
+---------------------------------------+
| Niveau : [4+] [5] [6a] [6b+] [7a] [>] |
+---------------------------------------+
|                  ^                    |  <- Swipe haut = suivant
| +-----------------------------------+ |
| |                                   | |
| |         [Picto bloc]              | |
| |                                   | |
| |  Bloc "Nia"                       | |
| |  6a+ - Mathias               [i]  | |  <- Social cache
| |                                   | |
| |        <- Swipe = Like ->         | |
| |                                   | |
| +-----------------------------------+ |
|                  v                    |  <- Swipe bas = precedent
|                                       |
| Bloc 12 / 156                         |
|                                       |
+---------------------------------------+
| Compte Sync Simple Avance Creer Moi   |
+---------------------------------------+
```

### 5.4 Mode Recherche Avancee

```
+---------------------------------------+
| Recherche Avancee                     |
+---------------------------------------+
| Niveau : [4+]----*----*----[8A]       |
|                                       |
| +-----------------------------------+ |
| |                                   | |
| |      [Image mur avec prises]      | |
| |      Prises colorees par niveau   | |
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
+---------------------------------------+
| Compte Sync Simple Avance Creer Moi   |
+---------------------------------------+
```

### 5.5 Mode Creer - Wizard

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
| ! Minimum 2 prises START requises     |
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
|                                       |
| Grade                                 |
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
| [***] 3/3                             |
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
|    [Modifier]        [Publier ok]     |
|                                       |
+---------------------------------------+
```

### 5.6 Mode Moi

```
+---------------------------------------+
| Moi                             [cog] |
+---------------------------------------+
|                                       |
|           [Avatar]                    |
|         Pierre Martin                 |
|                                       |
| ------------------------------------- |
|                                       |
| [Mes blocs]  [Mes likes]  [Favoris]   |
|                                       |
| ------------------------------------- |
|                                       |
| Onglet "Mes blocs" (12) :             |
|                                       |
| +-----------------------------------+ |
| | [Picto] Moonlight - 6b+ - 15 dec  | |
| +-----------------------------------+ |
| +-----------------------------------+ |
| | [Picto] Sunrise - 5+ - 10 dec     | |
| +-----------------------------------+ |
|                                       |
+---------------------------------------+
| Compte Sync Simple Avance Creer Moi   |
+---------------------------------------+
```

### 5.7 Detail Bloc

**Etat initial (social cache) :**

```
+---------------------------------------+
| <- Retour                             |
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
| [heart]  [bookmark]             [i]   |
| Like     Save                  Social |
|                                       |
+---------------------------------------+
```

**Apres tap sur [i] (panel social revele) :**

```
+---------------------------------------+
| <- Retour                             |
+---------------------------------------+
|         [Image mur + prises]          |
|         (reduite)                     |
+---------------------------------------+
| ------------------------------------- |  <- Drag handle
|                                       |
| Bloc "Nia" - 6a+ - Mathias            |
|                                       |
| 12 likes  3 commentaires              |
|                                       |
| ------------------------------------- |
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
| [Ajouter un commentaire...]           |
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

### 6.4 Snackbars (Feedback Actions)

| Action | Message | Duree |
|--------|---------|-------|
| Like | "Bloc aime" | 2s |
| Unlike | "Like retire" | 2s |
| Bookmark | "Ajoute aux favoris" | 2s + [Voir] |
| Comment | "Commentaire publie" | 2s |
| Sync OK | "Synchronisation terminee" | 2s |
| Bloc cree | "Bloc publie !" | 3s + [Voir] |

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
- Espacement 8dp minimum entre cibles adjacentes
- Zone de tap peut depasser la zone visuelle

### 7.3 Labels et Descriptions

| Element | Requirement |
|---------|-------------|
| Boutons icone | contentDescription obligatoire |
| Images | alt text si informatif |
| Formulaires | labels visibles + hints |
| Etats | annonces vocales (TalkBack/VoiceOver) |

### 7.4 Navigation

- Focus order logique (haut -> bas, gauche -> droite)
- Skip links pour contenu principal
- Gestes alternatifs pour swipe actions

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
| **Apparence** | Luminosite, colormap, epaisseur, mode | Local (SharedPreferences) |
| **Filtres** | Dernier niveau selectionne, ouvreur | Local |
| **Selection** | Prises selectionnees (recherche avancee) | Session uniquement |
| **Navigation** | Dernier mode actif, position scroll | Local |

**Implementation Android :**
- `SharedPreferences` pour settings simples
- Room/SQLite pour donnees complexes

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

### 8.5 Acces aux Controles d'Apparence

Depuis n'importe quel mode avec visualisation du mur :
- Icone [cog] en haut a droite
- Tap -> Bottom Sheet avec controles
- Bouton Reset dans le sheet

---

## Checklist Pre-Implementation

Avant chaque nouvel ecran, verifier :

- [ ] Respect zones de pouce (actions principales en bas)
- [ ] Touch targets >= 48dp
- [ ] Espacement multiples de 4dp
- [ ] Composants M3 standards utilises
- [ ] Loading state defini
- [ ] Etat vide defini
- [ ] Messages erreur prevus
- [ ] Feedback actions (snackbars)
- [ ] Contraste WCAG AA
- [ ] Labels accessibilite
- [ ] Settings persistables identifies
- [ ] Boutons Reset disponibles si applicable
- [ ] Controles d'apparence homogenes

---

**Version** : 1.0
**Date** : 2025-12-22
