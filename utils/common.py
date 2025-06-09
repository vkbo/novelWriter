"""
novelWriter – Common Utils
==========================

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

import shutil
import subprocess
import sys

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
SETUP_DIR = ROOT_DIR / "setup"


def extractVersion(beQuiet: bool = False) -> tuple[str, str, str]:
    """Extract the novelWriter version number without having to import
    anything else from the main package.
    """
    def getValue(text: str) -> str:
        bits = text.partition("=")
        return bits[2].strip().strip('"')

    numVers = "0"
    hexVers = "0x0"
    relDate = "Unknown"
    initFile = ROOT_DIR / "novelwriter" / "__init__.py"
    try:
        for aLine in initFile.read_text(encoding="utf-8").splitlines():
            if aLine.startswith("__version__"):
                numVers = getValue(aLine)
            if aLine.startswith("__hexversion__"):
                hexVers = getValue(aLine)
            if aLine.startswith("__date__"):
                relDate = getValue(aLine)
    except Exception as exc:
        print(f"Could not read file: {initFile}")
        print(str(exc))

    if not beQuiet:
        print(f"novelWriter version: {numVers} ({hexVers}) at {relDate}")

    return numVers, hexVers, relDate


def stripVersion(version: str) -> str:
    """Strip the pre-release part from a version number."""
    if "a" in version:
        return version.partition("a")[0]
    elif "b" in version:
        return version.partition("b")[0]
    elif "rc" in version:
        return version.partition("rc")[0]
    else:
        return version


def copySourceCode(dst: Path) -> None:
    """Copy the novelwriter source tree to path."""
    src = ROOT_DIR / "novelwriter"
    for item in src.glob("**/*"):
        relSrc = item.relative_to(ROOT_DIR)
        if item.suffix in (".pyc", ".pyo"):
            print("Ignored:", relSrc)
            continue
        if item.parent.is_dir() and item.parent.name != "__pycache__":
            dstDir = dst / relSrc.parent
            if not dstDir.exists():
                dstDir.mkdir(parents=True)
                print("Created:", dstDir.relative_to(ROOT_DIR))
        if item.is_file():
            shutil.copyfile(item, dst / relSrc)
            print("Copied:", relSrc)
    return


def copyPackageFiles(dst: Path, setupPy: bool = False) -> None:
    """Copy files needed for packaging."""
    copyFiles = ["LICENSE.md", "CREDITS.md", "pyproject.toml"]
    for copyFile in copyFiles:
        shutil.copyfile(copyFile, dst / copyFile)
        print("Copied:", copyFile)

    writeFile(dst / "MANIFEST.in", (
        "include LICENSE.md\n"
        "include CREDITS.md\n"
        "recursive-include novelwriter/assets *\n"
    ))

    if setupPy:
        writeFile(dst / "setup.py", (
            "import setuptools\n"
            "setuptools.setup()\n"
        ))

    text = readFile(ROOT_DIR / "pyproject.toml")
    text = text.replace("setup/description_pypi.md", "data/description_short.txt")
    writeFile(dst / "pyproject.toml", text)

    return


def toUpload(srcPath: str | Path, dstName: str | None = None) -> None:
    """Copy a file produced by one of the build functions to the upload
    directory. The file can optionally be given a new name.
    """
    uplDir = Path("dist_upload")
    uplDir.mkdir(exist_ok=True)
    srcPath = Path(srcPath)
    shutil.copyfile(srcPath, uplDir / (dstName or srcPath.name))
    return


def makeCheckSum(sumFile: str, cwd: Path | None = None) -> str:
    """Create a SHA256 checksum file."""
    try:
        if cwd is None:
            shaFile = f"{sumFile}.sha256"
        else:
            shaFile = cwd / f"{sumFile}.sha256"
        with open(shaFile, mode="w", encoding="utf-8") as fOut:
            subprocess.call(["shasum", "-a", "256", sumFile], stdout=fOut, cwd=cwd)
        print(f"SHA256 Sum: {shaFile}")
    except Exception as exc:
        print("Could not generate sha256 file")
        print(str(exc))
        return ""

    return str(shaFile)


def checkAssetsExist() -> bool:
    """Check that the necessary assets exist ahead of a build."""
    hasSample = False
    hasManual = False
    hasQmData = False

    sampleZip = ROOT_DIR / "novelwriter" / "assets" / "sample.zip"
    if sampleZip.is_file():
        print(f"Found: {sampleZip}")
        hasSample = True

    pdfManual = ROOT_DIR / "novelwriter" / "assets" / "manual.pdf"
    if pdfManual.is_file():
        print(f"Found: {pdfManual}")
        hasManual = True

    i18nAssets = ROOT_DIR / "novelwriter" / "assets" / "i18n"
    if len(list(i18nAssets.glob("*.qm"))) > 0:
        print(f"Found: {i18nAssets}/*.qm")
        hasQmData = True

    return hasSample and hasManual and hasQmData


def appdataXml() -> str:
    """Generate the appdata XML content."""
    raw = readFile(SETUP_DIR / "description_short.txt")
    desc = " ".join(raw.strip().splitlines()).strip()
    xml = readFile(SETUP_DIR / "novelwriter.appdata.xml")
    xml = xml.format(description=desc)
    return xml


def readFile(file: Path) -> str:
    """Read an entire file and return as a string."""
    return file.read_text(encoding="utf-8")


def writeFile(file: Path, text: str) -> int:
    """Write string to file."""
    result = file.write_text(text, encoding="utf-8")
    print("Wrote:", file.relative_to(ROOT_DIR))
    return result


def freshFolder(path: Path) -> None:
    """Make sure a folder exists and is empty."""
    if path.exists():
        print("Removing:", str(path))
        shutil.rmtree(path)
    path.mkdir()
    return


def systemCall(cmd: list, cwd: Path | str | None = None, env: dict | None = None) -> None:
    """Make a system call using subprocess."""
    if isinstance(cwd, Path):
        cwd = str(cwd)
    try:
        subprocess.call([str(c) for c in cmd], cwd=cwd, env=env)
    except Exception as exc:
        print("ERROR:", str(exc))
        sys.exit(1)
    return


def removeRedundantQt(qtBase: Path) -> None:
    """Delete Qt files that are not needed"""

    def unlinkIfFound(file: Path) -> None:
        if file.is_file():
            file.unlink()
            print("Deleted:", file.relative_to(ROOT_DIR))

    def deleteFolder(folder: Path) -> None:
        if folder.is_dir():
            shutil.rmtree(folder)
            print("Deleted:", folder.relative_to(ROOT_DIR))

    def unlinkIfPrefix(folder: Path, prefix: tuple[str, ...]) -> None:
        if folder.is_dir():
            for item in folder.iterdir():
                if item.name.startswith(prefix):
                    if item.is_file():
                        unlinkIfFound(item)
                    elif item.is_dir():
                        deleteFolder(item)

    print("Deleting redundant files ...")

    pyQt6Dir = qtBase / "PyQt6"
    bindDir  = qtBase / "PyQt6" / "bindings"
    qt6Dir   = qtBase / "PyQt6" / "Qt6"
    binDir   = qtBase / "PyQt6" / "Qt6" / "bin"
    libDir   = qtBase / "PyQt6" / "Qt6" / "lib"
    plugDir  = qtBase / "PyQt6" / "Qt6" / "plugins"
    qmDir    = qtBase / "PyQt6" / "Qt6" / "translations"
    dictDir  = qtBase / "enchant" / "data" / "mingw64" / "share" / "enchant" / "hunspell"

    # Prune Dictionaries
    if dictDir.exists():
        for item in dictDir.iterdir():
            if not item.name.startswith(("en_GB", "en_US")):
                unlinkIfFound(item)

    # Prune Translations
    for item in qmDir.iterdir():
        if not item.name.startswith("qtbase"):
            unlinkIfFound(item)

    # Delete Modules
    modules = [
        "Qt6Qml", "Qt6Quick", "Qt6Bluetooth", "Qt6Nfc",
        "Qt6Sensors", "Qt6SerialPort", "Qt6Test",
    ]
    modules.extend([x.replace("Qt6", "Qt") for x in modules])
    modules.extend([f"lib{x}" for x in modules])
    modules = tuple(modules)

    unlinkIfPrefix(pyQt6Dir, modules)
    unlinkIfPrefix(bindDir, modules)
    unlinkIfPrefix(binDir, modules)
    unlinkIfPrefix(libDir, modules)

    # Other Files
    deleteFolder(qt6Dir / "qml")
    deleteFolder(plugDir / "qmlls")
    deleteFolder(plugDir / "qmllint")

    return
