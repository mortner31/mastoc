# Rapport de Session - TODO 17 Authentification

**Date** : 2025-12-31

## Objectifs Atteints

- [x] TODO 17 complété à 100% (7 phases)
- [x] Migration DB Railway exécutée avec succès
- [x] Serveur local testé et fonctionnel

## Travail Réalisé

### Phase 1 : Extension Modèle User
- Ajout champs : email, username, password_hash, is_active, role
- Timestamps : updated_at, last_login_at
- Reset password : reset_token, reset_token_expires
- Enum `UserRole` (user/admin)

### Phase 2 : Endpoints Auth
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion (OAuth2 form)
- `POST /api/auth/refresh` - Renouvellement token
- `POST /api/auth/logout` - Déconnexion
- `POST /api/auth/reset-password` - Demande reset
- `POST /api/auth/reset-password/confirm` - Confirmation reset

### Phase 3 : Endpoints Users
- `GET /api/users/me` - Profil connecté
- `PATCH /api/users/me` - Modifier profil
- `POST /api/users/me/password` - Changer mot de passe
- `POST /api/users/me/avatar` - Upload avatar
- `GET /api/users/{id}` - Profil public
- `GET /api/users` - Liste (admin)

### Phase 4 : Middleware JWT
- `security.py` : hashing bcrypt + JWT (python-jose)
- `dependencies.py` : get_current_user, coexistence API Key + JWT
- `AuthenticatedUser` : abstraction user JWT ou API Key

### Phase 5 : Client AuthManager
- `mastoc/core/auth.py` : login, register, refresh, logout
- Persistance tokens dans `~/.mastoc/auth.json`
- Auto-refresh avant expiration
- Intégration MastocAPI

### Phase 6 : Client UI
- `MastocLoginDialog` : connexion + inscription
- `ProfileDialog` : profil + changer mot de passe
- `PasswordResetDialog` : mot de passe oublié

### Phase 7 : Traçabilité
- `created_by_id`, `updated_by_id`, `updated_at` sur Climb
- Injection automatique lors CRUD
- Permissions suppression (créateur ou admin)

## Migration DB Railway

```bash
cd /media/veracrypt1/Repositories/mastock/server
PYTHONPATH=src python scripts/migrate_user_auth.py
```

Résultat : 14 OK, 0 skipped, 0 errors

## Problèmes Résolus

1. **Conflit SQLAlchemy relations** : plusieurs FK vers User dans Climb
   - Solution : `foreign_keys="[Climb.setter_id]"` explicite

2. **Script migration** : ordre incorrect (index avant colonnes)
   - Solution : liste ordonnée + commit individuel par requête

3. **Dépendances manquantes** : email-validator
   - Solution : `pip install email-validator`

## Fichiers Créés

### Serveur
```
server/
├── .env                                # DATABASE_URL Railway
├── scripts/migrate_user_auth.py        # Script migration
└── src/mastoc_api/
    ├── security.py                     # JWT + hashing
    ├── dependencies.py                 # get_current_user
    └── routers/
        ├── auth.py                     # register, login, etc.
        └── users.py                    # profil, avatar
```

### Client
```
mastoc/src/mastoc/
├── core/auth.py                        # AuthManager
└── gui/dialogs/mastoc_auth.py          # Dialogs PyQt6
```

## Comment Lancer

### Serveur local (avec DB Railway)

```bash
cd /media/veracrypt1/Repositories/mastock/server

# Installer dépendances
pip install -r requirements.txt
pip install email-validator

# Créer .env avec DATABASE_URL Railway
echo 'DATABASE_URL=postgresql://...' > .env

# Lancer
PYTHONPATH=src python -m uvicorn mastoc_api.main:app --reload --port 8000

# Swagger UI : http://localhost:8000/docs
```

### Tester l'auth

1. Ouvrir http://localhost:8000/docs
2. `POST /api/auth/register` avec email/username/password/full_name
3. `POST /api/auth/login` avec credentials
4. Copier `access_token` de la réponse
5. Cliquer **Authorize** (cadenas), coller le token
6. `GET /api/users/me` retourne le profil

## Prochaines Étapes

1. **Push sur Railway** : `git push origin main`
2. **Intégrer dans app.py** : menu "Compte" avec login/logout
3. **Tester client Python** : AuthManager + MastocLoginDialog
4. **Créer premier admin** : via SQL ou endpoint dédié
