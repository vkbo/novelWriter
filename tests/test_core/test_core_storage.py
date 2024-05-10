"""
novelWriter – NWStorage Class Tester
====================================

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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
from __future__ import annotations

import json

from pathlib import Path
from zipfile import ZipFile

import pytest

from novelwriter import CONFIG
from novelwriter.constants import nwFiles
from novelwriter.core.document import NWDocument
from novelwriter.core.project import NWProject
from novelwriter.core.projectxml import ProjectXMLReader, ProjectXMLWriter
from novelwriter.core.storage import NWStorage, NWStorageCreate, NWStorageOpen, _LegacyStorage

from tests.mocked import causeOSError
from tests.tools import C, buildTestProject


class MockProject:
    """Test class for projects."""
    pass


@pytest.mark.core
def testCoreStorage_CreateNewProject(mockGUI, fncPath):
    """Test creating a project in a folder."""
    project = NWProject()

    # Create instance
    storage = NWStorage(project)

    # Check defaults
    assert storage.storagePath is None
    assert storage.runtimePath is None
    assert storage.contentPath is None
    assert storage._openMode == NWStorage.MODE_INACTIVE
    assert storage._ready is False

    # Check closed project return values
    assert storage.isOpen() is False
    assert storage.getXmlReader() is None
    assert storage.getXmlWriter() is None
    assert bool(storage.getDocument(C.hSceneDoc)) is False
    assert storage.getMetaFile("file") is None
    assert storage.scanContent() == []
    assert storage.getDocumentText(C.hSceneDoc) == ""

    # Cannot prepare a non-empty folder
    (fncPath / "foobar.txt").touch()
    assert storage.createNewProject(fncPath) == NWStorageCreate.NOT_EMPTY

    # Try creating in a non-existent subfolder instead
    assert storage.createNewProject(fncPath / "project1") == NWStorageCreate.READY
    assert (fncPath / "project1").is_dir()
    assert (fncPath / "project1" / "meta").is_dir()
    assert (fncPath / "project1" / "content").is_dir()

    # However, the parent folder must exist
    assert storage.createNewProject(fncPath / "foobar" / "project1") == NWStorageCreate.OS_ERROR
    assert isinstance(storage.exc, FileNotFoundError)

    project.closeProject()


@pytest.mark.core
def testCoreStorage_InitProjectStorage(monkeypatch, mockGUI, fncPath, mockRnd):
    """Test initialising a project in a folder."""
    project = NWProject()

    # Create instance
    storage = NWStorage(project)

    # Check defaults
    assert storage.storagePath is None
    assert storage.runtimePath is None
    assert storage.contentPath is None
    assert storage._openMode == NWStorage.MODE_INACTIVE
    assert storage._ready is False

    # Check closed project return values
    assert storage.isOpen() is False
    assert storage.getXmlReader() is None
    assert storage.getXmlWriter() is None
    assert bool(storage.getDocument(C.hSceneDoc)) is False
    assert storage.getMetaFile("file") is None
    assert storage.scanContent() == []

    # Create a new project
    buildTestProject(project, fncPath)

    # Init with the wrong file
    foo = fncPath / "foobar.txt"
    foo.touch()
    assert storage.initProjectStorage(fncPath / "foobar.txt") == NWStorageOpen.UNKOWN
    foo.unlink()
    storage._clearLockFile()
    storage.clear()

    # Init with the user's home dir
    assert storage.initProjectStorage(Path.home()) == NWStorageOpen.NOT_FOUND
    storage._clearLockFile()
    storage.clear()

    # Init with the project folder is OK
    assert storage.initProjectStorage(fncPath) == NWStorageOpen.READY
    assert storage.runtimePath == fncPath
    assert storage.storagePath == fncPath
    assert storage.contentPath == fncPath / "content"
    assert storage._openMode == NWStorage.MODE_INPLACE
    storage._clearLockFile()
    storage.clear()

    # Init with the project main file is OK
    assert storage.initProjectStorage(fncPath / nwFiles.PROJ_FILE) == NWStorageOpen.READY
    assert storage.runtimePath == fncPath
    assert storage.storagePath == fncPath
    assert storage.contentPath == fncPath / "content"
    assert storage._openMode == NWStorage.MODE_INPLACE
    storage._clearLockFile()
    storage.clear()

    # Open twice, where second should fail due to lockfile
    assert storage.initProjectStorage(fncPath) == NWStorageOpen.READY
    assert storage.initProjectStorage(fncPath) == NWStorageOpen.LOCKED
    assert isinstance(storage.lockStatus, list)
    assert len(storage.lockStatus) == 4

    # But open again with clear lock file flag set is OK
    assert storage.initProjectStorage(fncPath, clearLock=True) == NWStorageOpen.READY
    assert storage.lockStatus is None

    # We should now have access to project resources
    assert isinstance(storage.getXmlReader(), ProjectXMLReader)
    assert isinstance(storage.getXmlWriter(), ProjectXMLWriter)
    assert isinstance(storage.getDocument(C.hSceneDoc), NWDocument)
    assert repr(storage.getDocument(C.hSceneDoc)) == f"<NWDocument handle={C.hSceneDoc}>"

    # We can directly access the content of a document
    assert storage.getDocumentText(C.hSceneDoc) == "### New Scene\n\n"

    project.closeProject()


@pytest.mark.core
def testCoreStorage_InitProjectStorage_Invalid(mockGUI, fncPath):
    """Test initialising a project in an invalid folder."""
    project = NWProject()

    # Create instance
    storage = NWStorage(project)

    # Check defaults
    assert storage.storagePath is None
    assert storage.runtimePath is None
    assert storage.contentPath is None
    assert storage._openMode == NWStorage.MODE_INACTIVE
    assert storage._ready is False

    # Check closed project return values
    assert storage.isOpen() is False
    assert storage.getXmlReader() is None
    assert storage.getXmlWriter() is None
    assert bool(storage.getDocument(C.hSceneDoc)) is False
    assert storage.getMetaFile("file") is None
    assert storage.scanContent() == []

    # Populate folder with invalid files
    (fncPath / "meta").touch()  # These are now files but should be folders
    (fncPath / "content").touch()  # These are now files but should be folders

    # Try opening the folder, but there is no project file
    assert storage.initProjectStorage(fncPath) == NWStorageOpen.NOT_FOUND

    # Add the project file, and we should now fail on the folders
    (fncPath / nwFiles.PROJ_FILE).touch()
    assert storage.initProjectStorage(fncPath) == NWStorageOpen.FAILED

    project.closeProject()


@pytest.mark.core
def testCoreStorage_LockFile(monkeypatch, fncPath):
    """Test the project lock file."""
    monkeypatch.setattr("novelwriter.core.storage.time", lambda: 1000.0)

    storage = NWStorage(MockProject())  # type: ignore
    assert storage.isOpen() is False

    # Project not open, so cannot read/write lock file
    assert storage._readLockFile() is None
    assert storage._writeLockFile() is False
    assert storage._clearLockFile() is False

    # Set a path to work with
    lockFilePath = fncPath / nwFiles.PROJ_LOCK
    storage._lockFilePath = lockFilePath

    # Path is set, but there is no lockfile
    storage._readLockFile()
    assert storage.lockStatus is None

    # Write lockfile fails
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.write_text", causeOSError)
        assert storage._writeLockFile() is False
        assert not lockFilePath.exists()

    # Successful write
    assert storage._writeLockFile() is True
    assert lockFilePath.exists()
    assert lockFilePath.read_text().split(";")[3] == "1000"

    # Read lockfile fails
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.read_text", causeOSError)
        storage._readLockFile()
        assert storage.lockStatus == ["ERROR", "ERROR", "ERROR", "ERROR"]
        assert lockFilePath.exists()

    # Successful read
    storage._readLockFile()
    assert storage.lockStatus == [
        CONFIG.hostName, CONFIG.osType, CONFIG.kernelVer, "1000",
    ]

    # Write an invalid lockfile
    lockFilePath.write_text("a;b;c")
    storage._readLockFile()
    assert storage.lockStatus is None

    # Fail to remove lockfile
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.unlink", causeOSError)
        assert storage._clearLockFile() is False
        assert lockFilePath.exists()

    # Successful remove
    assert storage._clearLockFile() is True
    assert not lockFilePath.exists()


@pytest.mark.core
def testCoreStorage_ZipIt(monkeypatch, mockGUI, fncPath, tstPaths, mockRnd):
    """Test making a zip archive of a project."""
    zipFile = tstPaths.tmpDir / "project.zip"

    project = NWProject()
    storage = project.storage
    assert storage.zipIt(zipFile) is False

    # Make a project
    mockRnd.reset()
    buildTestProject(project, fncPath)

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

    project.closeProject()


@pytest.mark.core
def testCoreStorage_LegacyDataFolder(monkeypatch, fncPath):
    """Test project file format 1.0 folder structure conversion."""
    project = MockProject()
    storage = NWStorage(project)  # type: ignore
    assert storage.isOpen() is False
    storage._runtimePath = fncPath
    (fncPath / nwFiles.PROJ_FILE).touch()
    storage.initProjectStorage(fncPath)
    legacy = _LegacyStorage(project)  # type: ignore

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
        legacy.legacyDataFolder(fncPath, data[i])

    # Files form 0 to 8 should now be in content
    for i in range(9):
        assert (fncPath / "content" / f"{i}00000000000{i}.nwd").exists()

    # Folders 0 to 6 should be deleted
    for i in range(7):
        assert not data[i].exists()

    # While 7 and 8 remain
    assert data[7].exists()
    assert data[8].exists()

    # So does folder X, which is invalid
    legacy.legacyDataFolder(fncPath, data[16])
    assert data[16].exists()

    # Fail cleanup of folder 9
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.rename", causeOSError)
        mp.setattr("pathlib.Path.unlink", causeOSError)
        legacy.legacyDataFolder(fncPath, data[9])
        assert data[9].exists()
        assert not (fncPath / "content" / "9000000000009.nwd").exists()

    # Run the remaining through the prepare storage call
    assert storage.initProjectStorage(fncPath, clearLock=True) == NWStorageOpen.READY
    for c in "0123456789abcdef":
        assert (fncPath / "content" / f"{c}00000000000{c}.nwd").exists()


@pytest.mark.core
def testCoreStorage_DeprecatedFiles(monkeypatch, fncPath):
    """Test cleanup of deprecated files."""
    project = MockProject()
    storage = NWStorage(project)  # type: ignore
    assert storage.isOpen() is False
    storage._runtimePath = fncPath
    (fncPath / nwFiles.PROJ_FILE).touch()
    storage.initProjectStorage(fncPath)
    legacy = _LegacyStorage(project)  # type: ignore

    # Files/Folders to be Deleted or Renamed
    # ======================================

    remove = [
        fncPath / "meta" / "tagsIndex.json",
        fncPath / "meta" / "mainOptions.json",
        fncPath / "meta" / "exportOptions.json",
        fncPath / "meta" / "outlineOptions.json",
        fncPath / "meta" / "timelineOptions.json",
        fncPath / "meta" / "docMergeOptions.json",
        fncPath / "meta" / "sessionLogOptions.json",
        fncPath / "cache" / "prevBuild.json",
        fncPath / "ToC.json",
    ]
    (fncPath / "cache").mkdir()
    for depFile in remove:
        depFile.write_text("foo")
        assert depFile.exists()

    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.unlink", causeOSError)
        legacy.deprecatedFiles(fncPath)
        for depFile in remove:
            assert depFile.exists()

    legacy.deprecatedFiles(fncPath)
    for depFile in remove:
        assert not depFile.exists()


@pytest.mark.core
def testCoreStorage_OldFormatConvert(monkeypatch, mockGUI, fncPath):
    """Test cleanup of deprecated files that needs to be converted."""
    project = NWProject()
    buildTestProject(project, fncPath)
    legacy = _LegacyStorage(project)

    # The build project functions saves the project, so we must delete
    # the old gui options file
    (fncPath / "meta" / nwFiles.OPTS_FILE).unlink()

    # Word List
    wordListOld: Path = fncPath / "meta" / "wordlist.txt"
    wordListNew: Path = fncPath / "meta" / nwFiles.DICT_FILE

    wordListOld.write_text((
        "word_a\n"
        "word_b\n"
        "word_c\n"
    ), encoding="utf-8")

    assert wordListOld.exists() is True
    assert wordListNew.exists() is False

    # Log File
    sessLogOld: Path = fncPath / "meta" / "sessionStats.log"
    sessLogNew: Path = fncPath / "meta" / nwFiles.SESS_FILE

    sessLogOld.write_text((
        "# Offset 150\n"
        "# Start Time         End Time                Novel     Notes    Idle\n"
        "2021-02-02 02:02:02  2021-02-02 03:03:03       200      200       10\n"
        "2021-03-03 03:03:03  2021-03-03 04:04:04       300      300       20\n"
    ), encoding="utf-8")

    assert sessLogOld.exists() is True
    assert sessLogNew.exists() is False

    # Options File
    optionsOld: Path = fncPath / "meta" / "guiOptions.json"
    optionsNew: Path = fncPath / "meta" / nwFiles.OPTS_FILE

    optionsOld.write_text(json.dumps({
        "GuiProjectSettings": {
            "winWidth": 570,
            "winHeight": 375,
        },
        "GuiOutline": {
            "headerOrder": ["TITLE", "LEVEL", "LABEL", "LINE"],
            "columnWidth": {"TITLE": 325, "LEVEL": 40, "LABEL": 267, "LINE": 40},
            "columnHidden": {"TITLE": False, "LEVEL": True, "LABEL": False, "LINE": True},
        },
    }, indent=2), encoding="utf-8")

    assert optionsOld.exists() is True
    assert optionsNew.exists() is False

    # Check Failure
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        legacy.deprecatedFiles(fncPath)
        assert wordListOld.exists() is True
        assert wordListNew.exists() is False
        assert sessLogOld.exists() is True
        assert sessLogNew.exists() is False
        assert optionsOld.exists() is True
        assert optionsNew.exists() is False

    # Check Success
    legacy.deprecatedFiles(fncPath)
    assert wordListOld.exists() is False
    assert wordListNew.exists() is True
    assert sessLogOld.exists() is False
    assert sessLogNew.exists() is True
    assert optionsOld.exists() is False
    assert optionsNew.exists() is True

    # Check Word List
    data = json.loads(wordListNew.read_text(encoding="utf-8"))
    assert "word_a" in data["novelWriter.userDict"]
    assert "word_b" in data["novelWriter.userDict"]
    assert "word_c" in data["novelWriter.userDict"]

    # Check Session Log
    data = list(project.session.iterRecords())
    assert data[0] == {"type": "initial", "offset": 150}
    assert data[1] == {
        "type": "record",
        "start": "2021-02-02 02:02:02",
        "end": "2021-02-02 03:03:03",
        "novel": 200,
        "notes": 200,
        "idle": 10,
    }
    assert data[2] == {
        "type": "record",
        "start": "2021-03-03 03:03:03",
        "end": "2021-03-03 04:04:04",
        "novel": 300,
        "notes": 300,
        "idle": 20,
    }

    # Check Options File
    data = json.loads(optionsNew.read_text(encoding="utf-8"))
    assert data["novelWriter.guiOptions"]["GuiProjectSettings"] == {
        "winWidth": 570, "winHeight": 375
    }
    assert data["novelWriter.guiOptions"]["GuiOutline"]["columnState"] == {
        "TITLE": [False, 325],
        "LEVEL": [True, 40],
        "LABEL": [False, 267],
        "LINE": [True, 40]
    }
