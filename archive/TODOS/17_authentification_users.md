# TODO 17 - Système d'Authentification et Utilisateurs mastoc

## Objectif

Créer un système d'authentification mastoc **natif** permettant :
1. Inscription/Connexion utilisateurs mastoc (email/password + JWT)
2. Gestion de profil (nom, avatar)
3. Reset password par email
4. Traçabilité des actions (qui crée/modifie quoi)
5. Rôles : User + Admin

## Décisions

| Aspect | Décision |
|--------|----------|
| Auth type | Email/password + JWT |
| Rôles | User + Admin |
| Reset password | Oui (par email) |
| Vérification email | Non (v1) |
| OAuth | Non (v1) |
| 2FA | Non (v1) |
| Liaison Stokt | Reportée (v2) |

## Tâches

### Phase 1 : Extension Modèle User (Serveur)

- [ ] Ajouter champs au modèle User : `email`, `username`, `password_hash`, `is_active`, `role`, `updated_at`, `last_login_at`, `reset_token`, `reset_token_expires`
- [ ] Créer migration Alembic
- [ ] Index UNIQUE sur `email` et `username`

### Phase 2 : Endpoints Authentification (Serveur)

- [ ] Créer router `/api/auth`
- [ ] `POST /api/auth/register` - Créer compte
- [ ] `POST /api/auth/login` - Obtenir JWT
- [ ] `POST /api/auth/refresh` - Renouveler JWT
- [ ] `POST /api/auth/logout` - Invalider token
- [ ] `POST /api/auth/reset-password` - Demander reset
- [ ] `POST /api/auth/reset-password/confirm` - Confirmer reset

### Phase 3 : Endpoints Utilisateurs (Serveur)

- [ ] Créer router `/api/users`
- [ ] `GET /api/users/me` - Profil connecté
- [ ] `PATCH /api/users/me` - Modifier profil
- [ ] `POST /api/users/me/avatar` - Upload avatar
- [ ] `GET /api/users/{id}` - Profil public
- [ ] `GET /api/users/{id}/avatar` - Télécharger avatar
- [ ] `GET /api/users` - Liste (admin only)

### Phase 4 : Middleware JWT (Serveur)

- [ ] Ajouter dépendances : `python-jose`, `passlib[bcrypt]`
- [ ] Créer `get_current_user()` dependency
- [ ] Supporter API Key ET JWT en parallèle
- [ ] Configuration : `JWT_SECRET`, `JWT_EXPIRE`

### Phase 5 : Client AuthManager

- [ ] Créer module `mastoc/core/auth.py`
- [ ] Classe `AuthManager` avec login/register/refresh/logout
- [ ] Persistance tokens dans `~/.mastoc/auth.json`
- [ ] Auto-refresh avant expiration
- [ ] Intégration avec `MastocAPI`

### Phase 6 : Client UI

- [ ] Créer `gui/dialogs/auth.py` : MastocLoginDialog, MastocRegisterDialog
- [ ] Créer `gui/dialogs/profile.py` : ProfileDialog
- [ ] Intégrer menu "Compte" dans `app.py`
- [ ] Afficher utilisateur connecté dans barre de statut

### Phase 7 : Traçabilité Actions

- [ ] Ajouter `created_by_id` au modèle Climb
- [ ] Injecter `current_user.id` lors création climb
- [ ] Vérifier permissions sur modification/suppression

## Fichiers à Créer/Modifier

### Serveur
```
server/src/mastoc_api/
├── models/user.py              # Modifier
├── routers/auth.py             # Créer
├── routers/users.py            # Créer
├── auth.py                     # Modifier
├── dependencies.py             # Créer
└── config.py                   # Modifier
```

### Client
```
mastoc/src/mastoc/
├── core/auth.py                # Créer
├── api/railway_client.py       # Modifier
└── gui/dialogs/
    ├── auth.py                 # Créer
    └── profile.py              # Créer
```

## Dépendances

### Serveur (requirements.txt)
```
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
```

## Prérequis

- TODO 14 complété (MastocAPI client) ✅

## Références

- Plan détaillé : `/home/mortner/.claude/plans/compressed-launching-thacker.md`
- ADR-002 : Authentification par API Key (existant)
- `/server/src/mastoc_api/auth.py` : Auth actuelle
- `/mastoc/src/mastoc/gui/dialogs/login.py` : Login Stokt (pattern à réutiliser)
