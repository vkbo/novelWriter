#!/usr/bin/env python3
"""
novelWriter – Main Setup Script
===============================
The main setup and install script for all operating systems

File History:
Created: 2019-05-16 [0.5.1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import os
import sys
import shutil
import zipfile
import datetime
import subprocess
import email.utils

OS_NONE   = 0
OS_LINUX  = 1
OS_WIN    = 2
OS_DARWIN = 3


# =============================================================================================== #
#  Utilities
# =============================================================================================== #

def extractVersion():
    """Extract the novelWriter version number without having to import
    anything else from the main package.
    """
    def getValue(theString):
        theBits = theString.partition("=")
        return theBits[2].strip().strip('"')

    numVers = "Unknown"
    hexVers = "Unknown"
    relDate = "Unknown"
    initFile = os.path.join("novelwriter", "__init__.py")
    try:
        with open(initFile, mode="r", encoding="utf-8") as inFile:
            for aLine in inFile:
                if aLine.startswith("__version__"):
                    numVers = getValue((aLine))
                if aLine.startswith("__hexversion__"):
                    hexVers = getValue((aLine))
                if aLine.startswith("__date__"):
                    relDate = getValue((aLine))
    except Exception as exc:
        print("Could not read file: %s" % initFile)
        print(str(exc))

    print("novelWriter version: %s (%s) at %s" % (numVers, hexVers, relDate))

    return numVers, hexVers, relDate


def compactVersion(numVers):
    """Make the version number more compact."""
    numVers = numVers.replace("-alpha", "a")
    numVers = numVers.replace("-beta", "b")
    numVers = numVers.replace("-rc", "rc")
    return numVers


def sysCall(callArgs, cwd=None):
    """Wrapper function for system calls.
    """
    sysP = subprocess.Popen(
        callArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=cwd
    )
    stdOut, stdErr = sysP.communicate()
    return stdOut.decode("utf-8"), stdErr.decode("utf-8"), sysP.returncode


def readFile(fileName):
    """Read an entire file and return as a string.
    """
    with open(fileName, mode="r") as inFile:
        return inFile.read()


def writeFile(fileName, writeText):
    """Write string to file.
    """
    with open(fileName, mode="w+") as outFile:
        outFile.write(writeText)


def toUpload(srcPath, dstName=None):
    """Copy a file produced by one of the build functions to the uplaod
    directory. The file can optionally be given a new name."""
    uplDir = "dist_upload"
    if not os.path.isdir(uplDir):
        os.mkdir(uplDir)
    if dstName is None:
        dstName = os.path.basename(srcPath)
    shutil.copyfile(srcPath, os.path.join(uplDir, dstName))
    return


def makeCheckSum(sumFile, cwd=None):
    """Create a SHA256 checkcusm file.
    """
    try:
        if cwd is None:
            shaFile = sumFile+".sha256"
        else:
            shaFile = os.path.join(cwd, sumFile+".sha256")
        with open(shaFile, mode="w") as fOut:
            subprocess.call(["sha256sum", sumFile], stdout=fOut, cwd=cwd)
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

def installPackages(hostOS):
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

def cleanBuildDirs():
    """Recursively delete the 'build' and 'dist' folders.
    """
    print("")
    print("Cleaning up build environment ...")
    print("")

    def removeFolder(rmDir):
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
#  Additional Buiilds
# =============================================================================================== #

##
#  Build PDF Manual (manual)
##

def buildPdfManual():
    """This function will build the documentation as manual.pdf.
    """
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

def buildQtI18n():
    """Build the lang.qm files for Qt Linguist.
    """
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

def buildQtI18nTS(sysArgs):
    """Build the lang.ts files for Qt Linguist.
    """
    print("")
    print("Building Qt Translation Files")
    print("=============================")

    print("")
    print("Scanning Source Tree:")
    print("")

    srcList = [os.path.join("i18n", "qtbase.py")]
    for nRoot, _, nFiles in os.walk("novelwriter"):
        if os.path.isdir(nRoot):
            for aFile in nFiles:
                aPath = os.path.join(nRoot, aFile)
                if os.path.isfile(aPath) and aFile.endswith(".py"):
                    srcList.append(aPath)

    for aSource in srcList:
        print(aSource)

    print("")
    print("TS Files to Update:")
    print("")

    tsList = []
    if len(sysArgs) >= 2:
        for anArg in sysArgs[1:]:
            if not (anArg.startswith("i18n") and anArg.endswith(".ts")):
                continue

            fName = os.path.basename(anArg)
            if not fName.startswith("nw_") and len(fName) > 6:
                print("Skipping non-novelWriter TS file %s" % fName)
                continue

            if os.path.isfile(anArg):
                tsList.append(anArg)
            elif os.path.exists(anArg):
                pass
            else:  # Create an empty new language file
                lCode = fName[3:-3]
                writeFile(anArg, (
                    "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                    "<!DOCTYPE TS>\n"
                    f"<TS version=\"2.0\" language=\"{lCode}\" sourcelanguage=\"en_GB\"/>\n"
                ))
                tsList.append(anArg)

    else:
        print("No translation files selected for update ...")
        print("")
        return

    for aTS in tsList:
        print(aTS)

    print("")
    print("Updating Language Files:")
    print("")

    # Using the pylupdate tool from PyQt6 instead as it supports TS file
    # format 2.1. This can perhaps be changed back to the installed tool
    # at a later time.
    from i18n.pylupdate6 import lupdate
    lupdate(srcList, tsList, no_obsolete=True, no_summary=False)

    print("")

    return


##
#  Sample Project ZIP File Builder (sample)
##

def buildSampleZip():
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


def cleanBuiltAssets():
    """Remove assets built by this script.
    """
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


def checkAssetsExist():
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

def importI18nUpdates(sysArgs):
    """Import new translation files from a zip file.
    """
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

def makeMinimalPackage(targetOS):
    """Pack the core source file in a single zip file.
    """
    from zipfile import ZipFile, ZIP_DEFLATED

    print("")
    print("Building Minimal ZIP File")
    print("=========================")

    bldDir = "dist_minimal"
    if not os.path.isdir(bldDir):
        os.mkdir(bldDir)

    if targetOS == OS_LINUX:
        targName = "-linux"
        print("Target OS: Linux")
    elif targetOS == OS_DARWIN:
        targName = "-darwin"
        print("Target OS: Darwin")
    elif targetOS == OS_WIN:
        targName = "-win"
        print("Target OS: Windows")
    else:
        targName = ""
    print("")

    # Check Additional Assets
    # =======================

    if not checkAssetsExist():
        print("ERROR: Missing build assets")
        sys.exit(1)

    # Build Minimal Zip
    # =================

    numVers, _, _ = extractVersion()
    pkgVers = compactVersion(numVers)
    zipFile = f"novelwriter-{pkgVers}-minimal{targName}.zip"
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
        "setup.py",
        "setup.cfg",
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

        if targetOS == OS_WIN:
            zipObj.write("novelWriter.py", "novelWriter.pyw")
            print("Added: novelWriter.pyw")
            zipObj.write(os.path.join("setup", "windows_install.bat"), "windows_install.bat")
            print("Added: windows_install.bat")
            zipObj.write(os.path.join("setup", "windows_uninstall.bat"), "windows_uninstall.bat")
            print("Added: windows_uninstall.bat")

        else:  # Linux and Mac
            # Add icons
            for nRoot, _, nFiles in os.walk(os.path.join("setup", "data")):
                print("Added: %s/* [Files: %d]" % (nRoot, len(nFiles)))
                for aFile in nFiles:
                    zipObj.write(os.path.join(nRoot, aFile))

            zipObj.write(os.path.join("setup", "description_pypi.md"))
            print("Added: setup/description_pypi.md")

            zipObj.write("novelWriter.py")
            print("Added: novelWriter.py")

        for aFile in rootFiles:
            print("Added: %s" % aFile)
            zipObj.write(aFile)

        zipObj.write(os.path.join("novelwriter", "assets", "manual.pdf"), "UserManual.pdf")
        print("Added: UserManual.pdf")

    print("")
    print("Created File: %s" % outFile)

    # Create Checksum File
    # ====================

    shaFile = makeCheckSum(zipFile, cwd=bldDir)

    toUpload(outFile)
    toUpload(shaFile)

    print("")

    return


##
#  Make Debian Package (build-deb)
##

def makeDebianPackage(signKey=None, sourceBuild=False, distName="unstable", buildName=""):
    """Build a Debian package.
    """
    print("")
    print("Build Debian Package")
    print("====================")
    print("On Debian/Ubuntu install: dh-python python3-all debhelper devscripts")
    print("")

    # Version Info
    # ============

    numVers, hexVers, relDate = extractVersion()
    pkgVers = compactVersion(numVers)
    relDate = datetime.datetime.strptime(relDate, "%Y-%m-%d")
    pkgDate = email.utils.format_datetime(relDate.replace(hour=12, tzinfo=None))
    print("")

    if buildName:
        pkgVers = f"{pkgVers}{buildName}"

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

    setupCfg = readFile("setup.cfg").replace(
        "file: setup/description_pypi.md", "file: data/description_short.txt"
    )
    writeFile(f"{outDir}/setup.cfg", setupCfg)
    print("Wrote:  setup.cfg")

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
        if hexVers[-2] == "f":
            ppaName = "novelwriter"
        else:
            ppaName = "novelwriter-pre"

        return f"dput {ppaName}/{distName} {bldDir}/{bldPkg}_source.changes"

    return ""


##
#  Make Launchpad Package (build-ubuntu)
##

def makeForLaunchpad(doSign=False, isFirst=False, isSnapshot=False):
    """Wrapper for building debian packages for launchpad.
    """
    print("")
    print("Launchpad Packages")
    print("==================")
    print("")

    if isFirst or isSnapshot:
        bldNum = "0"
    else:
        bldNum = input("Build number [0]: ")
        if bldNum == "":
            bldNum = "0"

    distLoop = [
        ("20.04", "focal"),
        ("22.04", "jammy"),
        ("22.10", "kinetic"),
        ("23.04", "lunar"),
    ]

    tStamp = datetime.datetime.now().strftime("%Y%m%d~%H%M%S")
    if isSnapshot:
        print(f"Building Ununtu SNAPSHOT~{tStamp} for:")
        print("")
    else:
        print("Building Ubuntu packages for:")
        print("")
    for distNum, codeName in distLoop:
        print(f" * Ubuntu {distNum} {codeName.title()}")
    print("")

    if doSign:
        signKey = "D6A9F6B8F227CF7C6F6D1EE84DBBE4B734B0BD08"
    else:
        signKey = None

    print(f"Sign Key: {str(signKey)}")
    print("")

    dputCmd = []
    for distNum, codeName in distLoop:
        if isSnapshot:
            buildName = f"+SNAPSHOT~{tStamp}~ubuntu{distNum}.0"
        else:
            buildName = f"~ubuntu{distNum}.{bldNum}"

        dCmd = makeDebianPackage(
            signKey=signKey,
            sourceBuild=True,
            distName=codeName,
            buildName=buildName
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

def makeAppImage(sysArgs):
    """Build an Appimage
    """
    import glob
    import argparse
    import platform

    try:
        import python_appimage  # noqa F401
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
        default=f"manylinux2010_{platform.machine()}",
        help=(
            "linux compatibility tag (e.g. manylinux1_x86_64) \n"
            "see https://python-appimage.readthedocs.io/en/latest/#available-python-appimages \n"
            "and https://github.com/pypa/manylinux for a list of valid tags"
        ),
    )
    parser.add_argument(
        "--python-version", nargs="?", default="3.10", help="python version (e.g. 3.10)"
    )

    args, unparsedArgs = parser.parse_known_args(sysArgs)

    linuxTag = args.linux_tag
    pythonVer = args.python_version

    # Version Info
    # ============

    numVers, _, relDate = extractVersion()
    pkgVers = compactVersion(numVers)
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

    # Remove old Appimages
    outFiles = glob.glob(f"{bldDir}/*.AppImage")

    if outFiles:
        print("Removing old AppImages")
        print("")
        for image in outFiles:
            try:
                os.remove(image)
            except OSError:
                print("Error while deleting file : ", image)

    # Build Additional Assets
    # =======================

    buildQtI18n()
    buildSampleZip()
    buildPdfManual()

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

    setupCfg = readFile("setup.cfg").replace(
        "file: setup/description_pypi.md", "file: data/description_short.txt"
    )
    writeFile(f"{outDir}/setup.cfg", setupCfg)
    print("Wrote:  setup.cfg")

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
    print("Copied: setup/data/novelwriter.desktop")

    shutil.copyfile("setup/icons/novelwriter.svg", f"{imageDir}/novelwriter.svg")
    print("Copied: setup/icons/novelwriter.svg")

    shutil.copyfile(
        "setup/data/hicolor/256x256/apps/novelwriter.png", f"{imageDir}/novelwriter.png"
    )
    print("Copied: setup/data/hicolor/256x256/apps/novelwriter.png")

    # Build Appimage
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
        print("Dependencies:")
        print(" * pip install python-appimage")
        print("")
        sys.exit(1)

    bldFile = glob.glob(f"{bldDir}/*.AppImage")[0]
    outFile = f"{bldDir}/novelWriter-{pkgVers}-py{pythonVer}-{linuxTag}.AppImage"
    os.rename(bldFile, outFile)
    shaFile = makeCheckSum(os.path.basename(outFile), cwd=bldDir)

    toUpload(outFile)
    toUpload(shaFile)

    return unparsedArgs


##
#  Make Windows Setup EXE (build-win-exe)
##

def makeWindowsEmbedded(sysArgs):
    """Set up a package with embedded Python and dependencies for
    Windows installation.
    """
    import urllib.request
    import zipfile
    import compileall

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

    def unlinkIfFound(delFile):
        if os.path.isfile(delFile):
            os.unlink(delFile)
            print("Deleted: %s" % delFile)

    def deleteFolder(delPath):
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

    issName = os.path.join("dist", f"novelwriter-{packVersion}-win10-amd64-setup.exe")
    newName = os.path.join("dist", f"novelwriter-{packVersion}-py{pyVers}-win10-amd64-setup.exe")
    os.replace(issName, newName)

    print(f"Installer: {newName}")
    print("")

    return


# =============================================================================================== #
#  General Installers
# =============================================================================================== #

##
#  XDG Installation (xdg-install)
##

def xdgInstall():
    """Will attempt to install icons and make a launcher.
    """
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

def xdgUninstall():
    """Will attempt to uninstall icons and make a launcher.
    """
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


##
#  WIN Installation (win-install)
##

def winInstall():
    """Will attempt to install icons and make a launcher for Windows.
    """
    import winreg
    try:
        import win32com.client
    except ImportError:
        print(
            "ERROR: Package 'pywin32' is missing on this system.\n"
            "       Please run 'setup.py pip' to automatically install\n"
            "       dependecies, or run 'pip install --user pywin32'."
        )
        sys.exit(1)

    print("")
    print("Windows Install")
    print("===============")
    print("")

    numVers, hexVers, _ = extractVersion()
    nwTesting = not hexVers[-2] == "f"
    wShell = win32com.client.Dispatch("WScript.Shell")

    if nwTesting:
        linkName = "novelWriter Testing %s.lnk" % numVers
    else:
        linkName = "novelWriter %s.lnk" % numVers

    desktopDir = wShell.SpecialFolders("Desktop")
    desktopIcon = os.path.join(desktopDir, linkName)

    startMenuDir = wShell.SpecialFolders("StartMenu")
    startMenuProg = os.path.join(startMenuDir, "Programs", "novelWriter")
    startMenuIcon = os.path.join(startMenuProg, linkName)

    pythonDir = os.path.dirname(sys.executable)
    pythonExe = os.path.join(pythonDir, "pythonw.exe")

    targetDir = os.path.abspath(os.path.dirname(__file__))
    targetPy = os.path.join(targetDir, "novelWriter.pyw")
    targetIcon = os.path.join(targetDir, "novelwriter", "assets", "icons", "novelwriter.ico")

    if not os.path.isfile(targetPy):
        shutil.copy2(os.path.join(targetDir, "novelWriter.py"), targetPy)

    print("")
    print("Collecting Info ...")
    print("Desktop Folder:    %s" % desktopDir)
    print("Start Menu Folder: %s" % startMenuDir)
    print("Python Executable: %s" % pythonExe)
    print("Target Executable: %s" % targetPy)
    print("Target Icon:       %s" % targetIcon)
    print("")

    print("Creating Links ...")
    if os.path.isfile(desktopIcon):
        os.unlink(desktopIcon)
        print("Deleted: %s" % desktopIcon)

    if os.path.isdir(startMenuProg):
        for oldIcon in os.listdir(startMenuProg):
            oldPath = os.path.join(startMenuProg, oldIcon)
            if not oldIcon.startswith("novelWriter"):
                continue

            isTesting = oldIcon.startswith("novelWriter Testing")
            if isTesting and nwTesting:
                os.unlink(oldPath)
                print("Deleted: %s" % oldPath)
            if not isTesting and not nwTesting:
                os.unlink(oldPath)
                print("Deleted: %s" % oldPath)

    else:
        os.mkdir(startMenuProg)
        print("Created: %s" % startMenuProg)

    wShortcut = wShell.CreateShortCut(desktopIcon)
    wShortcut.TargetPath = targetPy
    wShortcut.WorkingDirectory = targetDir
    wShortcut.IconLocation = targetIcon
    wShortcut.WindowStyle = 1
    wShortcut.save()
    print("Created: %s" % desktopIcon)

    wShortcut = wShell.CreateShortCut(startMenuIcon)
    wShortcut.TargetPath = targetPy
    wShortcut.WorkingDirectory = targetDir
    wShortcut.IconLocation = targetIcon
    wShortcut.WindowStyle = 1
    wShortcut.save()
    print("Created: %s" % startMenuIcon)

    print("")
    print("Creating registry keys ...")

    def setKey(kPath, kName, kVal):
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, kPath)
        regKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, kPath, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(regKey, kName, 0, winreg.REG_SZ, kVal)
        winreg.CloseKey(regKey)

    mimeIcon = os.path.join(
        targetDir, "novelwriter", "assets", "icons", "x-novelwriter-project.ico"
    )
    mimeExec = '"%s" "%s" "%%1"' % (pythonExe, targetPy)

    try:
        setKey(r"Software\Classes\.nwx\OpenWithProgids", "novelWriterProject.nwx", "")
        setKey(r"Software\Classes\novelWriterProject.nwx", "", "novelWriter Project File")
        setKey(r"Software\Classes\novelWriterProject.nwx\DefaultIcon", "", mimeIcon)
        setKey(r"Software\Classes\novelWriterProject.nwx\shell\open\command", "", mimeExec)
        setKey(r"Software\Classes\Applications\novelWriter.pyw\SupportedTypes", ".nwx", "")
    except WindowsError:
        print("ERROR: Failed to set registry keys.")
        print("")

    print("")
    print("Done!")
    print("")

    return


##
#  WIN Uninstallation (win-uninstall)
##

def winUninstall():
    """Will attempt to uninstall icons previously installed.
    """
    import winreg
    try:
        import win32com.client
    except ImportError:
        print(
            "ERROR: Package 'pywin32' is missing on this system.\n"
            "       Please run 'pip install --user pywin32' to install it."
        )
        sys.exit(1)

    print("")
    print("Windows Uninstall")
    print("=================")
    print("")

    numVers, hexVers, _ = extractVersion()
    nwTesting = not hexVers[-2] == "f"
    wShell = win32com.client.Dispatch("WScript.Shell")

    if nwTesting:
        linkName = "novelWriter Testing %s.lnk" % numVers
    else:
        linkName = "novelWriter %s.lnk" % numVers

    desktopDir = wShell.SpecialFolders("Desktop")
    desktopIcon = os.path.join(desktopDir, linkName)

    startMenuDir = wShell.SpecialFolders("StartMenu")
    startMenuProg = os.path.join(startMenuDir, "Programs", "novelWriter")
    startMenuIcon = os.path.join(startMenuProg, linkName)

    print("")
    print("Deleting Links ...")
    if os.path.isfile(desktopIcon):
        os.unlink(desktopIcon)
        print("Deleted: %s" % desktopIcon)
    else:
        print("Not Found: %s" % desktopIcon)

    if os.path.isfile(startMenuIcon):
        os.unlink(startMenuIcon)
        print("Deleted: %s" % startMenuIcon)
    else:
        print("Not Found: %s" % startMenuIcon)

    if os.path.isdir(startMenuProg):
        if not os.listdir(startMenuProg):
            os.rmdir(startMenuProg)
            print("Deleted: %s" % startMenuProg)
        else:
            print("Not Empty: %s" % startMenuProg)

    print("")
    print("Removing registry keys ...")

    theKeys = [
        r"Software\Classes\novelWriterProject.nwx\shell\open\command",
        r"Software\Classes\novelWriterProject.nwx\shell\open",
        r"Software\Classes\novelWriterProject.nwx\shell",
        r"Software\Classes\novelWriterProject.nwx\DefaultIcon",
        r"Software\Classes\novelWriterProject.nwx",
        r"Software\Classes\.nwx\OpenWithProgids",
        r"Software\Classes\.nwx",
        r"Software\Classes\Applications\novelWriter.pyw\SupportedTypes",
        r"Software\Classes\Applications\novelWriter.pyw",
    ]

    for aKey in theKeys:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, aKey)
            print("Deleted: HKEY_CURRENT_USER\\%s" % aKey)
        except WindowsError:
            print("Not Found: HKEY_CURRENT_USER\\%s" % aKey)

    print("")
    print("Done!")
    print("")

    return


# =============================================================================================== #
#  Process Command Line
# =============================================================================================== #

if __name__ == "__main__":
    """Parse command line options and run the commands.
    """
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

    # Set Target OS
    if "--target-linux" in sys.argv:
        sys.argv.remove("--target-linux")
        targetOS = OS_LINUX
    elif "--target-darwin" in sys.argv:
        sys.argv.remove("--target-darwin")
        targetOS = OS_DARWIN
    elif "--target-win" in sys.argv:
        sys.argv.remove("--target-win")
        targetOS = OS_WIN
    else:
        targetOS = hostOS

    # Sign package
    if "--sign" in sys.argv:
        sys.argv.remove("--sign")
        doSign = True
    else:
        doSign = False

    # First build
    if "--first" in sys.argv:
        sys.argv.remove("--first")
        isFirstBuild = True
    else:
        isFirstBuild = False

    # Build snapshot
    if "--snapshot" in sys.argv:
        sys.argv.remove("--snapshot")
        isSnapshot = True
    else:
        isSnapshot = False

    helpMsg = [
        "",
        "novelWriter Setup Tool",
        "======================",
        "",
        "This tool provides setup and build commands for installing or distibuting",
        "novelWriter as a package on Linux, Mac and Windows. The available options",
        "are as follows:",
        "",
        "Some of the commands can be targeted towards a different OS than the host OS.",
        "To target the command, add one of '--target-linux', '--target-darwin' or",
        "'--target-win'.",
        "",
        "General:",
        "",
        "    help           Print the help message.",
        "    pip            Install all package dependencies for novelWriter using pip.",
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
        "",
        "Python Packaging:",
        "",
        "    import-i18n    Import updated i18n files from a zip file.",
        "    minimal-zip    Creates a minimal zip file of the core application without",
        "                   all the other source files. Defaults to tailor the zip file",
        "                   for the current OS, but accepts a target OS flag to build",
        "                   for another OS.",
        "    build-deb      Build a .deb package for Debian and Ubuntu. Add --sign to ",
        "                   sign package.",
        "    build-ubuntu   Build a .deb packages Launchpad. Add --sign to ",
        "                   sign package. Add --first to set build number to 0.",
        "                   Add --snapshot to make a snapshot package.",
        "    build-win-exe  Build a setup.exe file with Python embedded for Windows.",
        "                   The package must be built from a minimal windows zip file.",
        "    build-appimage Build an AppImage. Argument --linux-tag defaults to",
        "                   manylinux1_x86_64 / i386, and --python-version to 3.10.",
        "",
        "System Install:",
        "",
        "    install        Installs novelWriter to the system's Python install",
        "                   location. Run as root or with sudo for system-wide install,",
        "                   or as user for single user install.",
        "    xdg-install    Install launcher and icons for freedesktop systems. Run as",
        "                   root or with sudo for system-wide install, or as user for",
        "                   single user install.",
        "    xdg-uninstall  Remove the launcher and icons for the current system as",
        "                   installed by the 'xdg-install' command.",
        "    win-install    Install desktop icon, start menu icon, and registry entries",
        "                   for file association with .nwx files for Windows systems.",
        "    win-uninstall  Remove desktop icon, start menu icon, and registry keys,",
        "                   for the current system. Note that it only removes icons for",
        "                   the version number of the package the command is run from.",
        "",
    ]

    # General
    # =======

    if "help" in sys.argv:
        sys.argv.remove("help")
        print("\n".join(helpMsg))
        sys.exit(0)

    if "version" in sys.argv:
        sys.argv.remove("version")
        print("Checking source version info ...")
        extractVersion()
        sys.exit(0)

    if "pip" in sys.argv:
        sys.argv.remove("pip")
        installPackages(hostOS)

    if "build-clean" in sys.argv:
        sys.argv.remove("build-clean")
        cleanBuildDirs()

    # Additional Builds
    # =================

    if "manual" in sys.argv:
        sys.argv.remove("manual")
        buildPdfManual()

    if "qtlrelease" in sys.argv:
        sys.argv.remove("qtlrelease")
        buildQtI18n()

    if "qtlupdate" in sys.argv:
        sys.argv.remove("qtlupdate")
        buildQtI18nTS(sys.argv)
        sys.exit(0)  # Don't continue execution

    if "sample" in sys.argv:
        sys.argv.remove("sample")
        buildSampleZip()

    if "clean-assets" in sys.argv:
        sys.argv.remove("clean-assets")
        cleanBuiltAssets()

    # Python Packaging
    # ================

    if "import-i18n" in sys.argv:
        sys.argv.remove("import-i18n")
        importI18nUpdates(sys.argv)
        sys.exit(0)  # Don't continue execution

    if "minimal-zip" in sys.argv:
        sys.argv.remove("minimal-zip")
        makeMinimalPackage(targetOS)

    if "build-deb" in sys.argv:
        sys.argv.remove("build-deb")
        if hostOS == OS_LINUX:
            if doSign:
                signKey = "D6A9F6B8F227CF7C6F6D1EE84DBBE4B734B0BD08"
            else:
                signKey = None
            makeDebianPackage(signKey=signKey)
        else:
            print("ERROR: Command 'build-deb' can only be used on Linux")
            sys.exit(1)

    if "build-ubuntu" in sys.argv:
        sys.argv.remove("build-ubuntu")
        if hostOS == OS_LINUX:
            makeForLaunchpad(doSign=doSign, isFirst=isFirstBuild, isSnapshot=isSnapshot)
        else:
            print("ERROR: Command 'build-ubuntu' can only be used on Linux")
            sys.exit(1)

    if "build-win-exe" in sys.argv:
        sys.argv.remove("build-win-exe")
        makeWindowsEmbedded(sys.argv)
        sys.exit(0)  # Don't continue execution

    if "build-appimage" in sys.argv:
        sys.argv.remove("build-appimage")
        if hostOS == OS_LINUX:
            sys.argv = makeAppImage(sys.argv)  # Build appimage and prune its args
        else:
            print("ERROR: Command 'build-appimage' can only be used on Linux")
            sys.exit(1)

    # General Installers
    # ==================

    if "xdg-install" in sys.argv:
        sys.argv.remove("xdg-install")
        if hostOS == OS_WIN:
            print("ERROR: Command 'xdg-install' cannot be used on Windows")
            sys.exit(1)
        else:
            xdgInstall()

    if "xdg-uninstall" in sys.argv:
        sys.argv.remove("xdg-uninstall")
        if hostOS == OS_WIN:
            print("ERROR: Command 'xdg-uninstall' cannot be used on Windows")
            sys.exit(1)
        else:
            xdgUninstall()

    if "win-install" in sys.argv:
        sys.argv.remove("win-install")
        if hostOS == OS_WIN:
            winInstall()
        else:
            print("ERROR: Command 'win-install' can only be used on Windows")
            sys.exit(1)

    if "win-uninstall" in sys.argv:
        sys.argv.remove("win-uninstall")
        if hostOS == OS_WIN:
            winUninstall()
        else:
            print("ERROR: Command 'win-uninstall' can only be used on Windows")
            sys.exit(1)

    # Actions
    # =======

    if len(sys.argv) <= 1:
        # Nothing more to do
        sys.exit(0)

    # Run the standard setup
    import setuptools  # noqa: F401
    setuptools.setup()

# END Main
