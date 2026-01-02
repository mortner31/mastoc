# TODO 24 - Cartouches de Résultats de Recherche

## Objectif

Refonte des cartes de résultat (ClimbCard) avec un nouveau layout intégrant les pictos générés côté serveur.

## Design

```
┌─────────────────────────────────────────────────────┐
│ ┌──────────┐  ┌──────────────────┐  ┌────────────┐ │
│ │          │  │ Nom du bloc      │  │    6A+     │ │
│ │  PICTO   │  │ par Mathias      │  │            │ │
│ │  (carré) │  │ 15 déc. 2025     │  │ ❤️12  ✕42  │ │
│ └──────────┘  └──────────────────┘  └────────────┘ │
│    25%              50%                 25%        │
└─────────────────────────────────────────────────────┘
```

### Zones

| Zone | Largeur | Contenu |
|------|---------|---------|
| Gauche | 25% | Picto carré du bloc (miniature) |
| Centre | 50% | Titre (bold), Auteur, Date (de haut en bas) |
| Droite | 25% | Grade (haut), Stats (bas) |

### Stats (zone droite bas)

- `❤️ N` : nombre de likes (total_likes)
- `✕ N` : nombre de croix / ascensions (climbed_by)

## Algorithme Picto Python (référence)

Le picto est généré dans `mastoc/src/mastoc/core/picto.py` :

1. **Fond blanc** carré (128x128 ou 48x48)
2. **Top 20 prises populaires** en gris clair (contexte)
3. **Prises du bloc** avec couleur dominante extraite du mur
4. **Marqueurs spéciaux** :
   - TOP : double cercle
   - FEET : contour bleu néon (#31DAFF)
   - START : lignes de tape (V si 1 prise, centrales si plusieurs)
5. **Calcul taille** : rayon proportionnel à l'aire du polygone

### Extraction de couleur (IMPORTANT)

La couleur de chaque prise est extraite via `get_dominant_color()` :

```python
def get_dominant_color(img, centroid, radius=15):
    # Sample pixels autour du centroïde
    # Ignore les pixels gris (max_diff < 30)
    # Quantifie les couleurs (pas de 32)
    # Retourne la couleur la plus fréquente
```

**Contrainte** : nécessite l'image haute résolution du mur (2263x3000).

**Décision : Génération côté CLIENT (Android)**

Raisons :
- Calcul très léger (~1-5 ms par picto)
- Compatible avec les deux backends (Stokt ET mastoc)
- Pas de dépendance réseau supplémentaire
- Cache local possible

**Prérequis** : stocker `color_rgb` dans les données Hold (synchro avec le client)

## Tâches

### Phase 0 : Couleurs des Prises (prérequis)

- [ ] Ajouter colonne `color_rgb VARCHAR(7)` à table `holds` (ex: "#FF5733")
- [ ] Script d'extraction : parcourir l'image du mur et calculer couleur dominante
- [ ] Migration BDD Railway
- [ ] Endpoint `GET /api/holds` retourne la couleur

### Phase 1 : Endpoint Picto Serveur

- [ ] Créer endpoint `GET /api/climbs/{id}/picto` (retourne PNG)
- [ ] Porter logique `picto.py` côté serveur (FastAPI + Pillow)
- [ ] Utiliser `color_rgb` des holds (pas d'image mur)
- [ ] Cache filesystem pour les pictos générés
- [ ] Option taille (`?size=48|96|128`)

### Phase 2 : Android - Nouveau Layout ClimbCard

- [ ] Refactorer `ClimbCard.kt` avec layout Row 25|50|25
- [ ] Zone gauche : `AsyncImage` pour le picto (Coil)
- [ ] Zone centre : Column(titre, auteur, date)
- [ ] Zone droite : Column(GradeBadge, Row(likes, croix))
- [ ] Placeholder pendant chargement picto

### Phase 3 : Génération Picto Android (option B)

Alternative si endpoint serveur trop lourd :
- [ ] Porter `picto.py` en Kotlin (Canvas)
- [ ] Générer les pictos localement sur Android
- [ ] Cache Room ou fichier local

### Phase 4 : Tests et Polish

- [ ] Tests endpoint picto serveur
- [ ] Tests UI Android
- [ ] Gestion erreurs (picto manquant, timeout)
- [ ] Optimisation cache et lazy loading

## Fichiers impactés

### Serveur
- `server/src/mastoc_api/routers/climbs.py` (nouveau endpoint)
- `server/src/mastoc_api/services/picto_service.py` (nouveau)

### Android
- `android/app/src/main/java/com/mastoc/app/ui/components/ClimbCard.kt`

### Python (référence)
- `mastoc/src/mastoc/core/picto.py` (logique à porter)

## Références

- TODO 22 Phase 1 : Cartouche filtres (déjà implémentée)
- `ClimbCard.kt` : layout actuel (vertical, sans picto)
- `picto.py` : algorithme de génération Python
