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
"""  # noqa
from __future__ import annotations

import shutil
import subprocess
import sys
import tomllib

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
SETUP_DIR = ROOT_DIR / "setup"

MIN_QT_VERS = "6.4"
MIN_PY_VERSION = "3.11"


def extractReqs(groups: list[str]) -> list[str]:
    """Extract dependency groups from pyproject.toml."""
    data = tomllib.loads((ROOT_DIR / "pyproject.toml").read_text(encoding="utf-8"))
    reqs = []
    if "app" in groups or "all" in groups:
        reqs += data["project"]["dependencies"]
    for group in data["dependency-groups"]:
        if group in groups or "all" in groups:
            reqs += [d for d in data["dependency-groups"][group] if isinstance(d, str)]
    return reqs


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
        print(f"Could not read file: {initFile}", flush=True)
        print(str(exc), flush=True)

    if not beQuiet:
        print(f"novelWriter version: {numVers} ({hexVers}) at {relDate}", flush=True)

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
            print("Ignored:", relSrc, flush=True)
            continue
        if item.parent.is_dir() and item.parent.name != "__pycache__":
            dstDir = dst / relSrc.parent
            if not dstDir.exists():
                dstDir.mkdir(parents=True)
                print("Created:", dstDir.relative_to(ROOT_DIR), flush=True)
        if item.is_file():
            shutil.copyfile(item, dst / relSrc)
            print("Copied:", relSrc, flush=True)


def copyPackageFiles(dst: Path, oldLicense: bool = False) -> None:
    """Copy files needed for packaging."""
    copyFiles = [
        ROOT_DIR / "LICENSE.md",
        SETUP_DIR / "LICENSE-Apache-2.0.txt",
        ROOT_DIR / "CREDITS.md",
        ROOT_DIR / "pyproject.toml",
    ]
    for copyFile in copyFiles:
        shutil.copyfile(copyFile, dst / copyFile.name)
        print("Copied:", copyFile, flush=True)

    writeFile(dst / "MANIFEST.in", (
        "include LICENSE.md\n"
        "include LICENSE-Apache-2.0.txt\n"
        "include CREDITS.md\n"
        "recursive-include novelwriter/assets *\n"
    ))

    text = readFile(ROOT_DIR / "pyproject.toml")
    text = text.replace("setup/description_pypi.md", "data/description_short.txt")
    if oldLicense:
        new = []
        for line in text.splitlines():
            if line.startswith("license = "):
                line = 'license = {text = "GPL-3.0-or-later AND Apache-2.0 AND CC-BY-4.0"}'
            if line.startswith("license-files = "):
                continue
            new.append(line)
        text = "\n".join(new)
    writeFile(dst / "pyproject.toml", text)


def toUpload(srcPath: str | Path, dstName: str | None = None) -> None:
    """Copy a file produced by one of the build functions to the upload
    directory. The file can optionally be given a new name.
    """
    uplDir = Path("dist_upload")
    uplDir.mkdir(exist_ok=True)
    srcPath = Path(srcPath)
    shutil.copyfile(srcPath, uplDir / (dstName or srcPath.name))


def makeCheckSum(sumFile: str, cwd: Path | None = None) -> str:
    """Create a SHA256 checksum file."""
    try:
        if cwd is None:
            shaFile = f"{sumFile}.sha256"
        else:
            shaFile = cwd / f"{sumFile}.sha256"
        with open(shaFile, mode="w", encoding="utf-8") as fOut:
            subprocess.call(["shasum", "-a", "256", sumFile], stdout=fOut, cwd=cwd)
        print(f"SHA256 Sum: {shaFile}", flush=True)
    except Exception as exc:
        print("Could not generate sha256 file", flush=True)
        print(str(exc), flush=True)
        return ""

    return str(shaFile)


def checkAssetsExist() -> bool:
    """Check that the necessary assets exist ahead of a build."""
    hasSample = False
    hasManual = False
    hasQmData = False

    sampleZip = ROOT_DIR / "novelwriter" / "assets" / "sample.zip"
    if sampleZip.is_file():
        print(f"Found: {sampleZip}", flush=True)
        hasSample = True

    pdfManual = ROOT_DIR / "novelwriter" / "assets" / "manual.pdf"
    if pdfManual.is_file():
        print(f"Found: {pdfManual}", flush=True)
        hasManual = True

    i18nAssets = ROOT_DIR / "novelwriter" / "assets" / "i18n"
    if len(list(i18nAssets.glob("*.qm"))) > 0:
        print(f"Found: {i18nAssets}/*.qm", flush=True)
        hasQmData = True

    return hasSample and hasManual and hasQmData


def appdataXml() -> str:
    """Generate the appdata XML content."""
    raw = readFile(SETUP_DIR / "description_short.txt")
    desc = " ".join(raw.strip().splitlines()).strip()
    return readFile(SETUP_DIR / "novelwriter.appdata.xml").format(description=desc)


def readFile(file: Path) -> str:
    """Read an entire file and return as a string."""
    return file.read_text(encoding="utf-8")


def writeFile(file: Path, text: str) -> int:
    """Write string to file."""
    result = file.write_text(text, encoding="utf-8")
    print("Wrote:", file.relative_to(ROOT_DIR), flush=True)
    return result


def freshFolder(path: Path) -> None:
    """Make sure a folder exists and is empty."""
    if path.exists():
        print("Removing:", str(path), flush=True)
        shutil.rmtree(path)
    path.mkdir()


def systemCall(cmd: list, cwd: Path | str | None = None, env: dict | None = None) -> int:
    """Make a system call using subprocess."""
    if isinstance(cwd, Path):
        cwd = str(cwd)
    try:
        code = subprocess.call([str(c) for c in cmd], cwd=cwd, env=env)
    except Exception as exc:
        print("ERROR:", str(exc), flush=True)
        sys.exit(1)
    return code


def removeRedundantQt(qtBase: Path) -> None:
    """Delete Qt files that are not needed."""

    def unlinkIfFound(file: Path) -> None:
        if file.is_file():
            file.unlink()
            print("Deleted:", file.relative_to(ROOT_DIR), flush=True)

    def deleteFolder(folder: Path) -> None:
        if folder.is_dir():
            shutil.rmtree(folder)
            print("Deleted:", folder.relative_to(ROOT_DIR), flush=True)

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
