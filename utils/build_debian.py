"""
novelWriter – Debian Build
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

import argparse
import datetime
import email.utils
import shutil
import subprocess
import sys

from utils.common import (
    ROOT_DIR, SETUP_DIR, checkAssetsExist, copyPackageFiles, copySourceCode,
    extractVersion, makeCheckSum, toUpload, writeFile
)

SIGN_KEY = "D6A9F6B8F227CF7C6F6D1EE84DBBE4B734B0BD08"


def makeDebianPackage(
    signKey: str | None = None, sourceBuild: bool = False, distName: str = "unstable",
    buildName: str = "", forLaunchpad: bool = False
) -> str:
    """Build a Debian package."""
    print("")
    print("Build Debian Package")
    print("====================")
    print("On Debian/Ubuntu install: dh-python python3-all debhelper devscripts ")
    print("                          pybuild-plugin-pyproject")
    print("")

    # Version Info
    # ============

    numVers, hexVers, relDate = extractVersion()
    relDate = datetime.datetime.strptime(relDate, "%Y-%m-%d")
    pkgDate = email.utils.format_datetime(relDate.replace(hour=12, tzinfo=None))
    print("")

    if forLaunchpad:
        pkgVers = numVers.replace("a", "~a").replace("b", "~b").replace("rc", "~rc")
    else:
        pkgVers = numVers
    pkgVers = f"{pkgVers}+{buildName}" if buildName else pkgVers

    # Set Up Folder
    # =============

    bldDir = ROOT_DIR / "dist_deb"
    bldPkg = f"novelwriter_{pkgVers}"
    outDir = bldDir / bldPkg
    debDir = outDir / "debian"
    datDir = outDir / "data"

    bldDir.mkdir(exist_ok=True)
    if outDir.exists():
        print("Removing old build files ...")
        print("")
        shutil.rmtree(outDir)

    outDir.mkdir(exist_ok=False)

    # Check Additional Assets
    # =======================

    if not checkAssetsExist():
        print("ERROR: Missing build assets")
        sys.exit(1)

    # Copy novelWriter Source
    # =======================

    print("Copying novelWriter source ...")
    print("")

    copySourceCode(outDir)

    print("")
    print("Copying or generating additional files ...")
    print("")

    copyPackageFiles(outDir, setupPy=True)

    # Copy/Write Debian Files
    # =======================

    shutil.copytree(SETUP_DIR / "debian", debDir)
    print("Copied: debian/*")

    writeFile(debDir / "changelog", (
        f"novelwriter ({pkgVers}) {distName}; urgency=low\n\n"
        f"  * Update to version {pkgVers}\n\n"
        f" -- Veronica Berglyd Olsen <code@vkbo.net>  {pkgDate}\n"
    ))
    print("Wrote:  debian/changelog")

    # Copy/Write Data Files
    # =====================

    shutil.copytree(SETUP_DIR / "data", datDir)
    print("Copied: data/*")

    shutil.copyfile(SETUP_DIR / "description_short.txt", outDir / "data" / "description_short.txt")
    print("Copied: data/description_short.txt")

    # Build Package
    # =============

    print("")
    print("Running dpkg-buildpackage ...")
    print("")

    if signKey is None:
        signArgs = ["-us", "-uc"]
    else:
        signArgs = [f"-k{signKey}"]

    if sourceBuild:
        subprocess.call(["debuild", "-S"] + signArgs, cwd=outDir)
        toUpload(bldDir / f"{bldPkg}.tar.xz")
    else:
        subprocess.call(["dpkg-buildpackage"] + signArgs, cwd=outDir)
        shutil.copyfile(bldDir / f"{bldPkg}.tar.xz", bldDir / f"{bldPkg}.debian.tar.xz")
        toUpload(bldDir / f"{bldPkg}.debian.tar.xz")
        toUpload(bldDir / f"{bldPkg}_all.deb")
        toUpload(makeCheckSum(f"{bldPkg}.debian.tar.xz", cwd=bldDir))
        toUpload(makeCheckSum(f"{bldPkg}_all.deb", cwd=bldDir))

    print("")
    print("Done!")
    print("")

    if sourceBuild:
        ppaName = "novelwriter" if hexVers[-2] == "f" else "novelwriter-pre"
        return f"dput {ppaName}/{distName} {bldDir}/{bldPkg}_source.changes"

    return ""


def debian(args: argparse.Namespace) -> None:
    """Build a .deb package"""
    if sys.platform == "linux":
        print("ERROR: Command 'build-deb' can only be used on Linux")
        sys.exit(1)
    signKey = SIGN_KEY if args.sign else None
    makeDebianPackage(signKey)
    return


def launchpad(args: argparse.Namespace) -> None:
    """Wrapper for building Debian packages for Launchpad."""
    if sys.platform == "linux":
        print("ERROR: Command 'build-ubuntu' can only be used on Linux")
        sys.exit(1)

    print("")
    print("Launchpad Packages")
    print("==================")
    print("")

    if args.build:
        bldNum = str(args.build)
    else:
        bldNum = "0"

    distLoop = [
        ("24.04", "noble"),
        ("24.10", "oracular"),
        ("25.04", "plucky"),
    ]

    print("Building Ubuntu packages for:")
    print("")
    for distNum, codeName in distLoop:
        print(f" * Ubuntu {distNum} {codeName.title()}")
    print("")

    signKey = SIGN_KEY if args.sign else None

    print(f"Sign Key: {str(signKey)}")
    print("")

    dputCmd = []
    for distNum, codeName in distLoop:
        buildName = f"ubuntu{distNum}.{bldNum}"
        dCmd = makeDebianPackage(
            signKey=signKey,
            sourceBuild=True,
            distName=codeName,
            buildName=buildName,
            forLaunchpad=True,
        )
        dputCmd.append(dCmd)

    print("Packages Built")
    print("==============")
    print("")
    for dCmd in dputCmd:
        print(f" > {dCmd}")
    print("")

    return
