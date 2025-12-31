# STATUS - TODO 17 : Authentification et Utilisateurs mastoc

**Progression** : 0%

## Phase 1 : Extension Modèle User (0%)

- [ ] Ajouter champs (email, password_hash, role, etc.)
- [ ] Migration Alembic
- [ ] Index UNIQUE

## Phase 2 : Endpoints Auth (0%)

- [ ] Router `/api/auth`
- [ ] Register
- [ ] Login (JWT)
- [ ] Refresh
- [ ] Logout
- [ ] Reset password

## Phase 3 : Endpoints Users (0%)

- [ ] Router `/api/users`
- [ ] GET/PATCH /me
- [ ] Upload avatar
- [ ] Profil public

## Phase 4 : Middleware JWT (0%)

- [ ] Dépendances python-jose, passlib
- [ ] `get_current_user()` dependency
- [ ] Coexistence API Key + JWT

## Phase 5 : Client AuthManager (0%)

- [ ] Module `core/auth.py`
- [ ] Persistance tokens
- [ ] Auto-refresh

## Phase 6 : Client UI (0%)

- [ ] Dialogs login/register
- [ ] Dialog profil
- [ ] Menu Compte

## Phase 7 : Traçabilité (0%)

- [ ] `created_by_id` sur Climb
- [ ] Permissions modification/suppression
