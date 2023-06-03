"""
novelWriter – NWStorage Class Tester
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

from zipfile import ZipFile
import pytest

from mocked import causeOSError
from tools import C, buildTestProject, writeFile

from novelwriter import CONFIG
from novelwriter.constants import nwFiles
from novelwriter.core.project import NWProject
from novelwriter.core.storage import NWStorage
from novelwriter.core.projectxml import ProjectXMLReader, ProjectXMLWriter


class MockProject:
    pass


@pytest.mark.core
def testCoreStorage_OpenProjectInPlace(mockGUI, fncPath, mockRnd):
    """Test opening a project in a folder.
    """
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncPath)
    theProject.closeProject()

    # Create instance
    storage = NWStorage(theProject)

    # Check defaults
    assert storage.storagePath is None
    assert storage.runtimePath is None
    assert storage.contentPath is None
    assert storage._openMode == NWStorage.MODE_INACTIVE

    # Check closed project return values
    assert storage.isOpen() is False
    assert storage.getXmlReader() is None
    assert storage.getXmlWriter() is None
    assert bool(storage.getDocument(C.hSceneDoc)) is False
    assert storage.getMetaFile("file") is None
    assert storage.getCacheFile("file") is None

    # Open project as a new project should fail
    assert storage.openProjectInPlace(fncPath, newProject=True) is False

    # Opening as a non-new project is fine
    assert storage.openProjectInPlace(fncPath, newProject=False) is True

    # Opening the project file is also fine
    assert storage.openProjectInPlace(fncPath / nwFiles.PROJ_FILE, newProject=False) is True

    # Opening as a non-new project on a non-existing folder should fail
    assert storage.openProjectInPlace(fncPath / "foobar", newProject=False) is False

    # Check settings
    assert storage.storagePath == fncPath
    assert storage.runtimePath == fncPath
    assert storage.contentPath == fncPath / "content"
    assert storage._openMode == NWStorage.MODE_INPLACE

    # Open the project itself
    theProject.openProject(fncPath)
    storage = theProject.storage

    # Get XML components
    assert isinstance(storage.getXmlReader(), ProjectXMLReader)
    assert isinstance(storage.getXmlWriter(), ProjectXMLWriter)

    # Get document
    assert storage.getDocument(C.hSceneDoc).readDocument() == "### New Scene\n\n"

    # Get paths
    assert storage.getMetaFile("stuff") == fncPath / "meta" / "stuff"
    assert storage.getCacheFile("stuff") == fncPath / "cache" / "stuff"

    # Clean up
    assert theProject.closeProject() is True

    # Check closed project return values (again)
    assert storage.isOpen() is False
    assert storage.getXmlReader() is None
    assert storage.getXmlWriter() is None
    assert bool(storage.getDocument(C.hSceneDoc)) is False
    assert storage.getMetaFile("file") is None
    assert storage.getCacheFile("file") is None

# END Test testCoreStorage_ProjectInPlace


@pytest.mark.core
def testCoreStorage_LockFile(monkeypatch, fncPath):
    """Test the project lock file.
    """
    monkeypatch.setattr("novelwriter.core.storage.time", lambda: 1000.0)

    storage = NWStorage(MockProject())
    assert storage.isOpen() is False

    # Project not open, so cannot read/write lock file
    assert storage.readLockFile() == ["ERROR"]
    assert storage.writeLockFile() is False
    assert storage.clearLockFile() is False

    # Set a path to work with
    lockFilePath = fncPath / nwFiles.PROJ_LOCK
    storage._lockFilePath = lockFilePath

    # Path is set, but there is no lockfile
    assert storage.readLockFile() == []

    # Write lockfile fails
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.write_text", causeOSError)
        assert storage.writeLockFile() is False
        assert not lockFilePath.exists()

    # Successful write
    assert storage.writeLockFile() is True
    assert lockFilePath.exists()
    assert lockFilePath.read_text().split(";")[3] == "1000"

    # Read lockfile fails
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.read_text", causeOSError)
        assert storage.readLockFile() == ["ERROR"]
        assert lockFilePath.exists()

    # Successful read
    assert storage.readLockFile() == [
        CONFIG.hostName,
        CONFIG.osType,
        CONFIG.kernelVer,
        "1000",
    ]

    # Write an invalid lockfile
    writeFile(lockFilePath, "a;b;c")
    assert storage.readLockFile() == ["ERROR"]

    # Fail to remove lockfile
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.unlink", causeOSError)
        assert storage.clearLockFile() is False
        assert lockFilePath.exists()

    # Successful remove
    assert storage.clearLockFile() is True
    assert not lockFilePath.exists()

# END Test testCoreStorage_LockFile


@pytest.mark.core
def testCoreStorage_PrepareStorage(monkeypatch, fncPath):
    """Test the project path preparation functions.
    """
    storage = NWStorage(MockProject())
    assert storage.isOpen() is False

    # No path set
    assert storage._prepareStorage() is False

    # Set path to home
    storage._runtimePath = fncPath
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.home", lambda: fncPath)
        assert storage._prepareStorage() is False

    # Fail on mkdir
    storage._runtimePath = fncPath
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.mkdir", causeOSError)
        assert storage._prepareStorage() is False

    # Set up the folder
    storage._runtimePath = fncPath
    assert storage._prepareStorage(checkLegacy=False) is True
    assert (fncPath / "content").exists()
    assert (fncPath / "cache").exists()
    assert (fncPath / "meta").exists()

    # Add a legacy folder
    storage._runtimePath = fncPath
    dataDir = fncPath / "data_0"
    dataDir.mkdir()
    assert storage._prepareStorage(checkLegacy=True) is True
    assert not dataDir.exists()

    # We cannot add a new project here
    storage._runtimePath = fncPath
    assert storage._prepareStorage(checkLegacy=False, newProject=True) is False

    # Legacy Data Folder
    # ==================
    storage._runtimePath = fncPath

    data = []
    files = []
    for c in "0123456789abcdefX":
        dataDir = fncPath / f"data_{c}"
        dataDir.mkdir()
        data.append(dataDir)

        nwdFile = dataDir / f"00000000000{c}_main.nwd"
        bakFile = dataDir / f"00000000000{c}_main.bak"
        nwdFile.write_text("#")
        bakFile.write_text("#")
        files.append(nwdFile)
        files.append(bakFile)

    for item in files:
        assert item.exists()

    # Pollute folder 7 and 8
    (data[7] / "stuff.txt").write_text("foo")
    (data[8] / "bar").mkdir()

    # Process folders
    for i in range(9):
        storage._legacyDataFolder(fncPath, data[i])

    # Files form 0 to 8 should now be in content
    for c in "012345678":
        assert (fncPath / "content" / f"{c}00000000000{c}.nwd").exists()

    # Folders 0 to 6 should be deleted
    for i in range(7):
        assert not data[i].exists()

    # While 7 and 8 remain
    assert data[7].exists()
    assert data[8].exists()

    # So does folder X, which is invalid
    storage._legacyDataFolder(fncPath, data[16])
    assert data[16].exists()

    # Fail cleanup of folder 9
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.rename", causeOSError)
        mp.setattr("pathlib.Path.unlink", causeOSError)
        storage._legacyDataFolder(fncPath, data[9])
        assert data[9].exists()
        assert not (fncPath / "content" / "9000000000009.nwd").exists()

    # Run the remaining through the prepare storage call
    assert storage._prepareStorage(checkLegacy=True) is True
    for c in "0123456789abcdef":
        assert (fncPath / "content" / f"{c}00000000000{c}.nwd").exists()

    # Deprecated Files
    # ================

    remove = [
        fncPath / "meta" / "mainOptions.json",
        fncPath / "meta" / "exportOptions.json",
        fncPath / "meta" / "outlineOptions.json",
        fncPath / "meta" / "timelineOptions.json",
        fncPath / "meta" / "docMergeOptions.json",
        fncPath / "meta" / "sessionLogOptions.json",
        fncPath / "ToC.json",
    ]
    for depFile in remove:
        depFile.write_text("foo")
        assert depFile.exists()

    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.unlink", causeOSError)
        storage._deleteDeprecatedFiles(fncPath)
        for depFile in remove:
            assert depFile.exists()

    storage._deleteDeprecatedFiles(fncPath)
    for depFile in remove:
        assert not depFile.exists()

# END Test testCoreStorage_PrepareStorage


@pytest.mark.core
def testCoreStorage_ZipIt(monkeypatch, mockGUI, fncPath, tstPaths, mockRnd):
    """Test making a zip archive of a project.
    """
    zipFile = tstPaths.tmpDir / "project.zip"

    theProject = NWProject(mockGUI)
    storage = theProject.storage
    assert storage.zipIt(zipFile) is False

    # Make a project
    mockRnd.reset()
    buildTestProject(theProject, fncPath)

    # Fail to create archive
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.ZipFile.write", causeOSError)
        assert storage.zipIt(zipFile) is False

    # Create archive
    assert storage.zipIt(zipFile) is True

    # Check content
    with ZipFile(zipFile, mode="r") as archive:
        names = archive.namelist()
        assert nwFiles.PROJ_FILE in names
        assert f"meta/{nwFiles.OPTS_FILE}" in names
        assert f"meta/{nwFiles.INDEX_FILE}" in names
        assert f"content/{C.hTitlePage}.nwd" in names
        assert f"content/{C.hChapterDoc}.nwd" in names
        assert f"content/{C.hSceneDoc}.nwd" in names

    theProject.closeProject()

# END Test testCoreStorage_ZipIt
