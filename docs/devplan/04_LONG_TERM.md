# Plan Long Terme (6-12 mois)

**Période** : Juin - Décembre 2026

---

## Objectifs principaux

1. **Support multi-utilisateurs**
2. **Statistiques avancées**
3. **Export/Import de données**
4. **Écosystème complet**

---

## Phase 9 : Multi-Utilisateurs (Mois 7-8)

### Objectif

Permettre à plusieurs grimpeurs d'utiliser mastoc avec leurs propres données.

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Serveur Railway                            │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │  User A  │    │  User B  │    │  User C  │               │
│  │ ──────── │    │ ──────── │    │ ──────── │               │
│  │ • Sends  │    │ • Sends  │    │ • Sends  │               │
│  │ • Likes  │    │ • Likes  │    │ • Likes  │               │
│  │ • Notes  │    │ • Notes  │    │ • Notes  │               │
│  │ • Lists  │    │ • Lists  │    │ • Lists  │               │
│  └──────────┘    └──────────┘    └──────────┘               │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │              Données partagées                      │     │
│  │  • Climbs (sync Stokt)                              │     │
│  │  • Hold Annotations (consensus)                     │     │
│  │  • Images murs                                      │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### Fonctionnalités

| Feature | Description |
|---------|-------------|
| Authentification | Email + mot de passe simple |
| Profil utilisateur | Nom, avatar, stats publiques |
| Données privées | Sends, notes personnelles |
| Données partagées | Annotations, likes visibles |
| Privacy settings | Contrôle visibilité profil |

### Schéma DB étendu

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL,
    avatar_url TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_sends (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    climb_id UUID REFERENCES climbs(id),
    sent_at DATE NOT NULL,
    attempts INTEGER,
    rating INTEGER,
    notes TEXT,
    is_flash BOOLEAN DEFAULT FALSE
);

CREATE TABLE user_likes (
    user_id UUID REFERENCES users(id),
    climb_id UUID REFERENCES climbs(id),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, climb_id)
);
```

### Tâches

| Tâche | Effort |
|-------|--------|
| API authentification | 12h |
| Gestion sessions (JWT) | 8h |
| Migration DB multi-users | 8h |
| UI login/signup Android | 12h |
| Sync données par utilisateur | 12h |
| Tests sécurité | 8h |

---

## Phase 10 : Statistiques Avancées (Mois 9)

### Objectif

Fournir des insights sur sa progression et son activité.

### Tableaux de bord

#### Dashboard personnel

```
┌─────────────────────────────────────────────────────────────┐
│                    Mes Statistiques                          │
├─────────────────────────────────────────────────────────────┤
│  Blocs réussis        Niveau max         Taux de réussite   │
│  ┌──────────┐         ┌──────────┐       ┌──────────┐       │
│  │   142    │         │   7A     │       │   68%    │       │
│  │ (+12 ce mois)      │ (→ depuis 6B+)   │ (stable)         │
│  └──────────┘         └──────────┘       └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│  Progression par grade (graphique barres)                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  4  ████████████████████████████  28                    ││
│  │  5  ██████████████████████████████  32                  ││
│  │  5+ ████████████████████████  24                        ││
│  │  6A ██████████████████  18                              ││
│  │  6A+████████████  14                                    ││
│  │  6B ██████████  12                                      ││
│  │  6B+████████  10                                        ││
│  │  6C ████  4                                             ││
│  │  7A ██  2                                               ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  Activité (heatmap calendrier)                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  ││
│  │  ░░░  ▓▓▓  ░░░  ▓▓▓  ███  ███  ▓▓▓  ░░░  ▓▓▓  ███  ░░░ ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

#### Analyse des prises

```
┌─────────────────────────────────────────────────────────────┐
│               Analyse de mes forces/faiblesses               │
├─────────────────────────────────────────────────────────────┤
│  Types de prises (% réussite)                                │
│                                                              │
│  Bacs          ████████████████████████████████  92%        │
│  Plats         ██████████████████████████  78%              │
│  Pinces        ████████████████████  65%                    │
│  Réglettes     ████████████████  52%   ← Point faible       │
│  Bi-doigts     ██████████  38%         ← À travailler       │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Recommandation : Travailler les blocs avec réglettes       │
│  → 12 blocs suggérés à votre niveau                          │
└─────────────────────────────────────────────────────────────┘
```

### Tâches

| Tâche | Effort |
|-------|--------|
| API statistiques (agrégations) | 12h |
| Dashboard Android (Compose) | 16h |
| Graphiques (Vico ou Charts) | 12h |
| Heatmap calendrier | 8h |
| Analyse forces/faiblesses | 12h |
| Export stats (image/PDF) | 8h |

---

## Phase 11 : Export/Import (Mois 10)

### Objectif

Permettre la portabilité des données utilisateur.

### Formats supportés

| Format | Usage |
|--------|-------|
| JSON | Export complet, sauvegarde |
| CSV | Analyse externe (Excel) |
| PDF | Rapport imprimable |

### Export JSON

```json
{
  "version": "1.0",
  "exported_at": "2026-10-15T14:30:00Z",
  "user": {
    "id": "uuid",
    "display_name": "Grimpeur",
    "created_at": "2025-12-01"
  },
  "sends": [
    {
      "climb_id": "uuid",
      "climb_name": "Bloc difficile",
      "grade": "6B+",
      "sent_at": "2026-05-15",
      "attempts": 8,
      "rating": 4,
      "notes": "Mouvement clé sur la réglette"
    }
  ],
  "lists": [...],
  "annotations": [...]
}
```

### Export PDF

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    MASTOC                                   │
│                 Rapport de progression                      │
│                                                             │
│  Grimpeur : [Nom]                                           │
│  Période : Janvier 2026 - Octobre 2026                      │
│  Salle : Montoboard (Caraman)                               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RÉSUMÉ                                                     │
│  • 142 blocs réussis                                        │
│  • Niveau max atteint : 7A                                  │
│  • Progression : +2 niveaux                                 │
│                                                             │
│  DÉTAIL PAR GRADE                                           │
│  [Graphique barres]                                         │
│                                                             │
│  ACTIVITÉ                                                   │
│  [Calendrier heatmap]                                       │
│                                                             │
│  ANALYSE                                                    │
│  Forces : Bacs, Plats                                       │
│  Faiblesses : Réglettes, Bi-doigts                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Généré par mastoc le 2026-10-15                            │
└─────────────────────────────────────────────────────────────┘
```

### Tâches

| Tâche | Effort |
|-------|--------|
| Export JSON | 8h |
| Import JSON | 12h |
| Export CSV | 4h |
| Génération PDF (iText ou similaire) | 16h |
| UI export/import | 8h |
| Tests import/export | 8h |

---

## Phase 12 : Écosystème Complet (Mois 11-12)

### Objectif

Finaliser l'application avec des fonctionnalités avancées.

### Fonctionnalités optionnelles

| Feature | Priorité | Description |
|---------|----------|-------------|
| Widget Android | Basse | Stats rapides sur home screen |
| Notifications | Basse | Nouveaux blocs, rappels |
| Partage social | Basse | Partager un send sur réseaux |
| Mode entraînement | Moyenne | Timer, circuits, séries |
| Comparaison utilisateurs | Basse | Voir progression d'un ami |
| Wear OS | Très basse | App montre pour timer |

### Mode entraînement

```
┌─────────────────────────────────────────────────────────────┐
│                    MODE ENTRAÎNEMENT                        │
├─────────────────────────────────────────────────────────────┤
│  Session : Circuit Force                                    │
│                                                             │
│  Bloc actuel : "La dalle" (6A+)                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                [Image bloc]                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Repos : 02:45 restant                                      │
│  ████████████░░░░░░░░░░░░░░░░░░                            │
│                                                             │
│  Progression circuit : 3/8 blocs                            │
│                                                             │
│  [   RÉUSSI   ]  [   ÉCHOUÉ   ]  [   PASSER   ]            │
└─────────────────────────────────────────────────────────────┘
```

### Tâches

| Tâche | Effort |
|-------|--------|
| Mode entraînement | 20h |
| Widget Android | 8h |
| Notifications (WorkManager) | 8h |
| Partage social | 8h |
| Polish général | 16h |
| Documentation utilisateur | 8h |

---

## Calendrier prévisionnel

```
Mois 7 (Juillet)
├── Phase 9 : Multi-utilisateurs (partie 1)
Mois 8 (Août)
├── Phase 9 : Multi-utilisateurs (partie 2)
├── Tests et sécurité
Mois 9 (Septembre)
├── Phase 10 : Statistiques avancées
Mois 10 (Octobre)
├── Phase 11 : Export/Import
Mois 11 (Novembre)
├── Phase 12 : Écosystème (features optionnelles)
Mois 12 (Décembre)
├── Phase 12 : Polish et release V1.0
├── Documentation complète
├── Publication Play Store
```

---

## Critères de succès Phase Long Terme

### Application

- [ ] Support multi-utilisateurs stable
- [ ] Statistiques complètes et utiles
- [ ] Export/Import fonctionnel
- [ ] Publication Play Store (version stable)

### Métriques

- [ ] <5% crash rate
- [ ] >4.0 rating Play Store
- [ ] <100ms temps de réponse UI
- [ ] Support 5+ utilisateurs actifs

### Infrastructure

- [ ] Coût <$20/mois pour 5 utilisateurs
- [ ] 99.5% uptime serveur
- [ ] Backup automatique quotidien

---

## Vision finale

```
┌─────────────────────────────────────────────────────────────┐
│                         MASTOC V1.0                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Application Android complète pour grimpeurs                 │
│                                                              │
│  ✅ Visualisation interactive des blocs                     │
│  ✅ Recherche par prises                                    │
│  ✅ Création de blocs                                       │
│  ✅ Hold Annotations (communautaire)                        │
│  ✅ Listes personnalisées                                   │
│  ✅ Multi-utilisateurs                                      │
│  ✅ Statistiques avancées                                   │
│  ✅ Export/Import                                           │
│  ✅ Mode entraînement                                       │
│                                                              │
│  Support : Montoboard + Pan personnel                       │
│  Mode : 100% offline-first                                  │
│  Indépendant de Stokt (sync optionnelle)                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Au-delà de V1.0 (2027+)

### Idées futures

- **iOS** : Portage SwiftUI
- **Web** : Dashboard statistiques
- **API publique** : Pour intégrations tierces
- **IA** : Recommandation de blocs personnalisée
- **AR** : Visualisation en réalité augmentée
- **Communauté** : Challenges, classements

---

*Plan long terme créé le 2025-12-23*
