# STATUS - TODO 17 : Authentification et Utilisateurs mastoc

**Progression** : 100%

## Phase 1 : Extension Modèle User (100%)

- [x] Ajouter champs (email, password_hash, role, etc.)
- [x] Enum UserRole (user/admin)
- [x] Script migration SQL

## Phase 2 : Endpoints Auth (100%)

- [x] Router `/api/auth`
- [x] `POST /api/auth/register` - Créer compte
- [x] `POST /api/auth/login` - Obtenir JWT (OAuth2)
- [x] `POST /api/auth/refresh` - Renouveler token
- [x] `POST /api/auth/logout` - Déconnexion (stateless)
- [x] `POST /api/auth/reset-password` - Demander reset
- [x] `POST /api/auth/reset-password/confirm` - Confirmer reset

## Phase 3 : Endpoints Users (100%)

- [x] Router `/api/users`
- [x] `GET /api/users/me` - Profil connecté
- [x] `PATCH /api/users/me` - Modifier profil
- [x] `POST /api/users/me/password` - Changer mot de passe
- [x] `POST /api/users/me/avatar` - Upload avatar
- [x] `GET /api/users/{id}` - Profil public
- [x] `GET /api/users/{id}/avatar` - Télécharger avatar
- [x] `GET /api/users` - Liste (admin only)

## Phase 4 : Middleware JWT (100%)

- [x] Module `security.py` (hashing, JWT)
- [x] Module `dependencies.py` (get_current_user, etc.)
- [x] Dépendances python-jose, passlib
- [x] Coexistence API Key + JWT
- [x] AuthenticatedUser class

## Phase 5 : Client AuthManager (100%)

- [x] Module `mastoc/core/auth.py`
- [x] Classe `AuthManager` avec login/register/refresh/logout
- [x] Persistance tokens dans `~/.mastoc/auth.json`
- [x] Auto-refresh avant expiration
- [x] Intégration avec `MastocAPI`

## Phase 6 : Client UI (100%)

- [x] `MastocLoginDialog` (connexion + inscription)
- [x] `ProfileDialog` (profil + changer mot de passe)
- [x] `PasswordResetDialog` (mot de passe oublié)
- [x] Export dans `gui/dialogs/__init__.py`

## Phase 7 : Traçabilité (100%)

- [x] `created_by_id` sur Climb
- [x] `updated_by_id` et `updated_at` sur Climb
- [x] Injection automatique lors création/modification
- [x] Vérification permissions sur suppression

## Fichiers Créés/Modifiés

### Serveur
```
server/
├── requirements.txt                    # +python-jose, passlib
├── src/mastoc_api/
│   ├── models/
│   │   ├── base.py                     # +UserRole enum
│   │   ├── user.py                     # +champs auth
│   │   └── climb.py                    # +traçabilité
│   ├── security.py                     # NEW - JWT + hashing
│   ├── dependencies.py                 # NEW - get_current_user
│   ├── routers/
│   │   ├── __init__.py                 # +auth, users
│   │   ├── auth.py                     # NEW
│   │   ├── users.py                    # NEW
│   │   └── climbs.py                   # +traçabilité
│   └── main.py                         # +routers auth, users
└── scripts/
    └── migrate_user_auth.py            # NEW - migration SQL
```

### Client
```
mastoc/src/mastoc/
├── core/
│   └── auth.py                         # NEW - AuthManager
├── api/
│   └── railway_client.py               # +support JWT
└── gui/dialogs/
    ├── __init__.py                     # +exports
    └── mastoc_auth.py                  # NEW - dialogs
```

## Comment Lancer le Serveur Local

```bash
cd /media/veracrypt1/Repositories/mastack/server

# Installer dépendances (une fois)
pip install -r requirements.txt
pip install email-validator

# Fichier .env déjà créé avec DATABASE_URL Railway

# Lancer le serveur
PYTHONPATH=src python -m uvicorn mastoc_api.main:app --reload --port 8000

# Swagger UI : http://localhost:8000/docs
```

## Migration DB

**Déjà exécutée** sur Railway le 2025-12-31 :
```bash
PYTHONPATH=src python scripts/migrate_user_auth.py
# Résultat : 14 OK, 0 skipped, 0 errors
```

## Prochaines Étapes

1. ~~Déployer sur Railway~~ ✅ Migration exécutée
2. ~~Exécuter la migration~~ ✅
3. ~~Intégrer menu "Compte" dans app.py principale~~ ✅
4. ~~Tester inscription/connexion/profil~~ ✅ (15 tests automatisés)
5. ~~Push git pour déployer sur Railway~~ ✅

## TODO 17 COMPLÉTÉ ✅
