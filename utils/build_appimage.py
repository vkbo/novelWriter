"""
novelWriter – AppImage Build
============================

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
import datetime
import shutil
import subprocess
import sys

from utils.common import (
    ROOT_DIR, SETUP_DIR, appdataXml, copyPackageFiles, copySourceCode,
    extractVersion, makeCheckSum, toUpload, writeFile
)


def appImage(args: argparse.Namespace) -> None:
    """Build an AppImage."""
    try:
        import python_appimage  # noqa: F401 # type: ignore
    except ImportError:
        print(
            "ERROR: Package 'python-appimage' is missing on this system.\n"
            "       Please run 'pip install --user python-appimage' to install it.\n"
        )
        sys.exit(1)

    if sys.platform == "linux":
        print("ERROR: Command 'build-ubuntu' can only be used on Linux")
        sys.exit(1)

    print("")
    print("Build AppImage")
    print("==============")
    print("")

    linuxTag = args.linux_tag
    pythonVer = args.python_version

    # Version Info
    # ============

    pkgVers, _, relDate = extractVersion()
    relDate = datetime.datetime.strptime(relDate, "%Y-%m-%d")
    print("")

    # Set Up Folder
    # =============

    bldDir = ROOT_DIR / "dist_appimage"
    bldPkg = f"novelwriter_{pkgVers}"
    outDir = bldDir / bldPkg
    imgDir = bldDir / "appimage"

    # Set Up Folders
    # ==============

    bldDir.mkdir(exist_ok=True)

    if outDir.exists():
        print("Removing old build files ...")
        print("")
        shutil.rmtree(outDir)

    outDir.mkdir()

    if imgDir.exists():
        print("Removing old build metadata files ...")
        print("")
        shutil.rmtree(imgDir)

    imgDir.mkdir()

    # Remove old AppImages
    if images := bldDir.glob("*.AppImage"):
        print("Removing old AppImages")
        print("")
        for image in images:
            image.unlink()

    # Copy novelWriter Source
    # =======================

    print("Copying novelWriter source ...")
    print("")

    copySourceCode(outDir)

    print("")
    print("Copying or generating additional files ...")
    print("")

    copyPackageFiles(outDir)

    # Write Metadata
    # ==============

    writeFile(imgDir / "novelwriter.appdata.xml", appdataXml())
    print("Wrote:  novelwriter.appdata.xml")

    writeFile(imgDir / "entrypoint.sh", (
        '#! /bin/bash \n'
        '{{ python-executable }} -sE ${APPDIR}/opt/python{{ python-version }}/bin/novelwriter "$@"'
    ))
    print("Wrote:  entrypoint.sh")

    writeFile(imgDir / "requirements.txt", str(outDir))
    print("Wrote:  requirements.txt")

    shutil.copyfile(SETUP_DIR / "data" / "novelwriter.desktop", imgDir / "novelwriter.desktop")
    print("Copied: novelwriter.desktop")

    shutil.copyfile(SETUP_DIR / "icons" / "novelwriter.svg", imgDir / "novelwriter.svg")
    print("Copied: novelwriter.svg")

    shutil.copyfile(
        SETUP_DIR / "data" / "hicolor" / "256x256" / "apps" / "novelwriter.png",
        imgDir / "novelwriter.png"
    )
    print("Copied: novelwriter.png")

    # Build AppImage
    # ==============

    try:
        subprocess.call([
            sys.executable, "-m", "python_appimage", "build", "app",
            "-l", linuxTag, "-p", pythonVer, "appimage"
        ], cwd=bldDir)
    except Exception as exc:
        print("AppImage build: FAILED")
        print("")
        print(str(exc))
        print("")
        sys.exit(1)

    bldFile = list(bldDir.glob("*.AppImage"))[0]
    outFile = bldDir / f"novelWriter-{pkgVers}.AppImage"
    bldFile.rename(outFile)
    shaFile = makeCheckSum(outFile.name, cwd=bldDir)

    toUpload(outFile)
    toUpload(shaFile)

    return
