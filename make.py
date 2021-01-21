#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This make script is intended for building distributable packages of
novelWriter. These are either:

 * A single file executable named dist/novelWriter(.exe). This is a
   quite slow option, and the file is fairly big.
 * A single directory named dist/novelWriter with a novelWriter(.exe),
   and all dependecies included.
 * The latter can be combined with a build stage of a setup.exe file if
   on Windows. This requires Inno Setup to be installed and in path.

In addition, providing the pip otion will cause the script to try to
install all dependencies needed for runing the build, and for running
novelWriter itself.
"""

import os
import sys
import shutil
import subprocess

OS_NONE   = 0
OS_LINUX  = 1
OS_WIN    = 2
OS_DARWIN = 3

# =============================================================================================== #
#  Package Installer
# =============================================================================================== #

def installPackages(hostOS):
    """Install package dependencies both for this script and for running
    novelWriter itself.
    """
    print("")
    print("Installing Dependencies")
    print("#######################")
    print("")

    installQueue = ["pip", "-r requirements.txt"]
    if hostOS == OS_DARWIN:
        installQueue.append("pyobjc")

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

# =============================================================================================== #
#  Run PyInstaller on Package
# =============================================================================================== #

def freezePackage(buildWindowed, oneFile, makeSetup, hostOS):
    """Run PyInstaller to freeze the packages. This assumes all
    dependencies are already in place.
    """
    import PyInstaller.__main__ # noqa: E402

    print("")
    print("Running PyInstaller")
    print("###################")
    print("")

    if hostOS == OS_WIN:
        dotDot = ";"
    else:
        dotDot = ":"

    sys.modules["FixTk"] = None
    instOpt = [
        "--name=novelWriter",
        "--clean",
        "--add-data=%s%s%s" % (os.path.join("nw", "assets"), dotDot, "assets"),
        "--icon=%s" % os.path.join("nw", "assets", "icons", "novelwriter.ico"),
        "--exclude-module=PyQt5.QtQml",
        "--exclude-module=PyQt5.QtBluetooth",
        "--exclude-module=PyQt5.QtDBus",
        "--exclude-module=PyQt5.QtMultimedia",
        "--exclude-module=PyQt5.QtMultimediaWidgets",
        "--exclude-module=PyQt5.QtNetwork",
        "--exclude-module=PyQt5.QtNetworkAuth",
        "--exclude-module=PyQt5.QtNfc",
        "--exclude-module=PyQt5.QtQuick",
        "--exclude-module=PyQt5.QtQuickWidgets",
        "--exclude-module=PyQt5.QtRemoteObjects",
        "--exclude-module=PyQt5.QtSensors",
        "--exclude-module=PyQt5.QtSerialPort",
        "--exclude-module=PyQt5.QtSql",
        "--exclude-module=FixTk",
        "--exclude-module=tcl",
        "--exclude-module=tk",
        "--exclude-module=_tkinter",
        "--exclude-module=tkinter",
        "--exclude-module=Tkinter",
    ]

    if buildWindowed:
        instOpt.append("--windowed")

    if oneFile and not makeSetup:
        instOpt.append("--onefile")
    else:
        instOpt.append("--onedir")

    instOpt.append("novelWriter.py")

    # Make sample.zip first
    try:
        subprocess.call([sys.executable, "setup.py", "sample"])
    except Exception as e:
        print("Failed with error:")
        print(str(e))
        sys.exit(1)

    PyInstaller.__main__.run(instOpt)

    if not oneFile:
        # These files are not needed, and take up a fair bit of space.
        delFiles = []
        if hostOS == OS_WIN:
            delFiles = [
                "Qt5DBus.dll",
                "Qt5Network.dll",
                "Qt5Qml.dll",
                "Qt5QmlModels.dll",
                "Qt5Quick.dll",
                "Qt5Quick3D.dll",
                "Qt5Quick3DAssetImport.dll",
                "Qt5Quick3DRender.dll",
                "Qt5Quick3DRuntimeRender.dll",
                "Qt5Quick3DUtils.dll",
                "Qt5Sql.dll"
            ]
        elif hostOS == OS_LINUX:
            delFiles = [
                "libQt5DBus.so.5",
                "libQt5Network.so.5",
                "libQt5Qml.so.5",
                "libQt5QmlModels.so.5",
                "libQt5Quick.so.5",
                "libQt5Quick3D.so.5",
                "libQt5Quick3DAssetImport.so.5",
                "libQt5Quick3DRender.so.5",
                "libQt5Quick3DRuntimeRender.so.5",
                "libQt5Quick3DUtils.so.5",
                "libQt5Sql.so.5"
            ]
        distDir = os.path.join(os.getcwd(), "dist", "novelWriter")
        for delFile in delFiles:
            delPath = os.path.join(distDir, delFile)
            if os.path.isfile(delPath):
                print("Deleting file: %s" % delPath)
                os.unlink(delPath)

    print("")
    print("Build Finished")
    print("")
    print("The novelWriter executable should be in the folder named 'dist'")
    print("")

    return

# =============================================================================================== #
#  Make Simple Package
# =============================================================================================== #

def makeWindowsPackage():
    """Run zipapp to freeze the packages. This assumes zipapp and pip
    are already installed.
    """
    import urllib.request
    import zipfile

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

    # Download Python Embeddable
    # ==========================

    print("")
    print("# Downloading Python Embeddable")
    print("# =============================")
    print("")

    pyUrl = "https://www.python.org/ftp/python/3.8.7/python-3.8.7-embed-amd64.zip"
    pyZip = os.path.join(outDir, "python_embed.zip")
    print("URL: %s" % pyUrl)

    urllib.request.urlretrieve(pyUrl, pyZip)

    print("Extracting ...")
    with zipfile.ZipFile(pyZip, "r") as inFile:
        inFile.extractall(outDir)

    os.unlink(pyZip)
    print("")

    # Make sample.zip
    # ===============

    try:
        subprocess.call([sys.executable, "setup.py", "sample"])
    except Exception as e:
        print("Failed with error:")
        print(str(e))
        sys.exit(1)

    # Copy Package Files
    # ==================

    print("")
    print("# Copying Package Files")
    print("# =====================")
    print("")

    copyList = ["CHANGELOG.md", "LICENSE.md", "requirements.txt"]
    iconList = ["novelwriter.ico", "x-novelwriter-project.ico"]
    cpIgnore = shutil.ignore_patterns("__pycache__")

    print("Copying: nw")
    shutil.copytree("nw", os.path.join(outDir, "nw"), ignore=cpIgnore)
    for copyFile in copyList:
        print("Copying: %s" % copyFile)
        shutil.copy2(copyFile, os.path.join(outDir, copyFile))
    for iconFile in iconList:
        print("Copying: %s" % iconFile)
        shutil.copy2(os.path.join("setup", "icons", iconFile), os.path.join(outDir, iconFile))

    print("Writing: novelWriter.pyw")
    with open(os.path.join(outDir, "novelWriter.pyw"), mode="w") as outFile:
        outFile.write(
            "#!\"pythonw.exe\"\n"
            "\n"
            "import os\n"
            "import sys\n"
            "\n"
            "sys.path.insert(\n"
            "    0, os.path.abspath(os.path.join(os.path.dirname(__file__), \"lib\"))\n"
            ")\n\n"
            "if __name__ == \"__main__\":\n"
            "    import nw\n"
            "    nw.main()\n"
        )
    print("")

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
#  Inno Setup Builder
# =============================================================================================== #

def innoSetup(setupType):
    """Run the Inno Setup tool to build a setup.exe file for Windows.
    """
    print("")
    print("Running Inno Setup")
    print("##################")
    print("")

    # Read the iss template
    issData = ""
    with open(os.path.join("setup", "win_setup_%s.iss" % setupType), mode="r") as inFile:
        issData = inFile.read()

    import nw # noqa: E402
    issData = issData.replace(r"%%version%%", nw.__version__)
    issData = issData.replace(r"%%dir%%", os.getcwd())

    with open("setup.iss", mode="w+") as outFile:
        outFile.write(issData)

    try:
        subprocess.call(["iscc", "setup.iss"])
    except Exception as e:
        print("Inno Setup failed with error:")
        print(str(e))
        sys.exit(1)

    return

# =============================================================================================== #
#  Clean Build and Dist Folders
# =============================================================================================== #

def cleanInstall():
    """Recursively delete the 'build' and 'dist' folders.
    """
    print("")
    print("Cleaning up build environment ...")

    buildDir = os.path.join(os.getcwd(), "build")
    if os.path.isdir(buildDir):
        try:
            shutil.rmtree(buildDir)
            print("Deleted folder 'build'")
        except Exception as e:
            print("Error: Cannot delete 'build' folder.")
            print(str(e))
            sys.exit(1)
    else:
        print("Folder 'build' not found")

    distDir = os.path.join(os.getcwd(), "dist")
    if os.path.isdir(distDir):
        try:
            shutil.rmtree(distDir)
            print("Deleted folder 'dist'")
        except Exception as e:
            print("Error: Cannot delete 'dist' folder.")
            print(str(e))
            sys.exit(1)
    else:
        print("Folder 'dist' not found")

    print("")

    return

# =============================================================================================== #
#  Process Build Steps
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

    # Flags and Variables
    buildWindowed = True
    oneFile = False
    makeSetupExe = False
    makeSetupPyz = False
    doFreeze = False
    winPack = False

    helpMsg = (
        "\n"
        "novelWriter Make Tool\n"
        "=====================\n"
        "\n"
        "This tool provides build commands for distibuting novelWriter as a package on Linux and\n"
        "Windows. The available options are as follows:\n"
        "\n"
        "General:\n"
        "\n"
        "    help       Print the help message.\n"
        "    pip        Install all package dependencies for novelWriter using pip.\n"
        "    clean      Will attempt to delete the 'build' and 'dist' folders.\n"
        "\n"
        "Python Packaging:\n"
        "\n"
        "    winpack    Creates a pyz package in a folder with all dependencies using the zipapp\n"
        "               tool. This option is intended for Windows deployment.\n"
        "    freeze     Freeze the package and produces a folder with all dependencies using the\n"
        "               pyinstaller tool. This option is not designed for a specific OS.\n"
        "    onefile    Build a standalone executable with all dependencies bundled using the\n"
        "               pyinstaller tool. Implies 'freeze', cannot be used with 'setup_exe'.\n"
        "\n"
        "Windows Installers:\n"
        "\n"
        "    setup_exe  Build a Windows installer from a pyinstaller freeze package using Inno\n"
        "               Setup. This option automatically disables 'onefile'.\n"
        "    setup_pyz  Build a Windows installer from a zipapp package using Inno Setup.\n"
    )

    if "help" in sys.argv or len(sys.argv) <= 1:
        print(helpMsg)
        sys.exit(0)

    if not os.path.isfile(os.path.join(os.getcwd(), "novelWriter.py")):
        print("Error: This script must be run in the root folder of novelWriter.")
        sys.exit(1)

    if not os.path.isdir(os.path.join(os.getcwd(), "nw")):
        print("Error: This script must be run in the root folder of novelWriter.")
        sys.exit(1)

    if "clean" in sys.argv:
        sys.argv.remove("clean")
        cleanInstall()

    if "pip" in sys.argv:
        sys.argv.remove("pip")
        installPackages(hostOS)

    if "freeze" in sys.argv:
        sys.argv.remove("freeze")
        doFreeze = True

    if "onefile" in sys.argv:
        sys.argv.remove("onefile")
        doFreeze = True
        oneFile = True

    if "winpack" in sys.argv:
        sys.argv.remove("winpack")
        winPack = True

    if "setup_exe" in sys.argv:
        sys.argv.remove("setup_exe")
        if hostOS == OS_WIN:
            oneFile = False
            makeSetupExe = True
            makeSetupPyz = False
        else:
            print("Error: Argument 'setup' for Inno Setup is Windows only.")
            sys.exit(1)

    if "setup_pyz" in sys.argv:
        sys.argv.remove("setup_pyz")
        if hostOS == OS_WIN:
            makeSetupExe = False
            makeSetupPyz = True
        else:
            print("Error: Argument 'setup' for Inno Setup is Windows only.")
            sys.exit(1)

    if winPack:
        makeWindowsPackage()

    if doFreeze:
        freezePackage(buildWindowed, oneFile, makeSetupExe, hostOS)

    if makeSetupExe:
        innoSetup("exe")

    if makeSetupPyz:
        innoSetup("pyz")

# END Main
