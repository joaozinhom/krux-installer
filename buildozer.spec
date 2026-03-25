# =============================================================================
# buildozer.spec — Krux Installer Android APK
# =============================================================================
# Build targets:
#   debug APK  →  uv run poe build-android-debug
#   release AAB →  uv run poe build-android-release
#
# Prerequisites (Ubuntu / Debian):
#   sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool \
#       pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 \
#       cmake libffi-dev libssl-dev python3-pip
#   pip install buildozer cython
#
# The first run will download Android SDK, NDK and all p4a build deps (~5 GB).
# Use the official Kivy Docker image for reproducible CI builds:
#   docker run --rm -v "$PWD":/home/user/hostcwd kivy/buildozer android debug
# =============================================================================

[app]

# --------------------------------------------------------------------
# Identity
# --------------------------------------------------------------------
title           = Krux Installer
package.name    = kruxinstaller
package.domain  = io.selfcustody
version         = 0.0.22

# --------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------
# Tell buildozer where main.py (or the app entry point) lives.
# The top-level krux_installer.py is the entry point; buildozer
# expects it to be called main.py OR we point source.dir at the
# project root and set the main module explicitly below.
source.dir  = .

# Include all file types needed at runtime.
# "toml" is needed so pyproject.toml is available for setuptools/p4a.
source.include_exts = py,png,jpg,bmp,gif,kv,atlas,json,ttf,ico,icns,toml

# Exclude heavy dev/test artefacts from the APK.
source.exclude_dirs  = tests,e2e,e2e_drives,build,dist,htmlcov,.buildozer,.venv
source.exclude_exts  = spec,pyc

# --------------------------------------------------------------------
# Presplash & icon
# --------------------------------------------------------------------
presplash.filename  = %(source.dir)s/assets/welcome.bmp
icon.filename       = %(source.dir)s/assets/icon.png

# --------------------------------------------------------------------
# Orientation & display
# --------------------------------------------------------------------
orientation = portrait
fullscreen  = 0

# --------------------------------------------------------------------
# Requirements
# --------------------------------------------------------------------
# Rules:
#  - Use the p4a recipe name where a recipe exists (kivy, requests,
#    cryptography, pyserial, android).
#  - Pure-Python packages that have no C extensions can be listed by
#    their PyPI name and p4a will pip-install them.
#  - pysudoer and pyinstaller are desktop-only tools — excluded here.
#
# NOTE: "android" in requirements pulls in the pyjnius/android bridge
# needed for USB OTG / serial access on Android.
requirements =
    python3,
    kivy==2.3.1,
    pyserial,
    requests,
    cryptography,
    qrcode,
    android,
    pillow,
    pygame

# Whitelist termios.so so that pyserial can open USB-CDC serial ports
# (K210 devices enumerate as /dev/ttyACM* or similar via USB OTG).
android.whitelist = lib-dynload/termios.so

# --------------------------------------------------------------------
# Android permissions
# --------------------------------------------------------------------
android.permissions =
    android.permission.INTERNET,
    android.permission.USB_PERMISSION,
    android.hardware.usb.host

# USB host feature declaration (required to appear in the manifest).
android.features = android.hardware.usb.host

# Intent filter so Android routes USB device-attach events to the app.
# Create the file at:  src/android/intent-filter.xml
# (see notes at the bottom of this file for the XML content)
android.manifest.intent_filters = src/android/intent-filter.xml

# --------------------------------------------------------------------
# Android SDK / NDK
# --------------------------------------------------------------------
# Target and minimum API levels.
# API 33 = Android 13, widely adopted; minapi 24 = Android 7 (covers
# virtually all devices still in use that support USB OTG).
android.api    = 33
android.minapi = 24

# NDK 25b is stable and well-tested with python-for-android.
android.ndk = 25b

# Build for the two dominant ABIs: 64-bit ARM (modern) and 32-bit ARM
# (older/budget devices).  Add x86_64 if you want emulator support.
android.archs = arm64-v8a, armeabi-v7a

# Automatically accept SDK licences in CI (set False for local dev if
# you prefer to review them manually).
android.accept_sdk_license = True

# --------------------------------------------------------------------
# Release artifact format
# --------------------------------------------------------------------
# debug builds produce an APK for side-loading/testing.
# release builds produce an AAB for the Play Store; change to "apk"
# if you only want a side-loadable release binary.
android.debug_artifact   = apk
android.release_artifact = aab

# --------------------------------------------------------------------
# Miscellaneous Android settings
# --------------------------------------------------------------------
android.allow_backup = False

# Kivy's default PythonActivity is correct for this app.
# android.entrypoint = org.kivy.android.PythonActivity

# Keep logcat verbose during development.
android.logcat_filters = *:S python:D

# --------------------------------------------------------------------
# python-for-android (p4a) settings
# --------------------------------------------------------------------
# SDL2 bootstrap is required by Kivy.
p4a.bootstrap = sdl2

# Use the stable upstream p4a branch (tracks Kivy releases).
p4a.branch = master

# Expose pyproject.toml to p4a's setuptools integration so it can
# pick up metadata from the project without needing a setup.py.
# "toml" must also be in source.include_exts (already set above).
p4a.setup_py = false

# --------------------------------------------------------------------
# Buildozer global settings
# --------------------------------------------------------------------
[buildozer]
log_level   = 2
warn_on_root = 1

# =============================================================================
# NOTES
# =============================================================================
#
# 1. USB intent-filter (src/android/intent-filter.xml)
# -------------------------------------------------------
# Create this file to receive USB device-attach events:
#
#   <?xml version="1.0" encoding="utf-8"?>
#   <resources>
#       <intent-filter>
#           <action android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED"/>
#       </intent-filter>
#       <meta-data
#           android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED"
#           android:resource="@xml/device_filter"/>
#   </resources>
#
# And create src/android/res/xml/device_filter.xml:
#
#   <?xml version="1.0" encoding="utf-8"?>
#   <resources>
#       <usb-device vendor-id="0x0403" />   <!-- FTDI (most K210 boards) -->
#       <usb-device vendor-id="0x1a86" />   <!-- CH340/CH341            -->
#       <usb-device vendor-id="0x10c4" />   <!-- Silicon Labs CP210x    -->
#   </resources>
#
# 2. Release signing
# ------------------
# To produce a signed release APK/AAB set the following env vars
# before running `buildozer android release`:
#
#   KEYSTORE_FILE, KEYSTORE_ALIAS, KEYSTORE_PASSWD, KEY_PASSWD
#
# 3. cryptography / cffi on Android
# ------------------------------------
# The `cryptography` package requires cffi which has a p4a recipe.
# If the build fails on cffi, pin the version:
#   requirements = ..., cryptography==42.0.8, cffi==1.16.0
#
# =============================================================================