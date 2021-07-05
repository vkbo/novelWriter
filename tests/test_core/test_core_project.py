"""
novelWriter – NWProject Class Tester
====================================

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

import pytest
import os

from shutil import copyfile
from zipfile import ZipFile
from lxml import etree

from tools import cmpFiles, writeFile, readFile
from mock import causeOSError

from nw.core.project import NWProject
from nw.enum import nwItemClass, nwItemType, nwItemLayout
from nw.common import formatTimeStamp
from nw.constants import nwFiles


@pytest.mark.core
def testCoreProject_NewMinimal(fncDir, outDir, refDir, mockGUI):
    """Create a new project from a project wizard dictionary. With
    default setting, creating a Minimal project.
    """
    projFile = os.path.join(fncDir, "nwProject.nwx")
    testFile = os.path.join(outDir, "coreProject_NewMinimal_nwProject.nwx")
    compFile = os.path.join(refDir, "coreProject_NewMinimal_nwProject.nwx")

    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)

    # Setting no data should fail
    assert not theProject.newProject({})

    # Try again with a proper path
    assert theProject.newProject({"projPath": fncDir})
    assert theProject.saveProject()
    assert theProject.closeProject()

    # Creating the project once more should fail
    assert not theProject.newProject({"projPath": fncDir})

    # Check the new project
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8])

    # Open again
    assert theProject.openProject(projFile)

    # Save and close
    assert theProject.saveProject()
    assert theProject.closeProject()
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8])
    assert not theProject.projChanged

    # Open a second time
    assert theProject.openProject(projFile)
    assert not theProject.openProject(projFile)
    assert theProject.openProject(projFile, overrideLock=True)
    assert theProject.saveProject()
    assert theProject.closeProject()
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8])

# END Test testCoreProject_NewMinimal


@pytest.mark.core
def testCoreProject_NewCustomA(fncDir, outDir, refDir, mockGUI):
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
            nwItemClass.TIMELINE,
            nwItemClass.OBJECT,
            nwItemClass.ENTITY,
        ],
        "numChapters": 3,
        "numScenes": 3,
        "chFolders": True,
    }
    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)

    assert theProject.newProject(projData)
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8])

# END Test testCoreProject_NewCustomA


@pytest.mark.core
def testCoreProject_NewCustomB(fncDir, outDir, refDir, mockGUI):
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
            nwItemClass.TIMELINE,
            nwItemClass.OBJECT,
            nwItemClass.ENTITY,
        ],
        "numChapters": 0,
        "numScenes": 6,
        "chFolders": True,
    }
    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)

    assert theProject.newProject(projData)
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8])

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
    theProject.projTree.setSeed(42)

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

    assert theProject.newProject(projData)
    assert theProject.openProject(fncDir)
    assert theProject.projName == "Sample Project"
    assert theProject.saveProject()
    assert theProject.closeProject()
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
    theProject.projTree.setSeed(42)

    # Make sure we do not pick up the nw/assets/sample.zip file
    tmpConf.assetPath = tmpDir

    # Set a fake project file name
    monkeypatch.setattr(nwFiles, "PROJ_FILE", "nothing.nwx")
    assert not theProject.newProject(projData)

    monkeypatch.setattr(nwFiles, "PROJ_FILE", "nwProject.nwx")
    assert theProject.newProject(projData)
    assert theProject.openProject(fncDir)
    assert theProject.projName == "Sample Project"
    assert theProject.saveProject()
    assert theProject.closeProject()

    # Misdirect the appRoot path so neither is possible
    tmpConf.appRoot = tmpDir
    assert not theProject.newProject(projData)

# END Test testCoreProject_NewSampleB


@pytest.mark.core
def testCoreProject_NewRoot(fncDir, outDir, refDir, mockGUI):
    """Check that new root folders can be added to the project.
    """
    projFile = os.path.join(fncDir, "nwProject.nwx")
    testFile = os.path.join(outDir, "coreProject_NewRoot_nwProject.nwx")
    compFile = os.path.join(refDir, "coreProject_NewRoot_nwProject.nwx")

    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)

    assert theProject.newProject({"projPath": fncDir})
    assert theProject.setProjectPath(fncDir)
    assert theProject.saveProject()
    assert theProject.closeProject()
    assert theProject.openProject(projFile)

    assert isinstance(theProject.newRoot("Novel",     nwItemClass.NOVEL),     type(None))
    assert isinstance(theProject.newRoot("Plot",      nwItemClass.PLOT),      type(None))
    assert isinstance(theProject.newRoot("Character", nwItemClass.CHARACTER), type(None))
    assert isinstance(theProject.newRoot("World",     nwItemClass.WORLD),     type(None))
    assert isinstance(theProject.newRoot("Timeline",  nwItemClass.TIMELINE),  str)
    assert isinstance(theProject.newRoot("Object",    nwItemClass.OBJECT),    str)
    assert isinstance(theProject.newRoot("Custom1",   nwItemClass.CUSTOM),    str)
    assert isinstance(theProject.newRoot("Custom2",   nwItemClass.CUSTOM),    str)

    assert theProject.projChanged
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8])
    assert not theProject.projChanged

# END Test testCoreProject_NewRoot


@pytest.mark.core
def testCoreProject_NewFile(fncDir, outDir, refDir, mockGUI):
    """Check that new files can be added to the project.
    """
    projFile = os.path.join(fncDir, "nwProject.nwx")
    testFile = os.path.join(outDir, "coreProject_NewFile_nwProject.nwx")
    compFile = os.path.join(refDir, "coreProject_NewFile_nwProject.nwx")

    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)

    assert theProject.newProject({"projPath": fncDir})
    assert theProject.setProjectPath(fncDir)
    assert theProject.saveProject()
    assert theProject.closeProject()
    assert theProject.openProject(projFile)

    assert isinstance(theProject.newFile("Hello", nwItemClass.NOVEL,     "31489056e0916"), str)
    assert isinstance(theProject.newFile("Jane",  nwItemClass.CHARACTER, "71ee45a3c0db9"), str)
    assert theProject.projChanged
    assert theProject.saveProject()
    assert theProject.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8])
    assert not theProject.projChanged

# END Test testCoreProject_NewFile


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

    # Larger hex version
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
    writeFile(os.path.join(nwMinimal, "junk"), "stuff")
    os.mkdir(os.path.join(nwMinimal, "data_0"))
    writeFile(os.path.join(nwMinimal, "data_0", "junk"), "stuff")
    mockGUI.clear()
    assert theProject.openProject(nwMinimal) is True
    assert "data_0" in mockGUI.lastAlert
    assert theProject.closeProject()

# END Test testCoreProject_Open


@pytest.mark.core
def testCoreProject_Save(monkeypatch, nwMinimal, mockGUI, refDir):
    """Test saving a project.
    """
    theProject = NWProject(mockGUI)
    testFile = os.path.join(nwMinimal, "nwProject.nwx")
    compFile = os.path.join(refDir, os.path.pardir, "minimal", "nwProject.nwx")

    # Nothing to save
    assert theProject.saveProject() is False

    # Open test project
    assert theProject.openProject(nwMinimal)

    # Fail on folder structure check
    with monkeypatch.context() as mp:
        mp.setattr("os.path.isdir", lambda *args: False)
        assert theProject.saveProject() is False

    # Fail on open file
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert theProject.saveProject() is False

    # Successful save
    saveCount = theProject.saveCount
    autoCount = theProject.autoCount
    assert theProject.saveProject() is True
    assert theProject.saveCount == saveCount + 1
    assert theProject.autoCount == autoCount
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8, 9])

    # Successful autosave
    saveCount = theProject.saveCount
    autoCount = theProject.autoCount
    assert theProject.saveProject(autoSave=True) is True
    assert theProject.saveCount == saveCount
    assert theProject.autoCount == autoCount + 1
    assert cmpFiles(testFile, compFile, [2, 6, 7, 8, 9])

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
        mp.setattr("nw.core.project.time", lambda: 123.4)
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
    assert theProject.projTree.handles() == oldOrder
    assert theProject.setTreeOrder(newOrder)
    assert theProject.projTree.handles() == newOrder

    # Add a non-existing item
    theProject.projTree._treeOrder.append("01234567789abc")

    # Add an item with a non-existent parent
    nHandle = theProject.newFile("Test File", nwItemClass.NOVEL, "a6d311a93600a")
    theProject.projTree[nHandle].setParent("cba9876543210")
    assert theProject.projTree[nHandle].itemParent == "cba9876543210"

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
    assert theProject.projTree[nHandle].itemParent is None

# END Test testCoreProject_AccessItems


@pytest.mark.core
def testCoreProject_Methods(monkeypatch, nwMinimal, mockGUI, tmpDir):
    """Test other project class methods and functions.
    """
    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal)
    assert theProject.projPath == nwMinimal

    # Setting project path
    assert theProject.setProjectPath(None)
    assert theProject.projPath is None
    assert theProject.setProjectPath("")
    assert theProject.projPath is None
    assert theProject.setProjectPath("~")
    assert theProject.projPath == os.path.expanduser("~")

    # Create a new folder and populate it
    projPath = os.path.join(nwMinimal, "dummy1")
    assert theProject.setProjectPath(projPath, newProject=True)

    # Make os.mkdir fail
    monkeypatch.setattr("os.mkdir", causeOSError)
    projPath = os.path.join(nwMinimal, "dummy2")
    assert not theProject.setProjectPath(projPath, newProject=True)

    # Set back
    assert theProject.setProjectPath(nwMinimal)

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
        mp.setattr("nw.core.project.time", lambda: 1600005600)
        assert theProject.getCurrentEditTime() == 6834

    # Trash folder
    # Should create on first call, and just returned on later calls
    assert theProject.projTree["73475cb40a568"] is None
    assert theProject.trashFolder() == "73475cb40a568"
    assert theProject.trashFolder() == "73475cb40a568"

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
    assert theProject.setSpellLang(None)
    assert theProject.projSpell is None
    assert theProject.setSpellLang("None")
    assert theProject.projSpell is None
    assert theProject.setSpellLang("en_GB")
    assert theProject.projSpell == "en_GB"
    assert theProject.projChanged

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
        "a508bb932959c", "a35baf2e93843", "a6d311a93600a",
        "f5ab3e30151e1", "8c659a11cd429", "7695ce551d265",
        "afb3043c7b2b3", "9d5247ab588e0", "73475cb40a568",
    ]
    newOrder = [
        "f5ab3e30151e1", "8c659a11cd429", "7695ce551d265",
        "a508bb932959c", "a35baf2e93843", "a6d311a93600a",
        "afb3043c7b2b3", "9d5247ab588e0",
    ]
    assert theProject.projTree.handles() == oldOrder
    assert theProject.setTreeOrder(newOrder)
    assert theProject.projTree.handles() == newOrder
    assert theProject.setTreeOrder(oldOrder)
    assert theProject.projTree.handles() == oldOrder

    # Change status
    theProject.projTree["a35baf2e93843"].setStatus("Finished")
    theProject.projTree["a6d311a93600a"].setStatus("Draft")
    theProject.projTree["f5ab3e30151e1"].setStatus("Note")
    theProject.projTree["8c659a11cd429"].setStatus("Finished")
    newList = [
        ("New", 1, 1, 1, "New"),
        ("Draft", 2, 2, 2, "Note"),       # These are swapped
        ("Note", 3, 3, 3, "Draft"),       # These are swapped
        ("Edited", 4, 4, 4, "Finished"),  # Renamed
        ("Finished", 5, 5, 5, None),      # New, with reused name
    ]
    assert theProject.setStatusColours(newList)
    assert theProject.statusItems._theLabels == [
        "New", "Draft", "Note", "Edited", "Finished"
    ]
    assert theProject.statusItems._theColours == [
        (1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4), (5, 5, 5)
    ]
    assert theProject.projTree["a35baf2e93843"].itemStatus == "Edited"  # Renamed
    assert theProject.projTree["a6d311a93600a"].itemStatus == "Note"    # Swapped
    assert theProject.projTree["f5ab3e30151e1"].itemStatus == "Draft"   # Swapped
    assert theProject.projTree["8c659a11cd429"].itemStatus == "Edited"  # Renamed

    # Change importance
    fHandle = theProject.newFile("Jane Doe", nwItemClass.CHARACTER, "afb3043c7b2b3")
    theProject.projTree[fHandle].setStatus("Main")
    newList = [
        ("New", 1, 1, 1, "New"),
        ("Minor", 2, 2, 2, "Minor"),
        ("Major", 3, 3, 3, "Major"),
        ("Min", 4, 4, 4, "Main"),
        ("Max", 5, 5, 5, None),
    ]
    assert theProject.setImportColours(newList)
    assert theProject.importItems._theLabels == [
        "New", "Minor", "Major", "Min", "Max"
    ]
    assert theProject.importItems._theColours == [
        (1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4), (5, 5, 5)
    ]
    assert theProject.projTree[fHandle].itemStatus == "Min"

    # Check status counts
    assert theProject.statusItems._theCounts == [0, 0, 0, 0, 0]
    assert theProject.importItems._theCounts == [0, 0, 0, 0, 0]
    theProject.countStatus()
    assert theProject.statusItems._theCounts == [1, 1, 1, 2, 0]
    assert theProject.importItems._theCounts == [3, 0, 0, 1, 0]

    # Check word counts
    theProject.currWCount = 200
    theProject.lastWCount = 100
    assert theProject.getSessionWordCount() == 100

    # Session stats
    with monkeypatch.context() as mp:
        mp.setattr("os.path.isdir", lambda *a, **k: False)
        assert not theProject._appendSessionStats(idleTime=0)

    # Block open
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert not theProject._appendSessionStats(idleTime=0)

    # Write entry
    assert theProject.projMeta == os.path.join(nwMinimal, "meta")
    statsFile = os.path.join(theProject.projMeta, nwFiles.SESS_STATS)

    theProject.projOpened = 1600002000
    theProject.novelWCount = 200
    theProject.notesWCount = 100

    with monkeypatch.context() as mp:
        mp.setattr("nw.core.project.time", lambda: 1600005600)
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

    assert theProject.openProject(nwLipsum)
    assert theProject.projTree["636b6aa9b697b"] is None
    assert theProject.closeProject()

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
    assert theProject.projTree["636b6aa9b697bb"] is None
    assert theProject.projTree["abcdefghijklm"] is None

    # First Item with Meta Data
    oItem = theProject.projTree["636b6aa9b697b"]
    assert oItem is not None
    assert oItem.itemName == "[Recovered] Mars"
    assert oItem.itemHandle == "636b6aa9b697b"
    assert oItem.itemParent == "60bdf227455cc"
    assert oItem.itemClass == nwItemClass.WORLD
    assert oItem.itemType == nwItemType.FILE
    assert oItem.itemLayout == nwItemLayout.NOTE

    # Second Item without Meta Data
    oItem = theProject.projTree["736b6aa9b697b"]
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

    # Add some files that shouldn't be there
    deleteFiles.append(os.path.join(nwOldProj, "data_f", "whatnow.nwd"))
    deleteFiles.append(os.path.join(nwOldProj, "data_f", "whatnow.txt"))

    # Add some folders that shouldn't be there
    os.mkdir(os.path.join(nwOldProj, "stuff"))
    os.mkdir(os.path.join(nwOldProj, "data_1", "stuff"))

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

    assert not os.path.isdir(os.path.join(nwOldProj, "data_1", "stuff"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_1"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_7"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_8"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_9"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_a"))
    assert not os.path.isdir(os.path.join(nwOldProj, "data_f"))

    # Check stuff that has been moved
    assert os.path.isdir(os.path.join(nwOldProj, "junk"))
    assert os.path.isdir(os.path.join(nwOldProj, "junk", "stuff"))
    assert os.path.isfile(os.path.join(nwOldProj, "junk", "whatnow.nwd"))
    assert os.path.isfile(os.path.join(nwOldProj, "junk", "whatnow.txt"))

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

    # assert theProject.newProject({"projPath": fncDir})
    # assert theProject.saveProject()
    # assert theProject.closeProject()

    # Check behaviour of deprecated files function on OSError
    tstFile = os.path.join(fncDir, "ToC.json")
    writeFile(tstFile, "stuff")
    assert os.path.isfile(tstFile)

    with monkeypatch.context() as mp:
        mp.setattr("os.unlink", causeOSError)
        assert not theProject._deprecatedFiles()

    assert theProject._deprecatedFiles()
    assert not os.path.isfile(tstFile)

    # Check processing non-folders
    tstFile = os.path.join(fncDir, "data_0")
    writeFile(tstFile, "stuff")
    assert os.path.isfile(tstFile)

    errList = []
    errList = theProject._legacyDataFolder(tstFile, errList)
    assert len(errList) > 0

    # Move folder in data folder, shouldn't be there
    tstData = os.path.join(fncDir, "data_1")
    errItem = os.path.join(fncDir, "data_1", "stuff")
    os.mkdir(tstData)
    os.mkdir(errItem)
    assert os.path.isdir(tstData)
    assert os.path.isdir(errItem)

    # This causes a failure to create the 'junk' folder
    with monkeypatch.context() as mp:
        mp.setattr("os.mkdir", causeOSError)
        errList = []
        errList = theProject._legacyDataFolder(tstData, errList)
        assert len(errList) > 0

    # This causes a failure to move 'stuff' to 'junk'
    with monkeypatch.context() as mp:
        mp.setattr("os.rename", causeOSError)
        errList = []
        errList = theProject._legacyDataFolder(tstData, errList)
        assert len(errList) > 0

    # This should be successful
    errList = []
    errList = theProject._legacyDataFolder(tstData, errList)
    assert len(errList) == 0
    assert os.path.isdir(os.path.join(fncDir, "junk", "stuff"))

    # Check renaming/deleting of old document files
    tstData = os.path.join(fncDir, "data_2")
    tstDoc1m = os.path.join(tstData, "000000000001_main.nwd")
    tstDoc1b = os.path.join(tstData, "000000000001_main.bak")
    tstDoc2m = os.path.join(tstData, "000000000002_main.nwd")
    tstDoc2b = os.path.join(tstData, "000000000002_main.bak")
    tstDoc3m = os.path.join(tstData, "tooshort003_main.nwd")
    tstDoc3b = os.path.join(tstData, "tooshort003_main.bak")

    os.mkdir(tstData)
    writeFile(tstDoc1m, "stuff")
    writeFile(tstDoc1b, "stuff")
    writeFile(tstDoc2m, "stuff")
    writeFile(tstDoc2b, "stuff")
    writeFile(tstDoc3m, "stuff")
    writeFile(tstDoc3b, "stuff")

    # Make the above fail
    with monkeypatch.context() as mp:
        mp.setattr("os.rename", causeOSError)
        mp.setattr("os.unlink", causeOSError)
        errList = []
        errList = theProject._legacyDataFolder(tstData, errList)
        assert len(errList) > 0
        assert os.path.isfile(tstDoc1m)
        assert os.path.isfile(tstDoc1b)
        assert os.path.isfile(tstDoc2m)
        assert os.path.isfile(tstDoc2b)
        assert os.path.isfile(tstDoc3m)
        assert os.path.isfile(tstDoc3b)

    # And succeed ...
    errList = []
    errList = theProject._legacyDataFolder(tstData, errList)
    assert len(errList) == 0

    assert not os.path.isdir(tstData)
    assert os.path.isfile(os.path.join(fncDir, "content", "2000000000001.nwd"))
    assert os.path.isfile(os.path.join(fncDir, "content", "2000000000002.nwd"))
    assert os.path.isfile(os.path.join(fncDir, "junk", "tooshort003_main.nwd"))
    assert os.path.isfile(os.path.join(fncDir, "junk", "tooshort003_main.bak"))

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
    assert not theProject.zipIt(doNotify=False)
    mockGUI.hasProject = True

    # Invalid path
    theProject.mainConf.backupPath = None
    assert not theProject.zipIt(doNotify=False)

    # Missing project name
    theProject.mainConf.backupPath = tmpDir
    theProject.projName = ""
    assert not theProject.zipIt(doNotify=False)

    # Non-existent folder
    theProject.mainConf.backupPath = os.path.join(tmpDir, "nonexistent")
    theProject.projName = "Test Minimal"
    assert not theProject.zipIt(doNotify=False)

    # Same folder as project (causes infinite loop in zipping)
    theProject.mainConf.backupPath = nwMinimal
    assert not theProject.zipIt(doNotify=False)

    # Set a valid folder
    theProject.mainConf.backupPath = tmpDir

    # Can't make folder
    with monkeypatch.context() as mp:
        mp.setattr("os.mkdir", causeOSError)
        assert not theProject.zipIt(doNotify=False)

    # Can't write archive
    with monkeypatch.context() as mp:
        mp.setattr("shutil.make_archive", causeOSError)
        assert not theProject.zipIt(doNotify=False)

    # Test correct settings
    assert theProject.zipIt(doNotify=True)

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
