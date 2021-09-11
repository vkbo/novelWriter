#!/usr/bin/env python3
"""
novelWriter – Main Setup Script
===============================
The main setup and install script for all operating systems

File History:
Created: 2019-05-16 [0.5.1]

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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
    except Exception as e:
        print("Could not read file: %s" % initFile)
        print(str(e))

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
    except Exception as e:
        print("Could not generate sha256 file")
        print(str(e))

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
        except Exception as e:
            print("Failed with error:")
            print(str(e))
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

    try:
        subprocess.call(["make", "clean"], cwd="docs")
        stdOut, stdErr, exCode = sysCall(["make latexpdf"], cwd="docs")
        if exCode == 0:
            if os.path.isfile(finalFile):
                os.unlink(finalFile)
            outLines = stdOut.splitlines()
            for aLine in outLines:
                if aLine.startswith("processing manual.tex..."):
                    break
                print(aLine)
            print("\n[LaTeX output truncated ...]\n")
            print("\n".join(outLines[-6:]))
            print("")
            os.rename(buildFile, finalFile)
        else:
            raise Exception(stdErr)

        print("PDF manual build: OK")
        print("")

    except Exception as e:
        print("PDF manual build: FAILED")
        print("")
        print(str(e))
        print("")
        print("Dependencies:")
        print(" * pip install sphinx")
        print(" * Package latexmk")
        print(" * LaTeX build system")
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

    try:
        subprocess.call(["lrelease", "-verbose", "novelWriter.pro"])
    except Exception as e:
        print("Qt5 Linguist tools seem to be missing")
        print("On Debian/Ubuntu, install: qttools5-dev-tools pyqt5-dev-tools")
        print(str(e))
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

def buildQtI18nTS():
    """Build the lang.ts files for Qt Linguist.
    """
    print("")
    print("Building Qt Translation Files")
    print("=============================")
    print("")

    try:
        subprocess.call(["pylupdate5", "-verbose", "-noobsolete", "novelWriter.pro"])
    except Exception as e:
        print("PyQt5 Linguist tools seem to be missing")
        print("On Debian/Ubuntu, install: qttools5-dev-tools pyqt5-dev-tools")
        print(str(e))
        sys.exit(1)

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


# =============================================================================================== #
#  Python Packaging
# =============================================================================================== #

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

    # Build Additional Assets
    # =======================

    buildQtI18n()
    buildSampleZip()
    buildPdfManual()

    # Build Minimal Zip
    # =================

    numVers, _, _ = extractVersion()
    pkgVers = compactVersion(numVers)
    zipFile = f"novelWriter-{pkgVers}-minimal{targName}.zip"
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
        toUpload(f"{bldDir}/{bldPkg}.tar.xz", f"{bldPkg}.debian.tar.xz")
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
    """Wrapper for building debian packages for launcpad.
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
        ("18.04", "bionic"),
        ("20.04", "focal"),
        ("21.04", "hirsute"),
        ("21.10", "impish"),
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
#  Make Simple Package (build-pyz)
##

def makeSimplePackage(embedPython):
    """Run zipapp to freeze the packages. This assumes zipapp and pip
    are already installed.
    """
    import urllib.request
    import zipfile
    import zipapp

    # Set Up Folder
    # =============

    if not os.path.isdir("dist"):
        os.mkdir("dist")

    outDir = os.path.join("dist", "novelWriter")
    zipDir = os.path.join("dist", "zipapp_temp")
    libDir = os.path.join(outDir, "lib")
    if os.path.isdir(zipDir):
        shutil.rmtree(zipDir)
    if os.path.isdir(outDir):
        shutil.rmtree(outDir)

    os.mkdir(outDir)
    os.mkdir(libDir)

    # Download Python Embeddable
    # ==========================

    if embedPython:
        print("")
        print("# Adding Python Embeddable")
        print("# ========================")
        print("")

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

    # Build Additional Assets
    # =======================

    buildQtI18n()
    buildSampleZip()
    buildPdfManual()

    # Copy Package Files
    # ==================

    print("")
    print("# Copying Package Files")
    print("# =====================")
    print("")

    copyList = ["CREDITS.md", "CHANGELOG.md", "LICENSE.md", "requirements.txt"]
    iconList = ["novelwriter.ico", "x-novelwriter-project.ico"]
    cpIgnore = shutil.ignore_patterns("__pycache__")

    print("Copying: novelwriter")
    shutil.copytree("novelwriter", os.path.join(zipDir, "novelwriter"), ignore=cpIgnore)
    for copyFile in copyList:
        print("Copying: %s" % copyFile)
        shutil.copy2(copyFile, os.path.join(outDir, copyFile))
    for iconFile in iconList:
        print("Copying: %s" % iconFile)
        shutil.copy2(os.path.join("setup", "icons", iconFile), os.path.join(outDir, iconFile))

    # Move assets to outDir as it should not be packed with the rest
    print("Copying: assets")
    os.rename(os.path.join(zipDir, "novelwriter", "assets"), os.path.join(outDir, "assets"))

    print("Writing: __main__.py")
    writeFile(os.path.join(zipDir, "__main__.py"), (
        "#!/usr/bin/env python3\n"
        "\n"
        "import os\n"
        "import sys\n"
        "\n"
        "sys.path.insert(\n"
        "    0, os.path.abspath(\n"
        "        os.path.join(os.path.dirname(__file__), os.path.pardir, \"lib\")\n"
        "    )\n"
        ")\n\n"
        "if __name__ == \"__main__\":\n"
        "    import novelwriter\n"
        "    novelwriter.main()\n"
    ))
    print("")

    pyzFile = os.path.join(outDir, "novelWriter.pyz")
    zipapp.create_archive(zipDir, target=pyzFile, interpreter="/usr/bin/env python3")

    # Install Dependencies
    # ====================

    print("")
    print("# Installing Dependencies")
    print("# =======================")
    print("")

    sysCmd  = [sys.executable]
    sysCmd += "-m pip install -r requirements.txt --target".split()
    sysCmd += [libDir]
    try:
        subprocess.call(sysCmd)
    except Exception as e:
        print("Failed with error:")
        print(str(e))
        sys.exit(1)

    for subDir in os.listdir(libDir):
        chkDir = os.path.join(libDir, subDir)
        if os.path.isdir(chkDir) and chkDir.endswith(".dist-info"):
            shutil.rmtree(chkDir)

    print("")

    # Remove Unneeded Library Files
    # =============================

    delQtLibs = [
        "opengl32sw.dll",
        "Qt5DBus.dll",
        "Qt5Designer.dll",
        "Qt5Network.dll",
        "Qt5OpenGL.dll",
        "Qt5Qml.dll",
        "Qt5QmlModels.dll",
        "Qt5QmlWorkerScript.dll",
        "Qt5Quick.dll",
        "Qt5Quick3D.dll",
        "Qt5Quick3DAssetImport.dll",
        "Qt5Quick3DRender.dll",
        "Qt5Quick3DRuntimeRender.dll",
        "Qt5Quick3DUtils.dll",
        "Qt5QuickControls2.dll",
        "Qt5QuickParticles.dll",
        "Qt5QuickShapes.dll",
        "Qt5QuickTemplates2.dll",
        "Qt5QuickTest.dll",
        "Qt5QuickWidgets.dll",
        "Qt5Sql.dll",
    ]
    qtLibDir = os.path.join(libDir, "PyQt5", "Qt", "bin")
    for libName in delQtLibs:
        delFile = os.path.join(qtLibDir, libName)
        if os.path.isfile(delFile):
            print("Deleting: %s" % delFile)
            os.unlink(delFile)

    qmlDir = os.path.join(libDir, "PyQt5", "Qt", "qml")
    if os.path.isdir(qmlDir):
        shutil.rmtree(qmlDir)

    print("")
    print("Done!")
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
#  Windows Installers
# =============================================================================================== #

##
#  Inno Setup Builder (setup-pyz)
##

def innoSetup():
    """Run the Inno Setup tool to build a setup.exe file for Windows based on the pyz package.
    """
    print("")
    print("Running Inno Setup")
    print("##################")
    print("")

    # Read the iss template
    numVers, _, _ = extractVersion()
    issData = readFile(os.path.join("setup", "win_setup_pyz.iss"))
    issData = issData.replace(r"%%version%%", numVers)
    issData = issData.replace(r"%%dir%%", os.getcwd())
    writeFile("setup.iss", issData)
    print("")

    try:
        subprocess.call(["iscc", "setup.iss"])
    except Exception as e:
        print("Inno Setup failed with error:")
        print(str(e))
        sys.exit(1)

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
        "    clean          Will attempt to delete the 'build' and 'dist' folders.",
        "",
        "Additional Builds:",
        "",
        "    manual         Build the help documentation as PDF (requires LaTeX).",
        "    qtlupdate      Update the translation files for internationalisation.",
        "    qtlrelease     Build the language files for internationalisation.",
        "    sample         Build the sample project zip file and add it to assets.",
        "",
        "Python Packaging:",
        "",
        "    minimal-zip    Creates a minimal zip file of the core application without",
        "                   all the other source files. Defaults to tailor the zip file",
        "                   for the current OS, but accepts a target OS flag to build",
        "                   for another OS.",
        "    build-deb      Build a .deb package for Debian and Ubuntu. Add --sign to ",
        "                   sign package.",
        "    build-ubuntu   Build a .deb packages Launchpad. Add --sign to ",
        "                   sign package. Add --first to set build number to 0.",
        "                   Add --snapshot to make a snapshot package."
        "    build-pyz      Build a .pyz package in a folder with all dependencies",
        "                   using the zipapp tool. On Windows, python embeddable is",
        "                   added to the folder.",
        "    setup-pyz      Build a Windows executable installer from a zipapp package",
        "                   using Inno Setup. Must run 'build-pyz' first.",
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

    # Flags and Variables
    makeSetupPyz = False
    simplePack = False
    embedPython = False

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
        buildQtI18nTS()

    if "sample" in sys.argv:
        sys.argv.remove("sample")
        buildSampleZip()

    # Python Packaging
    # ================

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

    if "build-pyz" in sys.argv:
        sys.argv.remove("build-pyz")
        simplePack = True
        if hostOS == OS_WIN:
            embedPython = True

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

    # Windows Setup Installer
    # =======================

    if "setup-pyz" in sys.argv:
        sys.argv.remove("setup-pyz")
        if hostOS == OS_WIN:
            makeSetupPyz = True
        else:
            print("Error: Command 'setup-pyz' for Inno Setup is Windows only.")
            sys.exit(1)

    # Actions
    # =======
    # For functions that are controlled by multiple flags, or need to be
    # run in a specific order.

    if simplePack:
        makeSimplePackage(embedPython)

    if makeSetupPyz:
        innoSetup()

    if len(sys.argv) <= 1:
        # Nothing more to do
        sys.exit(0)

    # Run the standard setup
    import setuptools  # noqa: F401
    setuptools.setup()

# END Main
