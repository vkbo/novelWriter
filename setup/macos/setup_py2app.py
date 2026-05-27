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

Note on the chdir-to-build_py2app dance below: modern setuptools
auto-loads the project's pyproject.toml and refuses to coexist with
py2app's internal install_requires handling
("install_requires is no longer supported"). Running setup() from a
directory that does NOT contain pyproject.toml side-steps this.
"""
import os
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Make the novelwriter package importable for py2app's modulegraph scan.
sys.path.insert(0, str(ROOT))

# Run from a clean working directory without pyproject.toml.
WORK = ROOT / "build_py2app"
WORK.mkdir(exist_ok=True)
os.chdir(WORK)

from setuptools import setup  # noqa: E402  (must follow chdir/sys.path setup)

APP = [str(ROOT / "novelWriter.py")]
DATA_FILES = []

OPTIONS = {
    "argv_emulation": False,
    "iconfile": str(ROOT / "setup/macos/novelwriter.icns"),
    "plist": str(ROOT / "setup/macos/Info.plist"),
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
    # Write the .app where the workflow's subsequent steps expect it.
    "dist_dir": str(ROOT / "dist"),
}

setup(
    name="novelWriter",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
)
