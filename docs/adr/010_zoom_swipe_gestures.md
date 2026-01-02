# ADR 010 - Gestion des Gestes Zoom/Swipe dans VerticalPager

**Date** : 2026-01-01
**Statut** : Accepté

## Contexte

L'écran de détail d'un bloc (`ClimbDetailScreen`) combine :
- Un **VerticalPager** pour swiper entre les blocs (navigation verticale)
- Un **zoom/pan** sur l'image du mur (pinch + drag)

Le problème : `detectTransformGestures` de Compose consomme **tous** les gestes (y compris les swipes à un doigt), empêchant le VerticalPager de recevoir les événements de scroll.

## Décision

Implémenter une **gestion personnalisée des gestes** avec `awaitEachGesture` qui :

1. **Consomme toujours** les gestes de zoom (pinch à 2+ doigts)
2. **Consomme le pan** uniquement si l'image est zoomée (`scale > 1`)
3. **Laisse passer** les swipes verticaux à un doigt quand `scale == 1`

### Règle de consommation

```
┌─────────────────────────────────────────────────────────────┐
│                    Événement touch                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Zoom détecté ?  │
                    │ (zoomChange ≠ 1)│
                    └─────────────────┘
                      │ Oui      │ Non
                      ▼          ▼
              ┌───────────┐  ┌─────────────────┐
              │ Consommer │  │ scale > 1.01 ?  │
              │ + Appliquer│  └─────────────────┘
              │   zoom    │    │ Oui      │ Non
              └───────────┘    ▼          ▼
                        ┌───────────┐  ┌────────────────┐
                        │ Consommer │  │ NE PAS         │
                        │ + Appliquer│  │ consommer      │
                        │   pan     │  │ → Pager scroll │
                        └───────────┘  └────────────────┘
```

### Bouton Reset Zoom

Quand l'utilisateur est zoomé, un bouton apparaît (coin supérieur gauche) pour :
- Réinitialiser `scale = 1f`
- Réinitialiser `offset = Offset.Zero`
- Réactiver le swipe vertical

## Conséquences

### Positives
- Swipe vertical fonctionne quand non zoomé
- Zoom/pan fonctionne quand zoomé
- Transition claire via bouton reset
- Pattern réutilisable pour d'autres écrans avec pager + zoom

### Négatives
- Code plus complexe que `detectTransformGestures`
- Le seuil `1.01f` est arbitraire (évite les faux positifs de floating point)

## Implémentation

### Gestion des gestes (`ClimbDetailScreen.kt`)

```kotlin
.pointerInput(Unit) {
    awaitEachGesture {
        // Attendre le premier touch
        awaitFirstDown(requireUnconsumed = false)

        do {
            val event = awaitPointerEvent()
            val pointerCount = event.changes.count { it.pressed }

            // Calculer le zoom (pinch)
            val zoomChange = event.calculateZoom()
            if (zoomChange != 1f) {
                scale = (scale * zoomChange).coerceIn(1f, 4f)
                event.changes.forEach { it.consume() }
            }

            // Pan uniquement si zoomé (scale > 1) ou si 2+ doigts
            if (scale > 1.01f || pointerCount >= 2) {
                val pan = event.calculatePan()
                val maxOffsetX = (containerSize.width * (scale - 1) / 2).coerceAtLeast(0f)
                val maxOffsetY = (containerSize.height * (scale - 1) / 2).coerceAtLeast(0f)
                offset = Offset(
                    x = (offset.x + pan.x).coerceIn(-maxOffsetX, maxOffsetX),
                    y = (offset.y + pan.y).coerceIn(-maxOffsetY, maxOffsetY)
                )
                // Consommer les événements de pan SI on est zoomé
                if (scale > 1.01f) {
                    event.changes.forEach { it.consume() }
                }
            }
            // Sinon: ne pas consommer → le VerticalPager reçoit le swipe

        } while (event.changes.any { it.pressed })
    }
}
```

### Bouton Reset Zoom

```kotlin
// Bouton reset zoom (visible uniquement si zoomé)
AnimatedVisibility(
    visible = scale > 1.01f,
    enter = fadeIn(),
    exit = fadeOut(),
    modifier = Modifier
        .align(Alignment.TopStart)
        .padding(8.dp)
) {
    FilledIconButton(
        onClick = {
            scale = 1f
            offset = Offset.Zero
        },
        modifier = Modifier.size(40.dp),
        colors = IconButtonDefaults.filledIconButtonColors(
            containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.9f),
            contentColor = MaterialTheme.colorScheme.onSurface
        )
    ) {
        Icon(
            imageVector = Icons.Default.Close,
            contentDescription = "Réinitialiser le zoom"
        )
    }
}
```

## Alternatives Considérées

### 1. `userScrollEnabled` dynamique

```kotlin
VerticalPager(
    userScrollEnabled = currentZoom <= 1.01f
)
```

**Problème** : Ne résout pas le problème car les gestes sont consommés par `detectTransformGestures` avant d'atteindre le pager.

### 2. `nestedScroll` connection

**Problème** : Complexité supplémentaire, moins de contrôle sur la consommation des événements.

### 3. Double-tap pour toggle zoom

**Considéré** : Pourrait être ajouté en complément du bouton reset.

## Fichiers concernés

- `android/.../ui/screens/ClimbDetailScreen.kt`

## Références

- [ADR 009](009_climb_rendering_system.md) - Système de rendu des blocs
- [Compose Gestures](https://developer.android.com/develop/ui/compose/touch-input/pointer-input/understand-gestures)
- [VerticalPager](https://developer.android.com/develop/ui/compose/layouts/pager)
