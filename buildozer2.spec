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

# This is the visual version user sees (e.g. "1.2")
version = 1.2

# --------------------------------------------------
# Python / Kivy requirements
# --------------------------------------------------
# Pinned libraries ensure stability.
requirements = python3,kivy,kivymd,android,pillow,pyjnius

orientation = portrait
fullscreen = 1

# App icon
icon.filename = %(source.dir)s/data/icon.png
presplash.filename = %(source.dir)s/data/splash.png

# --------------------------------------------------
# Android configuration
# --------------------------------------------------
# (CRITICAL) Set to 'aab' for Google Play Store release
android.release_artifact = aab

# (CRITICAL) Google Play requires Target API 34+
android.api = 34
android.minapi = 21

# (CRITICAL) Version code must be an integer and increase with every release.
# Example: 1, 2, 3... (Google Play tracks this, not the 'version' string above)
android.numeric_version = 1

# NDK version recommended by python-for-android
android.ndk = 25b

# Supported architectures (Required for 64-bit support on Play Store)
android.archs = arm64-v8a, armeabi-v7a

# Permissions
# NOTE: 'MANAGE_EXTERNAL_STORAGE' is restricted by Google Play. 
# Only use if you are a File Manager app. I have disabled it for safety.
# android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Accept licenses automatically (CI)
android.accept_sdk_license = True

# Enable auto-backup
android.allow_backup = True

bootstrap = sdl2

# --------------------------------------------------
# Buildozer configuration
# --------------------------------------------------
[buildozer]

# Verbose logs are useful in CI
log_level = 2

warn_on_root = 1
