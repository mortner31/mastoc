#!/bin/bash
# Script pour configurer l'émulateur Android avec mitmproxy
# Usage: ./setup_emulator_proxy.sh

ANDROID_SDK="$HOME/Android/Sdk"
EMULATOR="$ANDROID_SDK/emulator/emulator"
ADB="$ANDROID_SDK/platform-tools/adb"
AVD_NAME="Medium_Phone_API_36.1"
PROXY_HOST="10.0.2.2"  # Adresse spéciale pour localhost depuis l'émulateur
PROXY_PORT="8080"
CERT_PATH="$HOME/.mitmproxy/mitmproxy-ca-cert.cer"
APK_PATH="/media/veracrypt1/Repositories/mastock/extracted/stockt_apk/base.apk"
CAPTURES_DIR="/media/veracrypt1/Repositories/mastock/tools/captures"

echo "=== Configuration Émulateur Android pour Capture Réseau ==="
echo ""

# Étape 1: Lancer mitmdump en arrière-plan
echo "[1/6] Lancement de mitmdump..."
mkdir -p "$CAPTURES_DIR"
mitmdump -w "$CAPTURES_DIR/stokt_capture.flow" --set flow_detail=2 > "$CAPTURES_DIR/mitmdump.log" 2>&1 &
MITM_PID=$!
echo "mitmdump lancé (PID: $MITM_PID)"
sleep 2

# Étape 2: Lancer l'émulateur avec proxy
echo "[2/6] Lancement de l'émulateur $AVD_NAME avec proxy..."
echo "Commande: $EMULATOR -avd $AVD_NAME -http-proxy http://$PROXY_HOST:$PROXY_PORT -writable-system &"
$EMULATOR -avd "$AVD_NAME" -http-proxy "http://$PROXY_HOST:$PROXY_PORT" -writable-system &
EMU_PID=$!
echo "Émulateur lancé (PID: $EMU_PID)"

echo "[3/6] Attente du démarrage de l'émulateur..."
$ADB wait-for-device
sleep 10
echo "Émulateur démarré!"

# Étape 3: Installer le certificat CA
echo "[4/6] Installation du certificat CA mitmproxy..."
# Copier le certificat
$ADB push "$CERT_PATH" /sdcard/mitmproxy-ca-cert.cer
echo "Certificat copié sur l'émulateur"
echo ""
echo ">>> ACTION MANUELLE REQUISE <<<"
echo "Sur l'émulateur, allez dans:"
echo "  Paramètres → Sécurité → Chiffrement et identifiants → Installer un certificat → Certificat CA"
echo "  Puis sélectionnez le fichier mitmproxy-ca-cert.cer"
echo ""
read -p "Appuyez sur Entrée une fois le certificat installé..."

# Étape 4: Installer l'APK Stōkt
echo "[5/6] Installation de l'APK Stōkt..."
if [ -f "$APK_PATH" ]; then
    $ADB install -r "$APK_PATH"
    echo "APK installé!"
else
    echo "APK non trouvé: $APK_PATH"
fi

# Étape 5: Instructions finales
echo ""
echo "[6/6] Configuration terminée!"
echo ""
echo "=== INSTRUCTIONS ==="
echo "1. Ouvrez l'application Stōkt sur l'émulateur"
echo "2. Connectez-vous et naviguez dans l'app"
echo "3. Les requêtes sont capturées dans: $CAPTURES_DIR/stokt_capture.flow"
echo "4. Pour voir les logs en direct: tail -f $CAPTURES_DIR/mitmdump.log"
echo ""
echo "Pour arrêter:"
echo "  kill $MITM_PID  # Arrêter mitmdump"
echo "  kill $EMU_PID   # Arrêter l'émulateur"
echo ""
echo "Pour analyser la capture ensuite:"
echo "  mitmproxy -r $CAPTURES_DIR/stokt_capture.flow"
