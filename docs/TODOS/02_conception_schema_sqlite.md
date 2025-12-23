# TODO 02 - Conception du Schéma SQLite pour mastoc

## 🎯 Objectif

Concevoir une base de données SQLite offline-first pour l'application mastoc, basée sur l'analyse de l'application Stōkt.

---

## 📋 Tâches

### Phase 1 : Analyse des entités
- [ ] Identifier toutes les entités métier (gyms, walls, climbs, holds, etc.)
- [ ] Définir les relations entre entités
- [ ] Lister les attributs de chaque entité

### Phase 2 : Conception du schéma
- [ ] Créer le diagramme entité-relation
- [ ] Définir les tables SQL
- [ ] Définir les index pour les performances
- [ ] Gérer la synchronisation (timestamps, flags dirty)

### Phase 3 : Données de test
- [ ] Créer des données mock réalistes
- [ ] Importer des exemples de blocs
- [ ] Tester les requêtes courantes

### Phase 4 : Documentation
- [ ] Documenter le schéma final
- [ ] Créer le script de création des tables

---

## 📚 Références

### Entités identifiées dans l'analyse

| Entité | Description | Source |
|--------|-------------|--------|
| `gyms` | Salles d'escalade | `/api/gyms/` |
| `walls` | Murs dans une salle | `/api/walls/` |
| `faces` | Images des murs (photos) | `/api/faces/` |
| `climbs` | Blocs/problèmes | `/api/climbs/` |
| `holds` | Prises avec coordonnées X/Y | Redux actions |
| `efforts` | Tentatives/envois | `/api/efforts/` |
| `users` | Utilisateurs | `/api/user/` |
| `lists` | Listes personnalisées | `/api/lists/` |
| `ratings` | Notes des blocs | `/api/ratings/` |

### Actions Redux pertinentes
- `stokt-app/myGym/` - Gestion salle active
- `stokt-app/problem/` - Gestion des blocs
- `stokt-app/problemCreation/` - Création de blocs
- `stokt-app/lists/` - Listes personnalisées

### Système de prises
- Coordonnées : X/Y absolues sur l'image
- Types : `start`, `finish`, `foot`, `other`, `circuit`
- Limite : 1500 prises/mur, 600 prises/bloc

---

## 💡 Points d'attention

1. **Offline-first** : Toutes les données doivent être accessibles sans connexion
2. **Images** : Stocker les images localement (cache)
3. **Synchronisation** : Prévoir les champs pour sync future (created_at, updated_at, synced)
4. **Performance** : Index sur les recherches fréquentes (gym_id, wall_id)

---

## 📁 Fichiers à créer

- `/mastoc/database/schema.sql` - Script de création
- `/mastoc/database/migrations/` - Migrations futures
- `/docs/03_schema_database.md` - Documentation du schéma
