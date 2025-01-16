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
                numVers = getValue((aLine))
            if aLine.startswith("__hexversion__"):
                hexVers = getValue((aLine))
            if aLine.startswith("__date__"):
                relDate = getValue((aLine))
    except Exception as exc:
        print("Could not read file: %s" % initFile)
        print(str(exc))

    if not beQuiet:
        print("novelWriter version: %s (%s) at %s" % (numVers, hexVers, relDate))

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
            print(f"Ignore: {relSrc}")
            continue
        if item.parent.is_dir() and item.parent.name != "__pycache__":
            dstDir = dst / relSrc.parent
            if not dstDir.exists():
                dstDir.mkdir(parents=True)
                print(f"Folder: {dstDir}")
        if item.is_file():
            shutil.copyfile(item, dst / relSrc)
            print(f"Copied: {dst / relSrc}")
    return


def copyPackageFiles(dst: Path, setupPy: bool = False) -> None:
    """Copy files needed for packaging."""
    copyFiles = ["LICENSE.md", "CREDITS.md", "pyproject.toml"]
    for copyFile in copyFiles:
        shutil.copyfile(copyFile, dst / copyFile)
        print("Copied: %s" % copyFile)

    writeFile(dst / "MANIFEST.in", (
        "include LICENSE.md\n"
        "include CREDITS.md\n"
        "recursive-include novelwriter/assets *\n"
    ))
    print("Wrote:  MANIFEST.in")

    if setupPy:
        writeFile(dst / "setup.py", (
            "import setuptools\n"
            "setuptools.setup()\n"
        ))
        print("Wrote:  setup.py")

    text = readFile(ROOT_DIR / "pyproject.toml")
    text = text.replace("setup/description_pypi.md", "data/description_short.txt")
    writeFile(dst / "pyproject.toml", text)
    print("Wrote:  pyproject.toml")

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
        with open(shaFile, mode="w") as fOut:
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


def readFile(file: Path) -> str:
    """Read an entire file and return as a string."""
    return file.read_text(encoding="utf-8")


def writeFile(file: Path, text: str) -> int:
    """Write string to file."""
    return file.write_text(text, encoding="utf-8")
