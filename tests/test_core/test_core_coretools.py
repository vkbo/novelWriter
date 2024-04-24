"""
novelWriter – Project Document Tools Tester
===========================================

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

import shutil
import uuid

from pathlib import Path
from shutil import copyfile
from zipfile import ZipFile

import pytest

from novelwriter import CONFIG
from novelwriter.constants import nwConst, nwFiles, nwItemClass
from novelwriter.core.coretools import (
    DocDuplicator, DocMerger, DocSearch, DocSplitter, ProjectBuilder
)
from novelwriter.core.project import NWProject

from tests.mocked import causeOSError
from tests.tools import NWD_IGNORE, XML_IGNORE, C, buildTestProject, cmpFiles


@pytest.mark.core
def testCoreTools_DocMerger(monkeypatch, mockGUI, fncPath, tstPaths, mockRnd, ipsumText):
    """Test the DocMerger utility."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    # Create Files to Merge
    # =====================

    hChapter1 = project.newFile("Chapter 1", C.hNovelRoot)
    hSceneOne11 = project.newFile("Scene 1.1", hChapter1)  # type: ignore
    hSceneOne12 = project.newFile("Scene 1.2", hChapter1)  # type: ignore
    hSceneOne13 = project.newFile("Scene 1.3", hChapter1)  # type: ignore

    docText1 = "\n\n".join(ipsumText[0:2]) + "\n\n"
    docText2 = "\n\n".join(ipsumText[1:3]) + "\n\n"
    docText3 = "\n\n".join(ipsumText[2:4]) + "\n\n"
    docText4 = "\n\n".join(ipsumText[3:5]) + "\n\n"

    project.writeNewFile(hChapter1, 2, True, docText1)  # type: ignore
    project.writeNewFile(hSceneOne11, 3, True, docText2)  # type: ignore
    project.writeNewFile(hSceneOne12, 3, True, docText3)  # type: ignore
    project.writeNewFile(hSceneOne13, 3, True, docText4)  # type: ignore

    # Basic Checks
    # ============

    docMerger = DocMerger(project)

    # No writing without a target set
    assert docMerger.writeTargetDoc() is False

    # Cannot append invalid handle
    assert docMerger.appendText(C.hInvalid, True, "Merge") is False

    # Cannot create new target from invalid handle
    assert docMerger.newTargetDoc(C.hInvalid, "Test") is None

    # Merge to New
    # ============

    saveFile = fncPath / "content" / "0000000000014.nwd"
    testFile = tstPaths.outDir / "coreDocTools_DocMerger_0000000000014.nwd"
    compFile = tstPaths.refDir / "coreDocTools_DocMerger_0000000000014.nwd"

    assert docMerger.newTargetDoc(hChapter1, "All of Chapter 1") == "0000000000014"  # type: ignore

    assert docMerger.appendText(hChapter1, True, "Merge") is True  # type: ignore
    assert docMerger.appendText(hSceneOne11, True, "Merge") is True  # type: ignore
    assert docMerger.appendText(hSceneOne12, True, "Merge") is True  # type: ignore
    assert docMerger.appendText(hSceneOne13, True, "Merge") is True  # type: ignore

    # Block writing and check error handling
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert docMerger.writeTargetDoc() is False
        assert not saveFile.exists()
        assert docMerger.getError() != ""

    # Write properly, and compare
    assert docMerger.writeTargetDoc() is True
    copyfile(saveFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=NWD_IGNORE)

    # Merge into Existing
    # ===================

    saveFile = fncPath / "content" / "0000000000010.nwd"
    testFile = tstPaths.outDir / "coreDocTools_DocMerger_0000000000010.nwd"
    compFile = tstPaths.refDir / "coreDocTools_DocMerger_0000000000010.nwd"

    docMerger.setTargetDoc(hChapter1)  # type: ignore

    assert docMerger.appendText(hSceneOne11, True, "Merge") is True  # type: ignore
    assert docMerger.appendText(hSceneOne12, True, "Merge") is True  # type: ignore
    assert docMerger.appendText(hSceneOne13, True, "Merge") is True  # type: ignore

    assert docMerger.writeTargetDoc() is True
    copyfile(saveFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=NWD_IGNORE)

    # Just for debugging
    docMerger.writeTargetDoc()

# END Test testCoreTools_DocMerger


@pytest.mark.core
def testCoreTools_DocSplitter(monkeypatch, mockGUI, fncPath, mockRnd, ipsumText):
    """Test the DocSplitter utility."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    # Create File to Split
    # ====================

    hSplitDoc = project.newFile("Split Doc", C.hNovelRoot)

    docData = [
        "# Part One", ipsumText[0],
        "## Chapter One", ipsumText[1],
        "### Scene One", ipsumText[2],
        "#### Section One", ipsumText[3],
        "#### Section Two", ipsumText[4],
        "### Scene Two", ipsumText[0],
        "## Chapter Two", ipsumText[1],
        "### Scene Three", ipsumText[2],
        "### Scene Four", ipsumText[3],
        "### Scene Five", ipsumText[4],
    ]
    splitData = [
        (0, 1,  "Part One"),
        (4, 2,  "Chapter One"),
        (8, 3,  "Scene One"),
        (12, 4, "Section One"),
        (16, 4, "Section Two"),
        (20, 3, "Scene Two"),
        (24, 2, "Chapter Two"),
        (28, 3, "Scene Three"),
        (32, 3, "Scene Four"),
        (36, 3, "Scene Five"),
    ]

    docText = "\n\n".join(docData)
    docRaw = docText.splitlines()
    assert project.storage.getDocument(hSplitDoc).writeDocument(docText) is True
    project.tree[hSplitDoc].setStatus(C.sFinished)  # type: ignore
    project.tree[hSplitDoc].setImport(C.iMain)  # type: ignore

    docSplitter = DocSplitter(project, hSplitDoc)  # type: ignore
    assert docSplitter._srcItem.isFileType()  # type: ignore
    assert docSplitter.getError() == ""

    # Run the split algorithm
    docSplitter.splitDocument(splitData, docRaw)  # type: ignore
    for i, (lineNo, hLevel, hLabel) in enumerate(splitData):
        assert docSplitter._rawData[i] == (docRaw[lineNo:lineNo+4], hLevel, hLabel)

    # Test flat split into same parent
    docSplitter.setParentItem(C.hNovelRoot)
    assert docSplitter._inFolder is False

    # Cause write error on all chunks
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        resStatus = []
        for status, _, _ in docSplitter.writeDocuments(False):
            resStatus.append(status)
        assert not any(resStatus)
        assert docSplitter.getError() == "OSError: Mock OSError"

    # Generate as flat structure in root folder
    resStatus = []
    resDocHandle = []
    resNearHandle = []
    for status, dHandle, nHandle in docSplitter.writeDocuments(False):
        resStatus.append(status)
        resDocHandle.append(dHandle)
        resNearHandle.append(nHandle)

    assert all(resStatus)
    assert resDocHandle == [
        "000000000001b", "000000000001c", "000000000001d", "000000000001e", "000000000001f",
        "0000000000020", "0000000000021", "0000000000022", "0000000000023", "0000000000024",
    ]
    assert resNearHandle == [  # Each document should be next to the previous one
        hSplitDoc,       "000000000001b", "000000000001c", "000000000001d", "000000000001e",
        "000000000001f", "0000000000020", "0000000000021", "0000000000022", "0000000000023",
    ]

    # Generate as hierarchy in new folder
    hSplitFolder = docSplitter.newParentFolder(C.hNovelRoot, "Split Folder")
    assert docSplitter._inFolder is True

    resStatus = []
    resDocHandle = []
    resNearHandle = []
    for status, dHandle, nHandle in docSplitter.writeDocuments(True):
        resStatus.append(status)
        resDocHandle.append(dHandle)
        resNearHandle.append(nHandle)

    assert all(resStatus)
    assert resDocHandle == [
        "0000000000026",  # Part One
        "0000000000027",  # Chapter One
        "0000000000028",  # Scene One
        "0000000000029",  # Section One
        "000000000002a",  # Section Two
        "000000000002b",  # Scene Two
        "000000000002c",  # Chapter Two
        "000000000002d",  # Scene Three
        "000000000002e",  # Scene Four
        "000000000002f",  # Scene Five
    ]
    assert resNearHandle == [
        hSplitFolder,     # Part One is after Split Folder
        "0000000000026",  # Chapter One is after Part One
        "0000000000027",  # Scene One is after Chapter One
        "0000000000028",  # Section One is after Scene One
        "0000000000029",  # Section Two is after Section One
        "0000000000028",  # Scene Two is after Scene One
        "0000000000027",  # Chapter Two is after Chapter One
        "000000000002c",  # Scene Three is after Chapter Two
        "000000000002d",  # Scene Four is after Scene Three
        "000000000002e",  # Scene Five is after Scene Four
    ]

    # Check that status and importance has been preserved
    for rHandle in resDocHandle:
        assert project.tree[rHandle].itemStatus == C.sFinished  # type: ignore
        assert project.tree[rHandle].itemImport == C.iMain  # type: ignore

    # Check handling of improper initialisation
    docSplitter = DocSplitter(project, C.hInvalid)
    assert docSplitter._srcHandle is None
    assert docSplitter._srcItem is None
    assert docSplitter.newParentFolder(C.hNovelRoot, "Split Folder") is None
    assert list(docSplitter.writeDocuments(False)) == []

    project.saveProject()

# END Test testCoreTools_DocSplitter


@pytest.mark.core
def testCoreTools_DocDuplicator(mockGUI, fncPath, tstPaths, mockRnd):
    """Test the DocDuplicator utility."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    dup = DocDuplicator(project)

    ttText = "#! New Novel\n\n>> By Jane Doe <<\n"
    chText = "## New Chapter\n\n"
    scText = "### New Scene\n\n"

    # Check document content
    assert project.storage.getDocument(C.hTitlePage).readDocument() == ttText
    assert project.storage.getDocument(C.hChapterDoc).readDocument() == chText
    assert project.storage.getDocument(C.hSceneDoc).readDocument() == scText

    # Nothing to do
    assert list(dup.duplicate([])) == []

    # Single Document
    # ===============

    # A new copy is created
    assert list(dup.duplicate([C.hSceneDoc])) == [
        ("0000000000010", C.hSceneDoc),  # The Scene
    ]
    assert project.tree._order == [
        C.hNovelRoot, C.hPlotRoot, C.hCharRoot, C.hWorldRoot,
        C.hTitlePage, C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010",
    ]

    # With the same content
    assert project.storage.getDocument("0000000000010").readDocument() == scText

    # They should have the same parent
    assert project.tree["0000000000010"].itemParent == C.hChapterDir  # type: ignore

    # Folder w/Two Files
    # ==================

    # The folder is copied, with two docs
    assert list(dup.duplicate([C.hChapterDir, C.hChapterDoc, C.hSceneDoc])) == [
        ("0000000000011", C.hChapterDir),  # The Folder
        ("0000000000012", None),           # The Chapter
        ("0000000000013", None),           # The Scene
    ]
    assert project.tree._order == [
        C.hNovelRoot, C.hPlotRoot, C.hCharRoot, C.hWorldRoot,
        C.hTitlePage, C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010",
        "0000000000011", "0000000000012", "0000000000013",
    ]

    # With the same content
    assert project.storage.getDocument("0000000000012").readDocument() == chText
    assert project.storage.getDocument("0000000000013").readDocument() == scText

    # The chapter dirs should have the same parent
    assert project.tree["0000000000011"].itemParent == C.hNovelRoot  # type: ignore

    # The new files should have the new folder as parent
    assert project.tree["0000000000012"].itemParent == "0000000000011"  # type: ignore
    assert project.tree["0000000000013"].itemParent == "0000000000011"  # type: ignore

    # Full Root Folder
    # ================

    # The root is copied, with three docs and a folder
    assert list(dup.duplicate(
        [C.hNovelRoot, C.hTitlePage, C.hChapterDir, C.hChapterDoc, C.hSceneDoc]
    )) == [
        ("0000000000014", C.hNovelRoot),  # The Root
        ("0000000000015", None),          # The Title Page
        ("0000000000016", None),          # The Folder
        ("0000000000017", None),          # The Chapter
        ("0000000000018", None),          # The Scene
    ]
    assert project.tree._order == [
        C.hNovelRoot, C.hPlotRoot, C.hCharRoot, C.hWorldRoot,
        C.hTitlePage, C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010",
        "0000000000011", "0000000000012", "0000000000013",
        "0000000000014", "0000000000015", "0000000000016", "0000000000017", "0000000000018",
    ]

    # With the same content
    assert project.storage.getDocument("0000000000015").readDocument() == ttText
    assert project.storage.getDocument("0000000000017").readDocument() == chText
    assert project.storage.getDocument("0000000000018").readDocument() == scText

    # The root folder should have no parent
    assert project.tree["0000000000014"].itemParent is None  # type: ignore

    # The folder and files should have the new root
    assert project.tree["0000000000015"].itemRoot == "0000000000014"  # type: ignore
    assert project.tree["0000000000016"].itemRoot == "0000000000014"  # type: ignore
    assert project.tree["0000000000017"].itemRoot == "0000000000014"  # type: ignore
    assert project.tree["0000000000018"].itemRoot == "0000000000014"  # type: ignore

    # And they should have new parents
    assert project.tree["0000000000015"].itemParent == "0000000000014"  # type: ignore
    assert project.tree["0000000000016"].itemParent == "0000000000014"  # type: ignore
    assert project.tree["0000000000017"].itemParent == "0000000000016"  # type: ignore
    assert project.tree["0000000000018"].itemParent == "0000000000016"  # type: ignore

    # Exceptions
    # ==========

    # Handle invalid items
    assert list(dup.duplicate([C.hInvalid])) == []

    # Also stop early if invalid items are encountered
    assert list(dup.duplicate([C.hInvalid, C.hSceneDoc])) == []

    # Don't overwrite existing files
    content = project.storage.contentPath
    assert isinstance(content, Path)
    (content / "0000000000019.nwd").touch()
    assert (content / "0000000000019.nwd").exists()
    assert list(dup.duplicate([C.hChapterDoc, C.hSceneDoc])) == []

    # Save and Close
    project.saveProject()

    projFile = fncPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "coreTools_DocDuplicator_nwProject.nwx"
    compFile = tstPaths.refDir / "coreTools_DocDuplicator_nwProject.nwx"

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

# END Test testCoreTools_DocDuplicator


@pytest.mark.core
def testCoreTools_DocSearch(monkeypatch, mockGUI, fncPath, mockRnd, ipsumText):
    """Test the DocDuplicator utility."""
    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)
    project.storage.getDocument(C.hSceneDoc).writeDocument(
        "### New Scene\n\n" + "\n\n".join(ipsumText)
    )

    search = DocSearch()

    # Defaults
    # ========

    result = [(i.itemHandle, r, c) for i, r, c in search.iterSearch(project, "Scene")]
    assert result[0] == (C.hTitlePage, [], False)
    assert result[1] == (C.hChapterDoc, [], False)
    assert result[2] == (C.hSceneDoc, [(8, 5, "Scene")], False)

    # Patterns
    # ========

    # Escape Using QRegularExpression
    assert search._buildPattern("[A-Za-z0-9_]+") == r"\[A\-Za\-z0\-9_\]\+"

    # Whole Words
    search.setWholeWords(True)
    search.setUserRegEx(True)
    assert search._buildPattern("Hi") == r"(?:^|\b)Hi(?:$|\b)"
    search.setWholeWords(False)
    search.setUserRegEx(False)

    # Test Settings
    # =============

    def pruneResult(result, index):
        temp = [(i.itemHandle, r, c) for i, r, c in result][index][1]
        return [(s, n, c.split()[0]) for s, n, c in temp]

    # Defaults
    assert pruneResult(search.iterSearch(project, "Lorem"), 2) == [
        (15, 5, "Lorem"), (754, 5, "lorem"), (2056, 5, "lorem,"), (2209, 5, "lorem"),
        (2425, 5, "lorem"), (2840, 5, "lorem."), (3399, 5, "lorem"),
    ]

    # Whole Words
    search.setWholeWords(True)
    assert pruneResult(search.iterSearch(project, "Lor"), 2) == []
    search.setWholeWords(False)
    assert pruneResult(search.iterSearch(project, "Lor"), 2) == [
        (15, 3, "Lorem"), (29, 3, "lor"), (754, 3, "lorem"), (2056, 3, "lorem,"),
        (2209, 3, "lorem"), (2425, 3, "lorem"), (2840, 3, "lorem."), (3328, 3, "lor."),
        (3399, 3, "lorem"),
    ]

    # As RegEx
    search.setWholeWords(False)
    search.setUserRegEx(True)
    assert pruneResult(search.iterSearch(project, r"Lor\b"), 2) == [
        (29, 3, "lor"), (3328, 3, "lor."),
    ]

    # Max Results
    with monkeypatch.context() as mp:
        mp.setattr(nwConst, "MAX_SEARCH_RESULT", 3)
        assert pruneResult(search.iterSearch(project, "Lorem"), 2) == [
            (15, 5, "Lorem"), (754, 5, "lorem"), (2056, 5, "lorem,"),
        ]

    # Case Sensitive
    search.setCaseSensitive(True)
    assert pruneResult(search.iterSearch(project, "Lorem"), 2) == [(15, 5, "Lorem")]
    search.setCaseSensitive(False)

# END Test testCoreTools_DocSearch


@pytest.mark.core
def testCoreTools_ProjectBuilderWrapper(monkeypatch, caplog, fncPath, mockGUI):
    """Test the wrapper function of the project builder."""
    builder = ProjectBuilder()

    # Setting no data should fail
    assert builder.buildProject({}) is False

    # Wrong type should also fail
    assert builder.buildProject("stuff") is False  # type: ignore

    # Folder not writable
    caplog.clear()
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.mkdir", causeOSError)
        assert builder.buildProject({"path": fncPath}) is False
        assert "An error occurred" in caplog.text

    # Try again with a proper path
    assert builder.buildProject({"path": fncPath}) is True
    assert builder.projPath == fncPath

    # Creating the project once more should fail
    caplog.clear()
    assert builder.buildProject({"path": fncPath}) is False
    assert "The target folder is not empty." in caplog.text

# END Test testCoreTools_ProjectBuilderWrapper


@pytest.mark.core
def testCoreTools_ProjectBuilderA(monkeypatch, fncPath, tstPaths, mockGUI, mockRnd):
    """Create a new project from a project dictionary, with chapters."""
    monkeypatch.setattr("uuid.uuid4", lambda *a: uuid.UUID("d0f3fe10-c6e6-4310-8bfd-181eb4224eed"))

    projFile = fncPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "coreTools_ProjectBuilderA_nwProject.nwx"
    compFile = tstPaths.refDir / "coreTools_ProjectBuilderA_nwProject.nwx"

    data = {
        "name": "Test Project A",
        "author": "Jane Doe",
        "language": -1,
        "path": fncPath,
        "sample": False,
        "template": None,
        "chapters": 3,
        "scenes": 3,
        "roots": [
            nwItemClass.PLOT,
            nwItemClass.CHARACTER,
            nwItemClass.WORLD,
        ],
        "notes": True,
    }

    builder = ProjectBuilder()
    assert builder.buildProject(data) is True

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

# END Test testCoreTools_ProjectBuilderA


@pytest.mark.core
def testCoreTools_ProjectBuilderB(monkeypatch, fncPath, tstPaths, mockGUI, mockRnd):
    """Create a new project from a project dictionary, without chapters."""
    monkeypatch.setattr("uuid.uuid4", lambda *a: uuid.UUID("d0f3fe10-c6e6-4310-8bfd-181eb4224eed"))

    projFile = fncPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "coreTools_ProjectBuilderB_nwProject.nwx"
    compFile = tstPaths.refDir / "coreTools_ProjectBuilderB_nwProject.nwx"

    data = {
        "name": "Test Project B",
        "author": "Jane Doe",
        "language": -1,
        "path": fncPath,
        "sample": False,
        "template": None,
        "chapters": 0,
        "scenes": 6,
        "roots": [
            nwItemClass.PLOT,
            nwItemClass.CHARACTER,
            nwItemClass.WORLD,
        ],
        "notes": True,
    }

    builder = ProjectBuilder()
    assert builder.buildProject(data) is True

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

# END Test testCoreTools_ProjectBuilderB


@pytest.mark.core
def testCoreTools_ProjectBuilderCopyPlain(monkeypatch, caplog, mockGUI, prjLipsum, fncPath):
    """Create a new project copied from existing project."""
    srcPath = prjLipsum / nwFiles.PROJ_FILE
    dstPath = fncPath / "lipsum"
    data = {
        "name": "Test Project",
        "author": "Jane Doe",
        "path": dstPath,
        "template": srcPath,
    }

    builder = ProjectBuilder()

    # No path set
    assert builder.buildProject({"template": srcPath}) is False

    # No project at path
    assert builder.buildProject({"path": fncPath, "template": fncPath}) is False

    # Cannot copy to existing folder
    assert builder.buildProject({"path": fncPath, "template": srcPath}) is False

    # Valid data, but copy fails
    caplog.clear()
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.mkdir", lambda *a, **k: causeOSError)
        assert builder.buildProject(data) is False
        assert "Could not copy project files." in caplog.text
        dstPath.unlink(missing_ok=True)  # The failed mkdir leaves an empty file

    # Copy project properly
    assert builder.buildProject(data) is True

    # Check Copy
    # ==========

    srcProject = NWProject()
    srcProject.openProject(srcPath)

    dstProject = NWProject()
    dstProject.openProject(dstPath)

    # UUID should be different
    assert srcProject.data.uuid != dstProject.data.uuid

    # Name should be different
    assert srcProject.data.name == "Lorem Ipsum"
    assert dstProject.data.name == "Test Project"

    # Author should be different
    assert srcProject.data.author == "lipsum.com"
    assert dstProject.data.author == "Jane Doe"

    # Language should be the same
    assert srcProject.data.language == "en_GB"
    assert dstProject.data.language == "en_GB"

    # Counts should be more or less zeroed
    assert dstProject.data.saveCount < 5
    assert dstProject.data.autoCount < 5
    assert dstProject.data.editTime < 10

# END Test testCoreTools_ProjectBuilderCopyPlain


@pytest.mark.core
def testCoreTools_ProjectBuilderCopyZipped(monkeypatch, caplog, mockGUI, fncPath, mockRnd):
    """Create a new project copied from existing zipped project."""

    # Create a project
    origPath = fncPath / "original"
    srcProject = NWProject()
    buildTestProject(srcProject, origPath)

    # Zip it
    shutil.make_archive(str(fncPath / "original"), "zip", origPath)

    # Make fake zip file
    fakeZip = fncPath / "broken.zip"
    fakeZip.write_bytes(b"stuff")

    # Set up the builder
    srcPath = fncPath / "original.zip"
    dstPath = fncPath / "copy"
    data = {
        "name": "Test Project",
        "author": "Jane Doe",
        "language": "en_US",
        "path": dstPath,
        "template": srcPath,
    }

    builder = ProjectBuilder()

    # No path set
    assert builder.buildProject({"template": srcPath}) is False

    # No project at path
    assert builder.buildProject({"path": fncPath, "template": fncPath}) is False

    # Cannot copy to existing folder
    assert builder.buildProject({"path": fncPath, "template": srcPath}) is False

    # Cannot copy to existing folder
    caplog.clear()
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.coretools.is_zipfile", lambda *a: True)
        assert builder.buildProject({"path": dstPath, "template": fakeZip}) is False
        assert "Could not copy project files." in caplog.text
        shutil.rmtree(dstPath, ignore_errors=True)

    # Copy project properly
    assert builder.buildProject(data) is True

    # Check Copy
    # ==========

    dstProject = NWProject()
    dstProject.openProject(dstPath)

    # UUID should be different
    assert srcProject.data.uuid != dstProject.data.uuid

    # Name should be different
    assert srcProject.data.name == "New Project"
    assert dstProject.data.name == "Test Project"

    # Author should be different
    assert srcProject.data.author == "Jane Doe"
    assert dstProject.data.author == "Jane Doe"

    # Language should be the same
    assert srcProject.data.language is None
    assert dstProject.data.language is None

    # Counts should be more or less zeroed
    assert dstProject.data.saveCount < 5
    assert dstProject.data.autoCount < 5
    assert dstProject.data.editTime < 10

# END Test testCoreTools_ProjectBuilderCopyZipped


@pytest.mark.core
def testCoreTools_ProjectBuilderSample(monkeypatch, mockGUI, fncPath, tstPaths):
    """Create a new sample project."""
    data = {
        "name": "Test Sample",
        "author": "Jane Doe",
        "path": fncPath / "project",
        "sample": True,
    }

    builder = ProjectBuilder()

    # No path set
    assert builder.buildProject({"sample": True}) is False

    # Force the lookup path for assets to our temp folder
    srcSample = CONFIG._appRoot / "sample"
    dstSample = tstPaths.tmpDir / "sample.zip"
    monkeypatch.setattr(
        "novelwriter.config.Config.assetPath", lambda *a: tstPaths.tmpDir / "sample.zip"
    )

    # Cannot extract when the zip does not exist
    assert builder.buildProject(data) is False

    # Create and open a defective zip file
    with open(dstSample, mode="w+") as outFile:
        outFile.write("foo")

    assert builder.buildProject(data) is False
    dstSample.unlink()

    # Create a real zip file, and unpack it
    with ZipFile(dstSample, "w") as zipObj:
        zipObj.write(srcSample / "nwProject.nwx", "nwProject.nwx")
        for docFile in (srcSample / "content").iterdir():
            zipObj.write(docFile, f"content/{docFile.name}")

    assert builder.buildProject(data) is True

    # Can't create to the same target again
    assert builder.buildProject(data) is False
    dstSample.unlink()

# END Test testCoreTools_ProjectBuilderSample
