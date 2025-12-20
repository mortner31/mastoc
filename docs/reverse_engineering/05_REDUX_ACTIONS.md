# Actions Redux Stōkt

**Source** : `stokt_disasm.hasm` - Strings `stokt-app/*`

## Module: user

### Authentification
| Action | Description |
|--------|-------------|
| `stokt-app/user/LOGIN_PENDING` | Login en cours |
| `stokt-app/user/LOGIN_SUCCESS` | Login réussi |
| `stokt-app/user/LOGIN_ERROR` | Erreur login |
| `stokt-app/user/CLEAR_LOGIN_ERROR` | Effacer erreur |

### Gym
| Action | Description |
|--------|-------------|
| `stokt-app/user/GET_GYM_REQUEST` | Demande gym |
| `stokt-app/user/GET_GYM_INITIAL_REQUEST` | Demande initiale |
| `stokt-app/user/GET_GYM_SUCCESS` | Gym reçu |
| `stokt-app/user/GET_GYM_ERROR` | Erreur |

### Favoris
| Action | Description |
|--------|-------------|
| `stokt-app/user/ADD_FAVORITE_GYM_REQUEST` | Ajouter favori |
| `stokt-app/user/ADD_FAVORITE_GYM_SUCCESS` | Favori ajouté |
| `stokt-app/user/ADD_FAVORITE_GYM_ERROR` | Erreur |
| `stokt-app/user/REMOVE_FAVORITE_GYM_REQUEST` | Retirer favori |
| `stokt-app/user/REMOVE_FAVORITE_GYM_SUCCESS` | Favori retiré |
| `stokt-app/user/REMOVE_FAVORITE_GYM_ERROR` | Erreur |

### Climbs
| Action | Description |
|--------|-------------|
| `stokt-app/user/GET_NEW_CLIMBS_REQUEST` | Nouveaux climbs |
| `stokt-app/user/GET_NEW_CLIMBS_SUCCESS` | Reçus |
| `stokt-app/user/GET_NEW_CLIMBS_ERROR` | Erreur |
| `stokt-app/user/GET_MY_SENT_REQUEST` | Mes envois |
| `stokt-app/user/GET_MY_SENT_SUCCESS` | Reçus |
| `stokt-app/user/GET_MY_SENT_ERROR` | Erreur |
| `stokt-app/user/GET_MY_LIKED_REQUEST` | Mes likes |
| `stokt-app/user/GET_MY_LIKED_SUCCESS` | Reçus |
| `stokt-app/user/GET_MY_LIKED_ERROR` | Erreur |
| `stokt-app/user/GET_MY_BOOKMARKED_REQUEST` | Mes favoris |
| `stokt-app/user/GET_MY_BOOKMARKED_SUCCESS` | Reçus |
| `stokt-app/user/GET_MY_BOOKMARKED_ERROR` | Erreur |
| `stokt-app/user/GET_MY_CLIMBS_REQUEST` | Mes climbs |
| `stokt-app/user/GET_MY_CLIMBS_SUCCESS` | Reçus |
| `stokt-app/user/UPDATE_CLIMBS` | Mise à jour |
| `stokt-app/user/UPDATE_CLIMBS_FOR_SWIPE` | MAJ pour swipe |
| `stokt-app/user/UPDATE_CLIMB_IDS` | MAJ IDs |
| `stokt-app/user/UPDATE_CLIMB_LIST_IDS` | MAJ liste IDs |

### Events
| Action | Description |
|--------|-------------|
| `stokt-app/user/GYM_EVENTS_REQUEST` | Events gym |
| `stokt-app/user/GYM_EVENTS_SUCCESS` | Reçus |
| `stokt-app/user/GYM_EVENTS_ERROR` | Erreur |
| `stokt-app/user/GYM_EVENTS_RESET` | Reset |
| `stokt-app/user/GYM_EVENT_CLIMBS_REQUEST` | Climbs event |
| `stokt-app/user/GYM_EVENT_CLIMBS_SUCCESS` | Reçus |
| `stokt-app/user/GYM_EVENT_CLIMBS_ERROR` | Erreur |
| `stokt-app/user/GYM_EVENT_LEADERBOARD_REQUEST` | Leaderboard |
| `stokt-app/user/GYM_EVENT_LEADERBOARD_SUCCESS` | Reçu |
| `stokt-app/user/GYM_EVENT_LEADERBOARD_ERROR` | Erreur |
| `stokt-app/user/GYM_EVENT_RULES_REQUEST` | Règles |
| `stokt-app/user/GYM_EVENT_RULES_SUCCESS` | Reçues |
| `stokt-app/user/GYM_EVENT_RULES_ERROR` | Erreur |

## Module: myGym

### Faces
| Action | Description |
|--------|-------------|
| `stokt-app/myGym/FACE_PENDING` | Chargement face |
| `stokt-app/myGym/FACE_SUCCESS` | Face reçue |
| `stokt-app/myGym/FACE_ERROR` | Erreur |

### Climbs
| Action | Description |
|--------|-------------|
| `stokt-app/myGym/CLIMBS_PENDING` | Chargement climbs |
| `stokt-app/myGym/CLIMBS_SUCCESS` | Climbs reçus |
| `stokt-app/myGym/CLIMBS_ERROR` | Erreur |
| `stokt-app/myGym/GET_MORE_CLIMBS_PENDING` | Plus de climbs |
| `stokt-app/myGym/GET_MORE_CLIMBS_SUCCESS` | Reçus |
| `stokt-app/myGym/GET_MORE_CLIMBS_ERROR` | Erreur |
| `stokt-app/myGym/GET_CLIMBS_COUNT_PENDING` | Compte |
| `stokt-app/myGym/GET_CLIMBS_COUNT_SUCCESS` | Compte reçu |
| `stokt-app/myGym/GET_CLIMBS_COUNT_ERROR` | Erreur |
| `stokt-app/myGym/CLIMBS_REFRESHING` | Rafraîchissement |
| `stokt-app/myGym/CLIMBS_REFRESHED` | Rafraîchi |
| `stokt-app/myGym/CLIMBS_REFRESH_COMPLETE` | Complet |
| `stokt-app/myGym/FILTER_CLIMBS_SUCCESS` | Filtrage OK |
| `stokt-app/myGym/UPDATE_NUMBER_OF_CLIMBS` | MAJ nombre |
| `stokt-app/myGym/CLEAR_CLIMBS_ERROR` | Effacer erreur |
| `stokt-app/myGym/DELETE_PENDING` | Suppression |
| `stokt-app/myGym/DELETE_SUCCESS` | Supprimé |

### LED
| Action | Description |
|--------|-------------|
| `stokt-app/myGym/TOGGLE_LED_HOLD` | Toggle LED |
| `stokt-app/myGym/UPDATE_SHOW_LED_TIPS` | MAJ tips LED |
| `stokt-app/myGym/UPDATE_LED_TIPS` | MAJ LED tips |
| `stokt-app/myGym/TOGGLE_LED_TIPS` | Toggle tips |
| `stokt-app/myGym/RESET_LEDS_PENDING` | Reset LEDs |
| `stokt-app/myGym/RESET_LEDS_SUCCESS` | Reset OK |
| `stokt-app/myGym/RESET_LEDS_ERROR` | Erreur |
| `stokt-app/myGym/EDIT_LEDS_PENDING` | Edit LEDs |
| `stokt-app/myGym/EDIT_LEDS_SUCCESS` | Edit OK |
| `stokt-app/myGym/EDIT_LEDS_ERROR` | Erreur |
| `stokt-app/myGym/GET_LED_SETTINGS_PENDING` | Params LED |
| `stokt-app/myGym/GET_LED_SETTINGS_SUCCESS` | Reçus |
| `stokt-app/myGym/GET_LED_SETTINGS_ERROR` | Erreur |

### Holds Appairées
| Action | Description |
|--------|-------------|
| `stokt-app/myGym/PAIR_HOLD_PENDING` | Appairage |
| `stokt-app/myGym/PAIR_HOLD_SUCCESS` | Appairé |
| `stokt-app/myGym/PAIR_HOLD_ERROR` | Erreur |
| `stokt-app/myGym/UNPAIR_HOLD_PENDING` | Désappairage |
| `stokt-app/myGym/UNPAIR_HOLD_SUCCESS` | Désappairé |
| `stokt-app/myGym/UNPAIR_HOLD_ERROR` | Erreur |
| `stokt-app/myGym/GET_PAIRED_HOLDS_PENDING` | Prises appairées |
| `stokt-app/myGym/GET_PAIRED_HOLDS_SUCCESS` | Reçues |
| `stokt-app/myGym/GET_PAIRED_HOLDS_ERROR` | Erreur |

## Module: problemCreation

### CRUD Climb
| Action | Description |
|--------|-------------|
| `stokt-app/problemCreation/POST_CLIMB_PENDING` | Création climb |
| `stokt-app/problemCreation/POST_CLIMB_SUCCESS` | Créé |
| `stokt-app/problemCreation/POST_CLIMB_ERROR` | Erreur |
| `stokt-app/problemCreation/GET_NAME_PENDING` | Nom |
| `stokt-app/problemCreation/GET_NAME_SUCCESS` | Reçu |
| `stokt-app/problemCreation/GET_NAME_ERROR` | Erreur |
| `stokt-app/problemCreation/GET_CLIMB_TAGS_PENDING` | Tags |
| `stokt-app/problemCreation/GET_CLIMB_TAGS_SUCCESS` | Reçus |
| `stokt-app/problemCreation/GET_CLIMB_TAGS_ERROR` | Erreur |

### Holds
| Action | Description |
|--------|-------------|
| `stokt-app/problemCreation/TOGGLE_OTHER_HOLD` | Toggle autre |
| `stokt-app/problemCreation/TOGGLE_FOOT_HOLD` | Toggle pied |
| `stokt-app/problemCreation/TOGGLE_CIRCUIT_HOLD` | Toggle circuit |
| `stokt-app/problemCreation/TOGGLE_START_HOLD` | Toggle départ |
| `stokt-app/problemCreation/TOGGLE_FINISH_HOLD` | Toggle arrivée |
| `stokt-app/problemCreation/CLEAR_HOLDS` | Effacer prises |

### Paramètres
| Action | Description |
|--------|-------------|
| `stokt-app/problemCreation/UPDATE_NAME` | MAJ nom |
| `stokt-app/problemCreation/UPDATE_ATTEMPTS` | MAJ tentatives |
| `stokt-app/problemCreation/UPDATE_GRADE` | MAJ grade |
| `stokt-app/problemCreation/UPDATE_SWITCH` | MAJ switch |
| `stokt-app/problemCreation/UPDATE_FEET_SELECTION` | MAJ pieds |
| `stokt-app/problemCreation/UPDATE_TAG_SELECTION` | MAJ tags |
| `stokt-app/problemCreation/UPDATE_DESCRIPTION` | MAJ description |
| `stokt-app/problemCreation/UPDATE_MAKE_PRIVATE` | MAJ privé |
| `stokt-app/problemCreation/UPDATE_ANGLE` | MAJ angle |
| `stokt-app/problemCreation/TOOGLE_FEET_RULES` | Toggle règles pieds |
| `stokt-app/problemCreation/RESET_CLIMB` | Reset climb |

### Circuits
| Action | Description |
|--------|-------------|
| `stokt-app/problemCreation/TOGGLE_CIRCUIT_MODE` | Mode circuit |
| `stokt-app/problemCreation/UPDATE_CIRCUIT_ACTIONS` | Actions circuit |
| `stokt-app/problemCreation/UPDATE_CIRCUIT_COUNT` | Compte circuit |
| `stokt-app/problemCreation/POST_CIRCUIT_PENDING` | Création |
| `stokt-app/problemCreation/POST_CIRCUIT_SUCCESS` | Créé |
| `stokt-app/problemCreation/POST_CIRCUIT_ERROR` | Erreur |
| `stokt-app/problemCreation/PATCH_CIRCUIT_PENDING` | MAJ |
| `stokt-app/problemCreation/PATCH_CIRCUIT_SUCCESS` | MAJ OK |
| `stokt-app/problemCreation/PATCH_CIRCUIT_ERROR` | Erreur |
| `stokt-app/problemCreation/DELETE_CIRCUIT_PENDING` | Suppression |
| `stokt-app/problemCreation/DELETE_CIRCUIT_SUCCESS` | Supprimé |
| `stokt-app/problemCreation/DELETE_CIRCUIT_ERROR` | Erreur |

---

**Dernière mise à jour** : 2025-12-20
