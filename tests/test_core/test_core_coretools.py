"""
novelWriter – Project Document Tools Tester
===========================================

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

import uuid
import pytest

from shutil import copyfile
from pathlib import Path
from zipfile import ZipFile

from mocked import causeOSError
from tools import C, buildTestProject, cmpFiles, XML_IGNORE

from novelwriter import CONFIG
from novelwriter.constants import nwItemClass
from novelwriter.core.project import NWProject
from novelwriter.core.coretools import DocDuplicator, DocMerger, DocSplitter, ProjectBuilder


@pytest.mark.core
def testCoreTools_DocMerger(monkeypatch, mockGUI, fncPath, tstPaths, mockRnd, ipsumText):
    """Test the DocMerger utility."""
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncPath)

    # Create Files to Merge
    # =====================

    hChapter1 = theProject.newFile("Chapter 1", C.hNovelRoot)
    hSceneOne11 = theProject.newFile("Scene 1.1", hChapter1)
    hSceneOne12 = theProject.newFile("Scene 1.2", hChapter1)
    hSceneOne13 = theProject.newFile("Scene 1.3", hChapter1)

    docText1 = "\n\n".join(ipsumText[0:2]) + "\n\n"
    docText2 = "\n\n".join(ipsumText[1:3]) + "\n\n"
    docText3 = "\n\n".join(ipsumText[2:4]) + "\n\n"
    docText4 = "\n\n".join(ipsumText[3:5]) + "\n\n"

    theProject.writeNewFile(hChapter1, 2, True, docText1)
    theProject.writeNewFile(hSceneOne11, 3, True, docText2)
    theProject.writeNewFile(hSceneOne12, 3, True, docText3)
    theProject.writeNewFile(hSceneOne13, 3, True, docText4)

    # Basic Checks
    # ============

    docMerger = DocMerger(theProject)

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

    assert docMerger.newTargetDoc(hChapter1, "All of Chapter 1") == "0000000000014"

    assert docMerger.appendText(hChapter1, True, "Merge") is True
    assert docMerger.appendText(hSceneOne11, True, "Merge") is True
    assert docMerger.appendText(hSceneOne12, True, "Merge") is True
    assert docMerger.appendText(hSceneOne13, True, "Merge") is True

    # Block writing and check error handling
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert docMerger.writeTargetDoc() is False
        assert not saveFile.exists()
        assert docMerger.getError() != ""

    # Write properly, and compare
    assert docMerger.writeTargetDoc() is True
    copyfile(saveFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Merge into Existing
    # ===================

    saveFile = fncPath / "content" / "0000000000010.nwd"
    testFile = tstPaths.outDir / "coreDocTools_DocMerger_0000000000010.nwd"
    compFile = tstPaths.refDir / "coreDocTools_DocMerger_0000000000010.nwd"

    docMerger.setTargetDoc(hChapter1)

    assert docMerger.appendText(hSceneOne11, True, "Merge") is True
    assert docMerger.appendText(hSceneOne12, True, "Merge") is True
    assert docMerger.appendText(hSceneOne13, True, "Merge") is True

    assert docMerger.writeTargetDoc() is True
    copyfile(saveFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Just for debugging
    docMerger.writeTargetDoc()

# END Test testCoreTools_DocMerger


@pytest.mark.core
def testCoreTools_DocSplitter(monkeypatch, mockGUI, fncPath, mockRnd, ipsumText):
    """Test the DocSplitter utility."""
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncPath)

    # Create File to Split
    # ====================

    hSplitDoc = theProject.newFile("Split Doc", C.hNovelRoot)

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
    assert theProject.storage.getDocument(hSplitDoc).writeDocument(docText) is True
    theProject.tree[hSplitDoc].setStatus(C.sFinished)
    theProject.tree[hSplitDoc].setImport(C.iMain)

    docSplitter = DocSplitter(theProject, hSplitDoc)
    assert docSplitter._srcItem.isFileType()
    assert docSplitter.getError() == ""

    # Run the split algorithm
    docSplitter.splitDocument(splitData, docRaw)
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
        assert theProject.tree[rHandle].itemStatus == C.sFinished
        assert theProject.tree[rHandle].itemImport == C.iMain

    # Check handling of improper initialisation
    docSplitter = DocSplitter(theProject, C.hInvalid)
    assert docSplitter._srcHandle is None
    assert docSplitter._srcItem is None
    assert docSplitter.newParentFolder(C.hNovelRoot, "Split Folder") is None
    assert list(docSplitter.writeDocuments(False)) == []

    theProject.saveProject()

# END Test testCoreTools_DocSplitter


@pytest.mark.core
def testCoreTools_DocDuplicator(mockGUI, fncPath, tstPaths, mockRnd):
    """Test the DocDuplicator utility."""
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncPath)

    dup = DocDuplicator(theProject)

    ttText = "#! New Novel\n\n>> By Jane Doe <<\n"
    chText = "## New Chapter\n\n"
    scText = "### New Scene\n\n"

    # Check document content
    assert theProject.storage.getDocument(C.hTitlePage).readDocument() == ttText
    assert theProject.storage.getDocument(C.hChapterDoc).readDocument() == chText
    assert theProject.storage.getDocument(C.hSceneDoc).readDocument() == scText

    # Nothing to do
    assert list(dup.duplicate([])) == []

    # Single Document
    # ===============

    # A new copy is created
    assert list(dup.duplicate([C.hSceneDoc])) == [
        ("0000000000010", C.hSceneDoc),  # The Scene
    ]
    assert theProject.tree._treeOrder == [
        C.hNovelRoot, C.hPlotRoot, C.hCharRoot, C.hWorldRoot,
        C.hTitlePage, C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010",
    ]

    # With the same content
    assert theProject.storage.getDocument("0000000000010").readDocument() == scText

    # They should have the same parent
    assert theProject.tree["0000000000010"].itemParent == C.hChapterDir  # type: ignore

    # Folder w/Two Files
    # ==================

    # The folder is copied, with two docs
    assert list(dup.duplicate([C.hChapterDir, C.hChapterDoc, C.hSceneDoc])) == [
        ("0000000000011", C.hChapterDir),  # The Folder
        ("0000000000012", None),           # The Chapter
        ("0000000000013", None),           # The Scene
    ]
    assert theProject.tree._treeOrder == [
        C.hNovelRoot, C.hPlotRoot, C.hCharRoot, C.hWorldRoot,
        C.hTitlePage, C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010",
        "0000000000011", "0000000000012", "0000000000013",
    ]

    # With the same content
    assert theProject.storage.getDocument("0000000000012").readDocument() == chText
    assert theProject.storage.getDocument("0000000000013").readDocument() == scText

    # The chapter dirs should have the same parent
    assert theProject.tree["0000000000011"].itemParent == C.hNovelRoot  # type: ignore

    # The new files should have the new folder as parent
    assert theProject.tree["0000000000012"].itemParent == "0000000000011"  # type: ignore
    assert theProject.tree["0000000000013"].itemParent == "0000000000011"  # type: ignore

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
    assert theProject.tree._treeOrder == [
        C.hNovelRoot, C.hPlotRoot, C.hCharRoot, C.hWorldRoot,
        C.hTitlePage, C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        "0000000000010",
        "0000000000011", "0000000000012", "0000000000013",
        "0000000000014", "0000000000015", "0000000000016", "0000000000017", "0000000000018",
    ]

    # With the same content
    assert theProject.storage.getDocument("0000000000015").readDocument() == ttText
    assert theProject.storage.getDocument("0000000000017").readDocument() == chText
    assert theProject.storage.getDocument("0000000000018").readDocument() == scText

    # The root folder should have no parent
    assert theProject.tree["0000000000014"].itemParent is None  # type: ignore

    # The folder and files should have the new root
    assert theProject.tree["0000000000015"].itemRoot == "0000000000014"  # type: ignore
    assert theProject.tree["0000000000016"].itemRoot == "0000000000014"  # type: ignore
    assert theProject.tree["0000000000017"].itemRoot == "0000000000014"  # type: ignore
    assert theProject.tree["0000000000018"].itemRoot == "0000000000014"  # type: ignore

    # And they should have new parents
    assert theProject.tree["0000000000015"].itemParent == "0000000000014"  # type: ignore
    assert theProject.tree["0000000000016"].itemParent == "0000000000014"  # type: ignore
    assert theProject.tree["0000000000017"].itemParent == "0000000000016"  # type: ignore
    assert theProject.tree["0000000000018"].itemParent == "0000000000016"  # type: ignore

    # Exceptions
    # ==========

    # Handle invalid items
    assert list(dup.duplicate([C.hInvalid])) == []

    # Also stop early if invalid items are encountered
    assert list(dup.duplicate([C.hInvalid, C.hSceneDoc])) == []

    # Don't overwrite existing files
    content = theProject.storage.contentPath
    assert isinstance(content, Path)
    (content / "0000000000019.nwd").touch()
    assert (content / "0000000000019.nwd").exists()
    assert list(dup.duplicate([C.hChapterDoc, C.hSceneDoc])) == []

    # Save and Close
    theProject.saveProject()

    projFile = fncPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "coreTools_DocDuplicator_nwProject.nwx"
    compFile = tstPaths.refDir / "coreTools_DocDuplicator_nwProject.nwx"

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

# END Test testCoreTools_DocDuplicator


@pytest.mark.core
def testCoreTools_NewMinimal(monkeypatch, fncPath, tstPaths, mockGUI, mockRnd):
    """Create a new project from a project wizard dictionary. With
    default setting, creating a Minimal project.
    """
    monkeypatch.setattr("uuid.uuid4", lambda *a: uuid.UUID("d0f3fe10-c6e6-4310-8bfd-181eb4224eed"))

    projFile = fncPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "coreTools_NewMinimal_nwProject.nwx"
    compFile = tstPaths.refDir / "coreTools_NewMinimal_nwProject.nwx"

    projBuild = ProjectBuilder(mockGUI)

    # Setting no data should fail
    assert projBuild.buildProject({}) is False

    # Wrong type should also fail
    assert projBuild.buildProject("stuff") is False

    # Try again with a proper path
    assert projBuild.buildProject({"projPath": fncPath}) is True

    # Creating the project once more should fail
    assert projBuild.buildProject({"projPath": fncPath}) is False

    # Save and close
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

# END Test testCoreTools_NewMinimal


@pytest.mark.core
def testCoreTools_NewCustomA(monkeypatch, fncPath, tstPaths, mockGUI, mockRnd):
    """Create a new project from a project wizard dictionary.
    Custom type with chapters and scenes.
    """
    monkeypatch.setattr("uuid.uuid4", lambda *a: uuid.UUID("d0f3fe10-c6e6-4310-8bfd-181eb4224eed"))

    projFile = fncPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "coreTools_NewCustomA_nwProject.nwx"
    compFile = tstPaths.refDir / "coreTools_NewCustomA_nwProject.nwx"

    projData = {
        "projName": "Test Custom",
        "projTitle": "Test Novel",
        "projAuthor": "Jane Doe",
        "projPath": fncPath,
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

    projBuild = ProjectBuilder(mockGUI)
    assert projBuild.buildProject(projData) is True

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

# END Test testCoreTools_NewCustomA


@pytest.mark.core
def testCoreTools_NewCustomB(monkeypatch, fncPath, tstPaths, mockGUI, mockRnd):
    """Create a new project from a project wizard dictionary.
    Custom type without chapters, but with scenes.
    """
    monkeypatch.setattr("uuid.uuid4", lambda *a: uuid.UUID("d0f3fe10-c6e6-4310-8bfd-181eb4224eed"))

    projFile = fncPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "coreTools_NewCustomB_nwProject.nwx"
    compFile = tstPaths.refDir / "coreTools_NewCustomB_nwProject.nwx"

    projData = {
        "projName": "Test Custom",
        "projTitle": "Test Novel",
        "projAuthor": "Jane Doe",
        "projPath": fncPath,
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

    projBuild = ProjectBuilder(mockGUI)
    assert projBuild.buildProject(projData) is True

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

# END Test testCoreTools_NewCustomB


@pytest.mark.core
def testCoreTools_NewSample(monkeypatch, fncPath, tstPaths, mockGUI):
    """Check that we can create a new project can be created from the
    provided sample project via a zip file.
    """
    projData = {
        "projName": "Test Sample",
        "projTitle": "Test Novel",
        "projAuthor": "Jane Doe",
        "projPath": fncPath,
        "popSample": True,
        "popMinimal": False,
        "popCustom": False,
    }

    projBuild = ProjectBuilder(mockGUI)

    # No path set
    assert projBuild.buildProject({"popSample": True}) is False

    # Force the lookup path for assets to our temp folder
    srcSample = CONFIG._appRoot / "sample"
    dstSample = tstPaths.tmpDir / "sample.zip"
    monkeypatch.setattr(
        "novelwriter.config.Config.assetPath", lambda *a: tstPaths.tmpDir / "sample.zip"
    )

    # Cannot extract when the zip does not exist
    assert projBuild.buildProject(projData) is False

    # Create and open a defective zip file
    with open(dstSample, mode="w+") as outFile:
        outFile.write("foo")

    assert projBuild.buildProject(projData) is False
    dstSample.unlink()

    # Create a real zip file, and unpack it
    with ZipFile(dstSample, "w") as zipObj:
        zipObj.write(srcSample / "nwProject.nwx", "nwProject.nwx")
        for docFile in (srcSample / "content").iterdir():
            zipObj.write(docFile, f"content/{docFile.name}")

    assert projBuild.buildProject(projData) is True
    dstSample.unlink()

# END Test testCoreTools_NewSample
