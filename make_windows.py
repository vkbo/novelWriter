#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will either build:
 * A single file executable named dist/novelWriter.exe. This is a quite
   slow option, and the file is fairly big. Option --onefile
 * A single directory named dist/novelWriter with a novelWriter.exe, and
   all dependecies included. This is the default.
 * The latter can be combined with a build stage of a setup.exe file
   named setup-novelwriter-<version>.exe. Option --setup.

In addition, providing the --pip flag will cause the script to try to
install all dependencies needed for runing the build, and for running
novelWriter itself.
"""

import os
import sys
import getopt
import subprocess

# Defaults
buildWindowed = True
runPip = False
oneFile = False
makeSetup = False
innoSetup = None

# Parse Options
shortOpt = "hd"
longOpt  = [
    "help",
    "debug",
    "pip",
    "onefile",
    "setup",
    "inno=",
]
helpMsg = (
    "\n"
    "novelWriter Install Script for Windows\n"
    "\n"
    "Usage:\n"
    " -h, --help     Print this message.\n"
    "     --pip      Install dependecies first.\n"
    "     --onefile  Create a single executable file.\n"
    "     --setup    Make Inno Setup file.\n"
    "     --inno=    Path to the Inno Setup exec.\n"
    " -d, --debug    Build novelWriter for debugging. To debug novelwriter after build,\n"
    "                run it from command line with the debug options. Please check the\n"
    "                novelWriter --help output for details.\n"
)

try:
    inOpts, inArgs = getopt.getopt(sys.argv[1:], shortOpt, longOpt)
except getopt.GetoptError:
    print(helpMsg)
    sys.exit(1)

for inOpt, inArg in inOpts:
    if inOpt in ("-h", "--help"):
        print(helpMsg)
        sys.exit(0)
    elif inOpt in ("-d", "--debug"):
        buildWindowed = False
    elif inOpt == "--pip":
        runPip = True
    elif inOpt == "--onefile":
        oneFile = True
    elif inOpt == "--setup":
        makeSetup = True
    elif inOpt == "--inno":
        innoSetup = inArg

# Run pip
if runPip:
    print("")
    print("###########################")
    print("  Installing Dependencies")
    print("###########################")
    print("")
    try:
        subprocess.call([
            sys.executable, "-m",
            "pip", "install", "--user", "--upgrade", "pip"
        ])
        subprocess.call([
            sys.executable, "-m",
            "pip", "install", "--user", "--upgrade", "pyinstaller"
        ])
        subprocess.call([
            sys.executable, "-m",
            "pip", "install", "--user", "--upgrade", "-r", "requirements.txt"
        ])
    except Exception as e:
        print("Failed with error:")
        print(str(e))
        sys.exit(1)

# Run pyinstaller
print("")
print("#######################")
print("  Running PyInstaller")
print("#######################")
print("")
instOpt = [
    "--name=novelWriter",
    "--clean",
    "--add-data=%s;%s" % (os.path.join("nw", "assets"), "assets"),
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
]

if buildWindowed:
    instOpt.append("--windowed")

if oneFile and not makeSetup:
    instOpt.append("--onefile")
else:
    instOpt.append("--onedir")

instOpt.append("novelWriter.py")

import PyInstaller.__main__ # noqa: E402
PyInstaller.__main__.run(instOpt)

if not oneFile:
    # These dll files are not nee3ded, and take up a fair bit of space.
    delIfExists = [
        "Qt5DBus.dll", "Qt5Network.dll", "Qt5Qml.dll", "Qt5QmlModels.dll", "Qt5Quick.dll",
        "Qt5Quick3D.dll", "Qt5Quick3DAssetImport.dll", "Qt5Quick3DRender.dll",
        "Qt5Quick3DRuntimeRender.dll", "Qt5Quick3DUtils.dll", "Qt5Sql.dll"
    ]
    distDir = os.path.join(os.getcwd(), "dist", "novelWriter")
    for delFile in delIfExists:
        delPath = os.path.join(distDir, delFile)
        if os.path.isfile(delPath):
            print("Deleting file: %s" % delPath)
            os.unlink(delPath)

print("")
print("Build Finished")
print("")
print("If everything went well, the novelWriter executable should be in the folder named 'dist'")
print("")

if makeSetup:
    print("")
    print("######################")
    print("  Running Inno Setup")
    print("######################")
    print("")
    if innoSetup is None:
        innoSetup = "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"
    if not os.path.isfile(innoSetup):
        print("ERROR: Cannot fine Inno Setup's ISCC.exe file.")
        print("       Looked in: %s" % innoSetup)
        print("       Please provide a path with the --inno= option.")
        sys.exit(1)

    # Read the iss template
    issData = ""
    with open(os.path.join("setup", "win_setup.iss"), mode="r") as inFile:
        issData = inFile.read()

    import nw # noqa: E402
    issData = issData.replace(r"%%version%%", nw.__version__)
    issData = issData.replace(r"%%dir%%", os.getcwd())

    with open("setup.iss", mode="w+") as outFile:
        outFile.write(issData)

    try:
        subprocess.call([innoSetup, "setup.iss"])
    except Exception as e:
        print("Failed with error:")
        print(str(e))
        sys.exit(1)
