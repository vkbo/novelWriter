"""
novelWriter – NWIndex Class Tester
==================================

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

import pytest
import os
import json

from shutil import copyfile

from mock import causeException
from tools import cmpFiles

from novelwriter.core.project import NWProject
from novelwriter.core.index import NWIndex, countWords
from novelwriter.enum import nwItemClass, nwItemLayout


@pytest.mark.core
def testCoreIndex_LoadSave(monkeypatch, nwLipsum, mockGUI, outDir, refDir):
    """Test core functionality of scaning, saving, loading and checking
    the index cache file.
    """
    projFile = os.path.join(nwLipsum, "meta", "tagsIndex.json")
    testFile = os.path.join(outDir, "coreIndex_LoadSave_tagsIndex.json")
    compFile = os.path.join(refDir, "coreIndex_LoadSave_tagsIndex.json")

    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwLipsum)

    theIndex = NWIndex(theProject)
    notIndexable = {
        "b3643d0f92e32": False,  # Novel ROOT
        "45e6b01ca35c1": False,  # Chapter One FOLDER
        "6bd935d2490cd": False,  # Chapter Two FOLDER
        "67a8707f2f249": False,  # Character ROOT
        "6c6afb1247750": False,  # Plot ROOT
        "60bdf227455cc": False,  # World ROOT
    }
    for tItem in theProject.projTree:
        assert theIndex.reIndexHandle(tItem.itemHandle) is notIndexable.get(tItem.itemHandle, True)

    assert theIndex.reIndexHandle(None) is False

    # Make the save fail
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeException)
        assert theIndex.saveIndex() is False

    # Make the save pass
    assert theIndex.saveIndex() is True

    # Take a copy of the index
    tagIndex = str(theIndex._tagIndex)
    refIndex = str(theIndex._refIndex)
    fileIndex = str(theIndex._fileIndex)
    textCounts = str(theIndex._fileMeta)

    # Delete a handle
    assert theIndex._tagIndex.get("Bod", None) is not None
    assert theIndex._refIndex.get("4c4f28287af27", None) is not None
    assert theIndex._fileIndex.get("4c4f28287af27", None) is not None
    assert theIndex._fileMeta.get("4c4f28287af27", None) is not None
    theIndex.deleteHandle("4c4f28287af27")
    assert theIndex._tagIndex.get("Bod", None) is None
    assert theIndex._refIndex.get("4c4f28287af27", None) is None
    assert theIndex._fileIndex.get("4c4f28287af27", None) is None
    assert theIndex._fileMeta.get("4c4f28287af27", None) is None

    # Clear the index
    theIndex.clearIndex()
    assert theIndex._tagIndex == {}
    assert theIndex._refIndex == {}
    assert theIndex._fileIndex == {}
    assert theIndex._fileMeta == {}

    # Make the load fail
    with monkeypatch.context() as mp:
        mp.setattr(json, "load", causeException)
        assert theIndex.loadIndex() is False

    # Make the load pass
    assert theIndex.loadIndex() is True

    assert str(theIndex._tagIndex) == tagIndex
    assert str(theIndex._refIndex) == refIndex
    assert str(theIndex._fileIndex) == fileIndex
    assert str(theIndex._fileMeta) == textCounts

    # Break the index and check that we notice
    assert theIndex.indexBroken is False
    theIndex._tagIndex["Bod"].append("Stuff")
    theIndex._checkIndex()
    assert theIndex.indexBroken is True

    # Finalise
    assert theProject.closeProject() is True

    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

# END Test testCoreIndex_LoadSave


@pytest.mark.core
def testCoreIndex_ScanThis(nwMinimal, mockGUI):
    """Test the tag scanner function scanThis.
    """
    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal) is True

    theIndex = NWIndex(theProject)

    isValid, theBits, thePos = theIndex.scanThis("tag: this, and this")
    assert isValid is False

    isValid, theBits, thePos = theIndex.scanThis("@")
    assert isValid is False

    isValid, theBits, thePos = theIndex.scanThis("@:")
    assert isValid is False

    isValid, theBits, thePos = theIndex.scanThis(" @a: b")
    assert isValid is False

    isValid, theBits, thePos = theIndex.scanThis("@a:")
    assert isValid is True
    assert theBits == ["@a"]
    assert thePos  == [0]

    isValid, theBits, thePos = theIndex.scanThis("@a:b")
    assert isValid is True
    assert theBits == ["@a", "b"]
    assert thePos  == [0, 3]

    isValid, theBits, thePos = theIndex.scanThis("@a:b,c,d")
    assert isValid is True
    assert theBits == ["@a", "b", "c", "d"]
    assert thePos  == [0, 3, 5, 7]

    isValid, theBits, thePos = theIndex.scanThis("@a : b , c , d")
    assert isValid is True
    assert theBits == ["@a", "b", "c", "d"]
    assert thePos  == [0, 5, 9, 13]

    isValid, theBits, thePos = theIndex.scanThis("@tag: this, and this")
    assert isValid is True
    assert theBits == ["@tag", "this", "and this"]
    assert thePos  == [0, 6, 12]

    assert theProject.closeProject() is True

# END Test testCoreIndex_ScanThis


@pytest.mark.core
def testCoreIndex_CheckThese(nwMinimal, mockGUI):
    """Test the tag checker function checkThese.
    """
    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal) is True

    theIndex = NWIndex(theProject)
    nHandle = theProject.newFile("Hello", nwItemClass.NOVEL,     "a508bb932959c")
    cHandle = theProject.newFile("Jane",  nwItemClass.CHARACTER, "afb3043c7b2b3")
    nItem = theProject.projTree[nHandle]
    cItem = theProject.projTree[cHandle]

    assert theIndex.novelChangedSince(0) is False
    assert theIndex.notesChangedSince(0) is False
    assert theIndex.indexChangedSince(0) is False

    assert theIndex.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane\n"
        "@tag:\n"
        "@:\n"
    ))
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@invalid: John\n"  # Checks for issue #688
    ))
    assert theIndex._tagIndex == {"Jane": [2, cHandle, "CHARACTER", "T000001"]}
    assert theIndex.getNovelData(nHandle, "T000001")["title"] == "Hello World!"
    assert theIndex.getReferences(nHandle, "T000001") == {
        "@char": [],
        "@custom": [],
        "@entity": [],
        "@focus": [],
        "@location": [],
        "@object": [],
        "@plot": [],
        "@pov": ["Jane"],
        "@time": []
    }

    assert theIndex.novelChangedSince(0) is True
    assert theIndex.notesChangedSince(0) is True
    assert theIndex.indexChangedSince(0) is True

    assert theIndex.getHandleHeaderLevel(cHandle) == "H1"
    assert theIndex.getHandleHeaderLevel(nHandle) == "H1"

    # Zero Items
    assert theIndex.checkThese([], cItem) == []

    # One Item
    assert theIndex.checkThese(["@tag"], cItem) == [True]
    assert theIndex.checkThese(["@who"], cItem) == [False]

    # Two Items
    assert theIndex.checkThese(["@tag", "Jane"], cItem) == [True, True]
    assert theIndex.checkThese(["@tag", "John"], cItem) == [True, True]
    assert theIndex.checkThese(["@tag", "Jane"], nItem) == [True, False]
    assert theIndex.checkThese(["@tag", "John"], nItem) == [True, True]
    assert theIndex.checkThese(["@pov", "John"], nItem) == [True, False]
    assert theIndex.checkThese(["@pov", "Jane"], nItem) == [True, True]
    assert theIndex.checkThese(["@ pov", "Jane"], nItem) == [False, False]
    assert theIndex.checkThese(["@what", "Jane"], nItem) == [False, False]

    # Three Items
    assert theIndex.checkThese(["@tag", "Jane", "John"], cItem) == [True, True, False]
    assert theIndex.checkThese(["@who", "Jane", "John"], cItem) == [False, False, False]
    assert theIndex.checkThese(["@pov", "Jane", "John"], nItem) == [True, True, False]

    assert theProject.closeProject() is True

# END Test testCoreIndex_CheckThese


@pytest.mark.core
def testCoreIndex_ScanText(nwMinimal, mockGUI):
    """Check the index text scanner.
    """
    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal) is True

    theIndex = NWIndex(theProject)

    # Some items for fail to scan tests
    dHandle = theProject.newFolder("Folder", nwItemClass.NOVEL, "a508bb932959c")
    xHandle = theProject.newFile("No Layout", nwItemClass.NOVEL, "a508bb932959c")
    xItem = theProject.projTree[xHandle]
    xItem.setLayout(nwItemLayout.NO_LAYOUT)

    # Check invalid data
    assert theIndex.scanText(None, "Hello World!") is False
    assert theIndex.scanText(dHandle, "Hello World!") is False
    assert theIndex.scanText(xHandle, "Hello World!") is False

    xItem.setLayout(nwItemLayout.DOCUMENT)
    xItem.setParent(None)
    assert theIndex.scanText(xHandle, "Hello World!") is False

    # Create the trash folder
    tHandle = theProject.trashFolder()
    assert theProject.projTree[tHandle] is not None
    xItem.setParent(tHandle)
    assert theIndex.scanText(xHandle, "Hello World!") is False

    # Create the archive root
    aHandle = theProject.newRoot("Archive", nwItemClass.ARCHIVE)
    assert theProject.projTree[aHandle] is not None
    xItem.setParent(aHandle)
    assert theIndex.scanText(xHandle, "Hello World!") is False

    # Make some usable items
    tHandle = theProject.newFile("Title", nwItemClass.NOVEL, "a508bb932959c")
    pHandle = theProject.newFile("Page",  nwItemClass.NOVEL, "a508bb932959c")
    nHandle = theProject.newFile("Hello", nwItemClass.NOVEL, "a508bb932959c")
    cHandle = theProject.newFile("Jane",  nwItemClass.CHARACTER, "afb3043c7b2b3")
    sHandle = theProject.newFile("Scene", nwItemClass.NOVEL, "a508bb932959c")

    # Text Indexing
    # =============

    # Index correct text
    assert theIndex.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane\n"
    ))
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n"
    ))
    assert theIndex._tagIndex == {"Jane": [2, cHandle, "CHARACTER", "T000001"]}
    assert theIndex.getNovelData(nHandle, "T000001")["title"] == "Hello World!"

    # Title Indexing
    # ==============

    # Document File
    assert theIndex.scanText(nHandle, (
        "# Title One\n\n"
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
        "## Title Two\n\n"
        "% synopsis: Synopsis Two.\n\n"
        "Paragraph Two.\n\n"
        "### Title Three\n\n"
        "% synopsis: Synopsis Three.\n\n"
        "Paragraph Three.\n\n"
        "#### Title Four\n\n"
        "% synopsis: Synopsis Four.\n\n"
        "Paragraph Four.\n\n"
        "##### Title Five\n\n"  # Not interpreted as a title, the hashes are counted as a word
        "Paragraph Five.\n\n"
    ))
    assert nHandle not in theIndex._refIndex

    assert theIndex._fileIndex[nHandle]["T000001"]["level"] == "H1"
    assert theIndex._fileIndex[nHandle]["T000007"]["level"] == "H2"
    assert theIndex._fileIndex[nHandle]["T000013"]["level"] == "H3"
    assert theIndex._fileIndex[nHandle]["T000019"]["level"] == "H4"

    assert theIndex._fileIndex[nHandle]["T000001"]["title"] == "Title One"
    assert theIndex._fileIndex[nHandle]["T000007"]["title"] == "Title Two"
    assert theIndex._fileIndex[nHandle]["T000013"]["title"] == "Title Three"
    assert theIndex._fileIndex[nHandle]["T000019"]["title"] == "Title Four"

    assert theIndex._fileIndex[nHandle]["T000001"]["layout"] == "DOCUMENT"
    assert theIndex._fileIndex[nHandle]["T000007"]["layout"] == "DOCUMENT"
    assert theIndex._fileIndex[nHandle]["T000013"]["layout"] == "DOCUMENT"
    assert theIndex._fileIndex[nHandle]["T000019"]["layout"] == "DOCUMENT"

    assert theIndex._fileIndex[nHandle]["T000001"]["cCount"] == 23
    assert theIndex._fileIndex[nHandle]["T000007"]["cCount"] == 23
    assert theIndex._fileIndex[nHandle]["T000013"]["cCount"] == 27
    assert theIndex._fileIndex[nHandle]["T000019"]["cCount"] == 56

    assert theIndex._fileIndex[nHandle]["T000001"]["wCount"] == 4
    assert theIndex._fileIndex[nHandle]["T000007"]["wCount"] == 4
    assert theIndex._fileIndex[nHandle]["T000013"]["wCount"] == 4
    assert theIndex._fileIndex[nHandle]["T000019"]["wCount"] == 9

    assert theIndex._fileIndex[nHandle]["T000001"]["pCount"] == 1
    assert theIndex._fileIndex[nHandle]["T000007"]["pCount"] == 1
    assert theIndex._fileIndex[nHandle]["T000013"]["pCount"] == 1
    assert theIndex._fileIndex[nHandle]["T000019"]["pCount"] == 3

    assert theIndex._fileIndex[nHandle]["T000001"]["synopsis"] == "Synopsis One."
    assert theIndex._fileIndex[nHandle]["T000007"]["synopsis"] == "Synopsis Two."
    assert theIndex._fileIndex[nHandle]["T000013"]["synopsis"] == "Synopsis Three."
    assert theIndex._fileIndex[nHandle]["T000019"]["synopsis"] == "Synopsis Four."

    # Note File
    assert theIndex.scanText(cHandle, (
        "# Title One\n\n"
        "@tag: One\n\n"
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
    ))
    assert cHandle not in theIndex._refIndex

    assert theIndex._fileIndex[cHandle]["T000001"]["level"] == "H1"
    assert theIndex._fileIndex[cHandle]["T000001"]["title"] == "Title One"
    assert theIndex._fileIndex[cHandle]["T000001"]["layout"] == "NOTE"
    assert theIndex._fileIndex[cHandle]["T000001"]["cCount"] == 23
    assert theIndex._fileIndex[cHandle]["T000001"]["wCount"] == 4
    assert theIndex._fileIndex[cHandle]["T000001"]["pCount"] == 1
    assert theIndex._fileIndex[cHandle]["T000001"]["synopsis"] == "Synopsis One."

    # Valid and Invalid References
    assert theIndex.scanText(sHandle, (
        "# Title One\n\n"
        "@pov: One\n\n"  # Valid
        "@char: Two\n\n"  # Invalid tag
        "@:\n\n"  # Invalid line
        "% synopsis: Synopsis One.\n\n"
        "Paragraph One.\n\n"
    ))
    assert theIndex._refIndex[sHandle]["T000001"] == (
        [[3, "@pov", "One"], [5, "@char", "Two"]]
    )

    # Special Titles
    # ==============

    assert theIndex.scanText(tHandle, (
        "#! My Project\n\n"
        ">> By Jane Doe <<\n\n"
    ))
    assert tHandle not in theIndex._refIndex

    assert theIndex._fileIndex[tHandle]["T000001"]["level"] == "H1"
    assert theIndex._fileIndex[tHandle]["T000001"]["title"] == "My Project"
    assert theIndex._fileIndex[tHandle]["T000001"]["layout"] == "DOCUMENT"
    assert theIndex._fileIndex[tHandle]["T000001"]["cCount"] == 21
    assert theIndex._fileIndex[tHandle]["T000001"]["wCount"] == 5
    assert theIndex._fileIndex[tHandle]["T000001"]["pCount"] == 1
    assert theIndex._fileIndex[tHandle]["T000001"]["synopsis"] == ""

    assert theIndex.scanText(tHandle, (
        "##! Prologue\n\n"
        "In the beginning there was time ...\n\n"
    ))
    assert tHandle not in theIndex._refIndex

    assert theIndex._fileIndex[tHandle]["T000001"]["level"] == "H2"
    assert theIndex._fileIndex[tHandle]["T000001"]["title"] == "Prologue"
    assert theIndex._fileIndex[tHandle]["T000001"]["layout"] == "DOCUMENT"
    assert theIndex._fileIndex[tHandle]["T000001"]["cCount"] == 43
    assert theIndex._fileIndex[tHandle]["T000001"]["wCount"] == 8
    assert theIndex._fileIndex[tHandle]["T000001"]["pCount"] == 1
    assert theIndex._fileIndex[tHandle]["T000001"]["synopsis"] == ""

    # Page wo/Title
    # =============

    theProject.projTree[pHandle]._layout = nwItemLayout.DOCUMENT
    assert theIndex.scanText(pHandle, (
        "This is a page with some text on it.\n\n"
    ))
    assert pHandle in theIndex._fileIndex
    assert theIndex._fileIndex[pHandle]["T000000"]["level"] == "H0"
    assert theIndex._fileIndex[pHandle]["T000000"]["title"] == ""
    assert theIndex._fileIndex[pHandle]["T000000"]["layout"] == "DOCUMENT"
    assert theIndex._fileIndex[pHandle]["T000000"]["cCount"] == 36
    assert theIndex._fileIndex[pHandle]["T000000"]["wCount"] == 9
    assert theIndex._fileIndex[pHandle]["T000000"]["pCount"] == 1
    assert theIndex._fileIndex[pHandle]["T000000"]["synopsis"] == ""

    theProject.projTree[pHandle]._layout = nwItemLayout.NOTE
    assert theIndex.scanText(pHandle, (
        "This is a page with some text on it.\n\n"
    ))
    assert pHandle in theIndex._fileIndex
    assert theIndex._fileIndex[pHandle]["T000000"]["level"] == "H0"
    assert theIndex._fileIndex[pHandle]["T000000"]["title"] == ""
    assert theIndex._fileIndex[pHandle]["T000000"]["layout"] == "NOTE"
    assert theIndex._fileIndex[pHandle]["T000000"]["cCount"] == 36
    assert theIndex._fileIndex[pHandle]["T000000"]["wCount"] == 9
    assert theIndex._fileIndex[pHandle]["T000000"]["pCount"] == 1
    assert theIndex._fileIndex[pHandle]["T000000"]["synopsis"] == ""

    assert theProject.closeProject() is True

# END Test testCoreIndex_ScanText


@pytest.mark.core
def testCoreIndex_ExtractData(nwMinimal, mockGUI):
    """Check the index data extraction functions.
    """
    theProject = NWProject(mockGUI)
    theProject.projTree.setSeed(42)
    assert theProject.openProject(nwMinimal) is True

    theIndex = NWIndex(theProject)
    nHandle = theProject.newFile("Hello", nwItemClass.NOVEL,     "a508bb932959c")
    cHandle = theProject.newFile("Jane",  nwItemClass.CHARACTER, "afb3043c7b2b3")

    assert theIndex.getNovelData("", "") is None
    assert theIndex.getNovelData("a508bb932959c", "") is None

    assert theIndex.scanText(cHandle, (
        "# Jane Smith\n"
        "@tag: Jane\n"
    ))
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n"
    ))

    # The novel structure should contain the pointer to the novel file header
    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure():
        theKeys.append(aKey)

    assert theKeys == ["%s:T000001" % nHandle]

    # Check that excluded files can be skipped
    theProject.projTree[nHandle].setExported(False)

    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure(skipExcluded=False):
        theKeys.append(aKey)

    assert theKeys == ["%s:T000001" % nHandle]

    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure(skipExcluded=True):
        theKeys.append(aKey)

    assert theKeys == []

    theKeys = []
    for aKey, _, _, _ in theIndex.novelStructure():
        theKeys.append(aKey)

    assert theKeys == []

    # The novel file should have the correct counts
    cC, wC, pC = theIndex.getCounts(nHandle)
    assert cC == 62  # Characters in text and title only
    assert wC == 12  # Words in text and title only
    assert pC == 2   # Paragraphs in text only

    # getReferences
    # =============

    # Look up an ivalid handle
    theRefs = theIndex.getReferences("Not a handle")
    assert theRefs["@pov"] == []
    assert theRefs["@char"] == []

    # The novel file should now refer to Jane as @pov and @char
    theRefs = theIndex.getReferences(nHandle)
    assert theRefs["@pov"] == ["Jane"]
    assert theRefs["@char"] == ["Jane"]

    # getBackReferenceList
    # ====================

    # None handle should return an empty dict
    assert theIndex.getBackReferenceList(None) == {}

    # The character file should have a record of the reference from the novel file
    theRefs = theIndex.getBackReferenceList(cHandle)
    assert theRefs == {nHandle: "T000001"}

    # getTagSource
    # ============

    assert theIndex.getTagSource("Jane") == (cHandle, 2, "T000001")
    assert theIndex.getTagSource("John") == (None, 0, "T000000")

    # getCounts
    # =========
    # For whole text and sections

    # Get section counts for a novel file
    assert theIndex.scanText(nHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n\n"
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really. She's still awesome though.\n"
    ))
    # Whole document
    cC, wC, pC = theIndex.getCounts(nHandle)
    assert cC == 152
    assert wC == 28
    assert pC == 4

    # First part
    cC, wC, pC = theIndex.getCounts(nHandle, "T000001")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # Second part
    cC, wC, pC = theIndex.getCounts(nHandle, "T000011")
    assert cC == 90
    assert wC == 16
    assert pC == 2

    # Get section counts for a note file
    assert theIndex.scanText(cHandle, (
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really.\n\n"
        "# Hello World!\n"
        "@pov: Jane\n"
        "@char: Jane\n\n"
        "% this is a comment\n\n"
        "This is a story about Jane Smith.\n\n"
        "Well, not really. She's still awesome though.\n"
    ))
    # Whole document
    cC, wC, pC = theIndex.getCounts(cHandle)
    assert cC == 152
    assert wC == 28
    assert pC == 4

    # First part
    cC, wC, pC = theIndex.getCounts(cHandle, "T000001")
    assert cC == 62
    assert wC == 12
    assert pC == 2

    # Second part
    cC, wC, pC = theIndex.getCounts(cHandle, "T000011")
    assert cC == 90
    assert wC == 16
    assert pC == 2

    # Novel Stats
    # ===========

    hHandle = theProject.newFile("Chapter", nwItemClass.NOVEL, "a508bb932959c")
    sHandle = theProject.newFile("Scene One", nwItemClass.NOVEL, "a508bb932959c")
    tHandle = theProject.newFile("Scene Two", nwItemClass.NOVEL, "a508bb932959c")

    theProject.projTree[hHandle].itemLayout == nwItemLayout.DOCUMENT
    theProject.projTree[sHandle].itemLayout == nwItemLayout.DOCUMENT
    theProject.projTree[tHandle].itemLayout == nwItemLayout.DOCUMENT

    assert theIndex.scanText(hHandle, "## Chapter One\n\n")
    assert theIndex.scanText(sHandle, "### Scene One\n\n")
    assert theIndex.scanText(tHandle, "### Scene Two\n\n")

    assert theIndex._listNovelHandles(False) == [nHandle, hHandle, sHandle, tHandle]
    assert theIndex._listNovelHandles(True) == [hHandle, sHandle, tHandle]

    # Add a fake handle to the tree and check that it's ignored
    theProject.projTree._treeOrder.append("0000000000000")
    assert theIndex._listNovelHandles(False) == [nHandle, hHandle, sHandle, tHandle]
    theProject.projTree._treeOrder.remove("0000000000000")

    # Extract stats
    assert theIndex.getNovelWordCount(False) == 34
    assert theIndex.getNovelWordCount(True) == 6
    assert theIndex.getNovelTitleCounts(False) == [0, 2, 1, 2, 0]
    assert theIndex.getNovelTitleCounts(True) == [0, 0, 1, 2, 0]

    # Table of Contents
    assert theIndex.getTableOfContents(0, True) == []
    assert theIndex.getTableOfContents(1, True) == []
    assert theIndex.getTableOfContents(2, True) == [
        ("%s:T000001" % hHandle, 2, "Chapter One", 6),
    ]
    assert theIndex.getTableOfContents(3, True) == [
        ("%s:T000001" % hHandle, 2, "Chapter One", 2),
        ("%s:T000001" % sHandle, 3, "Scene One", 2),
        ("%s:T000001" % tHandle, 3, "Scene Two", 2),
    ]

    assert theIndex.getTableOfContents(0, False) == []
    assert theIndex.getTableOfContents(1, False) == [
        ("%s:T000001" % nHandle, 1, "Hello World!", 12),
        ("%s:T000011" % nHandle, 1, "Hello World!", 22),
    ]

    # Header Word Counts
    bHandle = "0000000000000"
    assert theIndex.getHandleWordCounts(bHandle) == []
    assert theIndex.getHandleWordCounts(hHandle) == [("%s:T000001" % hHandle, 2)]
    assert theIndex.getHandleWordCounts(sHandle) == [("%s:T000001" % sHandle, 2)]
    assert theIndex.getHandleWordCounts(tHandle) == [("%s:T000001" % tHandle, 2)]
    assert theIndex.getHandleWordCounts(nHandle) == [
        ("%s:T000001" % nHandle, 12), ("%s:T000011" % nHandle, 16)
    ]

    assert theProject.closeProject()

    # Header Record
    bHandle = "0000000000000"
    assert theIndex.getHandleHeaders(bHandle) == []
    assert theIndex.getHandleHeaders(hHandle) == [("T000001", "H2", "Chapter One")]
    assert theIndex.getHandleHeaders(sHandle) == [("T000001", "H3", "Scene One")]
    assert theIndex.getHandleHeaders(tHandle) == [("T000001", "H3", "Scene Two")]
    assert theIndex.getHandleHeaders(nHandle) == [
        ("T000001", "H1", "Hello World!"), ("T000011", "H1", "Hello World!")
    ]

# END Test testCoreIndex_ExtractData


@pytest.mark.core
def testCoreIndex_CheckTagIndex(mockGUI):
    """Test the tag index checker.
    """
    theProject = NWProject(mockGUI)
    theIndex = NWIndex(theProject)

    # Valid Index
    theIndex._tagIndex = {
        "John": [3, "14298de4d9524", "CHARACTER", "T000001"],
        "Jane": [3, "bb2c23b3c42cc", "CHARACTER", "T000001"],
    }
    assert theIndex._checkTagIndex() is None

    # Wrong Key Type
    theIndex._tagIndex = {
        "John": [3, "14298de4d9524", "CHARACTER", "T000001"],
        123456: [3, "bb2c23b3c42cc", "CHARACTER", "T000001"],
    }
    with pytest.raises(KeyError):
        theIndex._checkTagIndex()

    # Wrong Length
    theIndex._tagIndex = {
        "John": [3, "14298de4d9524", "CHARACTER", "T000001"],
        "Jane": [3, "bb2c23b3c42cc", "CHARACTER", "T000001", "Stuff"],
    }
    with pytest.raises(IndexError):
        theIndex._checkTagIndex()

    # Wrong Type of Entry 0
    theIndex._tagIndex = {
        "John": [3, "14298de4d9524", "CHARACTER", "T000001"],
        "Jane": ["3", "bb2c23b3c42cc", "CHARACTER", "T000001"],
    }
    with pytest.raises(ValueError):
        theIndex._checkTagIndex()

    # Wrong Type of Entry 1
    theIndex._tagIndex = {
        "John": [3, "14298de4d9524", "CHARACTER", "T000001"],
        "Jane": [3, 0xbb2c23b3c42cc, "CHARACTER", "T000001"],
    }
    with pytest.raises(ValueError):
        theIndex._checkTagIndex()

    # Wrong Type of Entry 2
    theIndex._tagIndex = {
        "John": [3, "14298de4d9524", "CHARACTER", "T000001"],
        "Jane": [3, "bb2c23b3c42cc", "INVALID_CLASS", "T000001"],
    }
    with pytest.raises(ValueError):
        theIndex._checkTagIndex()

    # Wrong Type of Entry 3
    theIndex._tagIndex = {
        "John": [3, "14298de4d9524", "CHARACTER", "T000001"],
        "Jane": [3, "bb2c23b3c42cc", "CHARACTER", "INVALID"],
    }
    with pytest.raises(ValueError):
        theIndex._checkTagIndex()

# END Test testCoreIndex_CheckTagIndex


@pytest.mark.core
def testCoreIndex_CheckRefIndex(mockGUI):
    """Test the reference index checker.
    """
    theProject = NWProject(mockGUI)
    theIndex = NWIndex(theProject)

    # Valid Index
    theIndex._refIndex = {
        "6a2d6d5f4f401": {
            "T000000": [],
            "T000001": [[3, "@pov", "Jane"], [4, "@location", "Earth"]],
        }
    }
    assert theIndex._checkRefIndex() is None

    # Invalid Handle
    theIndex._refIndex = {
        "Ha2d6d5f4f401": {
            "T000000": [],
            "T000001": [[3, "@pov", "Jane"], [4, "@location", "Earth"]],
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkRefIndex()

    # Invalid Title
    theIndex._refIndex = {
        "6a2d6d5f4f401": {
            "T000000": [],
            "INVALID": [[3, "@pov", "Jane"], [4, "@location", "Earth"]],
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkRefIndex()

    # Wrong Length
    theIndex._refIndex = {
        "6a2d6d5f4f401": {
            "T000000": [],
            "T000001": [[3, "@pov", "Jane"], [4, "@location", "Earth", "Stuff"]],
        }
    }
    with pytest.raises(IndexError):
        theIndex._checkRefIndex()

    # Wrong Type of Entry 0
    theIndex._refIndex = {
        "6a2d6d5f4f401": {
            "T000000": [],
            "T000001": [[3, "@pov", "Jane"], ["4", "@location", "Earth"]],
        }
    }
    with pytest.raises(ValueError):
        theIndex._checkRefIndex()

    # Wrong Type of Entry 1
    theIndex._refIndex = {
        "6a2d6d5f4f401": {
            "T000000": [],
            "T000001": [[3, "@pov", "Jane"], [4, "@stuff", "Earth"]],
        }
    }
    with pytest.raises(ValueError):
        theIndex._checkRefIndex()

    # Wrong Type of Entry 2
    theIndex._refIndex = {
        "6a2d6d5f4f401": {
            "T000000": [],
            "T000001": [[3, "@pov", "Jane"], [4, "@location", 123456]],
        }
    }
    with pytest.raises(ValueError):
        theIndex._checkRefIndex()

# END Test testCoreIndex_CheckRefIndex


@pytest.mark.core
def testCoreIndex_CheckFileIndex(mockGUI):
    """Test the file index checker.
    """
    theProject = NWProject(mockGUI)
    theIndex = NWIndex(theProject)

    # Valid Index
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    theIndex._fileIndex = theIndex._fileIndex.copy()
    assert theIndex._checkFileIndex() is None

    # Invalid Handle
    theIndex._fileIndex = {
        "H3b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkFileIndex()

    # Invalid Title
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "INVALID": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkFileIndex()

    # Wrong Length
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
                "stuff": None
            }
        }
    }
    with pytest.raises(IndexError):
        theIndex._checkFileIndex()

    # Missing Keys
    # ============

    # Missing 'level'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "stuff": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkFileIndex()

    # Missing 'title'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "stuff": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkFileIndex()

    # Missing 'layout'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "stuff": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkFileIndex()

    # Missing 'cCount'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "stuff": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkFileIndex()

    # Missing 'wCount'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "stuff": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkFileIndex()

    # Missing 'pCount'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "stuff": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkFileIndex()

    # Missing 'synopsis'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "stuff": "text",
            }
        }
    }
    with pytest.raises(KeyError):
        theIndex._checkFileIndex()

    # Wrong Types
    # ===========

    # Wrong Type for 'level'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "XX",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(ValueError):
        theIndex._checkFileIndex()

    # Wrong Type for 'title'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": 12345678,
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(ValueError):
        theIndex._checkFileIndex()

    # Wrong Type for 'layout'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "INVALID",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(ValueError):
        theIndex._checkFileIndex()

    # Wrong Type for 'cCount'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": "72",
                "wCount": 15,
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(ValueError):
        theIndex._checkFileIndex()

    # Wrong Type for 'wCount'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": "15",
                "pCount": 2,
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(ValueError):
        theIndex._checkFileIndex()

    # Wrong Type for 'pCount'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": "2",
                "synopsis": "text",
            }
        }
    }
    with pytest.raises(ValueError):
        theIndex._checkFileIndex()

    # Wrong Type for 'synopsis'
    theIndex._fileIndex = {
        "53b69b83cdafc": {
            "T000001": {
                "level": "H1",
                "title": "My Novel",
                "layout": "DOCUMENT",
                "cCount": 72,
                "wCount": 15,
                "pCount": 2,
                "synopsis": 123456,
            }
        }
    }
    with pytest.raises(ValueError):
        theIndex._checkFileIndex()

# END Test testCoreIndex_CheckFileIndex


@pytest.mark.core
def testCoreIndex_CheckFileMeta(mockGUI):
    """Test the file meta checker.
    """
    theProject = NWProject(mockGUI)
    theIndex = NWIndex(theProject)

    # Valid Index
    theIndex._fileMeta = {
        "53b69b83cdafc": ["H0", 72, 15, 2],
        "974e400180a99": ["H0", 210, 40, 2],
    }
    assert theIndex._checkFileMeta() is None

    # Invalid Handle
    theIndex._fileMeta = {
        "53b69b83cdafc": ["H0", 72, 15, 2],
        "h74e400180a99": ["H0", 210, 40, 2],
    }
    with pytest.raises(KeyError):
        theIndex._checkFileMeta()

    # Wrong Length
    theIndex._fileMeta = {
        "53b69b83cdafc": ["H0", 72, 15, 2],
        "974e400180a99": ["H0", 210, 40, 2, 8],
    }
    with pytest.raises(IndexError):
        theIndex._checkFileMeta()

    # Content of Entry 0
    theIndex._fileMeta = {
        "53b69b83cdafc": ["H0", 72, 15, 2],
        "974e400180a99": ["XXX", 210, 40, 2],
    }
    with pytest.raises(ValueError):
        theIndex._checkFileMeta()

    # Type of Entry 1
    theIndex._fileMeta = {
        "53b69b83cdafc": ["H0", 72, 15, 2],
        "974e400180a99": ["H0", "210", 40, 2],
    }
    with pytest.raises(ValueError):
        theIndex._checkFileMeta()

    # Type of Entry 2
    theIndex._fileMeta = {
        "53b69b83cdafc": ["H0", 72, 15, 2],
        "974e400180a99": ["H0", 210, "40", 2],
    }
    with pytest.raises(ValueError):
        theIndex._checkFileMeta()

    # Type of Entry 3
    theIndex._fileMeta = {
        "53b69b83cdafc": ["H0", 72, 15, 2],
        "974e400180a99": ["H0", 210, 40, "2"],
    }
    with pytest.raises(ValueError):
        theIndex._checkFileMeta()

# END Test testCoreIndex_CheckTextCounts


@pytest.mark.core
def testCoreIndex_CountWords():
    """Test the word counter and the exclusion filers.
    """
    # Non-Text
    assert countWords(None) == (0, 0, 0)
    assert countWords(1234) == (0, 0, 0)

    # General Text
    cC, wC, pC = countWords((
        "# Heading One\n"
        "## Heading Two\n"
        "### Heading Three\n"
        "#### Heading Four\n\n"
        "@tag: value\n\n"
        "% A comment that should not be counted.\n\n"
        "The first paragraph.\n\n"
        "The second paragraph.\n\n\n"
        "The third paragraph.\n\n"
        "Dashes\u2013and even longer\u2014dashes."
    ))
    assert cC == 138
    assert wC == 22
    assert pC == 4

    # Text Alignment
    cC, wC, pC = countWords((
        "# Title\n\n"
        "Left aligned<<\n\n"
        "Left aligned <<\n\n"
        "Right indent<\n\n"
        "Right indent <\n\n"
    ))
    assert cC == 53
    assert wC == 9
    assert pC == 4

    cC, wC, pC = countWords((
        "# Title\n\n"
        ">>Right aligned\n\n"
        ">> Right aligned\n\n"
        ">Left indent\n\n"
        "> Left indent\n\n"
    ))
    assert cC == 53
    assert wC == 9
    assert pC == 4

    cC, wC, pC = countWords((
        "# Title\n\n"
        ">>Centre aligned<<\n\n"
        ">> Centre aligned <<\n\n"
        ">Double indent<\n\n"
        "> Double indent <\n\n"
    ))
    assert cC == 59
    assert wC == 9
    assert pC == 4

    # Formatting Codes
    cC, wC, pC = countWords((
        "Some text\n\n"
        "[NEWPAGE]\n\n"
        "more text\n\n"
        "[NEW PAGE]]\n\n"
        "even more text\n\n"
        "[VSPACE]\n\n"
        "and some final text\n\n"
        "[VSPACE:4]\n\n"
        "THE END\n\n"
    ))
    assert cC == 58
    assert wC == 13
    assert pC == 5

# END Test testCoreIndex_CountWords
