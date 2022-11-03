"""
novelWriter – Project Document Tools Tester
===========================================

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

from mock import causeOSError
from tools import C, buildTestProject, cmpFiles

from novelwriter.core.project import NWProject
from novelwriter.core.document import NWDoc
from novelwriter.core.coretools import DocMerger, DocSplitter


@pytest.mark.core
def testCoreTools_DocMerger(monkeypatch, mockGUI, fncDir, outDir, refDir, mockRnd, ipsumText):
    """Test the DocMerger utility.
    """
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncDir)

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

    saveFile = os.path.join(fncDir, "content", "0000000000014.nwd")
    testFile = os.path.join(outDir, "coreDocTools_DocMerger_0000000000014.nwd")
    compFile = os.path.join(refDir, "coreDocTools_DocMerger_0000000000014.nwd")

    assert docMerger.newTargetDoc(hChapter1, "All of Chapter 1") == "0000000000014"

    assert docMerger.appendText(hChapter1, True, "Merge") is True
    assert docMerger.appendText(hSceneOne11, True, "Merge") is True
    assert docMerger.appendText(hSceneOne12, True, "Merge") is True
    assert docMerger.appendText(hSceneOne13, True, "Merge") is True

    # Block writing and check error handling
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert docMerger.writeTargetDoc() is False
        assert not os.path.isfile(saveFile)
        assert docMerger.getError() != ""

    # Write properly, and compare
    assert docMerger.writeTargetDoc() is True
    copyfile(saveFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Merge into Existing
    # ===================

    saveFile = os.path.join(fncDir, "content", "0000000000010.nwd")
    testFile = os.path.join(outDir, "coreDocTools_DocMerger_0000000000010.nwd")
    compFile = os.path.join(refDir, "coreDocTools_DocMerger_0000000000010.nwd")

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
def testCoreTools_DocSplitter(monkeypatch, mockGUI, fncDir, outDir, refDir, mockRnd, ipsumText):
    """Test the DocSplitter utility.
    """
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncDir)

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
    assert NWDoc(theProject, hSplitDoc).writeDocument(docText) is True
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
