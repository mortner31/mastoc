# Rapport de Session - Contre-Analyse Critique du Guide UI/UX

**Date** : 2025-12-22

---

## Résumé Exécutif

Analyse critique approfondie du document `/docs/03_ergonomie_ui_ux.md` (754 lignes) destiné à guider le développement Android de mastock.

**Verdict global :** Document bien structuré avec des bases solides, mais **4 problèmes critiques** à corriger avant implémentation.

---

## 🔴 Problèmes Critiques

### 1. Navigation 6 Destinations = Violation M3

| Aspect | Spécification | Guideline M3 |
|--------|--------------|--------------|
| **Destinations** | 6 (Compte, Sync, Simple, Avancé, Créer, Moi) | **3-5 maximum** |
| **Largeur item** | 360dp ÷ 6 = 60dp | Min 80dp, Max 168dp |

**Impact :** Touch targets trop petits, erreurs de tap fréquentes.

**Solution recommandée :** Fusionner "Compte" et "Moi" → 5 destinations conformes.

**Source :** [M3 Navigation Bar Guidelines](https://m3.material.io/components/navigation-bar/guidelines)

---

### 2. Wizard Création Bloc Sous-Spécifié

**Scénarios non couverts :**

| Scénario | Question ouverte |
|----------|-----------------|
| Interruption (back, home) | Sauvegarde brouillon ? |
| Erreur réseau étape 3 | Retry ? Perte données ? |
| Rotation écran | État préservé ? |
| Validation étape 1→2 | Bloquant ou warning ? |

**Risque :** Perte de travail utilisateur, frustration, abandon.

**Recommandation :** Documenter autosave, retry policy, dialog confirmation.

**Source :** [NN/G - Wizards](https://www.nngroup.com/articles/wizards/)

---

### 3. Features Desktop Absentes du Spec Mobile

**Features TODO 08 (100% complété en Python) :**
- 4 modes coloration (Min, Max, Fréquence, Rareté)
- 7 palettes heatmap
- Panel ouvreurs rétractable
- Contrôles luminosité/épaisseur

**Statut dans spec mobile :** Section 8 mentionne les contrôles mais :
- Aucun wireframe ne les intègre
- Aucun placement UI défini
- Phase de livraison non spécifiée

**Recommandation :** Clarifier explicitement Phase 0 (MVP) vs Phase 1.

---

### 4. Comportement Offline Non Spécifié

**Raison d'être du projet :**
> "Réponse aux limitations de Stokt qui manque de capacités offline"

**Éléments manquants :**
- Indicateur visuel mode offline
- Actions fonctionnelles sans réseau
- Queue de synchronisation
- Résolution de conflits

**Recommandation :** Ajouter section "Offline Behavior" complète.

---

## 🟡 Problèmes Modérés

### 5. Social Caché par Défaut = Friction

**Spec :** Infos sociales cachées, tap [i] pour révéler.

**Contre-argument :**
- +1 tap = friction inutile
- Contraire à "Recognition > Recall" (Nielsen #6)
- Apps concurrentes (TopLogger, Vertical-Life) montrent les stats directement

**Étude terrain :**
> "Chalky fingers sometimes cause inaccurate/unresponsive taps"
> — ClimbOn UX Study

**Recommandation :** Rendre configurable (visible par défaut, option "mode focus").

---

### 6. Swipe Horizontal = Conflits Android

**Spec :** Swipe droite = Like, Swipe gauche = Ignorer

**Problèmes :**
- Conflit avec gesture navigation Android (back depuis edges)
- Erreurs accidentelles avec doigts magnesite

**Recommandation :** Remplacer par boutons explicites ou double-tap.

---

### 7. Stack Technique Non Spécifié

**Question ouverte :** Jetpack Compose vs XML Views ?

**Impact :** Architecture fondamentalement différente.

---

### 8. Performance Ignorée

**Données réelles :**
| Élément | Volume |
|---------|--------|
| Blocs | 1017 |
| Prises | 776 polygones |
| Image mur | 2263×3000 (~500KB) |

**Non adressé :**
- Stratégie pagination
- Image loading (Coil/Glide)
- Polygon rendering
- ANR prevention

---

## 🟢 Points Positifs

| Aspect | Évaluation |
|--------|------------|
| Structure document | Excellente (sections logiques, tables) |
| Références théoriques | Complètes (Nielsen, ISO 9241, Fitts) |
| Wireframes ASCII | Pratiques (versionnables) |
| Zones de pouce | Bien documentées |
| Accessibilité | WCAG AA mentionné |
| Progressive disclosure | Bien appliqué |
| Persistance settings | Clairement spécifiée |

---

## Comparaison Apps Concurrentes

| Feature | mastock | TopLogger | Stōkt | Vertical-Life |
|---------|---------|-----------|-------|---------------|
| Offline | ❓ | ✅ | ❌ | ✅ |
| Social visible | ❌ | ✅ | ✅ | ✅ |
| Bottom nav | 6 ❌ | 4 ✅ | 5 ✅ | 4 ✅ |
| Heatmaps | ❓ | ❌ | ❌ | ❌ |

**Note :** Les heatmaps sont un différenciateur potentiel unique à mastock.

---

## Recommandations Prioritaires

### Avant implémentation (bloquant) :

1. ✅ **Réduire à 5 destinations** - Fusionner Compte+Moi
2. ✅ **Détailler wizard** - Interruption, erreurs, autosave
3. ✅ **Clarifier scope mobile** - Features Phase 0 vs Phase 1
4. ✅ **Documenter offline** - Indicateurs, queue, conflits

### Améliorations (recommandé) :

5. ⚡ **Social configurable** plutôt que caché
6. ⚡ **Remplacer swipes horizontaux** par boutons
7. ⚡ **Section performance** avec stratégies
8. ⚡ **Spécifier stack** Compose vs XML

---

## Méthode d'Analyse

| Source | Utilisation |
|--------|-------------|
| Exploration codebase | Contexte projet, état actuel |
| Recherche web M3 guidelines | Validation navigation |
| Recherche UX wizard patterns | Best practices formulaires |
| Études UX apps escalade | Benchmarking concurrence |
| Analyse TODOs projet | Cohérence features |

---

## Sources

- [Material Design 3 - Navigation Bar](https://m3.material.io/components/navigation-bar/guidelines)
- [NN/G - Wizards](https://www.nngroup.com/articles/wizards/)
- [NN/G - 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
- [Smashing Magazine - Better Form Design](https://www.smashingmagazine.com/2017/05/better-form-design-one-thing-per-page/)
- [ClimbOn UX Case Study](http://stephaniehuang.io/ux-climbon)
- [ChalkBot Climbing App UX](https://www.enfineitz.com/chalk-bot-ux-story.html)
- [Eleken - Wizard UI Pattern](https://www.eleken.co/blog-posts/wizard-ui-pattern-explained)
- [UX Matters - Wizards vs Forms](https://www.uxmatters.com/mt/archives/2011/09/wizards-versus-forms.php)

---

**Conclusion :** Le document `03_ergonomie_ui_ux.md` constitue une base solide mais nécessite des corrections sur la navigation (6→5 destinations) et des clarifications majeures (wizard, offline, scope features) avant de démarrer l'implémentation Android.
