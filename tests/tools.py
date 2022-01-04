"""
novelWriter – Test Suite Tools
==============================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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
import shutil

from PyQt5.QtWidgets import qApp


def cmpFiles(fileOne, fileTwo, ignoreLines=None, ignoreStart=None):
    """Compare two files, but optionally ignore lines given by a list.
    """
    if ignoreLines is None:
        ignoreLines = []

    try:
        foOne = open(fileOne, mode="r", encoding="utf-8")
    except Exception as exc:
        print(str(exc))
        return False

    try:
        foTwo = open(fileTwo, mode="r", encoding="utf-8")
    except Exception as exc:
        print(str(exc))
        return False

    txtOne = foOne.readlines()
    txtTwo = foTwo.readlines()

    if len(txtOne) != len(txtTwo):
        print("Files are not the same length")
        return False

    diffFound = False
    for n in range(len(txtOne)):
        lnOne = txtOne[n].strip()
        lnTwo = txtTwo[n].strip()

        if n+1 in ignoreLines:
            print("Ignoring line %d" % (n+1))
            continue

        if ignoreStart is not None:
            if lnOne.startswith(ignoreStart):
                print("Ignoring line %d" % (n+1))
                continue

        if lnOne != lnTwo:
            print("Diff on line %d:" % (n+1))
            print(" << '%s'" % lnOne)
            print(" >> '%s'" % lnTwo)
            diffFound = True

    foOne.close()
    foTwo.close()

    return not diffFound


def getGuiItem(theName):
    """Returns a QtWidget based on its objectName.
    """
    for qWidget in qApp.topLevelWidgets():
        if qWidget.objectName() == theName:
            return qWidget
    return None


def readFile(fileName):
    """Returns the content of a file as a string.
    """
    with open(fileName, mode="r", encoding="utf-8") as inFile:
        return inFile.read()


def writeFile(fileName, fileData):
    """Write the contents of a string to a file.
    """
    with open(fileName, mode="w", encoding="utf-8") as outFile:
        outFile.write(fileData)


def cleanProject(projPath):
    """Delete all generated files in a project.
    """
    cacheDir = os.path.join(projPath, "cache")
    if os.path.isdir(cacheDir):
        shutil.rmtree(cacheDir)

    metaDir = os.path.join(projPath, "meta")
    if os.path.isdir(metaDir):
        shutil.rmtree(metaDir)

    bakFile = os.path.join(projPath, "nwProject.bak")
    if os.path.isfile(bakFile):
        os.unlink(bakFile)

    tocFile = os.path.join(projPath, "ToC.txt")
    if os.path.isfile(tocFile):
        os.unlink(tocFile)

    return
