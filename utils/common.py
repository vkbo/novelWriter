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
    initFile = Path("novelwriter") / "__init__.py"
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


def readFile(file: Path) -> str:
    """Read an entire file and return as a string."""
    return file.read_text(encoding="utf-8")


def writeFile(file: Path, text: str) -> int:
    """Write string to file."""
    return file.write_text(text, encoding="utf-8")
