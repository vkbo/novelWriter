#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import subprocess

# Defaults
buildWindowed = True

# Parse Options
shortOpt = "hd"
longOpt  = [
    "help",
    "debug",
]
helpMsg = (
    "\n"
    "novelWriter Install Script\n"
    "\n"
    "Usage:\n"
    " -h, --help   Print this message.\n"
    " -d, --debug  Build novelWriter for debugging. To debug novelwriter after build,\n"
    "              run it from command line with the debug options. Please check the\n"
    "              novelWriter --help output for details.\n"
)

try:
    inOpts, inArgs = getopt.getopt(sys.argv[1:],shortOpt,longOpt)
except getopt.GetoptError:
    print(helpMsg)
    sys.exit(2)

for inOpt, inArg in inOpts:
    if inOpt in ("-h","--help"):
        print(helpMsg)
        sys.exit()
    elif inOpt in ("-d", "--debug"):
        buildWindowed = False

# Run pip
packList = ["pyinstaller"]
with open("requirements.txt",mode="r") as reqFile:
    for reqPack in reqFile:
        if len(reqPack.strip()) > 0:
            packList.append(reqPack)

for packName in packList:
    print("Installing package dependency: %s" % packName)
    try:
        subprocess.call([sys.executable, "-m", "pip", "install", packName])
    except Exception as e:
        print("Failed with error:")
        print(str(e))

# Run pyinstaller
if sys.platform.startswith("win32"):
    dotDot = ";"
else:
    dotDot = ":"

instOpt = [
    "--name=novelWriter",
    "--onefile",
    "--add-data=%s%s%s" % (os.path.join("nw", "assets", "themes"),   dotDot,"themes"),
    "--add-data=%s%s%s" % (os.path.join("nw", "assets", "graphics"), dotDot,"graphics"),
    "--icon=%s" % os.path.join("nw", "assets", "icons", "novelWriter.ico"),
]
if buildWindowed:
    instOpt.append("--windowed")

instOpt.append("novelWriter.py")

import PyInstaller.__main__
PyInstaller.__main__.run(instOpt)

print("")
print("##################")
print("  Build Finished")
print("##################")
print("")
print("If everything went well, the novelWriter executable should be in the folder named 'dist'")
print("")

