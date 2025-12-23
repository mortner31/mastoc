# Archive - mastoc

Ce dossier contient les documents et tâches archivés du projet mastoc.

## 🗂️ Structure

- **`/TODOS/`** : TODOs complétés ou devenus obsolètes
- **`/sessions/`** : Documents de sessions obsolètes (si nécessaire)
- **`/docs/`** : Anciennes versions de documentation

## 📋 Règles d'Archivage

### Quand archiver ?

1. **TODO complété** : Déplacer le fichier TODO et son STATUS associé
2. **Document obsolète** : Déplacer dans le sous-dossier approprié
3. **Versions remplacées** : Conserver les anciennes versions si pertinent

### Comment archiver ?

```bash
# Archiver un TODO complété
mv /docs/TODOS/XX_nom_tache.md /archive/TODOS/
mv /docs/TODOS/XX_nom_tache_STATUS.md /archive/TODOS/

# Mettre à jour la timeline
echo "YYYY-MM-DD | TODO XX archivé (complété/obsolète)" >> /docs/TIMELINE.md
```

## 📝 Format

Conserver la structure originale des fichiers archivés pour pouvoir les consulter ultérieurement.

## ⚠️ Important

- Les **rapports de session** restent dans `/docs/reports/` (historique permanent)
- Seuls les TODOs et documents obsolètes sont archivés ici

---

**Dernière mise à jour** : 2025-11-10
