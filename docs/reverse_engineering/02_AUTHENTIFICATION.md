# Authentification Stōkt API

**Source** : `stokt_disasm.hasm`

## Endpoint Principal

```
POST https://www.sostokt.com/api/token-auth
```

## Requête

### Headers
```
Content-Type: application/x-www-form-urlencoded
```

### Body
```
username=<email>&password=<password>
```

## Réponse

```json
{
  "token": "abc123..."
}
```

## Utilisation du Token

### Header Authorization
```
Authorization: Token <token_value>
```

**Note** : C'est le format DRF (Django Rest Framework) standard, pas Bearer.

### Configuration dans Axios
```javascript
// Fonction setToken (Function #12737)
headers.common['Authorization'] = 'Token ' + tokenValue
```

## Actions Redux

| Action | Description |
|--------|-------------|
| `stokt-app/user/LOGIN_PENDING` | Login en cours |
| `stokt-app/user/LOGIN_SUCCESS` | Login réussi |
| `stokt-app/user/LOGIN_ERROR` | Erreur de login |
| `stokt-app/user/CLEAR_LOGIN_ERROR` | Effacer erreur |

## Méthodes d'Auth Alternatives

### Social Auth
- `api/social-auth/apple/login` - Apple
- `api/social-auth/facebook/login` - Facebook
- `api/social-auth/google/login` - Google

### Autres
- `api/signup/` - Inscription
- `api/logout/` - Déconnexion
- `api/password/reset/` - Reset mot de passe

## Exemple cURL

```bash
# Authentification
curl -X POST https://www.sostokt.com/api/token-auth \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=email@example.com&password=secret"

# Réponse
# {"token":"abc123..."}

# Requête authentifiée
curl https://www.sostokt.com/api/users/me \
  -H "Authorization: Token abc123..."
```

---

**Dernière mise à jour** : 2025-12-20
