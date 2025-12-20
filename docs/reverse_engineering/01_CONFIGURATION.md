# Configuration de l'Application Stōkt

**Source** : `stokt_disasm.hasm` - Objet NewObjectWithBuffer

## Configuration Principale (Production)

```javascript
{
  'name': 'prod',
  'baseURL': 'https://www.sostokt.com/',
  'appVersion': '6.1.13',
  'contentType': 'application/x-www-form-urlencoded',
  'timeout': 60000,

  // URLs externes
  'termsAndConditionsURL': 'https://www.getstokt.com/terms-and-conditions',
  'privacyPolicyURL': 'https://www.getstokt.com/privacy-policy',
  'addYourWallURL': 'https://www.getstokt.com/add/',
  'faqURL': 'https://www.getstokt.com/faq/',

  // Stores
  'appStoreURL': 'https://itunes.apple.com/gb/app/stōkt/id1436843282?mt=8',
  'playStoreURL': 'https://play.google.com/store/apps/details?id=com.getstokt.stokt',

  // Google OAuth Client IDs
  'webClientId': '255278761985-64d76bbdr7p305u66t19pn9p4vq74pgd.apps.googleusercontent.com',
  'androidClientId': '255278761985-ersv7puknqcuhdl97agfp501ngopv95e.apps.googleusercontent.com',
  'androidStandaloneAppClientId': '255278761985-ums2c11833ef554un8dfevfqhabg21nh.apps.googleusercontent.com',
  'iosStandaloneAppClientId': '255278761985-48t9lk7lfkt2oh0ovfdecasl8kj5162e.apps.googleusercontent.com',
  'expoClientId': '255278761985-vmb4gn45bmu143kbtp1ujun1mn8gjjnl.apps.googleusercontent.com',

  // Analytics & Socket
  'googleAnalyticsKey': 'UA-143459590-1',
  'socketServer': 'https://wip-project-server.glitch.me/stokt-0',

  // Assets
  'defaultAvatar': 'https://www.sostokt.com/static/main/img/hand_avatar_small.jpg'
}
```

## Configuration Axios (Requêtes HTTP)

```javascript
{
  'baseURL': 'https://www.sostokt.com/',
  'timeout': 60000
}
```

## Configuration XSRF

```javascript
{
  'adapter': null,
  'transformRequest': null,
  'transformResponse': null,
  'timeout': 0,
  'xsrfCookieName': 'XSRF-TOKEN',
  'xsrfHeaderName': 'X-XSRF-TOKEN',
  'maxContentLength': 4294967295
}
```

## Constantes de Couleur

| Nom | Usage |
|-----|-------|
| `STOKT_RED` | Couleur principale de l'app |
| `BLUEY_GRAY` | Couleur secondaire |
| `DARK_TEXT` | Texte sombre |
| `FEET_OPTION_TEXT` | Texte options pieds |

## Grades par Système

### Système Français
- `grade_from`: '4'
- `grade_to`: '?'

### Système V (US)
- `grade_from`: 'V0'
- `grade_to`: '?'

### Système Q
- `grade_from`: '6Q'
- `grade_to`: '?'

---

**Dernière mise à jour** : 2025-12-20
