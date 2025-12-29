[app]

# --------------------------------------------------
# App metadata
# --------------------------------------------------
title = Domino Scorebook
package.name = domscores
package.domain = com.gicki

source.dir = .
source.include_exts = py,kv,json,png,jpg,ttf,dom

version = 0.5

# --------------------------------------------------
# Python / Kivy requirements
# --------------------------------------------------
requirements = kivy,kivymd,pyjnius

orientation = portrait
fullscreen = 0

# App icon
icon.filename = %(source.dir)s/data/icon.png
presplash.filename = %(source.dir)s/data/splash.png

# --------------------------------------------------
# Android configuration (CLEAN)
# --------------------------------------------------

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