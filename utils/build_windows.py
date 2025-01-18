"""
novelWriter – Windows Build
===========================

This file is a part of novelWriter
Copyright (C) 2025 Veronica Berglyd Olsen and novelWriter contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

import argparse
import compileall
import shutil
import subprocess
import sys
import urllib.request
import zipfile

from pathlib import Path

from utils.common import ROOT_DIR, SETUP_DIR, copySourceCode, extractVersion, readFile, writeFile


def prepareCode(outDir: Path) -> None:
    """Set up folders and copy code."""
    print("Copying and compiling novelWriter source ...")
    print("")

    copySourceCode(outDir)

    files = [
        ROOT_DIR / "CREDITS.md",
        ROOT_DIR / "LICENSE.md",
        ROOT_DIR / "requirements.txt",
        SETUP_DIR / "iss_license.txt",
        SETUP_DIR / "windows" / "novelWriter.ico",
        SETUP_DIR / "windows" / "novelWriter.exe",

    ]
    for item in files:
        shutil.copyfile(item, outDir / item.name)
        print(f"Copied: {item} > {outDir / item.name}")

    compileall.compile_dir(outDir / "novelwriter")

    print("Done")
    print("")

    return


def embedPython(bldDir: Path, outDir: Path) -> None:
    """Embed Python library."""
    print("Adding Python embeddable ...")

    pyVers = "%d.%d.%d" % (sys.version_info[:3])
    zipFile = f"python-{pyVers}-embed-amd64.zip"
    pyZip = bldDir / zipFile
    if not pyZip.is_file():
        pyUrl = f"https://www.python.org/ftp/python/{pyVers}/{zipFile}"
        print("Downloading: %s" % pyUrl)
        urllib.request.urlretrieve(pyUrl, pyZip)

    print("Extracting ...")
    with zipfile.ZipFile(pyZip, "r") as inFile:
        inFile.extractall(outDir)

    print("Done")
    print("")

    return


def installRequirements(libDir: Path) -> None:
    """Install dependencies."""
    print("Install dependencies ...")

    try:
        subprocess.call([
            sys.executable, "-m",
            "pip", "install", "-r", "requirements.txt", "--target", str(libDir)
        ])
    except Exception as exc:
        print("Failed with error:")
        print(str(exc))
        sys.exit(1)

    print("Done")
    print("")

    return


def removeRedundantQt(libDir: Path) -> None:
    """Delete Qt files that are not needed"""

    def unlinkIfFound(file: Path) -> None:
        if file.is_file():
            file.unlink()
            print(f"Deleted: {file}")

    def deleteFolder(folder: Path) -> None:
        if folder.is_dir():
            shutil.rmtree(folder)
            print(f"Deleted: {folder}")

    def unlinkIfPrefix(folder: Path, prefix: tuple[str, ...]) -> None:
        if folder.is_dir():
            for item in folder.iterdir():
                if item.name.startswith(prefix):
                    if item.is_file():
                        unlinkIfFound(item)
                    elif item.is_dir():
                        deleteFolder(item)

    print("Deleting Redundant Files")
    print("========================")
    print("")

    pyQt6Dir = libDir / "PyQt6"
    bindDir  = libDir / "PyQt6" / "bindings"
    qt6Dir   = libDir / "PyQt6" / "Qt6"
    binDir   = libDir / "PyQt6" / "Qt6" / "bin"
    plugDir  = libDir / "PyQt6" / "Qt6" / "plugins"
    qmDir    = libDir / "PyQt6" / "Qt6" / "translations"
    dictDir  = libDir / "enchant" / "data" / "mingw64" / "share" / "enchant" / "hunspell"

    for item in dictDir.iterdir():
        if not item.name.startswith(("en_GB", "en_US")):
            unlinkIfFound(item)

    for item in qmDir.iterdir():
        if not item.name.startswith("qtbase"):
            unlinkIfFound(item)

    bulkDel = ("QtQml", "Qt6Qml", "QtQuick", "Qt6Quick")
    unlinkIfPrefix(pyQt6Dir, bulkDel)
    unlinkIfPrefix(bindDir, bulkDel)
    unlinkIfPrefix(binDir, bulkDel)

    delQt6 = [
        "Qt6Bluetooth", "Qt6DBus", "Qt6Designer", "Qt6Help", "Qt6Multimedia",
        "Qt6MultimediaWidgets", "Qt6Network", "Qt6Nfc", "Qt6OpenGL", "Qt6Positioning",
        "Qt6PositioningQuick", "Qt6Sensors", "Qt6SerialPort", "Qt6Sql", "Qt6Test",
        "Qt6TextToSpeech", "Qt6WebChannel", "Qt6WebSockets", "Qt6Xml",
    ]
    for item in delQt6:
        qtItem = item.replace("Qt6", "Qt")
        unlinkIfFound(binDir / f"{item}.dll")
        unlinkIfFound(pyQt6Dir / f"{qtItem}.pyd")
        unlinkIfFound(pyQt6Dir / f"{qtItem}.pyi")
        deleteFolder(bindDir / qtItem)

    delList = [
        binDir / "opengl32sw.dll",
        qt6Dir / "qml",
        plugDir / "renderers",
        plugDir / "sensors",
        plugDir / "sqldrivers",
        plugDir / "texttospeech",
        plugDir / "webview",
    ]
    for item in delList:
        unlinkIfFound(item)
        deleteFolder(item)

    print("Done")
    print("")

    return


def main(args: argparse.Namespace) -> None:
    """Set up a package with embedded Python and dependencies for
    Windows installation.
    """
    print("")
    print("Build Standalone Windows Package")
    print("================================")
    print("")

    numVers, _, _ = extractVersion()
    print("Version: %s" % numVers)

    bldDir = ROOT_DIR / "dist"
    outDir = bldDir / "novelWriter"
    libDir = outDir / "lib"
    if outDir.exists():
        shutil.rmtree(outDir)

    bldDir.mkdir(exist_ok=True)
    outDir.mkdir()
    libDir.mkdir()

    copySourceCode(outDir)
    embedPython(bldDir, outDir)
    installRequirements(libDir)
    removeRedundantQt(libDir)

    print("Updating starting script ...")
    writeFile(outDir / "novelWriter.pyw", (
        "#!/usr/bin/env python3\n"
        "import os\n"
        "import sys\n"
        "\n"
        "os.curdir = os.path.abspath(os.path.dirname(__file__))\n"
        "sys.path.insert(0, os.path.join(os.curdir, \"lib\"))\n"
        "\n"
        "if __name__ == \"__main__\":\n"
        "    import novelwriter\n"
        "    novelwriter.main(sys.argv[1:])\n"
    ))
    print("Done")
    print("")

    print("Running Inno Setup")
    print("##################")
    print("")

    # Read the iss template
    issData = readFile(SETUP_DIR / "win_setup_embed.iss")
    issData = issData.replace(r"%%version%%", numVers)
    issData = issData.replace(r"%%dist%%", str(bldDir))
    writeFile(ROOT_DIR / "setup.iss", issData)
    print("")

    try:
        subprocess.call(["iscc", "setup.iss"])
    except Exception as exc:
        print("Inno Setup failed with error:")
        print(str(exc))
        sys.exit(1)

    print("")
    print("Done")
    print("")

    return
