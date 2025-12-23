# TODO 11 - Principes d'Ergonomie UI/UX

## Objectif

Definir les regles d'ergonomie Material Design 3 mobile-first pour guider le developpement de l'application mastoc Android.

## Document de Reference

**Le guide complet est disponible dans :**

> `/docs/03_ergonomie_ui_ux.md`

Ce document contient :

1. **Fondamentaux** - Heuristiques Nielsen, ISO 9241
2. **Ergonomie Tactile** - Loi de Fitts, zones de pouce, tailles M3
3. **Material Design 3** - Composants, typographie, espacement
4. **Navigation** - 6 modes, gestes, social cache, options depliables
5. **Wireframes** - Tous les ecrans en ASCII art
6. **Etats et Feedback** - Loading, erreurs, snackbars
7. **Accessibilite** - WCAG AA, touch targets, labels
8. **Persistance** - Settings sauvegardes, reset independant

## Resume des Decisions Cles

| Decision | Choix |
|----------|-------|
| Design System | Material Design 3 |
| Approche | Mobile-first |
| Navigation | 6 modes (Compte, Sync, Simple, Avance, Creer, Moi) |
| Blocs | Scroll vertical + swipe droite = like |
| Social | Cache par defaut, revele sur tap |
| Options | Depliables (Progressive Disclosure) |
| Settings | Persistes entre sessions |
| Reset | Independant par categorie |

## Taches

- [x] Recherche principes UX modernes
- [x] Documentation heuristiques Nielsen
- [x] Documentation Material Design 3
- [x] Definition 6 modes navigation
- [x] Wireframes tous ecrans
- [x] Persistance settings
- [x] Creation document de reference

## References

- [Nielsen Norman Group - 10 Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
- [Material Design 3](https://m3.material.io/)
- [Smashing Magazine - Fitts' Law](https://www.smashingmagazine.com/2022/02/fitts-law-touch-era/)
