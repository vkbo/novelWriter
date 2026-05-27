#!/usr/bin/env python3
"""
py2app build configuration for the novelWriter macOS .app bundle.

Invoke from the repository root:
    python setup/macos/setup_py2app.py py2app

The companion workflow (.github/workflows/build-macos-dmg-py2app.yaml)
runs `pkgutils.py build-assets` first so that novelwriter/assets/
contains the compiled .qm translations, sample.zip, the PDF manual and
the optional icon themes before this script is invoked.

The chdir-to-build_py2app dance below side-steps a setuptools/py2app
incompatibility: modern setuptools auto-loads the project's
pyproject.toml, whose PEP 621 [project] table refuses to coexist with
py2app's internal install_requires handling
("install_requires is no longer supported"). Running setup() from a
directory that does NOT contain pyproject.toml avoids the auto-load.
"""
import os
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

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
    "dist_dir": str(ROOT / "dist"),
}


def main() -> None:
    sys.path.insert(0, str(ROOT))
    work = ROOT / "build_py2app"
    work.mkdir(exist_ok=True)
    os.chdir(work)

    from setuptools import setup

    setup(
        name="novelWriter",
        app=[str(ROOT / "novelWriter.py")],
        options={"py2app": OPTIONS},
    )


if __name__ == "__main__":
    main()
