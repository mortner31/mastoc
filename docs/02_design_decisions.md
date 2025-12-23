# Décisions de Design - mastoc

## Visualisation des Blocs

### Paramètres par Défaut du Viewer
| Paramètre | Valeur | Raison |
|-----------|--------|--------|
| Fond gris | 70% | Bon contraste sans perdre les détails |
| Luminosité max | 66% | Fond suffisamment foncé pour contours blancs |
| Contour blanc | 100% | Maximum de visibilité |
| Épaisseur | 12px | Lisible même zoomé |

### Marqueurs de Prises Spéciales

**Prise de Départ (START)**
- Trait à 45° vers le bas-droite
- Point de départ : milieu du côté bas-droit du polygone
- Même épaisseur que le contour principal

**Prise d'Arrivée (TOP)**
- Double polygone
- Deuxième polygone écarté à 135% depuis le centroïde
- Visible distinctement, pas de "patate"

## Pictos (Miniatures)

### Représentation
- Cercles proportionnels à l'aire des prises
- Couleurs extraites de l'image du mur (centroïde)
- Fond blanc
- Liseré noir sur prises claires (luminance > 180)

### Contexte Visuel
- 20 prises les plus utilisées affichées en gris clair
- Permet de situer le bloc sur le mur
- Non affichées si déjà dans le bloc

### Marqueurs dans Pictos
- START : trait 45° depuis bas-droit du cercle
- TOP : double cercle (cercle extérieur +3px)

### Cache
- Stockage : `~/.mastoc/pictos/`
- Format : PNG
- Noms : hash MD5 du climb_id (12 chars)
- Taille : 48×48 pour la liste

## Filtrage des Blocs

### Grade Min/Max
- Deux sliders indépendants
- Contrainte : min ≤ max
- Grades Fontainebleau : 4 à 8A (17 niveaux)
- Valeurs IRCRA pour le filtrage interne

### Navigation
- Clic : sélectionne et affiche
- Flèches haut/bas : navigation avec mise à jour auto
- Signal `currentItemChanged` utilisé

## Couleurs des Prises

### Extraction
- Échantillonnage autour du centroïde (rayon 15px)
- Ignorer les pixels gris (diff < 30)
- Quantification 32 niveaux par canal
- Couleur dominante = mode statistique

### Détection Couleur Claire
- Luminance = 0.299×R + 0.587×G + 0.114×B
- Claire si luminance > 180
- Ajoute liseré noir pour visibilité
