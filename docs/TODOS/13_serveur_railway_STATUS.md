# STATUS - TODO 13 : Serveur Railway

**Progression** : 70%

---

## Phase 1 : Structure de base (100%)

- [x] pyproject.toml
- [x] config.py
- [x] database.py
- [x] Modèles SQLAlchemy (7 fichiers)
- [x] Routers (4 fichiers)
- [x] main.py
- [x] README.md

## Phase 2 : Déploiement Railway (100%)

- [x] Projet Railway connecté au repo GitHub
- [x] PostgreSQL Railway configuré
- [x] Variable DATABASE_URL partagée
- [x] Domaine public généré
- [x] API en ligne et fonctionnelle

## Phase 3 : Script d'import (0%)

- [ ] init_from_stokt.py
- [ ] Import gym/faces/holds
- [ ] Import climbs
- [ ] Duplication images

## Phase 4 : Intégration client (0%)

- [ ] Modifier client mastoc pour utiliser Railway
- [ ] Tests end-to-end

---

## URL Production

https://mastoc-production.up.railway.app

## Notes

### Session 2025-12-30 (suite)

**Travail effectué :**
- Finalisation main.py (app FastAPI)
- Création README serveur avec doc Railway
- Création Procfile + requirements.txt
- Déploiement Railway réussi
- PostgreSQL connecté et fonctionnel

**Problèmes résolus :**
- `uvicorn: command not found` → ajout requirements.txt
- Module non trouvé → ajout PYTHONPATH=src dans Procfile

### Prochaine session

1. Créer script `init_from_stokt.py`
2. Importer données Montoboard
3. Mettre à jour client mastoc
