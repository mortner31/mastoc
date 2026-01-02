# Backup Données Stokt

Sauvegarde versionnée des données extraites de l'API Stokt.

## Fichiers

| Fichier | Description | Date extraction |
|---------|-------------|-----------------|
| `montoboard_setup.json` | Setup face avec 776 prises (polygones, tapes) | 2025-12-21 |
| `montoboard_ALL_climbs.json` | Tous les climbs (~1017) | 2025-12-20 |
| `montoboard_20251220.json` | Export climbs (format simplifié) | 2025-12-20 |

## Importance

Ces données sont la source de vérité pour :
- Les polygones des prises
- Les lignes de tape (START)
- Les grades et métadonnées des climbs

## Mise à jour

Pour mettre à jour depuis Stokt :
1. Utiliser les scripts dans `mastoc/src/mastoc/tools/`
2. Copier les nouveaux fichiers ici
3. Commiter les changements
