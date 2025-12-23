# Rapport de Session - Tentative de Patch APK pour Interception HTTPS

**Date** : 2025-12-20

---

## 🎯 Objectif

Patcher l'application Stōkt pour permettre l'interception HTTPS avec mitmproxy afin de capturer les structures JSON des requêtes API.

---

## ✅ Ce qui a été fait

### 1. Installation de mitmproxy
```bash
pip install mitmproxy
# Version installée : 11.0.2
```

### 2. Patch avec apk-mitm
```bash
# Création d'un bundle APKS avec tous les splits
cd /media/veracrypt1/Repositories/mastoc/extracted/stockt_apk
zip stokt_bundle.apks base.apk split_config.arm64_v8a.apk split_config.fr.apk split_config.xxhdpi.apk

# Patch du bundle complet
npx apk-mitm stokt_bundle.apks
```

**Résultat** : APKs patchés et signés avec la même clé ✅

### 3. Fichiers générés
```
/extracted/stockt_apk/
├── stokt_bundle.apks              # Bundle original
├── stokt_bundle-patched.apks      # Bundle patché
└── patched_bundle/                # APKs extraits
    ├── base.apk
    ├── split_config.arm64_v8a.apk
    ├── split_config.fr.apk
    └── split_config.xxhdpi.apk
```

---

## ❌ Problème rencontré

### Erreur d'installation
```
Failure [INSTALL_PARSE_FAILED_MANIFEST_MALFORMED:
Failed parse during installPackageLI: /data/app/.../base.apk
(at Binary XML file line #90): <meta-data> requires an android:value
or android:resource attribute]
```

### Cause identifiée
Le manifest contient des entrées `android:resource="@null"` qui sont invalides :
```xml
<meta-data android:name="com.google.firebase.messaging.default_notification_icon"
           android:resource="@null"/>
<meta-data android:name="expo.modules.notifications.default_notification_icon"
           android:resource="@null"/>
```

### Tentatives de correction
1. **Modification manuelle du manifest** → Échec à la recompilation (problème de ressources `$`)
2. **Mise à jour d'apktool** (2.7.0 → 2.9.3) → Échec (framework Android 35 manquant)
3. **Installation du framework** → En cours

---

## 🔧 Solutions possibles pour la prochaine session

### Option 1 : Corriger le problème @null dans apk-mitm
- Ouvrir une issue sur le repo apk-mitm
- Ou forker et corriger le script de patch du manifest

### Option 2 : Utiliser un émulateur rootable
```bash
# Télécharger une image "Google APIs" (pas "Google Play Store")
sdkmanager "system-images;android-30;google_apis;x86_64"
avdmanager create avd -n test_mitm -k "system-images;android-30;google_apis;x86_64"
```
Avantage : On peut installer le certificat dans le système sans modifier l'APK.

### Option 3 : Télécharger un XAPK depuis APKPure
- Certaines versions pourraient ne pas avoir ce bug
- URL : https://apkpure.com/stokt-climbing/com.getstokt.stokt

### Option 4 : Utiliser Frida (nécessite téléphone rooté)
```bash
pip install frida-tools
frida -U -f com.getstokt.stokt -l ssl_bypass.js
```

### Option 5 : Passer à l'analyse sans interception
- Utiliser les données déjà extraites de l'analyse statique
- Concevoir le schéma SQLite basé sur les endpoints identifiés
- Créer des données mock pour le développement

---

## 📁 Fichiers de référence

| Fichier | Description |
|---------|-------------|
| `/docs/02_guide_interception_https.md` | Guide complet (à mettre à jour) |
| `/extracted/stockt_apk/stokt_bundle-patched.apks` | Bundle patché (non installable) |
| `/extracted/apk_mitm_bundle/` | Dossier de travail apk-mitm |
| `/tools/captures/` | Dossier pour les futures captures |

---

## 📊 Résumé

| Étape | Statut |
|-------|--------|
| Installation mitmproxy | ✅ |
| Patch APK avec apk-mitm | ✅ |
| Signature des splits | ✅ |
| Installation sur téléphone | ❌ Échec (manifest malformé) |
| Capture des requêtes | ⏳ En attente |

---

## 🚀 Prochaines étapes recommandées

1. **Court terme** : Tester avec un émulateur Android 30 (Google APIs) rootable
2. **Moyen terme** : Concevoir le schéma SQLite basé sur l'analyse statique
3. **Alternative** : Utiliser les données mock pour commencer le développement de mastoc

---

**Temps passé** : ~1h30 sur le patch APK
**Bloqueur principal** : Bug `@null` dans le manifest lors de la recompilation apktool
