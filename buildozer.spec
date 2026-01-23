[app]

# --------------------------------------------------
# App metadata
# --------------------------------------------------
title = Domino Scorebook
package.name = dominoscores
package.domain = com.gicki

source.dir = .
source.include_exts = py,kv,json,png,jpg,ttf,dom
exclude_patterns = **/test*, **/tests*, **/Testing*

version = 0.8.3

# --------------------------------------------------
# Python / Kivy requirements
# --------------------------------------------------
requirements = kivy,kivymd,android
#old requirements:
#requirements = kivy,kivymd,pyjnius,android

orientation = portrait
fullscreen = 1

# App icon
icon.filename = %(source.dir)s/data/icon.png
presplash.filename = %(source.dir)s/data/splash.png

# --------------------------------------------------
# Android configuration (CLEAN)
# --------------------------------------------------
#android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
#android.manifest.application_arguments = --requestLegacyExternalStorage="true"


# Target Android SDK
android.api = 33
android.sdk = 33

# Minimum supported Android version
android.minapi = 21

# NDK version recommended by python-for-android
android.ndk = 25b

# Supported architectures
android.archs = arm64-v8a, armeabi-v7a

# Accept licenses automatically (CI)
android.accept_sdk_license = True

# Enable auto-backup
android.allow_backup = True

bootstrap = sdl2

# --------------------------------------------------
# Python-for-Android (p4a)
# --------------------------------------------------

# Default bootstrap is correct for Kivy
# p4a.bootstrap = sdl2


# --------------------------------------------------
# Buildozer configuration
# --------------------------------------------------
[buildozer]

# Verbose logs are useful in CI
log_level = 2

warn_on_root = 1
