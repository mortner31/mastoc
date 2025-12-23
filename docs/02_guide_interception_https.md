# Guide d'Interception HTTPS avec mitmproxy

Ce document décrit la procédure complète pour intercepter le trafic HTTPS de l'application Stōkt.

---

## Prérequis

### Outils nécessaires
- **mitmproxy** : `pip install mitmproxy`
- **Node.js + npx** : pour apk-mitm
- **ADB** : Android Debug Bridge
- **Java JDK** : pour keytool et jarsigner

### Vérification
```bash
mitmproxy --version
npx --version
adb version
java -version
keytool -help
```

---

## Étape 1 : Patcher l'APK

### Option A : Utiliser apk-mitm (recommandé)

```bash
cd /media/veracrypt1/Repositories/mastoc/extracted/stockt_apk

# Patcher l'APK principal
npx apk-mitm base.apk

# Résultat : base-patched.apk
```

**Ce que fait apk-mitm automatiquement :**
1. Décompile l'APK
2. Modifie `network_security_config.xml` pour accepter les certificats utilisateur
3. Désactive le certificate pinning dans OkHttp
4. Recompile et signe l'APK

### Option B : Patch manuel (si apk-mitm échoue)

1. **Modifier network_security_config.xml** :
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

2. **Recompiler** : `apktool b stockt_decompiled -o patched.apk --use-aapt2`
3. **Signer** : voir section signature ci-dessous

---

## Étape 2 : Gérer les Split APKs

Stōkt utilise Android App Bundle (split APKs). Tous doivent avoir la **même signature**.

### Fichiers requis
- `base-patched.apk` - APK principal patché
- `split_config.arm64_v8a.apk` - Libs natives (pour arm64)
- `split_config.fr.apk` - Ressources françaises
- `split_config.xxhdpi.apk` - Ressources haute densité

### Re-signer avec la même clé

```bash
# 1. Créer un keystore de debug
keytool -genkey -v -keystore debug.keystore \
    -storepass android -alias androiddebugkey -keypass android \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -dname "CN=Android Debug,O=Android,C=US"

# 2. Supprimer l'ancienne signature du base-patched
zip -d base-patched.apk "META-INF/*"

# 3. Signer tous les APKs avec la même clé
for apk in base-patched.apk split_config.*.apk; do
    jarsigner -sigalg SHA256withRSA -digestalg SHA-256 \
        -keystore debug.keystore -storepass android \
        "$apk" androiddebugkey
done
```

---

## Étape 3 : Installer sur le téléphone

### Via ADB (recommandé)
```bash
adb install-multiple \
    base-patched.apk \
    split_config.arm64_v8a-signed.apk \
    split_config.fr-signed.apk \
    split_config.xxhdpi-signed.apk
```

### Via SAI (Split APKs Installer)
1. Installer SAI depuis le Play Store
2. Transférer les APKs sur le téléphone
3. Ouvrir SAI et sélectionner tous les APKs

**Note** : Désinstaller d'abord l'app originale si présente (signatures différentes).

---

## Étape 4 : Configurer mitmproxy

### Lancer le proxy
```bash
# Capture simple
mitmdump -w captures/stokt.flow

# Avec interface web
mitmweb

# Filtrer uniquement getstokt.com
mitmdump -w captures/stokt.flow --set flow_detail=2 \
    "~d getstokt.com"
```

### Trouver l'IP du PC
```bash
hostname -I | awk '{print $1}'
# Exemple : 192.168.10.69
```

---

## Étape 5 : Configurer le téléphone

### Configurer le proxy WiFi
1. **Paramètres WiFi** → Réseau actuel → **Modifier**
2. **Options avancées** → **Proxy manuel**
3. Entrer :
   - Hôte : `<IP_DU_PC>` (ex: 192.168.10.69)
   - Port : `8080`

### Installer le certificat CA
1. Ouvrir le navigateur sur : `http://mitm.it`
2. Télécharger le certificat Android
3. **Paramètres → Sécurité → Installer certificat → CA**
4. Sélectionner le fichier téléchargé

---

## Étape 6 : Capturer le trafic

1. **Lancer mitmproxy** sur le PC
2. **Ouvrir Stōkt** sur le téléphone
3. **Naviguer** dans l'app (connexion, salles, blocs...)
4. Les requêtes apparaissent dans mitmproxy

### Analyser la capture
```bash
# Ouvrir une capture existante
mitmproxy -r captures/stokt.flow

# Exporter en HAR (pour analyse)
mitmdump -r captures/stokt.flow --set hardump=captures/stokt.har

# Filtrer par domaine
mitmproxy -r captures/stokt.flow "~d getstokt.com"
```

---

## Fichiers de référence

| Fichier | Emplacement |
|---------|-------------|
| APKs patchés | `/extracted/stockt_patched/` |
| Keystore debug | `/extracted/stockt_patched/debug.keystore` |
| Captures | `/tools/captures/` |
| APK original | `/extracted/stockt_apk/base.apk` |
| APK décompilé | `/extracted/stockt_decompiled/` |

---

## Dépannage

### L'app ne se connecte pas
- Vérifier que le proxy est bien configuré sur le téléphone
- Vérifier que mitmproxy est lancé
- Vérifier le pare-feu (`sudo ufw allow 8080`)

### Erreur de certificat
- Réinstaller le certificat CA
- Vérifier que l'APK patché est bien installé
- Utiliser `adb logcat | grep -i ssl` pour débugger

### L'app plante au démarrage
- Vérifier que tous les split APKs sont installés
- Vérifier qu'ils ont la même signature
- Essayer sur un émulateur

### L'API rejette les requêtes
- Le backend peut vérifier la signature de l'app
- Essayer avec un émulateur rooté + certificat système
- Analyser le bundle JS pour comprendre l'auth

---

## Commandes rapides

```bash
# === SETUP COMPLET ===

# 1. Patcher
cd /media/veracrypt1/Repositories/mastoc/extracted/stockt_apk
npx apk-mitm base.apk

# 2. Re-signer les splits
keytool -genkey -v -keystore debug.keystore -storepass android \
    -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 \
    -validity 10000 -dname "CN=Android Debug,O=Android,C=US"

zip -d base-patched.apk "META-INF/*"

for apk in base-patched.apk split_config.arm64_v8a.apk split_config.fr.apk split_config.xxhdpi.apk; do
    jarsigner -sigalg SHA256withRSA -digestalg SHA-256 \
        -keystore debug.keystore -storepass android "$apk" androiddebugkey
done

# 3. Installer
adb install-multiple base-patched.apk split_config.*.apk

# 4. Lancer mitmproxy
mitmdump -w ../tools/captures/stokt.flow --set flow_detail=2

# 5. Configurer proxy sur téléphone : <IP>:8080
# 6. Installer certificat : http://mitm.it
# 7. Ouvrir l'app et capturer !
```

---

**Dernière mise à jour** : 2025-12-20
