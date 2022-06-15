"""
novelWriter – NWProject Class Tester
====================================

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
import pytest

from shutil import copyfile
from zipfile import ZipFile
from lxml import etree

from tools import cmpFiles, writeFile, readFile, buildTestProject, XML_IGNORE
from mock import causeOSError

from novelwriter.enum import nwItemClass, nwItemType, nwItemLayout
from novelwriter.common import formatTimeStamp
from novelwriter.constants import nwFiles
from novelwriter.core.tree import NWTree
from novelwriter.core.index import NWIndex
from novelwriter.core.project import NWProject
from novelwriter.core.options import OptionState
from novelwriter.core.document import NWDoc


@pytest.mark.core
def testCoreProject_NewMinimal(fncDir, outDir, refDir, mockGUI, mockRnd):
    """Create a new project from a project wizard dictionary. With
    default setting, creating a Minimal project.
    """
    projFile = os.path.join(fncDir, "nwProject.nwx")
    testFile = os.path.join(outDir, "coreProject_NewMinimal_nwProject.nwx")
    compFile = os.path.join(refDir, "coreProject_NewMinimal_nwProject.nwx")

    theProject = NWProject(mockGUI)

    # Setting no data should fail
    assert theProject.newProject({}) is False

    # Wrong type should also fail
    assert theProject.newProject("stuff") is False

    # Try again with a proper path
    assert theProject.newProject({"projPath": fncDir}) is True
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True

    # Creating the project once more should fail
    assert theProject.newProject({"projPath": fncDir}) is False

    # Open again
    assert theProject.openProject(projFile) is True

    # Save and close
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)
    assert theProject.projChanged is False

    # Open a second time
    assert theProject.openProject(projFile) is True
    assert theProject.openProject(projFile) is False
    assert theProject.openProject(projFile, overrideLock=True) is True
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

# END Test testCoreProject_NewMinimal


@pytest.mark.core
def testCoreProject_NewCustomA(fncDir, outDir, refDir, mockGUI, mockRnd):
    """Create a new project from a project wizard dictionary.
    Custom type with chapters and scenes.
    """
    projFile = os.path.join(fncDir, "nwProject.nwx")
    testFile = os.path.join(outDir, "coreProject_NewCustomA_nwProject.nwx")
    compFile = os.path.join(refDir, "coreProject_NewCustomA_nwProject.nwx")

    projData = {
        "projName": "Test Custom",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": fncDir,
        "popSample": False,
        "popMinimal": False,
        "popCustom": True,
        "addRoots": [
            nwItemClass.PLOT,
            nwItemClass.CHARACTER,
            nwItemClass.WORLD,
        ],
        "addNotes": True,
        "numChapters": 3,
        "numScenes": 3,
    }
    theProject = NWProject(mockGUI)

    assert theProject.newProject(projData) is True
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

# END Test testCoreProject_NewCustomA


@pytest.mark.core
def testCoreProject_NewCustomB(fncDir, outDir, refDir, mockGUI, mockRnd):
    """Create a new project from a project wizard dictionary.
    Custom type without chapters, but with scenes.
    """
    projFile = os.path.join(fncDir, "nwProject.nwx")
    testFile = os.path.join(outDir, "coreProject_NewCustomB_nwProject.nwx")
    compFile = os.path.join(refDir, "coreProject_NewCustomB_nwProject.nwx")

    projData = {
        "projName": "Test Custom",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": fncDir,
        "popSample": False,
        "popMinimal": False,
        "popCustom": True,
        "addRoots": [
            nwItemClass.PLOT,
            nwItemClass.CHARACTER,
            nwItemClass.WORLD,
        ],
        "addNotes": True,
        "numChapters": 0,
        "numScenes": 6,
    }
    theProject = NWProject(mockGUI)

    assert theProject.newProject(projData) is True
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

# END Test testCoreProject_NewCustomB


@pytest.mark.core
def testCoreProject_NewSampleA(fncDir, tmpConf, mockGUI, tmpDir):
    """Check that we can create a new project can be created from the
    provided sample project via a zip file.
    """
    projData = {
        "projName": "Test Sample",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": fncDir,
        "popSample": True,
        "popMinimal": False,
        "popCustom": False,
    }
    theProject = NWProject(mockGUI)

    # Sample set, but no path
    assert not theProject.newProject({"popSample": True})

    # Force the lookup path for assets to our temp folder
    srcSample = os.path.abspath(os.path.join(tmpConf.appRoot, "sample"))
    dstSample = os.path.join(tmpDir, "sample.zip")
    tmpConf.assetPath = tmpDir

    # Create and open a defective zip file
    with open(dstSample, mode="w+") as outFile:
        outFile.write("foo")

    assert not theProject.newProject(projData)
    os.unlink(dstSample)

    # Create a real zip file, and unpack it
    with ZipFile(dstSample, "w") as zipObj:
        zipObj.write(os.path.join(srcSample, "nwProject.nwx"), "nwProject.nwx")
        for docFile in os.listdir(os.path.join(srcSample, "content")):
            srcDoc = os.path.join(srcSample, "content", docFile)
            zipObj.write(srcDoc, "content/"+docFile)

    assert theProject.newProject(projData) is True
    assert theProject.openProject(fncDir) is True
    assert theProject.projName == "Sample Project"
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True
    os.unlink(dstSample)

# END Test testCoreProject_NewSampleA


@pytest.mark.core
def testCoreProject_NewSampleB(monkeypatch, fncDir, tmpConf, mockGUI, tmpDir):
    """Check that we can create a new project can be created from the
    provided sample project folder.
    """
    projData = {
        "projName": "Test Sample",
        "projTitle": "Test Novel",
        "projAuthors": "Jane Doe\nJohn Doh\n",
        "projPath": fncDir,
        "popSample": True,
        "popMinimal": False,
        "popCustom": False,
    }
    theProject = NWProject(mockGUI)

    # Make sure we do not pick up the novelwriter/assets/sample.zip file
    tmpConf.assetPath = tmpDir

    # Set a fake project file name
    monkeypatch.setattr(nwFiles, "PROJ_FILE", "nothing.nwx")
    assert not theProject.newProject(projData)

    monkeypatch.setattr(nwFiles, "PROJ_FILE", "nwProject.nwx")
    assert theProject.newProject(projData) is True
    assert theProject.openProject(fncDir) is True
    assert theProject.projName == "Sample Project"
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True

    # Misdirect the appRoot path so neither is possible
    tmpConf.appRoot = tmpDir
    assert not theProject.newProject(projData)

# END Test testCoreProject_NewSampleB


@pytest.mark.core
def testCoreProject_NewRoot(fncDir, outDir, refDir, mockGUI, mockRnd):
    """Check that new root folders can be added to the project.
    """
    projFile = os.path.join(fncDir, "nwProject.nwx")
    testFile = os.path.join(outDir, "coreProject_NewRoot_nwProject.nwx")
    compFile = os.path.join(refDir, "coreProject_NewRoot_nwProject.nwx")

    theProject = NWProject(mockGUI)
    buildTestProject(theProject, fncDir)

    assert theProject.setProjectPath(fncDir) is True
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True
    assert theProject.openProject(projFile) is True

    assert isinstance(theProject.newRoot(nwItemClass.NOVEL),     str)
    assert isinstance(theProject.newRoot(nwItemClass.PLOT),      str)
    assert isinstance(theProject.newRoot(nwItemClass.CHARACTER), str)
    assert isinstance(theProject.newRoot(nwItemClass.WORLD),     str)
    assert isinstance(theProject.newRoot(nwItemClass.TIMELINE),  str)
    assert isinstance(theProject.newRoot(nwItemClass.OBJECT),    str)
    assert isinstance(theProject.newRoot(nwItemClass.CUSTOM),    str)
    assert isinstance(theProject.newRoot(nwItemClass.CUSTOM),    str)

    assert theProject.projChanged is True
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)
    assert theProject.projChanged is False

# END Test testCoreProject_NewRoot


@pytest.mark.core
def testCoreProject_NewFileFolder(fncDir, outDir, refDir, mockGUI, mockRnd):
    """Check that new files can be added to the project.
    """
    projFile = os.path.join(fncDir, "nwProject.nwx")
    testFile = os.path.join(outDir, "coreProject_NewFileFolder_nwProject.nwx")
    compFile = os.path.join(refDir, "coreProject_NewFileFolder_nwProject.nwx")

    theProject = NWProject(mockGUI)
    buildTestProject(theProject, fncDir)

    assert theProject.setProjectPath(fncDir) is True
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True
    assert theProject.openProject(projFile) is True

    # Invalid call
    assert theProject.newFolder("New Folder", "1234567890abc") is None
    assert theProject.newFile("New File", "1234567890abc") is None

    # Add files properly
    assert theProject.newFolder("Stuff", "0000000000015") == "0000000000028"
    assert theProject.newFile("Hello", "0000000000015") == "0000000000029"
    assert theProject.newFile("Jane", "0000000000012") == "000000000002a"

    assert "0000000000028" in theProject.tree
    assert "0000000000029" in theProject.tree
    assert "000000000002a" in theProject.tree

    # Write to file, failed
    assert theProject.writeNewFile("blabla", 1, True) is False         # Not a handle
    assert theProject.writeNewFile("0000000000028", 1, True) is False  # Not a file
    assert theProject.writeNewFile("0000000000014", 1, True) is False  # Already has content

    # Write to file, success
    assert theProject.writeNewFile("0000000000029", 2, True) is True
    assert NWDoc(theProject, "0000000000029").readDocument() == "## Hello\n\n"

    assert theProject.writeNewFile("000000000002a", 1, False) is True
    assert NWDoc(theProject, "000000000002a").readDocument() == "# Jane\n\n"

    # Save, close and check
    assert theProject.projChanged is True
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)
    assert theProject.projChanged is False

# END Test testCoreProject_NewFileFolder


@pytest.mark.core
def testCoreProject_Open(monkeypatch, nwMinimal, mockGUI):
    """Test opening a project.
    """
    theProject = NWProject(mockGUI)

    # Rename the project file to check handling
    rName = os.path.join(nwMinimal, nwFiles.PROJ_FILE)
    wName = os.path.join(nwMinimal, nwFiles.PROJ_FILE+"_sdfghj")
    os.rename(rName, wName)
    assert theProject.openProject(nwMinimal) is False
    os.rename(wName, rName)

    # Fail on folder structure check
    with monkeypatch.context() as mp:
        mp.setattr("os.mkdir", causeOSError)
        assert theProject.openProject(nwMinimal) is False

    # Fail on lock file
    theProject.setProjectPath(nwMinimal)
    assert theProject._writeLockFile()
    assert theProject.openProject(nwMinimal) is False

    # Fail to read lockfile (which still opens the project)
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert theProject.openProject(nwMinimal) is True
    assert theProject.closeProject()

    # Force open with lockfile
    theProject.setProjectPath(nwMinimal)
    assert theProject._writeLockFile()
    assert theProject.openProject(nwMinimal, overrideLock=True) is True
    assert theProject.closeProject()

    # Make a junk XML file
    oName = os.path.join(nwMinimal, nwFiles.PROJ_FILE[:-3]+"orig")
    bName = os.path.join(nwMinimal, nwFiles.PROJ_FILE[:-3]+"bak")
    os.rename(rName, oName)
    writeFile(rName, "stuff")
    assert theProject.openProject(nwMinimal) is False

    # Also write a jun XML backup file
    writeFile(bName, "stuff")
    assert theProject.openProject(nwMinimal) is False

    # Wrong root item
    writeFile(rName, "<not_novelWriterXML></not_novelWriterXML>\n")
    assert theProject.openProject(nwMinimal) is False

    # Wrong file version
    writeFile(rName, (
        "<?xml version='0.0' encoding='utf-8'?>\n"
        "<novelWriterXML "
        "appVersion=\"1.0\" "
        "hexVersion=\"0x01000000\" "
        "fileVersion=\"1.0\" "
        "timeStamp=\"2020-01-01 00:00:00\">\n"
        "</novelWriterXML>\n"
    ))
    mockGUI.askResponse = False
    assert theProject.openProject(nwMinimal) is False
    mockGUI.undo()

    # Future file version
    writeFile(rName, (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        "<novelWriterXML "
        "appVersion=\"1.0\" "
        "hexVersion=\"0x01000000\" "
        "fileVersion=\"99.99\" "
        "timeStamp=\"2020-01-01 00:00:00\">\n"
        "</novelWriterXML>\n"
    ))
    assert theProject.openProject(nwMinimal) is False

    # Update file version
    writeFile(rName, (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        "<novelWriterXML "
        "appVersion=\"1.0\" "
        "hexVersion=\"0xffffffff\" "
        "fileVersion=\"1.2\" "
        "timeStamp=\"2020-01-01 00:00:00\">\n"
        "</novelWriterXML>\n"
    ))
    mockGUI.askResponse = False
    assert theProject.openProject(nwMinimal) is False
    assert mockGUI.lastQuestion[0] == "File Version"
    mockGUI.undo()

    # Larger hex version
    writeFile(rName, (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        "<novelWriterXML "
        "appVersion=\"1.0\" "
        "hexVersion=\"0xffffffff\" "
        "fileVersion=\"%s\" "
        "timeStamp=\"2020-01-01 00:00:00\">\n"
        "</novelWriterXML>\n"
    ) % theProject.FILE_VERSION)
    mockGUI.askResponse = False
    assert theProject.openProject(nwMinimal) is False
    assert mockGUI.lastQuestion[0] == "Version Conflict"
    mockGUI.undo()

    # Test skipping XML entries
    writeFile(rName, (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        "<novelWriterXML "
        "appVersion=\"1.0\" "
        "hexVersion=\"0x01000000\" "
        "fileVersion=\"1.2\" "
        "timeStamp=\"2020-01-01 00:00:00\">\n"
        "<project><stuff/></project>\n"
        "<settings><stuff/></settings>\n"
        "</novelWriterXML>\n"
    ))
    assert theProject.openProject(nwMinimal) is True
    assert theProject.closeProject()

    # Clean up XML files
    os.unlink(rName)
    os.unlink(bName)
    os.rename(oName, rName)

    # Add some legacy stuff that cannot be removed
    with monkeypatch.context() as mp:
        mp.setattr(theProject, "_legacyDataFolder", causeOSError)
        os.mkdir(os.path.join(nwMinimal, "data_0"))
        writeFile(os.path.join(nwMinimal, "data_0", "123456789abc_main.nwd"), "stuff")
        writeFile(os.path.join(nwMinimal, "data_0", "123456789abc_main.bak"), "stuff")
        mockGUI.clear()
        assert theProject.openProject(nwMinimal) is True
        assert "There was an error updating the project." in mockGUI.lastAlert

    assert theProject.closeProject()

# END Test testCoreProject_Open


@pytest.mark.core
def testCoreProject_Save(monkeypatch, nwMinimal, mockGUI, refDir):
    """Test saving a project.
    """
    theProject = NWProject(mockGUI)
    testFile = os.path.join(nwMinimal, "nwProject.nwx")
    backFile = os.path.join(nwMinimal, "nwProject.bak")
    compFile = os.path.join(refDir, os.path.pardir, "minimal", "nwProject.nwx")

    # Nothing to save
    assert theProject.saveProject() is False

    # Open test project
    assert theProject.openProject(nwMinimal)

    # Fail on folder structure check
    with monkeypatch.context() as mp:
        mp.setattr("os.path.isdir", lambda *a: False)
        assert theProject.saveProject() is False

    # Fail on open file
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert theProject.saveProject() is False

    # Fail on creating .bak file
    with monkeypatch.context() as mp:
        mp.setattr("os.replace", causeOSError)
        assert theProject.saveProject() is False
        assert os.path.isfile(backFile) is False

    # Successful save
    saveCount = theProject.saveCount
    autoCount = theProject.autoCount
    assert theProject.saveProject() is True
    assert theProject.saveCount == saveCount + 1
    assert theProject.autoCount == autoCount
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

    # Check that a second save creates a .bak file
    assert os.path.isfile(backFile) is True

    # Successful autosave
    saveCount = theProject.saveCount
    autoCount = theProject.autoCount
    assert theProject.saveProject(autoSave=True) is True
    assert theProject.saveCount == saveCount
    assert theProject.autoCount == autoCount + 1
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

    # Close test project
    assert theProject.closeProject()

# END Test testCoreProject_Save


@pytest.mark.core
def testCoreProject_LockFile(monkeypatch, fncDir, mockGUI):
    """Test lock file functions for the project folder.
    """
    theProject = NWProject(mockGUI)

    lockFile = os.path.join(fncDir, nwFiles.PROJ_LOCK)

    # No project
    assert theProject._writeLockFile() is False
    assert theProject._readLockFile() == ["ERROR"]
    assert theProject._clearLockFile() is False

    theProject.projPath = fncDir
    theProject.mainConf.hostName = "TestHost"
    theProject.mainConf.osType = "TestOS"
    theProject.mainConf.kernelVer = "1.0"

    # Block open
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert theProject._writeLockFile() is False

    # Write lock file
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.project.time", lambda: 123.4)
        assert theProject._writeLockFile() is True
    assert readFile(lockFile) == "TestHost\nTestOS\n1.0\n123\n"

    # Block open
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert theProject._readLockFile() == ["ERROR"]

    # Read lock file
    assert theProject._readLockFile() == ["TestHost", "TestOS", "1.0", "123"]

    # Block unlink
    with monkeypatch.context() as mp:
        mp.setattr("os.unlink", causeOSError)
        assert os.path.isfile(lockFile)
        assert theProject._clearLockFile() is False
        assert os.path.isfile(lockFile)

    # Clear file
    assert os.path.isfile(lockFile)
    assert theProject._clearLockFile() is True
    assert not os.path.isfile(lockFile)

    # Read again, no file
    assert theProject._readLockFile() == []

    # Read an invalid lock file
    writeFile(lockFile, "A\nB")
    assert theProject._readLockFile() == ["ERROR"]
    assert theProject._clearLockFile() is True

# END Test testCoreProject_LockFile


@pytest.mark.core
def testCoreProject_Helpers(monkeypatch, fncDir, mockGUI):
    """Test helper functions for the project folder.
    """
    theProject = NWProject(mockGUI)

    # No path
    assert theProject.ensureFolderStructure() is False

    # Set the correct dir
    theProject.projPath = fncDir

    # Block user's home folder
    with monkeypatch.context() as mp:
        mp.setattr("os.path.expanduser", lambda *a, **k: fncDir)
        assert theProject.ensureFolderStructure() is False

    # Create a file to block meta folder
    metaDir = os.path.join(fncDir, "meta")
    writeFile(metaDir, "stuff")
    assert theProject.ensureFolderStructure() is False
    os.unlink(metaDir)

    # Create a file to block cache folder
    cacheDir = os.path.join(fncDir, "cache")
    writeFile(cacheDir, "stuff")
    assert theProject.ensureFolderStructure() is False
    os.unlink(cacheDir)

    # Create a file to block content folder
    contentDir = os.path.join(fncDir, "content")
    writeFile(contentDir, "stuff")
    assert theProject.ensureFolderStructure() is False
    os.unlink(contentDir)

    # Now, do it right
    assert theProject.ensureFolderStructure() is True
    assert os.path.isdir(metaDir)
    assert os.path.isdir(cacheDir)
    assert os.path.isdir(contentDir)

# END Test testCoreProject_Helpers


@pytest.mark.core
def testCoreProject_AccessItems(nwMinimal, mockGUI):
    """Test helper functions for the project folder.
    """
    theProject = NWProject(mockGUI)
    theProject.openProject(nwMinimal)

    # Storage Objects
    assert isinstance(theProject.index, NWIndex)
    assert isinstance(theProject.tree, NWTree)
    assert isinstance(theProject.options, OptionState)

    # Move Novel ROOT to after its files
    oldOrder = [
        "a508bb932959c",  # ROOT: Novel
        "a35baf2e93843",  # FILE: Title Page
        "a6d311a93600a",  # FOLDER: New Chapter
        "f5ab3e30151e1",  # FILE: New Chapter
        "8c659a11cd429",  # FILE: New Scene
        "7695ce551d265",  # ROOT: Plot
        "afb3043c7b2b3",  # ROOT: Characters
        "9d5247ab588e0",  # ROOT: World
    ]
    newOrder = [
        "a35baf2e93843",  # FILE: Title Page
        "f5ab3e30151e1",  # FILE: New Chapter
        "8c659a11cd429",  # FILE: New Scene
        "a6d311a93600a",  # FOLDER: New Chapter
        "a508bb932959c",  # ROOT: Novel
        "7695ce551d265",  # ROOT: Plot
        "afb3043c7b2b3",  # ROOT: Characters
        "9d5247ab588e0",  # ROOT: World
    ]
    assert theProject.tree.handles() == oldOrder
    assert theProject.setTreeOrder(newOrder)
    assert theProject.tree.handles() == newOrder

    # Add a non-existing item
    theProject.tree._treeOrder.append("01234567789abc")

    # Add an item with a non-existent parent
    nHandle = theProject.newFile("Test File", "a6d311a93600a")
    theProject.tree[nHandle].setParent("cba9876543210")
    assert theProject.tree[nHandle].itemParent == "cba9876543210"

    retOrder = []
    for tItem in theProject.getProjectItems():
        retOrder.append(tItem.itemHandle)

    assert retOrder == [
        "a508bb932959c",  # ROOT: Novel
        "7695ce551d265",  # ROOT: Plot
        "afb3043c7b2b3",  # ROOT: Characters
        "9d5247ab588e0",  # ROOT: World
        nHandle,          # FILE: Test File
        "a35baf2e93843",  # FILE: Title Page
        "a6d311a93600a",  # FOLDER: New Chapter
        "f5ab3e30151e1",  # FILE: New Chapter
        "8c659a11cd429",  # FILE: New Scene
    ]
    assert theProject.tree[nHandle].itemParent is None

# END Test testCoreProject_AccessItems


@pytest.mark.core
def testCoreProject_StatusImport(mockGUI, fncDir, mockRnd):
    """Test the status and importance flag handling.
    """
    theProject = NWProject(mockGUI)
    buildTestProject(theProject, fncDir)

    statusKeys = ["s000008", "s000009", "s00000a", "s00000b"]
    importKeys = ["i00000c", "i00000d", "i00000e", "i00000f"]

    # Change Status
    # =============

    theProject.tree["0000000000014"].setStatus("Finished")
    theProject.tree["0000000000015"].setStatus("Draft")
    theProject.tree["0000000000016"].setStatus("Note")
    theProject.tree["0000000000017"].setStatus("Finished")

    assert theProject.tree["0000000000014"].itemStatus == statusKeys[3]
    assert theProject.tree["0000000000015"].itemStatus == statusKeys[2]
    assert theProject.tree["0000000000016"].itemStatus == statusKeys[1]
    assert theProject.tree["0000000000017"].itemStatus == statusKeys[3]

    newList = [
        {"key": statusKeys[0], "name": "New", "cols": (1, 1, 1)},
        {"key": statusKeys[1], "name": "Draft", "cols": (2, 2, 2)},   # These are swapped
        {"key": statusKeys[2], "name": "Note", "cols": (3, 3, 3)},    # These are swapped
        {"key": statusKeys[3], "name": "Edited", "cols": (4, 4, 4)},  # Renamed
        {"key": None, "name": "Finished", "cols": (5, 5, 5)},         # New, reused name
    ]
    assert theProject.setStatusColours(None, None) is False
    assert theProject.setStatusColours([], []) is False
    assert theProject.setStatusColours(newList, []) is True

    assert theProject.statusItems.name(statusKeys[0]) == "New"
    assert theProject.statusItems.name(statusKeys[1]) == "Draft"
    assert theProject.statusItems.name(statusKeys[2]) == "Note"
    assert theProject.statusItems.name(statusKeys[3]) == "Edited"
    assert theProject.statusItems.cols(statusKeys[0]) == (1, 1, 1)
    assert theProject.statusItems.cols(statusKeys[1]) == (2, 2, 2)
    assert theProject.statusItems.cols(statusKeys[2]) == (3, 3, 3)
    assert theProject.statusItems.cols(statusKeys[3]) == (4, 4, 4)

    # Check the new entry
    lastKey = theProject.statusItems.check("Finished")
    assert lastKey == "s000018"
    assert theProject.statusItems.name(lastKey) == "Finished"
    assert theProject.statusItems.cols(lastKey) == (5, 5, 5)

    # Delete last entry
    assert theProject.setStatusColours([], [lastKey]) is True
    assert theProject.statusItems.name(lastKey) == "New"

    # Change Importance
    # =================

    fHandle = theProject.newFile("Jane Doe", "0000000000012")
    theProject.tree[fHandle].setImport("Main")

    assert theProject.tree[fHandle].itemImport == importKeys[3]
    newList = [
        {"key": importKeys[0], "name": "New", "cols": (1, 1, 1)},
        {"key": importKeys[1], "name": "Minor", "cols": (2, 2, 2)},
        {"key": importKeys[2], "name": "Major", "cols": (3, 3, 3)},
        {"key": importKeys[3], "name": "Min", "cols": (4, 4, 4)},
        {"key": None, "name": "Max", "cols": (5, 5, 5)},
    ]
    assert theProject.setImportColours(None, None) is False
    assert theProject.setImportColours([], []) is False
    assert theProject.setImportColours(newList, []) is True

    assert theProject.importItems.name(importKeys[0]) == "New"
    assert theProject.importItems.name(importKeys[1]) == "Minor"
    assert theProject.importItems.name(importKeys[2]) == "Major"
    assert theProject.importItems.name(importKeys[3]) == "Min"
    assert theProject.importItems.cols(importKeys[0]) == (1, 1, 1)
    assert theProject.importItems.cols(importKeys[1]) == (2, 2, 2)
    assert theProject.importItems.cols(importKeys[2]) == (3, 3, 3)
    assert theProject.importItems.cols(importKeys[3]) == (4, 4, 4)

    # Check the new entry
    lastKey = theProject.importItems.check("Max")
    assert lastKey == "i00001a"
    assert theProject.importItems.name(lastKey) == "Max"
    assert theProject.importItems.cols(lastKey) == (5, 5, 5)

    # Delete last entry
    assert theProject.setImportColours([], [lastKey]) is True
    assert theProject.importItems.name(lastKey) == "New"

    # Delete Status/Import
    # ====================

    theProject.statusItems.resetCounts()
    for key in list(theProject.statusItems.keys()):
        assert theProject.statusItems.remove(key) is True

    theProject.importItems.resetCounts()
    for key in list(theProject.importItems.keys()):
        assert theProject.importItems.remove(key) is True

    assert len(theProject.statusItems) == 0
    assert len(theProject.importItems) == 0
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True

    # This should restore the default status/import labels
    assert theProject.openProject(fncDir) is True
    assert theProject.saveProject() is True
    assert theProject.statusItems.name("s000023") == "New"
    assert theProject.statusItems.name("s000024") == "Note"
    assert theProject.statusItems.name("s000025") == "Draft"
    assert theProject.statusItems.name("s000026") == "Finished"
    assert theProject.importItems.name("i000027") == "New"
    assert theProject.importItems.name("i000028") == "Minor"
    assert theProject.importItems.name("i000029") == "Major"
    assert theProject.importItems.name("i00002a") == "Main"

# END Test testCoreProject_StatusImport


@pytest.mark.core
def testCoreProject_Methods(monkeypatch, mockGUI, tmpDir, fncDir, mockRnd):
    """Test other project class methods and functions.
    """
    theProject = NWProject(mockGUI)
    buildTestProject(theProject, fncDir)

    # Setting project path
    assert theProject.setProjectPath(None)
    assert theProject.projPath is None
    assert theProject.setProjectPath("")
    assert theProject.projPath is None
    assert theProject.setProjectPath("~")
    assert theProject.projPath == os.path.expanduser("~")

    # Create a new folder and populate it
    projPath = os.path.join(fncDir, "mock1")
    assert theProject.setProjectPath(projPath, newProject=True)

    # Make os.mkdir fail
    monkeypatch.setattr("os.mkdir", causeOSError)
    projPath = os.path.join(fncDir, "mock2")
    assert not theProject.setProjectPath(projPath, newProject=True)

    # Set back
    assert theProject.setProjectPath(fncDir)

    # Project Name
    assert theProject.setProjectName("  A Name ")
    assert theProject.projName == "A Name"

    # Project Title
    assert theProject.setBookTitle("  A Title ")
    assert theProject.bookTitle == "A Title"

    # Project Authors
    # Check that the list is cleaned up and that it can be extracted as
    # a properly formatted string, depending on number of names
    assert not theProject.setBookAuthors([])
    assert theProject.setBookAuthors(" Jane Doe \n John Doh \n ")
    assert theProject.bookAuthors == ["Jane Doe", "John Doh"]

    assert theProject.setBookAuthors("")
    assert theProject.getAuthors() == ""

    assert theProject.setBookAuthors("Jane Doe")
    assert theProject.getAuthors() == "Jane Doe"

    assert theProject.setBookAuthors("Jane Doe\nJohn Doh")
    assert theProject.getAuthors() == "Jane Doe and John Doh"

    assert theProject.setBookAuthors("Jane Doe\nJohn Doh\nBod Owens")
    assert theProject.getAuthors() == "Jane Doe, John Doh and Bod Owens"

    # Edit Time
    theProject.editTime = 1234
    theProject.projOpened = 1600000000
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.project.time", lambda: 1600005600)
        assert theProject.getCurrentEditTime() == 6834

    # Trash folder
    # Should create on first call, and just returned on later calls
    hTrash = "0000000000018"
    assert theProject.tree[hTrash] is None
    assert theProject.trashFolder() == hTrash
    assert theProject.trashFolder() == hTrash

    # Project backup
    assert theProject.doBackup is True
    assert theProject.setProjBackup(False)
    assert theProject.doBackup is False

    assert not theProject.setProjBackup(True)
    theProject.mainConf.backupPath = tmpDir
    assert theProject.setProjBackup(True)

    assert theProject.setProjectName("")
    assert not theProject.setProjBackup(True)
    assert theProject.setProjectName("A Name")
    assert theProject.setProjBackup(True)

    # Spell check
    theProject.projChanged = False
    assert theProject.setSpellCheck(True)
    assert not theProject.setSpellCheck(False)
    assert theProject.projChanged

    # Spell language
    theProject.projChanged = False
    assert theProject.projSpell is None
    assert theProject.setSpellLang(None) is False
    assert theProject.projSpell is None
    assert theProject.setSpellLang("None") is False  # Should be interpreded as None
    assert theProject.projSpell is None
    assert theProject.setSpellLang("en_GB")
    assert theProject.projSpell == "en_GB"
    assert theProject.projChanged

    # Project Language
    theProject.projChanged = False
    theProject.projLang = "en"
    assert theProject.setProjectLang(None) is True
    assert theProject.projLang is None
    assert theProject.setProjectLang("en_GB") is True
    assert theProject.projLang == "en_GB"

    # Language Lookup
    assert theProject.localLookup(1) == "One"
    assert theProject.localLookup(10) == "Ten"

    # Automatic outline update
    theProject.projChanged = False
    assert theProject.setAutoOutline(True)
    assert not theProject.setAutoOutline(False)
    assert theProject.projChanged

    # Last edited
    theProject.projChanged = False
    assert theProject.setLastEdited("0123456789abc")
    assert theProject.lastEdited == "0123456789abc"
    assert theProject.projChanged

    # Last viewed
    theProject.projChanged = False
    assert theProject.setLastViewed("0123456789abc")
    assert theProject.lastViewed == "0123456789abc"
    assert theProject.projChanged

    # Autoreplace
    theProject.projChanged = False
    assert theProject.setAutoReplace({"A": "B", "C": "D"})
    assert theProject.autoReplace == {"A": "B", "C": "D"}
    assert theProject.projChanged

    # Change project tree order
    oldOrder = [
        "0000000000010", "0000000000011", "0000000000012",
        "0000000000013", "0000000000014", "0000000000015",
        "0000000000016", "0000000000017", "0000000000018",
    ]
    newOrder = [
        "0000000000013", "0000000000014", "0000000000015",
        "0000000000010", "0000000000011", "0000000000012",
        "0000000000016", "0000000000017",
    ]
    assert theProject.tree.handles() == oldOrder
    assert theProject.setTreeOrder(newOrder)
    assert theProject.tree.handles() == newOrder
    assert theProject.setTreeOrder(oldOrder)
    assert theProject.tree.handles() == oldOrder

    # Session stats
    theProject.currWCount = 200
    theProject.lastWCount = 100
    with monkeypatch.context() as mp:
        mp.setattr("os.path.isdir", lambda *a, **k: False)
        assert not theProject._appendSessionStats(idleTime=0)

    # Block open
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert not theProject._appendSessionStats(idleTime=0)

    # Write entry
    assert theProject.projMeta == os.path.join(fncDir, "meta")
    statsFile = os.path.join(theProject.projMeta, nwFiles.SESS_STATS)

    theProject.projOpened = 1600002000
    theProject.currNovelWC = 200
    theProject.currNotesWC = 100

    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.project.time", lambda: 1600005600)
        assert theProject._appendSessionStats(idleTime=99)

    assert readFile(statsFile) == (
        "# Offset 100\n"
        "# Start Time         End Time                Novel     Notes      Idle\n"
        "%s  %s       200       100        99\n"
    ) % (formatTimeStamp(1600002000), formatTimeStamp(1600005600))

    # Pack XML Value
    xElem = etree.Element("element")
    theProject._packProjectValue(xElem, "A", "B", allowNone=False)
    assert etree.tostring(xElem, pretty_print=False, encoding="utf-8") == (
        b"<element><A>B</A></element>"
    )

    xElem = etree.Element("element")
    theProject._packProjectValue(xElem, "A", "", allowNone=False)
    assert etree.tostring(xElem, pretty_print=False, encoding="utf-8") == (
        b"<element/>"
    )

    # Pack XML Key/Value
    xElem = etree.Element("element")
    theProject._packProjectKeyValue(xElem, "item", {"A": "B", "C": "D"})
    assert etree.tostring(xElem, pretty_print=False, encoding="utf-8") == (
        b"<element>"
        b"<item>"
        b"<entry key=\"A\">B</entry>"
        b"<entry key=\"C\">D</entry>"
        b"</item>"
        b"</element>"
    )

# END Test testCoreProject_Methods


@pytest.mark.core
def testCoreProject_OrphanedFiles(mockGUI, nwLipsum):
    """Check that files in the content folder that are not tracked in
    the project XML file are handled correctly by the orphaned files
    function. It should also restore as much meta data as possible from
    the meta line at the top of the document file.
    """
    theProject = NWProject(mockGUI)

    assert theProject.openProject(nwLipsum) is True
    assert theProject.tree["636b6aa9b697b"] is None

    # Add a file with non-existent parent
    # This file will be renoved from the project on open
    oHandle = theProject.newFile("Oops", "b3643d0f92e32")
    theProject.tree[oHandle].setParent("1234567890abc")

    # Save and close
    assert theProject.saveProject() is True
    assert theProject.closeProject() is True

    # First Item with Meta Data
    orphPath = os.path.join(nwLipsum, "content", "636b6aa9b697b.nwd")
    writeFile(orphPath, (
        "%%~name:[Recovered] Mars\n"
        "%%~path:5eaea4e8cdee8/636b6aa9b697b\n"
        "%%~kind:WORLD/NOTE\n"
        "%%~invalid\n"
        "\n"
    ))

    # Second Item without Meta Data
    orphPath = os.path.join(nwLipsum, "content", "736b6aa9b697b.nwd")
    writeFile(orphPath, "\n")

    # Invalid File Name
    tstPath = os.path.join(nwLipsum, "content", "636b6aa9b697b.txt")
    writeFile(tstPath, "\n")

    # Invalid File Name
    tstPath = os.path.join(nwLipsum, "content", "636b6aa9b697bb.nwd")
    writeFile(tstPath, "\n")

    # Invalid File Name
    tstPath = os.path.join(nwLipsum, "content", "abcdefghijklm.nwd")
    writeFile(tstPath, "\n")

    assert theProject.openProject(nwLipsum)
    assert theProject.projPath is not None
    assert theProject.tree["636b6aa9b697bb"] is None
    assert theProject.tree["abcdefghijklm"] is None

    # First Item with Meta Data
    oItem = theProject.tree["636b6aa9b697b"]
    assert oItem is not None
    assert oItem.itemName == "[Recovered] Mars"
    assert oItem.itemHandle == "636b6aa9b697b"
    assert oItem.itemParent == "60bdf227455cc"
    assert oItem.itemClass == nwItemClass.WORLD
    assert oItem.itemType == nwItemType.FILE
    assert oItem.itemLayout == nwItemLayout.NOTE

    # Second Item without Meta Data
    oItem = theProject.tree["736b6aa9b697b"]
    assert oItem is not None
    assert oItem.itemName == "Recovered File 1"
    assert oItem.itemHandle == "736b6aa9b697b"
    assert oItem.itemParent == "b3643d0f92e32"
    assert oItem.itemClass == nwItemClass.NOVEL
    assert oItem.itemType == nwItemType.FILE
    assert oItem.itemLayout == nwItemLayout.NOTE

    assert theProject.saveProject(nwLipsum)
    assert theProject.closeProject()

    # Finally, check that the orphaned files function returns
    # if no project is open and no path is set
    assert not theProject._scanProjectFolder()

# END Test testCoreProject_OrphanedFiles


@pytest.mark.core
def testCoreProject_OldFormat(mockGUI, nwOldProj):
    """Test that a project folder structure of version 1.0 can be
    converted to the latest folder structure. Version 1.0 split the
    documents into 'data_0' ... 'data_f' folders, which are now all
    contained in a single 'content' folder.
    """
    theProject = NWProject(mockGUI)

    # Create mock files for known legacy files
    deleteFiles = [
        os.path.join(nwOldProj, "cache", "nwProject.nwx.0"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.1"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.2"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.3"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.4"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.5"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.6"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.7"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.8"),
        os.path.join(nwOldProj, "cache", "nwProject.nwx.9"),
        os.path.join(nwOldProj, "meta",  "mainOptions.json"),
        os.path.join(nwOldProj, "meta",  "exportOptions.json"),
        os.path.join(nwOldProj, "meta",  "outlineOptions.json"),
        os.path.join(nwOldProj, "meta",  "timelineOptions.json"),
        os.path.join(nwOldProj, "meta",  "docMergeOptions.json"),
        os.path.join(nwOldProj, "meta",  "sessionLogOptions.json"),
    ]

    # Create mock files
    os.mkdir(os.path.join(nwOldProj, "cache"))
    for aFile in deleteFiles:
        writeFile(aFile, "Hi")
    for aFile in deleteFiles:
        assert os.path.isfile(aFile)

    # Open project and check that files that are not supposed to be
    # there have been removed
    assert theProject.openProject(nwOldProj)
    for aFile in deleteFiles:
        assert not os.path.isfile(aFile)

    assert not os.path.isdir(os.path.join(nwOldProj, "data_1"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_7"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_8"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_9"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_a"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_f"))

    # Check that files we want to keep are in the right place
    assert os.path.isdir(os.path.join(nwOldProj, "cache"))
    assert os.path.isdir(os.path.join(nwOldProj, "content"))
    assert os.path.isdir(os.path.join(nwOldProj, "meta"))

    assert os.path.isfile(os.path.join(nwOldProj, "content", "f528d831f5b24.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "88124a4292d8b.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "91239bf2f8b69.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "19752e7f9d8af.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "a764d5acf5a21.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "9058ae29f0dfd.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "content", "7ff63b8afc4cd.nwd"))

    assert os.path.isfile(os.path.join(nwOldProj, "meta", "tagsIndex.json"))
    assert os.path.isfile(os.path.join(nwOldProj, "meta", "sessionInfo.log"))

    # Close the project
    theProject.closeProject()

    # Check that new files have been created
    assert os.path.isfile(os.path.join(nwOldProj, "meta", "guiOptions.json"))
    assert os.path.isfile(os.path.join(nwOldProj, "ToC.txt"))

# END Test testCoreProject_OldFormat


@pytest.mark.core
def testCoreProject_LegacyData(monkeypatch, mockGUI, fncDir):
    """Test the functins that handle legacy data folders and structure
    with additional tests of failure handling.
    """
    theProject = NWProject(mockGUI)
    theProject.setProjectPath(fncDir)

    # Check behaviour of deprecated files function on OSError
    tstFile = os.path.join(fncDir, "ToC.json")
    writeFile(tstFile, "stuff")
    assert os.path.isfile(tstFile)

    with monkeypatch.context() as mp:
        mp.setattr("os.unlink", causeOSError)
        assert theProject._deprecatedFiles() is False

    assert theProject._deprecatedFiles()
    assert not os.path.isfile(tstFile)

    # Check processing non-folders
    tstFile = os.path.join(fncDir, "data_0")
    writeFile(tstFile, "stuff")
    assert os.path.isfile(tstFile)
    assert theProject._legacyDataFolder(tstFile) is False

    # Check renaming/deleting of old document files
    tstData2 = os.path.join(fncDir, "data_2")
    tstData3 = os.path.join(fncDir, "data_3")
    tstDoc1m = os.path.join(tstData2, "000000000001_main.nwd")
    tstDoc1b = os.path.join(tstData2, "000000000001_main.bak")
    tstDoc2m = os.path.join(tstData2, "000000000002_main.nwd")
    tstDoc2b = os.path.join(tstData2, "000000000002_main.bak")
    tstDoc3m = os.path.join(tstData3, "tooshort003_main.nwd")
    tstDoc3b = os.path.join(tstData3, "tooshort003_main.bak")
    tstDir4a = os.path.join(tstData3, "stuff")

    os.mkdir(tstData2)
    os.mkdir(tstData3)
    writeFile(tstDoc1m, "stuff")
    writeFile(tstDoc1b, "stuff")
    writeFile(tstDoc2m, "stuff")
    writeFile(tstDoc2b, "stuff")
    writeFile(tstDoc3m, "stuff")
    writeFile(tstDoc3b, "stuff")
    os.mkdir(tstDir4a)

    # Make the above fail
    with monkeypatch.context() as mp:
        mp.setattr("os.rename", causeOSError)
        mp.setattr("os.unlink", causeOSError)
        with pytest.raises(OSError):
            theProject._legacyDataFolder(tstData2)
            theProject._legacyDataFolder(tstData3)
        assert os.path.isfile(tstDoc1m)
        assert os.path.isfile(tstDoc1b)
        assert os.path.isfile(tstDoc2m)
        assert os.path.isfile(tstDoc2b)
        assert os.path.isfile(tstDoc3m)
        assert os.path.isfile(tstDoc3b)

    # And succeed ...
    assert theProject._legacyDataFolder(tstData2) is True
    assert theProject._legacyDataFolder(tstData3) is True

    assert not os.path.isdir(tstData2)
    assert os.path.isdir(tstData3)
    assert os.path.isfile(os.path.join(fncDir, "content", "2000000000001.nwd"))
    assert os.path.isfile(os.path.join(fncDir, "content", "2000000000002.nwd"))
    assert os.path.isfile(os.path.join(fncDir, tstData3, "tooshort003_main.nwd"))
    assert os.path.isfile(os.path.join(fncDir, tstData3, "tooshort003_main.bak"))
    assert os.path.isdir(tstDir4a)

# END Test testCoreProject_LegacyData


@pytest.mark.core
def testCoreProject_Backup(monkeypatch, mockGUI, nwMinimal, tmpDir):
    """Test the automated backup feature of the project class. The test
    creates a backup of the Minimal test project, and then unzips the
    backupd file and checks that the project XML file is identical to
    the original file.
    """
    theProject = NWProject(mockGUI)
    assert theProject.openProject(nwMinimal)

    # Test faulty settings

    # No project
    mockGUI.hasProject = False
    assert theProject.zipIt(doNotify=False) is False
    mockGUI.hasProject = True

    # Invalid path
    theProject.mainConf.backupPath = None
    assert theProject.zipIt(doNotify=False) is False

    # Missing project name
    theProject.mainConf.backupPath = tmpDir
    theProject.projName = ""
    assert theProject.zipIt(doNotify=False) is False

    # Non-existent folder
    theProject.mainConf.backupPath = os.path.join(tmpDir, "nonexistent")
    theProject.projName = "Test Minimal"
    assert theProject.zipIt(doNotify=False) is False

    # Same folder as project (causes infinite loop in zipping)
    theProject.mainConf.backupPath = nwMinimal
    assert theProject.zipIt(doNotify=False) is False

    # Subfolder of project (causes infinite loop in zipping)
    theProject.mainConf.backupPath = os.path.join(nwMinimal, "subdir")
    assert theProject.zipIt(doNotify=False) is False

    # Set a valid folder
    theProject.mainConf.backupPath = tmpDir

    # Can't make folder
    with monkeypatch.context() as mp:
        mp.setattr("os.mkdir", causeOSError)
        assert theProject.zipIt(doNotify=False) is False

    # Can't write archive
    with monkeypatch.context() as mp:
        mp.setattr("shutil.make_archive", causeOSError)
        assert theProject.zipIt(doNotify=False) is False

    # Test correct settings
    assert theProject.zipIt(doNotify=True) is True

    theFiles = os.listdir(os.path.join(tmpDir, "Test Minimal"))
    assert len(theFiles) == 1

    theZip = theFiles[0]
    assert theZip[:12] == "Backup from "
    assert theZip[-4:] == ".zip"

    # Extract the archive
    with ZipFile(os.path.join(tmpDir, "Test Minimal", theZip), "r") as inZip:
        inZip.extractall(os.path.join(tmpDir, "extract"))

    # Check that the main project file was restored
    assert cmpFiles(
        os.path.join(nwMinimal, "nwProject.nwx"),
        os.path.join(tmpDir, "extract", "nwProject.nwx")
    )

# END Test testCoreProject_Backup
