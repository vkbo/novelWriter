#!/usr/bin/env python3
"""
py2app build configuration for the novelWriter macOS .app bundle.

Invoke from the repository root:
    python setup/macos/setup_py2app.py py2app

The companion workflow (.github/workflows/build-macos-dmg-py2app.yaml)
runs `pkgutils.py build-assets` first so that novelwriter/assets/
contains the compiled .qm translations, sample.zip, the PDF manual and
the optional icon themes before this script is invoked. The workflow
also copies novelwriter/assets/ to the correct in-bundle location after
py2app finishes — see comments there.
"""
from setuptools import setup

APP = ["novelWriter.py"]
DATA_FILES = []

OPTIONS = {
    "argv_emulation": False,
    "iconfile": "setup/macos/novelwriter.icns",
    "plist": "setup/macos/Info.plist",
    "packages": ["novelwriter", "PyQt6"],
    "includes": ["enchant"],
    "excludes": [
        "PyQt6.QtWebEngine",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtQml",
        "PyQt6.QtQuick",
        "PyQt6.QtWebChannel",
        "PyQt6.QtWebSockets",
        "tkinter",
    ],
    "optimize": 1,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
