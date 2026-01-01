# Makefile pour mastoc Android
# Usage: make build, make deploy, make all

APK_PATH = app/build/outputs/apk/debug/app-debug.apk
PACKAGE = com.mastoc.app

.PHONY: all build deploy run clean

# Build + Deploy
all: build deploy

# Compile l'APK debug
build:
	@echo "Building debug APK..."
	./gradlew assembleDebug
	@echo "APK: $(APK_PATH)"

# Installe sur le téléphone connecté
deploy:
	@echo "Installing on device..."
	adb install -r $(APK_PATH)
	@echo "Done!"

# Build + Deploy + Lance l'app
run: all
	@echo "Launching app..."
	adb shell am start -n $(PACKAGE)/.MainActivity

# Nettoie les builds
clean:
	@echo "Cleaning..."
	./gradlew clean

# Affiche les devices connectés
devices:
	adb devices

# Logs de l'app
logs:
	adb logcat --pid=$$(adb shell pidof $(PACKAGE)) | grep -v "ViewRootImpl"

# Logs erreurs seulement
errors:
	adb logcat "*:E" | grep -i "$(PACKAGE)\|fatal\|crash\|exception"
