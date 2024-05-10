#!/usr/bin/env python3
"""
novelWriter – Packaging Utils
=============================

File History:
Created: 2019-05-16 [0.5.1]
Renamed: 2023-07-26 [2.1b1]

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

import datetime
import email.utils
import os
import shutil
import subprocess
import sys
import zipfile

from pathlib import Path

OS_NONE   = 0
OS_LINUX  = 1
OS_WIN    = 2
OS_DARWIN = 3


# =============================================================================================== #
#  Utilities
# =============================================================================================== #

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


def readFile(fileName: str) -> str:
    """Read an entire file and return as a string."""
    return Path(fileName).read_text(encoding="utf-8")


def writeFile(fileName: str, text: str) -> None:
    """Write string to file."""
    Path(fileName).write_text(text, encoding="utf-8")
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


def makeCheckSum(sumFile: str, cwd: str | None = None) -> str:
    """Create a SHA256 checksum file."""
    try:
        if cwd is None:
            shaFile = sumFile+".sha256"
        else:
            shaFile = os.path.join(cwd, sumFile+".sha256")
        with open(shaFile, mode="w") as fOut:
            subprocess.call(["shasum", "-a", "256", sumFile], stdout=fOut, cwd=cwd)
        print("SHA256 Sum: %s" % shaFile)
    except Exception as exc:
        print("Could not generate sha256 file")
        print(str(exc))
        return ""

    return shaFile


# =============================================================================================== #
#  General
# =============================================================================================== #

##
# Package Installer (pip)
##

def installPackages(hostOS: int) -> None:
    """Install package dependencies both for this script and for running
    novelWriter itself.
    """
    print("")
    print("Installing Dependencies")
    print("=======================")
    print("")

    installQueue = ["pip", "-r requirements.txt"]
    if hostOS == OS_DARWIN:
        installQueue.append("pyobjc")
    elif hostOS == OS_WIN:
        installQueue.append("pywin32")

    pyCmd = [sys.executable, "-m"]
    pipCmd = ["pip", "install", "--user", "--upgrade"]
    for stepCmd in installQueue:
        pkgCmd = stepCmd.split(" ")
        try:
            subprocess.call(pyCmd + pipCmd + pkgCmd)
        except Exception as exc:
            print("Failed with error:")
            print(str(exc))
            sys.exit(1)

    return


##
#  Clean Build and Dist Folders (build-clean)
##

def cleanBuildDirs() -> None:
    """Recursively delete the 'build' and 'dist' folders."""
    print("")
    print("Cleaning up build environment ...")
    print("")

    def removeFolder(rmDir: str) -> None:
        if os.path.isdir(rmDir):
            try:
                shutil.rmtree(rmDir)
                print("Deleted: %s" % rmDir)
            except OSError:
                print("Failed:  %s" % rmDir)
        else:
            print("Missing: %s" % rmDir)

    removeFolder("build")
    removeFolder("dist")
    removeFolder("dist_deb")
    removeFolder("dist_minimal")
    removeFolder("dist_appimage")
    removeFolder("novelWriter.egg-info")

    print("")

    return


# =============================================================================================== #
#  Additional Builds
# =============================================================================================== #

##
#  Build PDF Manual (manual)
##

def buildPdfManual() -> None:
    """This function will build the documentation as manual.pdf."""
    print("")
    print("Building PDF Manual")
    print("===================")
    print("")

    buildFile = os.path.join("docs", "build", "latex", "manual.pdf")
    finalFile = os.path.join("novelwriter", "assets", "manual.pdf")

    if os.path.isfile(finalFile):
        # Make sure a new file is always generated
        os.unlink(finalFile)

    try:
        subprocess.call(["make", "clean"], cwd="docs")
        exCode = subprocess.call(["make", "latexpdf"], cwd="docs")
        if exCode == 0:
            if os.path.isfile(finalFile):
                os.unlink(finalFile)
            print("")
            os.rename(buildFile, finalFile)
        else:
            raise Exception(f"Build returned error code {exCode}")

        print("PDF manual build: OK")
        print("")

    except Exception as exc:
        print("PDF manual build: FAILED")
        print("")
        print(str(exc))
        print("")
        print("Dependencies:")
        print(" * pip install sphinx")
        print(" * Package latexmk")
        print(" * LaTeX build system")
        print("")
        print(" On Debian/Ubuntu, install: python3-sphinx latexmk texlive texlive-latex-extra")
        print("")
        sys.exit(1)

    if not os.path.isfile(finalFile):
        print("No output file was found!")
        print("")
        sys.exit(1)

    return


##
#  Qt Linguist QM Builder (qtlrelease)
##

def buildQtI18n() -> None:
    """Build the lang.qm files for Qt Linguist."""
    print("")
    print("Building Qt Localisation Files")
    print("==============================")

    print("")
    print("TS Files to Build:")
    print("")

    tsList = []
    for aFile in os.listdir("i18n"):
        aPath = os.path.join("i18n", aFile)
        if os.path.isfile(aPath) and aFile.endswith(".ts") and aFile != "nw_base.ts":
            tsList.append(aPath)
            print(aPath)

    print("")
    print("Building Translation Files:")
    print("")

    try:
        subprocess.call(["lrelease", "-verbose", *tsList])
    except Exception as exc:
        print("Qt5 Linguist tools seem to be missing")
        print("On Debian/Ubuntu, install: qttools5-dev-tools pyqt5-dev-tools")
        print(str(exc))
        sys.exit(1)

    print("")
    print("Moving QM Files to Assets")
    print("")

    langDir = os.path.join("novelwriter", "assets", "i18n")
    for langFile in os.listdir("i18n"):
        langPath = os.path.join("i18n", langFile)
        if not os.path.isfile(langPath):
            continue

        if langFile.endswith(".qm"):
            destPath = os.path.join(langDir, langFile)
            os.rename(langPath, destPath)
            print("Moved: %s -> %s" % (langPath, destPath))

    print("")

    return


##
#  Qt Linguist TS Builder (qtlupdate)
##

def buildQtI18nTS(sysArgs: list[str]) -> None:
    """Build the lang.ts files for Qt Linguist."""
    print("")
    print("Building Qt Translation Files")
    print("=============================")

    try:
        from PyQt6.lupdate.lupdate import lupdate
    except ImportError:
        print("ERROR: This command requires lupdate from PyQt6")
        print("On Debian/Ubuntu, install: pyqt6-dev-tools")
        sys.exit(1)

    print("")
    print("Scanning Source Tree:")
    print("")

    sources = [os.path.join("i18n", "qtbase.py")]
    for root, _, files in os.walk("novelwriter"):
        if os.path.isdir(root):
            for file in files:
                source = os.path.join(root, file)
                if os.path.isfile(source) and file.endswith(".py"):
                    sources.append(source)

    for source in sources:
        print(source)

    print("")
    print("TS Files to Update:")
    print("")

    translations = []
    if len(sysArgs) >= 2:
        for arg in sysArgs[1:]:
            if not (arg.startswith("i18n") and arg.endswith(".ts")):
                continue

            file = os.path.basename(arg)
            if not file.startswith("nw_") and len(file) > 6:
                print("Skipping non-novelWriter TS file %s" % file)
                continue

            if os.path.isfile(arg):
                translations.append(arg)
            elif os.path.exists(arg):
                pass
            else:  # Create an empty new language file
                langCode = file[3:-3]
                writeFile(arg, (
                    "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                    "<!DOCTYPE TS>\n"
                    f"<TS version=\"2.0\" language=\"{langCode}\" sourcelanguage=\"en_GB\"/>\n"
                ))
                translations.append(arg)

    else:
        print("No translation files selected for update ...")
        print("")
        return

    for translation in translations:
        print(translation)

    print("")
    print("Updating Language Files:")
    print("")

    # Using the pylupdate tool from PyQt6 as it supports TS file format 2.1.
    lupdate(sources, translations, no_obsolete=True, no_summary=False)

    print("")

    return


##
#  Generate MacOS PList
##

def genMacOSPlist() -> None:
    """Set necessary values for .plist file for MacOS build."""
    outDir = "setup/macos"
    numVers = stripVersion(extractVersion()[0])
    copyrightYear = datetime.datetime.now().year

    # These keys are no longer used but are present for compatibility
    pkgVersMaj, pkgVersMin = numVers.split(".")[:2]

    plistXML = readFile(f"{outDir}/Info.plist.template").format(
        macosBundleSVers=numVers,
        macosBundleVers=numVers,
        macosBundleVersMajor=pkgVersMaj,
        macosBundleVersMinor=pkgVersMin,
        macosBundleCopyright=f"Copyright 2018–{copyrightYear}, Veronica Berglyd Olsen",
    )

    print(f"Writing Info.plist to {outDir}/Info.plist")
    writeFile(f"{outDir}/Info.plist", plistXML)

    return


##
#  Sample Project ZIP File Builder (sample)
##

def buildSampleZip() -> None:
    """Bundle the sample project into a single zip file to be saved into
    the novelwriter/assets folder for further bundling into builds.
    """
    print("")
    print("Building Sample ZIP File")
    print("========================")
    print("")

    srcSample = "sample"
    dstSample = os.path.join("novelwriter", "assets", "sample.zip")

    if os.path.isdir(srcSample):
        if os.path.isfile(dstSample):
            os.unlink(dstSample)

        from zipfile import ZipFile

        with ZipFile(dstSample, "w") as zipObj:
            print("Compressing: nwProject.nwx")
            zipObj.write(os.path.join(srcSample, "nwProject.nwx"), "nwProject.nwx")
            for docFile in os.listdir(os.path.join(srcSample, "content")):
                print("Compressing: content/%s" % docFile)
                srcDoc = os.path.join(srcSample, "content", docFile)
                zipObj.write(srcDoc, "content/"+docFile)

    else:
        print("Error: Could not find sample project source directory.")
        sys.exit(1)

    print("")
    print("Built file: %s" % dstSample)
    print("")

    return


def cleanBuiltAssets() -> None:
    """Remove assets built by this script."""
    print("")
    print("Removing Built Assets")
    print("=====================")
    print("")

    sampleZip = os.path.join("novelwriter", "assets", "sample.zip")
    if os.path.isfile(sampleZip):
        print(f"Deleted: {sampleZip}")
        os.unlink(sampleZip)

    pdfManual = os.path.join("novelwriter", "assets", "manual.pdf")
    if os.path.isfile(pdfManual):
        print(f"Deleted: {pdfManual}")
        os.unlink(pdfManual)

    i18nAssets = os.path.join("novelwriter", "assets", "i18n")
    for i18nItem in os.listdir(i18nAssets):
        i18nPath = os.path.join(i18nAssets, i18nItem)
        if os.path.isfile(i18nPath) and i18nPath.endswith(".qm"):
            print(f"Deleted: {i18nPath}")
            os.unlink(i18nPath)

    print("")

    return


def checkAssetsExist() -> bool:
    """Check that the necessary compiled assets exist ahead of a build.
    """
    hasSample = False
    hasManual = False
    hasQmData = False

    sampleZip = os.path.join("novelwriter", "assets", "sample.zip")
    if os.path.isfile(sampleZip):
        print(f"Found: {sampleZip}")
        hasSample = True

    pdfManual = os.path.join("novelwriter", "assets", "manual.pdf")
    if os.path.isfile(pdfManual):
        print(f"Found: {pdfManual}")
        hasManual = True

    i18nAssets = os.path.join("novelwriter", "assets", "i18n")
    for i18nItem in os.listdir(i18nAssets):
        i18nPath = os.path.join(i18nAssets, i18nItem)
        if os.path.isfile(i18nPath) and i18nPath.endswith(".qm"):
            print(f"Found: {i18nPath}")
            hasQmData = True

    return hasSample and hasManual and hasQmData


# =============================================================================================== #
#  Python Packaging
# =============================================================================================== #

##
#  Import Translations (import-i18n)
##

def importI18nUpdates(sysArgs: list[str]) -> None:
    """Import new translation files from a zip file."""
    print("")
    print("Import Updated Translations")
    print("===========================")
    print("")

    fileName = None
    if len(sysArgs) >= 2:
        if os.path.isfile(sysArgs[1]):
            fileName = sysArgs[1]

    if fileName is None:
        print("File not found ...")
        sys.exit(1)

    projPath = os.path.join("novelwriter", "assets", "i18n")
    mainPath = "i18n"

    print("Loading file: %s" % fileName)
    with zipfile.ZipFile(fileName) as zipObj:
        for archFile in zipObj.namelist():
            if archFile.startswith("nw_") and archFile.endswith(".ts"):
                zipObj.extract(archFile, mainPath)
                print("Extracted: %s > %s" % (archFile, os.path.join(mainPath, archFile)))
            elif archFile.startswith("project_") and archFile.endswith(".json"):
                zipObj.extract(archFile, projPath)
                print("Extracted: %s > %s" % (archFile, os.path.join(projPath, archFile)))
            else:
                print("Skipped: %s" % archFile)

    print("")

    return


##
#  Make Minimal Package (minimal-zip)
##

def makeWindowsZip() -> None:
    """Pack the core source file in a single zip file."""
    from zipfile import ZIP_DEFLATED, ZipFile

    print("")
    print("Building Windows ZIP File")
    print("=========================")

    bldDir = "dist_minimal"
    if not os.path.isdir(bldDir):
        os.mkdir(bldDir)

    if not checkAssetsExist():
        print("ERROR: Missing build assets")
        sys.exit(1)

    pkgVers, _, _ = extractVersion()
    zipFile = f"novelwriter-{pkgVers}-minimal-win.zip"
    outFile = os.path.join(bldDir, zipFile)
    if os.path.isfile(outFile):
        os.unlink(outFile)
    print("")

    rootFiles = [
        "README.md",
        "LICENSE.md",
        "CREDITS.md",
        "CHANGELOG.md",
        "requirements.txt",
        "pkgutils.py",
        "pyproject.toml",
    ]

    with ZipFile(outFile, "w", compression=ZIP_DEFLATED, compresslevel=9) as zipObj:

        for nRoot, _, nFiles in os.walk("novelwriter"):
            if nRoot.endswith("__pycache__"):
                print("Skipped: %s" % nRoot)
                continue

            print("Added: %s/* [Files: %d]" % (nRoot, len(nFiles)))
            for aFile in nFiles:
                if aFile.endswith(".pyc"):
                    print("Skipping File: %s" % aFile)
                    continue
                zipObj.write(os.path.join(nRoot, aFile))

        zipObj.write("novelWriter.py", "novelWriter.pyw")
        print("Added: novelWriter.pyw")

        for aFile in rootFiles:
            print("Added: %s" % aFile)
            zipObj.write(aFile)

        zipObj.write(os.path.join("novelwriter", "assets", "manual.pdf"), "UserManual.pdf")
        print("Added: UserManual.pdf")

    print("")
    print("Created File: %s" % outFile)

    shaFile = makeCheckSum(zipFile, cwd=bldDir)
    toUpload(outFile)
    toUpload(shaFile)
    print("")

    return


##
#  Make Debian Package (build-deb)
##

def makeDebianPackage(
    signKey: str | None = None, sourceBuild: bool = False,
    distName: str = "unstable", buildName: str = "", oldSetuptools: bool = False
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

    pkgVers = numVers.replace("a", "~a").replace("b", "~b").replace("rc", "~rc")
    pkgVers = f"{pkgVers}+{buildName}" if buildName else pkgVers

    # Set Up Folder
    # =============

    bldDir = "dist_deb"
    bldPkg = f"novelwriter_{pkgVers}"
    outDir = f"{bldDir}/{bldPkg}"
    debDir = f"{outDir}/debian"
    datDir = f"{outDir}/data"

    if not os.path.isdir(bldDir):
        os.mkdir(bldDir)

    if os.path.isdir(outDir):
        print("Removing old build files ...")
        print("")
        shutil.rmtree(outDir)

    os.mkdir(outDir)

    # Check Additional Assets
    # =======================

    if not checkAssetsExist():
        print("ERROR: Missing build assets")
        sys.exit(1)

    # Copy novelWriter Source
    # =======================

    print("Copying novelWriter source ...")
    print("")

    for nPath, _, nFiles in os.walk("novelwriter"):
        if nPath.endswith("__pycache__"):
            print("Skipped: %s" % nPath)
            continue

        pPath = f"{outDir}/{nPath}"
        if not os.path.isdir(pPath):
            os.mkdir(pPath)

        fCount = 0
        for fFile in nFiles:
            nFile = f"{nPath}/{fFile}"
            pFile = f"{pPath}/{fFile}"

            if fFile.endswith(".pyc"):
                print("Skipped: %s" % nFile)
                continue

            shutil.copyfile(nFile, pFile)
            fCount += 1

        print("Copied: %s/*  [Files: %d]" % (nPath, fCount))

    print("")
    print("Copying or generating additional files ...")
    print("")

    # Copy/Write Root Files
    # =====================

    copyFiles = ["LICENSE.md", "CREDITS.md", "CHANGELOG.md", "pyproject.toml"]
    for copyFile in copyFiles:
        shutil.copyfile(copyFile, f"{outDir}/{copyFile}")
        print("Copied: %s" % copyFile)

    writeFile(f"{outDir}/MANIFEST.in", (
        "include LICENSE.md\n"
        "include CREDITS.md\n"
        "include CHANGELOG.md\n"
        "include data/*\n"
        "recursive-include novelwriter/assets *\n"
    ))
    print("Wrote:  MANIFEST.in")

    writeFile(f"{outDir}/setup.py", (
        "import setuptools\n"
        "setuptools.setup()\n"
    ))
    print("Wrote:  setup.py")

    if oldSetuptools:
        # This is needed for Ubuntu up to 22.04
        setupCfg = readFile("setup/launchpad_setup.cfg").replace(
            "file: setup/description_pypi.md", "file: data/description_short.txt"
        )
        writeFile(f"{outDir}/setup.cfg", setupCfg)
        print("Wrote:  setup.cfg")

        writeFile(f"{outDir}/pyproject.toml", (
            "[build-system]\n"
            "requires = [\"setuptools\"]\n"
            "build-backend = \"setuptools.build_meta\"\n"
        ))
        print("Wrote:  pyproject.toml")

    else:
        pyProject = readFile("pyproject.toml").replace(
            "setup/description_pypi.md", "data/description_short.txt"
        )
        writeFile(f"{outDir}/pyproject.toml", pyProject)
        print("Wrote:  pyproject.toml")

    # Copy/Write Debian Files
    # =======================

    shutil.copytree("setup/debian", debDir)
    print("Copied: debian/*")

    writeFile(f"{debDir}/changelog", (
        f"novelwriter ({pkgVers}) {distName}; urgency=low\n\n"
        f"  * Update to version {pkgVers}\n\n"
        f" -- Veronica Berglyd Olsen <code@vkbo.net>  {pkgDate}\n"
    ))
    print("Wrote:  debian/changelog")

    # Copy/Write Data Files
    # =====================

    shutil.copytree("setup/data", datDir)
    print("Copied: data/*")

    shutil.copyfile("setup/description_short.txt", f"{outDir}/data/description_short.txt")
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
        toUpload(f"{bldDir}/{bldPkg}.tar.xz")
    else:
        subprocess.call(["dpkg-buildpackage"] + signArgs, cwd=outDir)
        shutil.copyfile(f"{bldDir}/{bldPkg}.tar.xz", f"{bldDir}/{bldPkg}.debian.tar.xz")
        toUpload(f"{bldDir}/{bldPkg}.debian.tar.xz")
        toUpload(f"{bldDir}/{bldPkg}_all.deb")

        toUpload(makeCheckSum(f"{bldPkg}.debian.tar.xz", cwd=bldDir))
        toUpload(makeCheckSum(f"{bldPkg}_all.deb", cwd=bldDir))

    print("")
    print("Done!")
    print("")

    if sourceBuild:
        ppaName = "novelwriter" if hexVers[-2] == "f" else "novelwriter-pre"
        return f"dput {ppaName}/{distName} {bldDir}/{bldPkg}_source.changes"

    return ""


##
#  Make Launchpad Package (build-ubuntu)
##

def makeForLaunchpad(doSign: bool = False, isFirst: bool = False) -> None:
    """Wrapper for building Debian packages for Launchpad."""
    print("")
    print("Launchpad Packages")
    print("==================")
    print("")

    if isFirst:
        bldNum = "0"
    else:
        bldNum = input("Build number [0]: ")
        if bldNum == "":
            bldNum = "0"

    distLoop = [
        ("22.04", "jammy", True),
        ("23.10", "mantic", False),
        ("24.04", "noble", False),
    ]

    print("Building Ubuntu packages for:")
    print("")
    for distNum, codeName, _ in distLoop:
        print(f" * Ubuntu {distNum} {codeName.title()}")
    print("")

    if doSign:
        signKey = "D6A9F6B8F227CF7C6F6D1EE84DBBE4B734B0BD08"
    else:
        signKey = None

    print(f"Sign Key: {str(signKey)}")
    print("")

    dputCmd = []
    for distNum, codeName, oldSetup in distLoop:
        buildName = f"ubuntu{distNum}.{bldNum}"
        dCmd = makeDebianPackage(
            signKey=signKey,
            sourceBuild=True,
            distName=codeName,
            buildName=buildName,
            oldSetuptools=oldSetup,
        )
        dputCmd.append(dCmd)

    print("Packages Built")
    print("==============")
    print("")
    for dCmd in dputCmd:
        print(f" > {dCmd}")
    print("")

    return


##
#  Make AppImage (build-appimage)
##

def makeAppImage(sysArgs: list[str]) -> list[str]:
    """Build an AppImage."""
    import argparse
    import glob

    try:
        import python_appimage  # noqa: F401 # type: ignore
    except ImportError:
        print(
            "ERROR: Package 'python-appimage' is missing on this system.\n"
            "       Please run 'pip install --user python-appimage' to install it.\n"
        )
        sys.exit(1)

    print("")
    print("Build AppImage")
    print("==============")
    print("")

    parser = argparse.ArgumentParser(
        prog="build_appimage",
        description="Build an AppImage",
        epilog="see https://appimage.org/ for more details",
    )
    parser.add_argument(
        "--linux-tag",
        nargs="?",
        default="manylinux_2_28_x86_64",
        help=(
            "Linux compatibility tag (e.g. manylinux_2_28_x86_64)\n"
            "see https://python-appimage.readthedocs.io/en/latest/#available-python-appimages \n"
            "and https://github.com/pypa/manylinux for a list of valid tags"
        ),
    )
    parser.add_argument(
        "--python-version", nargs="?", default="3.11", help="Python version (e.g. 3.11)"
    )

    args, unparsedArgs = parser.parse_known_args(sysArgs)

    linuxTag = args.linux_tag
    pythonVer = args.python_version

    # Version Info
    # ============

    pkgVers, _, relDate = extractVersion()
    relDate = datetime.datetime.strptime(relDate, "%Y-%m-%d")
    print("")

    # Set Up Folder
    # =============

    bldDir = "dist_appimage"
    bldPkg = f"novelwriter_{pkgVers}"
    outDir = f"{bldDir}/{bldPkg}"
    imageDir = f"{bldDir}/appimage"

    # Set Up Folders
    # ==============

    if not os.path.isdir(bldDir):
        os.mkdir(bldDir)

    if os.path.isdir(outDir):
        print("Removing old build files ...")
        print("")
        shutil.rmtree(outDir)

    os.mkdir(outDir)

    if os.path.isdir(imageDir):
        print("Removing old build metadata files ...")
        print("")
        shutil.rmtree(imageDir)

    os.mkdir(imageDir)

    # Remove old AppImages
    outFiles = glob.glob(f"{bldDir}/*.AppImage")
    if outFiles:
        print("Removing old AppImages")
        print("")
        for image in outFiles:
            try:
                os.remove(image)
            except OSError:
                print("Error while deleting file : ", image)

    # Copy novelWriter Source
    # =======================

    print("Copying novelWriter source ...")
    print("")

    for nPath, _, nFiles in os.walk("novelwriter"):
        if nPath.endswith("__pycache__"):
            print("Skipped: %s" % nPath)
            continue

        pPath = f"{outDir}/{nPath}"
        if not os.path.isdir(pPath):
            os.mkdir(pPath)

        fCount = 0
        for fFile in nFiles:
            nFile = f"{nPath}/{fFile}"
            pFile = f"{pPath}/{fFile}"

            if fFile.endswith(".pyc"):
                print("Skipped: %s" % nFile)
                continue

            shutil.copyfile(nFile, pFile)
            fCount += 1

        print("Copied: %s/*  [Files: %d]" % (nPath, fCount))

    print("")
    print("Copying or generating additional files ...")
    print("")

    # Copy/Write Root Files
    # =====================

    copyFiles = ["LICENSE.md", "CREDITS.md", "CHANGELOG.md", "pyproject.toml"]
    for copyFile in copyFiles:
        shutil.copyfile(copyFile, f"{outDir}/{copyFile}")
        print("Copied: %s" % copyFile)

    writeFile(f"{outDir}/MANIFEST.in", (
        "include LICENSE.md\n"
        "include CREDITS.md\n"
        "include CHANGELOG.md\n"
        "include data/*\n"
        "recursive-include novelwriter/assets *\n"
    ))
    print("Wrote:  MANIFEST.in")

    writeFile(f"{outDir}/setup.py", (
        "import setuptools\n"
        "setuptools.setup()\n"
    ))
    print("Wrote:  setup.py")

    setupCfg = readFile("pyproject.toml").replace(
        "setup/description_pypi.md", "data/description_short.txt"
    )
    writeFile(f"{outDir}/pyproject.toml", setupCfg)
    print("Wrote:  pyproject.toml")

    # Write Metadata
    # ==============

    appDescription = readFile("setup/description_short.txt")
    appdataXML = readFile("setup/novelwriter.appdata.xml").format(description=appDescription)
    writeFile(f"{imageDir}/novelwriter.appdata.xml", appdataXML)
    print("Wrote:  novelwriter.appdata.xml")

    writeFile(f"{imageDir}/entrypoint.sh", (
        '#! /bin/bash \n'
        '{{ python-executable }} -sE ${APPDIR}/opt/python{{ python-version }}/bin/novelwriter "$@"'
    ))
    print("Wrote:  entrypoint.sh")

    writeFile(f"{imageDir}/requirements.txt", os.path.abspath(outDir))
    print("Wrote:  requirements.txt")

    shutil.copyfile("setup/data/novelwriter.desktop", f"{imageDir}/novelwriter.desktop")
    print("Copied: novelwriter.desktop")

    shutil.copyfile("setup/icons/novelwriter.svg", f"{imageDir}/novelwriter.svg")
    print("Copied: novelwriter.svg")

    shutil.copyfile(
        "setup/data/hicolor/256x256/apps/novelwriter.png", f"{imageDir}/novelwriter.png"
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

    bldFile = glob.glob(f"{bldDir}/*.AppImage")[0]
    outFile = f"{bldDir}/novelWriter-{pkgVers}.AppImage"
    os.rename(bldFile, outFile)
    shaFile = makeCheckSum(os.path.basename(outFile), cwd=bldDir)

    toUpload(outFile)
    toUpload(shaFile)

    return unparsedArgs


##
#  Make Windows Setup EXE (build-win-exe)
##

def makeWindowsEmbedded(sysArgs: list[str]) -> None:
    """Set up a package with embedded Python and dependencies for
    Windows installation.
    """
    import compileall
    import urllib.request
    import zipfile

    print("")
    print("Build Standalone Windows Package")
    print("================================")
    print("")

    minimalZip = None
    packVersion = "none"
    if len(sysArgs) >= 2:
        if os.path.isfile(sysArgs[1]):
            minimalZip = sysArgs[1]

    if minimalZip is None:
        print("Please provide the path to the minimal win package as an argument")
        sys.exit(1)

    packVersion = os.path.basename(minimalZip).split("-")[1]
    print("Version: %s" % packVersion)

    # Set Up Folder
    # =============

    if not os.path.isdir("dist"):
        os.mkdir("dist")

    outDir = os.path.join("dist", "novelWriter")
    libDir = os.path.join(outDir, "lib")
    if os.path.isdir(outDir):
        shutil.rmtree(outDir)

    os.mkdir(outDir)
    os.mkdir(libDir)

    # Extract Source Files
    # ====================

    print("Extracting source files ...")
    with zipfile.ZipFile(minimalZip, "r") as inFile:
        inFile.extractall(outDir)

    shutil.copyfile(
        os.path.join(outDir, "novelwriter", "assets", "icons", "novelwriter.ico"),
        os.path.join(outDir, "novelwriter.ico")
    )

    compileall.compile_dir(os.path.join(outDir, "novelwriter"))

    print("Done")
    print("")

    # Download Python Embeddable
    # ==========================

    print("Adding Python embeddable ...")

    pyVers = "%d.%d.%d" % (sys.version_info[:3])
    zipFile = "python-%s-embed-amd64.zip" % pyVers
    pyZip = os.path.join("dist", zipFile)
    if not os.path.isfile(pyZip):
        pyUrl = f"https://www.python.org/ftp/python/{pyVers}/{zipFile}"
        print("Downloading: %s" % pyUrl)
        urllib.request.urlretrieve(pyUrl, pyZip)

    print("Extracting ...")
    with zipfile.ZipFile(pyZip, "r") as inFile:
        inFile.extractall(outDir)

    print("Done")
    print("")

    # Sort Out Licence Files
    # ======================

    os.rename(
        os.path.join(outDir, "LICENSE.txt"),
        os.path.join(outDir, "PYTHON-LICENSE.txt")
    )
    shutil.copyfile(
        os.path.join("setup", "iss_license.txt"),
        os.path.join(outDir, "LICENSES.txt")
    )

    # Install Dependencies
    # ====================

    print("Install dependencies ...")

    sysCmd  = [sys.executable]
    sysCmd += "-m pip install -r requirements.txt --target".split()
    sysCmd += [libDir]
    try:
        subprocess.call(sysCmd)
    except Exception as exc:
        print("Failed with error:")
        print(str(exc))
        sys.exit(1)

    print("Done")
    print("")

    # Update Launch File
    # ==================

    print("Updating starting script ...")

    writeFile(os.path.join(outDir, "novelWriter.pyw"), (
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

    # Clean Up Files
    # ==============

    def unlinkIfFound(delFile: str) -> None:
        if os.path.isfile(delFile):
            os.unlink(delFile)
            print("Deleted: %s" % delFile)

    def deleteFolder(delPath: str) -> None:
        if os.path.isdir(delPath):
            shutil.rmtree(delPath)
            print("Deleted: %s" % delPath)

    print("Deleting Redundant Files")
    print("========================")
    print("")

    pyQt5Dir = os.path.join(libDir, "PyQt5")
    bindDir  = os.path.join(pyQt5Dir, "bindings")
    qt5Dir   = os.path.join(pyQt5Dir, "Qt5")
    binDir   = os.path.join(qt5Dir, "bin")
    plugDir  = os.path.join(qt5Dir, "plugins")
    qmDir    = os.path.join(qt5Dir, "translations")
    dictDir  = os.path.join(libDir, "enchant", "data", "mingw64", "share", "enchant", "hunspell")

    for dictFile in os.listdir(dictDir):
        if not dictFile.startswith(("en_GB", "en_US")):
            unlinkIfFound(os.path.join(dictDir, dictFile))

    for qmFile in os.listdir(qmDir):
        if not qmFile.startswith("qtbase"):
            unlinkIfFound(os.path.join(qmDir, qmFile))

    delQt5 = [
        "Qt5Bluetooth", "Qt5DBus", "Qt5Designer", "Qt5Designer", "Qt5Help", "Qt5Location",
        "Qt5Multimedia", "Qt5MultimediaWidgets", "Qt5Network", "Qt5Nfc", "Qt5OpenGL",
        "Qt5Positioning", "Qt5PositioningQuick", "Qt5Qml", "Qt5QmlModels", "Qt5QmlWorkerScript",
        "Qt5Quick", "Qt5Quick3D", "Qt5Quick3DAssetImport", "Qt5Quick3DRender",
        "Qt5Quick3DRuntimeRender", "Qt5Quick3DUtils", "Qt5QuickControls2", "Qt5QuickParticles",
        "Qt5QuickShapes", "Qt5QuickTemplates2", "Qt5QuickTest", "Qt5QuickWidgets", "Qt5Sensors",
        "Qt5SerialPort", "Qt5Sql", "Qt5Test", "Qt5TextToSpeech", "Qt5WebChannel", "Qt5WebSockets",
        "Qt5WebView", "Qt5Xml", "Qt5XmlPatterns"
    ]
    for qt5Item in delQt5:
        qtItem = qt5Item.replace("Qt5", "Qt")
        unlinkIfFound(os.path.join(binDir, qt5Item+".dll"))
        unlinkIfFound(os.path.join(pyQt5Dir, qtItem+".pyd"))
        unlinkIfFound(os.path.join(pyQt5Dir, qtItem+".pyi"))
        deleteFolder(os.path.join(bindDir, qtItem))

    delList = [
        os.path.join(binDir, "opengl32sw.dll"),
        os.path.join(qt5Dir, "qml"),
        os.path.join(plugDir, "geoservices"),
        os.path.join(plugDir, "playlistformats"),
        os.path.join(plugDir, "renderers"),
        os.path.join(plugDir, "sensorgestures"),
        os.path.join(plugDir, "sensors"),
        os.path.join(plugDir, "sqldrivers"),
        os.path.join(plugDir, "texttospeech"),
        os.path.join(plugDir, "webview"),
    ]
    for delItem in delList:
        if os.path.isfile(delItem):
            unlinkIfFound(delItem)
        elif os.path.isdir(delItem):
            deleteFolder(delItem)

    print("Done")
    print("")

    print("Running Inno Setup")
    print("##################")
    print("")

    # Read the iss template
    issData = readFile(os.path.join("setup", "win_setup_embed.iss"))
    issData = issData.replace(r"%%version%%", packVersion)
    issData = issData.replace(r"%%dir%%", os.getcwd())
    writeFile("setup.iss", issData)
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


# =============================================================================================== #
#  General Installers
# =============================================================================================== #

##
#  XDG Installation (xdg-install)
##

def xdgInstall() -> None:
    """Will attempt to install icons and make a launcher."""
    print("")
    print("XDG Install")
    print("===========")
    print("")

    # Find Executable(s)
    # ==================

    exOpts = []

    testExec = shutil.which("novelWriter")
    if testExec is not None:
        exOpts.append(testExec)

    testExec = shutil.which("novelwriter")
    if testExec is not None:
        exOpts.append(testExec)

    testExec = os.path.join(os.getcwd(), "novelWriter.py")
    if os.path.isfile(testExec):
        exOpts.append(testExec)

    useExec = ""
    nOpts = len(exOpts)
    if nOpts == 0:
        print("Error: No executables for novelWriter found.")
        sys.exit(1)
    elif nOpts == 1:
        useExec = exOpts[0]
    else:
        print("Found multiple novelWriter executables:")
        print("")
        for iExec, anExec in enumerate(exOpts):
            print(" [%d] %s" % (iExec, anExec))
        print("")
        intVal = int(input("Please select which novelWriter executable to use: "))
        print("")

        if intVal >= 0 and intVal < nOpts:
            useExec = exOpts[intVal]
        else:
            print("Error: Invalid selection.")
            sys.exit(1)

    print("Using executable: %s " % useExec)
    print("")

    # Create and Install Launcher
    # ===========================

    # Generate launcher
    desktopData = readFile(os.path.join("setup", "data", "novelwriter.desktop"))
    desktopData = desktopData.replace("Exec=novelwriter", f"Exec={useExec}")
    writeFile("novelwriter.desktop", desktopData)

    # Remove old desktop icon
    exCode = subprocess.call(
        ["xdg-desktop-icon", "uninstall", "novelwriter.desktop"]
    )

    # Install application launcher
    exCode = subprocess.call(
        ["xdg-desktop-menu", "install", "--novendor", "novelwriter.desktop"]
    )
    if exCode == 0:
        print("Installed menu launcher file")
    else:
        print(f"Error {exCode}: Could not install menu launcher file")

    # Install MimeType
    # ================

    exCode = subprocess.call([
        "xdg-mime", "install", "setup/data/x-novelwriter-project.xml"
    ])
    if exCode == 0:
        print("Installed mimetype")
    else:
        print(f"Error {exCode}: Could not install mimetype")

    # Install Icons
    # =============

    iconRoot = "setup/data/hicolor"
    sizeArr = ["16", "24", "32", "48", "64", "128", "256"]

    # App Icon
    for aSize in sizeArr:
        exCode = subprocess.call([
            "xdg-icon-resource", "install", "--novendor", "--noupdate",
            "--context", "apps", "--size", aSize,
            f"{iconRoot}/{aSize}x{aSize}/apps/novelwriter.png",
            "novelwriter"
        ])
        if exCode == 0:
            print(f"Installed app icon size {aSize}")
        else:
            print(f"Error {exCode}: Could not install app icon size {aSize}")

    # Mimetype
    for aSize in sizeArr:
        exCode = subprocess.call([
            "xdg-icon-resource", "install", "--noupdate",
            "--context", "mimetypes", "--size", aSize,
            f"{iconRoot}/{aSize}x{aSize}/mimetypes/application-x-novelwriter-project.png",
            "application-x-novelwriter-project"
        ])
        if exCode == 0:
            print(f"Installed mime icon size {aSize}")
        else:
            print(f"Error {exCode}: Could not install mime icon size {aSize}")

    # Update Cache
    exCode = subprocess.call(["xdg-icon-resource", "forceupdate"])
    if exCode == 0:
        print("Updated icon cache")
    else:
        print(f"Error {exCode}: Could not update icon cache")

    # Clean up
    if os.path.isfile("./novelwriter.desktop"):
        os.unlink("./novelwriter.desktop")

    print("")
    print("Done!")
    print("")

    return


##
#  XDG Uninstallation (xdg-uninstall)
##

def xdgUninstall() -> None:
    """Will attempt to uninstall icons and the launcher."""
    print("")
    print("XDG Uninstall")
    print("=============")
    print("")

    # Application Menu Icon
    exCode = subprocess.call(
        ["xdg-desktop-menu", "uninstall", "novelwriter.desktop"]
    )
    if exCode == 0:
        print("Uninstalled menu launcher file")
    else:
        print(f"Error {exCode}: Could not uninstall menu launcher file")

    # Desktop Icon
    # (No longer installed)
    exCode = subprocess.call(
        ["xdg-desktop-icon", "uninstall", "novelwriter.desktop"]
    )
    if exCode == 0:
        print("Uninstalled desktop launcher file")
    else:
        print(f"Error {exCode}: Could not uninstall desktop launcher file")

    # Also include no longer used sizes
    sizeArr = ["16", "22", "24", "32", "48", "64", "96", "128", "256", "512"]

    # App Icons
    for aSize in sizeArr:
        exCode = subprocess.call([
            "xdg-icon-resource", "uninstall", "--noupdate",
            "--context", "apps", "--size", aSize, "novelwriter"
        ])
        if exCode == 0:
            print(f"Uninstalled app icon size {aSize}")
        else:
            print(f"Error {exCode}: Could not uninstall app icon size {aSize}")

    # Mimetype
    for aSize in sizeArr:
        exCode = subprocess.call([
            "xdg-icon-resource", "uninstall", "--noupdate",
            "--context", "mimetypes", "--size", aSize,
            "application-x-novelwriter-project"
        ])
        if exCode == 0:
            print(f"Uninstalled mime icon size {aSize}")
        else:
            print(f"Error {exCode}: Could not uninstall mime icon size {aSize}")

    # Update Cache
    exCode = subprocess.call(["xdg-icon-resource", "forceupdate"])
    if exCode == 0:
        print("Updated icon cache")
    else:
        print(f"Error {exCode}: Could not update icon cache")

    print("")
    print("Done!")
    print("")

    return


# =============================================================================================== #
#  Process Command Line
# =============================================================================================== #

if __name__ == "__main__":
    """Parse command line options and run the commands."""
    # Detect OS
    if sys.platform.startswith("linux"):
        hostOS = OS_LINUX
    elif sys.platform.startswith("darwin"):
        hostOS = OS_DARWIN
    elif sys.platform.startswith("win32"):
        hostOS = OS_WIN
    elif sys.platform.startswith("cygwin"):
        hostOS = OS_WIN
    else:
        hostOS = OS_NONE

    sysArgs = sys.argv.copy()

    # Sign package
    if "--sign" in sysArgs:
        sysArgs.remove("--sign")
        doSign = True
    else:
        doSign = False

    # First build
    if "--first" in sysArgs:
        sysArgs.remove("--first")
        isFirstBuild = True
    else:
        isFirstBuild = False

    helpMsg = [
        "",
        "novelWriter Setup Tool",
        "======================",
        "",
        "This tool provides setup and build commands for installing or distibuting",
        "novelWriter as a package on Linux, Mac and Windows. The available options",
        "are as follows:",
        "",
        "General:",
        "",
        "    help           Print the help message.",
        "    pip            Install all package dependencies for novelWriter using pip.",
        "    version        Print the novelWriter version.",
        "    build-clean    Will attempt to delete 'build' and 'dist' folders.",
        "",
        "Additional Builds:",
        "",
        "    manual         Build the help documentation as PDF (requires LaTeX).",
        "    sample         Build the sample project zip file and add it to assets.",
        "    qtlupdate      Update translation files for internationalisation.",
        "                   The files to be updated must be provided as arguments.",
        "    qtlrelease     Build the language files for internationalisation.",
        "    clean-assets   Delete assets built by manual, sample and qtlrelease.",
        "    gen-plist      Generates an Info.plist for use in a MacOS Bundle",
        "",
        "Python Packaging:",
        "",
        "    import-i18n    Import updated i18n files from a zip file.",
        "    windows-zip    Creates a minimal zip file of the core application without",
        "                   all the other source files. Used for Windows builds.",
        "    build-deb      Build a .deb package for Debian and Ubuntu. Add --sign to ",
        "                   sign package.",
        "    build-ubuntu   Build a .deb packages Launchpad. Add --sign to ",
        "                   sign package. Add --first to set build number to 0.",
        "    build-win-exe  Build a setup.exe file with Python embedded for Windows.",
        "                   The package must be built from a minimal windows zip file.",
        "    build-appimage Build an AppImage. Argument --linux-tag defaults to",
        "                   manylinux_2_28_x86_64, and --python-version to 3.11.",
        "",
        "System Install:",
        "",
        "    xdg-install    Install launcher and icons for freedesktop systems. Run as",
        "                   root or with sudo for system-wide install, or as user for",
        "                   single user install.",
        "    xdg-uninstall  Remove the launcher and icons for the current system as",
        "                   installed by the 'xdg-install' command.",
        "",
    ]

    # General
    # =======

    if "help" in sysArgs:
        sysArgs.remove("help")
        print("\n".join(helpMsg))
        sys.exit(0)

    if "version" in sysArgs:
        sysArgs.remove("version")
        print(extractVersion(beQuiet=True)[0], end=None)
        sys.exit(0)

    if "pip" in sysArgs:
        sysArgs.remove("pip")
        installPackages(hostOS)

    if "build-clean" in sysArgs:
        sysArgs.remove("build-clean")
        cleanBuildDirs()

    # Additional Builds
    # =================

    if "manual" in sysArgs:
        sysArgs.remove("manual")
        buildPdfManual()

    if "qtlrelease" in sysArgs:
        sysArgs.remove("qtlrelease")
        buildQtI18n()

    if "qtlupdate" in sysArgs:
        sysArgs.remove("qtlupdate")
        buildQtI18nTS(sysArgs)
        sys.exit(0)  # Don't continue execution

    if "sample" in sysArgs:
        sysArgs.remove("sample")
        buildSampleZip()

    if "clean-assets" in sysArgs:
        sysArgs.remove("clean-assets")
        cleanBuiltAssets()

    if "gen-plist" in sysArgs:
        sysArgs.remove("gen-plist")
        genMacOSPlist()

    # Python Packaging
    # ================

    if "import-i18n" in sysArgs:
        sysArgs.remove("import-i18n")
        importI18nUpdates(sysArgs)
        sys.exit(0)  # Don't continue execution

    if "windows-zip" in sysArgs:
        sysArgs.remove("windows-zip")
        makeWindowsZip()

    if "build-deb" in sysArgs:
        sysArgs.remove("build-deb")
        if hostOS == OS_LINUX:
            if doSign:
                signKey = "D6A9F6B8F227CF7C6F6D1EE84DBBE4B734B0BD08"
            else:
                signKey = None
            makeDebianPackage(signKey=signKey)
        else:
            print("ERROR: Command 'build-deb' can only be used on Linux")
            sys.exit(1)

    if "build-ubuntu" in sysArgs:
        sysArgs.remove("build-ubuntu")
        if hostOS == OS_LINUX:
            makeForLaunchpad(doSign=doSign, isFirst=isFirstBuild)
        else:
            print("ERROR: Command 'build-ubuntu' can only be used on Linux")
            sys.exit(1)

    if "build-win-exe" in sysArgs:
        sysArgs.remove("build-win-exe")
        makeWindowsEmbedded(sysArgs)
        sys.exit(0)  # Don't continue execution

    if "build-appimage" in sysArgs:
        sysArgs.remove("build-appimage")
        if hostOS == OS_LINUX:
            sysArgs = makeAppImage(sysArgs)
        else:
            print("ERROR: Command 'build-appimage' can only be used on Linux")
            sys.exit(1)

    # General Installers
    # ==================

    if "xdg-install" in sysArgs:
        sysArgs.remove("xdg-install")
        if hostOS == OS_WIN:
            print("ERROR: Command 'xdg-install' cannot be used on Windows")
            sys.exit(1)
        else:
            xdgInstall()

    if "xdg-uninstall" in sysArgs:
        sysArgs.remove("xdg-uninstall")
        if hostOS == OS_WIN:
            print("ERROR: Command 'xdg-uninstall' cannot be used on Windows")
            sys.exit(1)
        else:
            xdgUninstall()
