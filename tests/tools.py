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
import time
import shutil

from PyQt5.QtWidgets import qApp

XML_IGNORE = ("<novelWriterXML", "<saveCount", "<autoCount", "<editTime")


class C:

    # Import and status items from test project when random generator is mocked
    sNew      = "s000000"
    sNote     = "s000001"
    sDraft    = "s000002"
    sFinished = "s000003"

    iNew   = "i000004"
    iMinor = "i000005"
    iMajor = "i000006"
    iMain  = "i000007"

    # Handles from test project when random generator is mocked
    hInvalid    = "0000000000000"
    hNovelRoot  = "0000000000008"
    hPlotRoot   = "0000000000009"
    hCharRoot   = "000000000000a"
    hWorldRoot  = "000000000000b"
    hTitlePage  = "000000000000c"
    hChapterDir = "000000000000d"
    hChapterDoc = "000000000000e"
    hSceneDoc   = "000000000000f"

# END Class C


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


def buildTestProject(theObject, projPath):
    """Build a standard test project in projPath using theProject
    object as the parent.
    """
    from novelwriter.enum import nwItemClass
    from novelwriter.core import NWProject, NWDoc

    if isinstance(theObject, NWProject):
        theGUI = None
        theProject = theObject
    else:
        theGUI = theObject
        theProject = theObject.theProject

    theProject.clearProject()
    theProject.setProjectPath(projPath, newProject=True)
    theProject.data.setName("New Project")
    theProject.setBookTitle("New Novel")
    theProject.setBookAuthors("Jane Doe")

    # Creating a minimal project with a few root folders and a
    # single chapter folder with a single file.
    xHandle = {}
    xHandle[1] = theProject.newRoot(nwItemClass.NOVEL, "Novel")
    xHandle[2] = theProject.newRoot(nwItemClass.PLOT, "Plot")
    xHandle[3] = theProject.newRoot(nwItemClass.CHARACTER, "Characters")
    xHandle[4] = theProject.newRoot(nwItemClass.WORLD, "World")
    xHandle[5] = theProject.newFile("Title Page", xHandle[1])
    xHandle[6] = theProject.newFolder("New Chapter", xHandle[1])
    xHandle[7] = theProject.newFile("New Chapter", xHandle[6])
    xHandle[8] = theProject.newFile("New Scene", xHandle[6])

    aDoc = NWDoc(theProject, xHandle[5])
    aDoc.writeDocument("#! New Novel\n\n>> By Jane Doe <<\n")
    theProject.index.reIndexHandle(xHandle[5])

    aDoc = NWDoc(theProject, xHandle[7])
    aDoc.writeDocument("## %s\n\n" % theProject.tr("New Chapter"))
    theProject.index.reIndexHandle(xHandle[7])

    aDoc = NWDoc(theProject, xHandle[8])
    aDoc.writeDocument("### %s\n\n" % theProject.tr("New Scene"))
    theProject.index.reIndexHandle(xHandle[8])

    theProject.projOpened = time.time()
    theProject.setProjectChanged(True)
    theProject.saveProject(autoSave=True)

    if theGUI is not None:
        theGUI.hasProject = True
        theGUI.rebuildTrees()

    return
