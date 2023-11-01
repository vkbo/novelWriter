"""
novelWriter – NWProject Class Tester
====================================

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

from PyQt5.QtWidgets import QMessageBox
import pytest

from shutil import copyfile
from zipfile import ZipFile

from mocked import causeOSError
from tools import C, cmpFiles, buildTestProject, XML_IGNORE

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwItemClass
from novelwriter.constants import nwFiles
from novelwriter.core.tree import NWTree
from novelwriter.core.index import NWIndex
from novelwriter.core.project import NWProject
from novelwriter.core.options import OptionState
from novelwriter.core.projectxml import ProjectXMLReader, ProjectXMLWriter, XMLReadState


@pytest.mark.core
def testCoreProject_NewRoot(fncPath, tstPaths, mockGUI, mockRnd):
    """Check that new root folders can be added to the project."""
    projFile = fncPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "coreProject_NewRoot_nwProject.nwx"
    compFile = tstPaths.refDir / "coreProject_NewRoot_nwProject.nwx"

    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    assert project.newRoot(nwItemClass.NOVEL) == "0000000000010"
    assert project.newRoot(nwItemClass.PLOT) == "0000000000011"
    assert project.newRoot(nwItemClass.CHARACTER) == "0000000000012"
    assert project.newRoot(nwItemClass.WORLD) == "0000000000013"
    assert project.newRoot(nwItemClass.TIMELINE) == "0000000000014"
    assert project.newRoot(nwItemClass.OBJECT) == "0000000000015"
    assert project.newRoot(nwItemClass.CUSTOM) == "0000000000016"
    assert project.newRoot(nwItemClass.CUSTOM) == "0000000000017"

    assert project.projChanged is True
    assert project.saveProject() is True
    project.closeProject()

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)
    assert project.projChanged is False

    # Delete the new items
    assert project.removeItem("0000000000010") is True
    assert project.removeItem("0000000000011") is True
    assert project.removeItem("0000000000012") is True
    assert project.removeItem("0000000000013") is True
    assert project.removeItem("0000000000014") is True
    assert project.removeItem("0000000000015") is True
    assert project.removeItem("0000000000016") is True
    assert project.removeItem("0000000000017") is True

    assert "0000000000010" not in project.tree
    assert "0000000000011" not in project.tree
    assert "0000000000012" not in project.tree
    assert "0000000000013" not in project.tree
    assert "0000000000014" not in project.tree
    assert "0000000000015" not in project.tree
    assert "0000000000016" not in project.tree
    assert "0000000000017" not in project.tree

# END Test testCoreProject_NewRoot


@pytest.mark.core
def testCoreProject_NewFileFolder(monkeypatch, fncPath, tstPaths, mockGUI, mockRnd):
    """Check that new files can be added to the project."""
    projFile = fncPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "coreProject_NewFileFolder_nwProject.nwx"
    compFile = tstPaths.refDir / "coreProject_NewFileFolder_nwProject.nwx"

    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    # Invalid call
    assert project.newFolder("New Folder", "1234567890abc") is None
    assert project.newFile("New File", "1234567890abc") is None

    # Add files properly
    assert project.newFolder("Stuff", C.hNovelRoot) == "0000000000010"
    assert project.newFile("Hello", "0000000000010") == "0000000000011"
    assert project.newFile("Jane", C.hCharRoot) == "0000000000012"

    assert "0000000000010" in project.tree
    assert "0000000000011" in project.tree
    assert "0000000000012" in project.tree

    # Write to file, failed
    assert project.writeNewFile("blabla", 1, True) is False         # Not a handle
    assert project.writeNewFile("0000000000010", 1, True) is False  # Not a file
    assert project.writeNewFile(C.hTitlePage, 1, True) is False  # Already has content

    # Write to file, success
    assert project.writeNewFile("0000000000011", 2, True) is True
    assert project.storage.getDocument("0000000000011").readDocument() == "## Hello\n\n"

    # Write to file with additional text, success
    assert project.writeNewFile("0000000000012", 1, False, "Hi Jane\n\n") is True
    assert project.storage.getDocument("0000000000012").readDocument() == (
        "# Jane\n\nHi Jane\n\n"
    )

    # Save, close and check
    assert project.projChanged is True
    assert project.saveProject() is True

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)
    assert project.projChanged is False

    # Delete new file, but block access
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.unlink", causeOSError)
        assert project.removeItem("0000000000011") is False
        assert "0000000000011" in project.tree

    # Delete new files and folders
    assert (fncPath / "content" / "0000000000012.nwd").exists()
    assert (fncPath / "content" / "0000000000011.nwd").exists()

    assert project.removeItem("0000000000012") is True
    assert project.removeItem("0000000000011") is True
    assert project.removeItem("0000000000010") is True

    assert not (fncPath / "content" / "0000000000012.nwd").exists()
    assert not (fncPath / "content" / "0000000000011.nwd").exists()

    assert "0000000000010" not in project.tree
    assert "0000000000011" not in project.tree
    assert "0000000000012" not in project.tree

    project.closeProject()

# END Test testCoreProject_NewFileFolder


@pytest.mark.core
def testCoreProject_Open(monkeypatch, caplog, mockGUI, fncPath, mockRnd):
    """Test opening a project."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    # Initialising the storage class fails
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.readProject", lambda *a, **k: False)
        assert project.openProject(fncPath) is False

    # Fail on lock file
    project.storage._lockFilePath = fncPath / nwFiles.PROJ_LOCK
    assert project.storage.writeLockFile() is True
    assert project.openProject(fncPath) is False
    assert isinstance(project.lockStatus, list)

    # Fail to read lockfile (which still opens the project)
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.readLockFile", lambda *a: ["ERROR"])
        caplog.clear()
        assert project.openProject(fncPath) is True
        assert "Failed to check lock file" in caplog.text
        project.closeProject()

    # Force open with lockfile
    project.storage._lockFilePath = fncPath / nwFiles.PROJ_LOCK
    assert project.storage.writeLockFile() is True
    assert project.openProject(fncPath, clearLock=True) is True
    project.closeProject()
    assert project.lockStatus is None

    # Fail getting xml reader
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.getXmlReader", lambda *a: None)
        assert project.openProject(fncPath) is False

    # Not a novelwriter XML file
    with monkeypatch.context() as mp:
        mp.setattr(ProjectXMLReader, "read", lambda *a: False)
        mp.setattr(ProjectXMLReader, "state", property(lambda *a: XMLReadState.NOT_NWX_FILE))
        assert project.openProject(fncPath) is False
        lastMsg = SHARED.alert.logMessage if SHARED.alert else ""
        assert "Project file does not appear" in lastMsg

    # Unknown project file version
    with monkeypatch.context() as mp:
        mp.setattr(ProjectXMLReader, "read", lambda *a: False)
        mp.setattr(ProjectXMLReader, "state", property(lambda *a: XMLReadState.UNKNOWN_VERSION))
        assert project.openProject(fncPath) is False
        lastMsg = SHARED.alert.logMessage if SHARED.alert else ""
        assert "Unknown or unsupported novelWriter project file" in lastMsg

    # Other parse error
    with monkeypatch.context() as mp:
        mp.setattr(ProjectXMLReader, "read", lambda *a: False)
        mp.setattr(ProjectXMLReader, "state", property(lambda *a: XMLReadState.CANNOT_PARSE))
        assert project.openProject(fncPath) is False
        lastMsg = SHARED.alert.logMessage if SHARED.alert else ""
        assert "Failed to parse project xml" in lastMsg

    # Won't convert legacy file
    with monkeypatch.context() as mp:
        mp.setattr(ProjectXMLReader, "state", property(lambda *a: XMLReadState.WAS_LEGACY))
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.No)
        assert project.openProject(fncPath) is False
        lastMsg = SHARED.alert.logMessage if SHARED.alert else ""
        assert "The file format of your project is about to be" in lastMsg

    # Won't open project from newer version
    with monkeypatch.context() as mp:
        mp.setattr(ProjectXMLReader, "hexVersion", property(lambda *a: 0x99999999))
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.No)
        assert project.openProject(fncPath) is False
        lastMsg = SHARED.alert.logMessage if SHARED.alert else ""
        assert "This project was saved by a newer version" in lastMsg

    # Fail checking items should still pass
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.tree.NWTree.updateItemData", lambda *a: False)
        assert project.openProject(fncPath) is True

    project.closeProject()

    # Trigger an index rebuild
    with monkeypatch.context() as mp:
        mp.setattr(ProjectXMLReader, "state", property(lambda *a: XMLReadState.WAS_LEGACY))
        mp.setattr("novelwriter.core.index.NWIndex.loadIndex", lambda *a: True)
        project.index._indexBroken = True
        assert project.openProject(fncPath) is True
        lastMsg = SHARED.alert.logMessage if SHARED.alert else ""
        assert "The file format of your project is about to be" in lastMsg
        assert project.index._indexBroken is False

    project.closeProject()

# END Test testCoreProject_Open


@pytest.mark.core
def testCoreProject_Save(monkeypatch, mockGUI, mockRnd, fncPath):
    """Test saving a project."""
    project = NWProject()

    # Nothing to save
    assert project.saveProject() is False

    mockRnd.reset()
    buildTestProject(project, fncPath)

    # Fail getting xml writer
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.getXmlWriter", lambda *a: None)
        assert project.saveProject() is False

    # Fail writing
    with monkeypatch.context() as mp:
        mp.setattr(ProjectXMLWriter, "write", lambda *a: False)
        assert project.saveProject() is False

    # Save with and without autosave
    assert project.saveProject(autoSave=False) is True
    assert project.saveProject(autoSave=True) is True
    project.closeProject()

# END Test testCoreProject_Save


@pytest.mark.core
def testCoreProject_AccessItems(mockGUI, fncPath, mockRnd):
    """Test helper functions for the project folder."""
    project = NWProject()
    buildTestProject(project, fncPath)

    # Storage Objects
    assert isinstance(project.index, NWIndex)
    assert isinstance(project.tree, NWTree)
    assert isinstance(project.options, OptionState)

    # Move Novel ROOT to after its files
    oldOrder = [
        C.hNovelRoot,
        C.hPlotRoot,
        C.hCharRoot,
        C.hWorldRoot,
        C.hTitlePage,
        C.hChapterDir,
        C.hChapterDoc,
        C.hSceneDoc,
    ]
    newOrder = [
        C.hTitlePage,
        C.hChapterDoc,
        C.hSceneDoc,
        C.hChapterDir,
        C.hNovelRoot,
        C.hPlotRoot,
        C.hCharRoot,
        C.hWorldRoot,
    ]
    assert project.tree.handles() == oldOrder
    project.setTreeOrder(newOrder)
    assert project.tree.handles() == newOrder

    # Add a non-existing item
    project.tree._order.append(C.hInvalid)

    # Add an item with a non-existent parent
    nHandle = project.newFile("Test File", C.hChapterDir)
    project.tree[nHandle].setParent("cba9876543210")
    assert project.tree[nHandle].itemParent == "cba9876543210"

    retOrder = []
    for tItem in project.iterProjectItems():
        retOrder.append(tItem.itemHandle)

    assert retOrder == [
        C.hNovelRoot,
        C.hPlotRoot,
        C.hCharRoot,
        C.hWorldRoot,
        nHandle,
        C.hTitlePage,
        C.hChapterDir,
        C.hChapterDoc,
        C.hSceneDoc,
    ]
    assert project.tree[nHandle].itemParent is None

# END Test testCoreProject_AccessItems


@pytest.mark.core
def testCoreProject_StatusImport(mockGUI, fncPath, mockRnd):
    """Test the status and importance flag handling."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    statusKeys = [C.sNew, C.sNote, C.sDraft, C.sFinished]
    importKeys = [C.iNew, C.iMinor, C.iMajor, C.iMain]

    # Change Status
    # =============

    project.tree[C.hNovelRoot].setStatus(statusKeys[3])
    project.tree[C.hPlotRoot].setStatus(statusKeys[2])
    project.tree[C.hCharRoot].setStatus(statusKeys[1])
    project.tree[C.hWorldRoot].setStatus(statusKeys[3])

    assert project.tree[C.hNovelRoot].itemStatus == statusKeys[3]
    assert project.tree[C.hPlotRoot].itemStatus == statusKeys[2]
    assert project.tree[C.hCharRoot].itemStatus == statusKeys[1]
    assert project.tree[C.hWorldRoot].itemStatus == statusKeys[3]

    newList = [
        {"key": statusKeys[0], "name": "New", "cols": (1, 1, 1)},
        {"key": statusKeys[1], "name": "Draft", "cols": (2, 2, 2)},   # These are swapped
        {"key": statusKeys[2], "name": "Note", "cols": (3, 3, 3)},    # These are swapped
        {"key": statusKeys[3], "name": "Edited", "cols": (4, 4, 4)},  # Renamed
        {"key": None, "name": "Finished", "cols": (5, 5, 5)},         # New, reused name
    ]
    assert project.setStatusColours(None, None) is False
    assert project.setStatusColours([], []) is False
    assert project.setStatusColours(newList, []) is True

    assert project.data.itemStatus.name(statusKeys[0]) == "New"
    assert project.data.itemStatus.name(statusKeys[1]) == "Draft"
    assert project.data.itemStatus.name(statusKeys[2]) == "Note"
    assert project.data.itemStatus.name(statusKeys[3]) == "Edited"
    assert project.data.itemStatus.cols(statusKeys[0]) == (1, 1, 1)
    assert project.data.itemStatus.cols(statusKeys[1]) == (2, 2, 2)
    assert project.data.itemStatus.cols(statusKeys[2]) == (3, 3, 3)
    assert project.data.itemStatus.cols(statusKeys[3]) == (4, 4, 4)

    # Check the new entry
    lastKey = project.data.itemStatus.check("s000010")
    assert lastKey == "s000010"
    assert project.data.itemStatus.name(lastKey) == "Finished"
    assert project.data.itemStatus.cols(lastKey) == (5, 5, 5)

    # Delete last entry
    assert project.setStatusColours([], [lastKey]) is True
    assert project.data.itemStatus.name(lastKey) == "New"

    # Change Importance
    # =================

    fHandle = project.newFile("Jane Doe", C.hCharRoot)
    project.tree[fHandle].setImport(importKeys[3])

    assert project.tree[fHandle].itemImport == importKeys[3]
    newList = [
        {"key": importKeys[0], "name": "New", "cols": (1, 1, 1)},
        {"key": importKeys[1], "name": "Minor", "cols": (2, 2, 2)},
        {"key": importKeys[2], "name": "Major", "cols": (3, 3, 3)},
        {"key": importKeys[3], "name": "Min", "cols": (4, 4, 4)},
        {"key": None, "name": "Max", "cols": (5, 5, 5)},
    ]
    assert project.setImportColours(None, None) is False
    assert project.setImportColours([], []) is False
    assert project.setImportColours(newList, []) is True

    assert project.data.itemImport.name(importKeys[0]) == "New"
    assert project.data.itemImport.name(importKeys[1]) == "Minor"
    assert project.data.itemImport.name(importKeys[2]) == "Major"
    assert project.data.itemImport.name(importKeys[3]) == "Min"
    assert project.data.itemImport.cols(importKeys[0]) == (1, 1, 1)
    assert project.data.itemImport.cols(importKeys[1]) == (2, 2, 2)
    assert project.data.itemImport.cols(importKeys[2]) == (3, 3, 3)
    assert project.data.itemImport.cols(importKeys[3]) == (4, 4, 4)

    # Check the new entry
    lastKey = project.data.itemImport.check("i000012")
    assert lastKey == "i000012"
    assert project.data.itemImport.name(lastKey) == "Max"
    assert project.data.itemImport.cols(lastKey) == (5, 5, 5)

    # Delete last entry
    assert project.setImportColours([], [lastKey]) is True
    assert project.data.itemImport.name(lastKey) == "New"

    # Delete Status/Import
    # ====================

    project.data.itemStatus.resetCounts()
    for key in list(project.data.itemStatus.keys()):
        assert project.data.itemStatus.remove(key) is True

    project.data.itemImport.resetCounts()
    for key in list(project.data.itemImport.keys()):
        assert project.data.itemImport.remove(key) is True

    assert len(project.data.itemStatus) == 0
    assert len(project.data.itemImport) == 0
    assert project.saveProject() is True
    project.closeProject()

# END Test testCoreProject_StatusImport


@pytest.mark.core
def testCoreProject_Methods(monkeypatch, mockGUI, fncPath, mockRnd):
    """Test other project class methods and functions."""
    project = NWProject()
    buildTestProject(project, fncPath)

    # Project Name
    project.data.setName("  A Name ")
    assert project.data.name == "A Name"

    # Project Title
    project.data.setTitle("  A Title ")
    assert project.data.title == "A Title"

    # Project Author
    project.data.setAuthor("  Jane\tDoe ")
    assert project.data.author == "Jane Doe"

    # Edit Time
    project.data.setEditTime(1234)
    project._session._start = 1600000000
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.project.time", lambda: 1600005600)
        assert project.currentEditTime == 6834

    # Trash folder
    # Should create on first call, and just returned on later calls
    hTrash = "0000000000010"
    assert project.tree[hTrash] is None
    assert project.trashFolder() == hTrash
    assert project.trashFolder() == hTrash

    # Spell check
    project.setProjectChanged(False)
    project.data.setSpellCheck(True)
    project.data.setSpellCheck(False)
    assert project.projChanged is True
    assert project.projOpened > 0

    # Spell language
    project.setProjectChanged(False)
    assert project.data.spellLang is None
    project.data.setSpellLang(None)
    assert project.data.spellLang is None
    project.data.setSpellLang("None")  # Should be interpreted as None
    assert project.data.spellLang is None
    project.data.setSpellLang("en_GB")
    assert project.data.spellLang == "en_GB"
    assert project.projChanged is True

    # Project Language
    project.setProjectChanged(False)
    project.data.setLanguage("en")
    project.setProjectLang(None)
    assert project.data.language is None
    project.setProjectLang("en_GB")
    assert project.data.language == "en_GB"

    # Language Lookup
    assert project.localLookup(1) == "One"
    assert project.localLookup(10) == "Ten"

    # Set invalid language
    project.data.setLanguage("foo")
    project._loadProjectLocalisation()
    assert project.localLookup(1) == "One"
    assert project.localLookup(10) == "Ten"

    # Block reading language data
    project.data.setLanguage("en")
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        project._loadProjectLocalisation()
        assert project.localLookup(1) == "One"
        assert project.localLookup(10) == "Ten"

    # Last edited
    project.setProjectChanged(False)
    project._data.setLastHandle("0123456789abc", "editor")
    assert project._data.getLastHandle("editor") == "0123456789abc"
    assert project.projChanged

    # Last viewed
    project.setProjectChanged(False)
    project._data.setLastHandle("0123456789abc", "viewer")
    assert project._data.getLastHandle("viewer") == "0123456789abc"
    assert project.projChanged

    # Autoreplace
    project.setProjectChanged(False)
    project.data.setAutoReplace({"A": "B", "C": "D"})
    assert project.data.autoReplace == {"A": "B", "C": "D"}
    assert project.projChanged

    # Change project tree order
    oldOrder = [
        "0000000000008", "0000000000009", "000000000000a",
        "000000000000b", "000000000000c", "000000000000d",
        "000000000000e", "000000000000f", "0000000000010",
    ]
    newOrder = [
        "000000000000b", "000000000000c", "000000000000d",
        "0000000000008", "0000000000009", "000000000000a",
        "000000000000e", "000000000000f",
    ]
    assert project.tree.handles() == oldOrder
    project.setTreeOrder(newOrder)
    assert project.tree.handles() == newOrder
    project.setTreeOrder(oldOrder)
    assert project.tree.handles() == oldOrder

# END Test testCoreProject_Methods


@pytest.mark.core
def testCoreProject_Backup(monkeypatch, mockGUI, fncPath, tstPaths):
    """Test the automated backup feature of the project class. The test
    creates a backup of the Minimal test project, and then unzips the
    backup file and checks that the project XML file is identical to
    the original file.
    """
    project = NWProject()

    # No Project
    assert project.backupProject(doNotify=False) is False

    buildTestProject(project, fncPath)

    # Invalid Settings
    # ================

    # Missing project name
    CONFIG._backupPath = tstPaths.tmpDir
    project.data.setName("")
    assert project.backupProject(doNotify=False) is False

    # Valid Settings
    # ==============
    CONFIG._backupPath = tstPaths.tmpDir
    project.data.setName("Test Minimal")

    # Can't make folder
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.mkdir", causeOSError)
        assert project.backupProject(doNotify=False) is False

    # Can't write archive
    with monkeypatch.context() as mp:
        mp.setattr("zipfile.ZipFile.write", causeOSError)
        assert project.backupProject(doNotify=False) is False

    # Test correct settings
    assert project.backupProject(doNotify=True) is True

    theFiles = sorted((tstPaths.tmpDir / "Test Minimal").iterdir())
    assert len(theFiles) in (1, 2)  # Sometimes 2 due to clock tick

    theZip = theFiles[0]
    assert theZip.name.startswith("Test Minimal")
    assert theZip.suffix == ".nwproj"

    # Extract the archive
    with ZipFile(tstPaths.tmpDir / "Test Minimal" / theZip.name, mode="r") as inZip:
        inZip.extractall(tstPaths.tmpDir / "extract")

    # Check that the main project file was restored
    assert cmpFiles(
        fncPath / nwFiles.PROJ_FILE,
        tstPaths.tmpDir / "extract" / nwFiles.PROJ_ARCH
    )

# END Test testCoreProject_Backup
